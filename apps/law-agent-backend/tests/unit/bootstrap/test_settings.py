import pytest
from pydantic import ValidationError

from agent.bootstrap.settings import Environment, Settings


def test_settings_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Settings(environment=Environment.TEST, unknown_value="x")
