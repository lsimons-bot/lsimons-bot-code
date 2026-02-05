import os
from unittest.mock import patch

import pytest

from lsimons_bot.blog.config import get_env_vars, validate_env_vars


class TestValidateEnvVars:
    def test_all_variables_present(self) -> None:
        with patch.dict(os.environ, {"VAR1": "value1", "VAR2": "value2"}, clear=True):
            result = validate_env_vars(["VAR1", "VAR2"])
            assert result == {"VAR1": "value1", "VAR2": "value2"}

    def test_missing_variables(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception, match="Missing required environment variables"):
                validate_env_vars(["VAR1", "VAR2"])


class TestGetEnvVars:
    def test_all_env_vars_present(self) -> None:
        env = {
            "WORDPRESS_USERNAME": "wp-user",
            "WORDPRESS_APPLICATION_PASSWORD": "wp-app-pass",
            "WORDPRESS_SITE_ID": "site123",
            "GITHUB_TOKEN": "gh-token",
            "LLM_BASE_URL": "http://localhost:8000",
            "LLM_AUTH_TOKEN": "test-key",
            "LLM_DEFAULT_MODEL": "gpt-4",
        }
        with patch.dict(os.environ, env, clear=True):
            result = get_env_vars()
            assert result == env

    def test_missing_env_vars(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception, match="Missing required environment variables"):
                get_env_vars()
