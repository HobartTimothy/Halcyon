from pathlib import Path

import yaml

COMPOSE_FILE = Path(__file__).parents[5] / "deploy" / "compose" / "compose.yml"


def load_services() -> dict[str, dict[str, object]]:
    document = yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))
    return document["services"]


def test_compose_declares_foundation_services() -> None:
    services = load_services()
    assert {
        "postgres",
        "valkey",
        "rabbitmq",
        "seaweedfs",
        "litellm",
        "api",
        "stream-api",
        "agent-worker",
        "web",
        "nginx",
    }.issubset(services)


def test_data_services_are_not_bound_to_host_ports() -> None:
    services = load_services()
    for service_name in ("postgres", "valkey", "rabbitmq"):
        assert "ports" not in services[service_name]
