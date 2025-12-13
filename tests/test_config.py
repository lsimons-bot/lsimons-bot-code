import os
from unittest.mock import patch

import pytest

from lsimons_bot.config import (
    get_env_vars,
    validate_env_vars,
)


class TestValidateEnvVars:
    def test_all_variables_present(self) -> None:
        with patch.dict(
            os.environ,
            {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3"},
            clear=True,
        ):
            result = validate_env_vars(["VAR1", "VAR2", "VAR3"])
            assert result == {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3"}

    def test_missing_single_variable(self) -> None:
        with patch.dict(os.environ, {"VAR1": "value1"}, clear=True):
            with pytest.raises(match="Missing required environment variables: VAR2"):
                validate_env_vars(["VAR1", "VAR2"])

    def test_missing_multiple_variables(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                match="Missing required environment variables: VAR1, VAR2, VAR3",
            ):
                validate_env_vars(["VAR1", "VAR2", "VAR3"])

    def test_empty_string_treated_as_missing(self) -> None:
        with patch.dict(os.environ, {"VAR1": ""}, clear=True):
            with pytest.raises(match="Missing required environment variables: VAR1"):
                validate_env_vars(["VAR1"])

    def test_empty_list(self) -> None:
        result = validate_env_vars([])
        assert result == {}


class TestGetEnvVars:
    def test_all_env_vars_present(self) -> None:
        with patch.dict(
            os.environ,
            {"SLACK_BOT_TOKEN": "xoxb-test", "SLACK_APP_TOKEN": "xapp-test"},
            clear=True,
        ):
            result = get_env_vars()
            assert result == {
                "SLACK_BOT_TOKEN": "xoxb-test",
                "SLACK_APP_TOKEN": "xapp-test",
            }

    def test_missing_slack_bot_token(self) -> None:
        with patch.dict(os.environ, {"SLACK_APP_TOKEN": "xapp-test"}, clear=True):
            with pytest.raises(
                match="Missing required environment variables: SLACK_BOT_TOKEN",
            ):
                get_env_vars()

    def test_missing_slack_app_token(self) -> None:
        """Test failure when SLACK_APP_TOKEN is missing."""
        with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test"}, clear=True):
            with pytest.raises(
                match="Missing required environment variables: SLACK_APP_TOKEN",
            ):
                get_env_vars()

    def test_missing_all__vars(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                match="Missing required environment variables: SLACK_BOT_TOKEN, SLACK_APP_TOKEN",
            ):
                get_env_vars()
