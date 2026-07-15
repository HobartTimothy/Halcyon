import pytest

from unittest.mock import patch, MagicMock
from lows_agent.llm.factory import get_chat_model



@pytest.fixture(autouse=True)
def clear_lru_cache():
    """
    【极其关键】每次测试前后自动清空函数的 lru_cache。
    如果不加这个，不同测试用例之间会因为共用同一个缓存而互相污染，导致断言失败。
    """
    get_chat_model.cache_clear()
    yield
    get_chat_model.cache_clear()

@pytest.fixture
def mock_settings():
    """
    构造一个虚拟的 Settings 对象，用于隔离真实的配置。
    """

    mock = MagicMock()
    mock.openapi_model = "gpt-4o-mini"
    mock.openai_api_key = "test-sk-12345"
    mock.openai_base_url = "https://api.test.com/v1"
    return mock

# ==========================================
# Test Cases (测试用例)
# ==========================================

@patch("lows_agent.llm.factory.get_settings")
def test_get_chat_model():
    model = get_chat_model()

    response = model.invoke("你是谁?")
    print(response)


# 注意：patch 的路径必须是你要测试的函数所在的模块，而不是它原始定义的模块
@patch("lows_agent.llm.factory.get_settings")
@patch("lows_agent.llm.factory.ChatOpenAI")
def test_get_chat_model_initialization_params(mock_chat_openai_class, mock_get_settings, mock_settings):
    """
    测试 1：验证函数是否正确读取了配置，并以正确的参数初始化了 ChatOpenAI。
    """
    # 注入虚拟配置
    mock_get_settings.return_value = mock_settings

    # 执行函数
    temperature_val = 0.7
    result = get_chat_model(temperature=temperature_val)

    # 验证获取配置的方法被调用
    mock_get_settings.assert_called_once()

    # 验证 ChatOpenAI 被正确的参数实例化
    mock_chat_openai_class.assert_called_once_with(
        max_retries=2,
        timeout=30.0,
        temperature=temperature_val,
        model="gpt-4o-mini",
        api_key="test-sk-12345",
        base_url="https://api.test.com/v1"
    )

    # 验证函数的返回值正是被 Mock 的 ChatOpenAI 实例
    assert result == mock_chat_openai_class.return_value


@patch("lows_agent.llm.factory.get_settings")
@patch("lows_agent.llm.factory.ChatOpenAI")
def test_get_chat_model_lru_cache_behavior(mock_chat_openai_class, mock_get_settings, mock_settings):
    """
    测试 2：验证 @lru_cache 缓存机制是否严格生效。
    """
    
    mock_get_settings.return_value = mock_settings

    # 连续两次使用【相同参数】调用
    model_first_call = get_chat_model(temperature=0.0)
    model_second_call = get_chat_model(temperature=0.0)

    # 断言 1：两次拿到的模型对象在内存中必须是同一个实例 (is 比较)
    assert model_first_call is model_second_call

    # 断言 2：底层的 ChatOpenAI 类应该【只被实例化了一次】
    mock_chat_openai_class.assert_called_once()

    # 使用【不同参数】发起第三次调用
    model_third_call = get_chat_model(temperature=0.5)

    # 断言 3：参数改变后，缓存不命中，应该返回一个全新的对象
    assert model_third_call is not model_first_call

    # 断言 4：底层的 ChatOpenAI 类被实例化了第二次
    assert mock_chat_openai_class.call_count == 2