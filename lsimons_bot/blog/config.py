import os

REQUIRED_VARS = [
    "WORDPRESS_USERNAME",
    "WORDPRESS_APPLICATION_PASSWORD",
    "WORDPRESS_CLIENT_ID",
    "WORDPRESS_CLIENT_SECRET",
    "WORDPRESS_SITE_ID",
    "GITHUB_TOKEN",
    "LLM_BASE_URL",
    "LLM_AUTH_TOKEN",
    "LLM_DEFAULT_MODEL",
]


def validate_env_vars(required_vars: list[str]) -> dict[str, str]:
    missing_vars: list[str] = []
    env_values: dict[str, str] = {}

    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        else:
            env_values[var] = value

    if missing_vars:
        raise Exception(f"Missing required environment variables: {', '.join(missing_vars)}")

    return env_values


def get_env_vars() -> dict[str, str]:
    return validate_env_vars(REQUIRED_VARS)
