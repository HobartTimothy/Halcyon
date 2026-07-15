from __future__ import annotations

import ipaddress
import socket
from dataclasses import asdict, dataclass
from functools import lru_cache
from io import BytesIO
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx
from bs4 import BeautifulSoup
from langchain.tools import tool
from langchain_tavily import TavilyExtract
from pypdf import PdfReader



DEFAULT_MAX_BYTES = 12 * 1024 * 1024
DEFAULT_MAX_CHARS = 24_000
MAX_REDIRECTS = 5
USER_AGENT = "lows-legal-search-agent/1.0 (+legal-research)"


class PageReadError(RuntimeError):
    """Raised when a public page cannot be downloaded or parsed."""


class UnsafeUrlError(PageReadError):
    """Raised when a URL could target a local or private network resource."""


@dataclass(frozen=True, slots=True)
class PageDocument:
    url: str
    title: str | None
    content: str
    content_type: str
    reader: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_public_ip(value: str) -> bool:
    address = ipaddress.ip_address(value)
    return address.is_global


def validate_public_url(url: str, *, resolve_dns: bool = True) -> str:
    """Validate HTTP(S) URLs and reject obvious SSRF targets."""
    try:
        parts = urlsplit(url.strip())
    except (AttributeError, ValueError) as exc:
        raise UnsafeUrlError("URL 格式无效") from exc

    if parts.scheme not in {"http", "https"}:
        raise UnsafeUrlError("仅允许 http 或 https URL")
    if parts.username or parts.password:
        raise UnsafeUrlError("URL 不得包含用户名或密码")
    if not parts.hostname:
        raise UnsafeUrlError("URL 缺少主机名")
    try:
        port = parts.port
    except ValueError as exc:
        raise UnsafeUrlError("URL 端口无效") from exc

    host = parts.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
        raise UnsafeUrlError("不允许访问本地主机")

    try:
        if not _is_public_ip(host):
            raise UnsafeUrlError("不允许访问私有或保留地址")
        return url
    except ValueError:
        pass

    if not resolve_dns:
        return url

    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(
                host,
                port or (443 if parts.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        }
    except socket.gaierror as exc:
        raise PageReadError("域名无法解析") from exc

    if not addresses or any(not _is_public_ip(value) for value in addresses):
        raise UnsafeUrlError("域名解析到了私有或保留地址")
    return url


def _download_page(
    url: str,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> tuple[str, str, bytes]:
    current_url = validate_public_url(url)
    timeout = httpx.Timeout(20.0, connect=6.0)

    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        for _ in range(MAX_REDIRECTS + 1):
            with client.stream(
                "GET",
                current_url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.5",
                },
            ) as response:
                if response.status_code in {301, 302, 303, 307, 308}:
                    location = response.headers.get("location")
                    if not location:
                        raise PageReadError("重定向响应缺少 Location")
                    current_url = validate_public_url(urljoin(current_url, location))
                    continue

                response.raise_for_status()
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > max_bytes:
                    raise PageReadError("页面超过允许的最大大小")

                body = bytearray()
                for chunk in response.iter_bytes():
                    body.extend(chunk)
                    if len(body) > max_bytes:
                        raise PageReadError("页面超过允许的最大大小")

                content_type = response.headers.get("content-type", "").lower()
                return current_url, content_type, bytes(body)

    raise PageReadError("页面重定向次数过多")


def _extract_pdf(data: bytes, *, max_chars: int) -> tuple[str | None, str]:
    try:
        reader = PdfReader(BytesIO(data))
        page_text = []
        current_length = 0
        for page in reader.pages:
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            remaining = max_chars - current_length
            if remaining <= 0:
                break
            page_text.append(text[:remaining])
            current_length += len(page_text[-1])

        metadata_title = None
        if reader.metadata:
            metadata_title = getattr(reader.metadata, "title", None)
    except Exception as exc:
        raise PageReadError("PDF 正文解析失败") from exc

    content = "\n\n".join(page_text).strip()
    if not content:
        raise PageReadError("PDF 未提取到可读文字，可能是扫描件")
    return metadata_title, content


def _extract_html(data: bytes, *, max_chars: int) -> tuple[str | None, str]:
    try:
        soup = BeautifulSoup(data, "html.parser")
        for element in soup.find_all(
            ["script", "style", "noscript", "svg", "nav", "header", "footer", "aside", "form"]
        ):
            element.decompose()

        title = soup.title.get_text(" ", strip=True) if soup.title else None
        root = soup.find("article") or soup.find("main") or soup.body or soup
        lines = [
            line.strip()
            for line in root.get_text("\n").splitlines()
            if line.strip()
        ]
        content = "\n".join(lines)[:max_chars]
    except Exception as exc:
        raise PageReadError("HTML 正文解析失败") from exc

    if not content:
        raise PageReadError("HTML 页面未提取到可读正文")
    return title, content


def read_page_direct(
    url: str,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> dict[str, Any]:
    """Download and parse one public HTML or text-based PDF page."""
    final_url, content_type, data = _download_page(url)
    is_pdf = "application/pdf" in content_type or data.startswith(b"%PDF-")

    if is_pdf:
        title, content = _extract_pdf(data, max_chars=max_chars)
        reader_name = "direct_pdf"
        normalized_content_type = "application/pdf"
    else:
        title, content = _extract_html(data, max_chars=max_chars)
        reader_name = "direct_html"
        normalized_content_type = content_type or "text/html"

    return PageDocument(
        url=final_url,
        title=title,
        content=content,
        content_type=normalized_content_type,
        reader=reader_name,
    ).to_dict()


@lru_cache(maxsize=1)
def _get_tavily_extract() -> TavilyExtract:
    return TavilyExtract(extract_depth="advanced", include_images=False)


def extract_page_with_tavily(
    url: str,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> dict[str, Any]:
    """Fallback extraction for dynamic or direct-download-resistant pages."""
    validate_public_url(url, resolve_dns=False)
    response = _get_tavily_extract().invoke({"urls": [url]})
    if not isinstance(response, dict):
        raise PageReadError("Tavily Extract 返回了未知格式")

    for item in response.get("results", []):
        if item.get("url") == url or item.get("raw_content"):
            content = str(item.get("raw_content") or "").strip()[:max_chars]
            if content:
                return PageDocument(
                    url=str(item.get("url") or url),
                    title=None,
                    content=content,
                    content_type="text/markdown",
                    reader="tavily_extract",
                ).to_dict()
    raise PageReadError("Tavily Extract 未返回正文")


@tool
def read_legal_page(url: str) -> dict[str, Any]:
    """读取法律资料原文，支持 HTML 和文字型 PDF。

    工具先直接读取页面；动态网页、反爬页面或直读失败时自动使用
    Tavily Extract。引用具体条款前应调用本工具核验正文。
    """
    try:
        result = read_page_direct(url)
    except UnsafeUrlError as exc:
        return {
            "ok": False,
            "url": url,
            "error": "unsafe_url",
            "message": str(exc),
        }
    except Exception as direct_exc:
        try:
            result = extract_page_with_tavily(url)
        except Exception as fallback_exc:
            return {
                "ok": False,
                "url": url,
                "error": "page_read_failed",
                "direct_error": type(direct_exc).__name__,
                "fallback_error": type(fallback_exc).__name__,
            }

    return {"ok": True, **result}