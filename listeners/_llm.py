"""LiteLLM integration module for AI assistant interactions.

Provides a wrapper around the OpenAI SDK configured to work with a LiteLLM proxy,
supporting streaming responses, error handling, and full type annotations.
"""

import logging
import os
from typing import AsyncGenerator, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LiteLLMClient:
    """OpenAI client wrapper pointing to LiteLLM proxy.

    Handles streaming, error handling, and environment variable configuration
    for LiteLLM proxy interactions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        """Initialize LiteLLM client.

        Args:
            api_key: LiteLLM API key. Defaults to LITELLM_API_KEY env var.
            base_url: LiteLLM proxy URL. Defaults to LITELLM_API_BASE env var
                     or https://litellm.sbp.ai/
            timeout: Request timeout in seconds. Defaults to 60.

        Raises:
            ValueError: If api_key is not provided or available from environment.
        """
        self.api_key = api_key or os.getenv("LITELLM_API_KEY")
        if not self.api_key:
            raise ValueError("LITELLM_API_KEY must be provided or set as environment variable")

        self.base_url = base_url or os.getenv("LITELLM_API_BASE", "https://litellm.sbp.ai/")
        self.timeout = timeout

        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
        )

    async def stream_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion from LiteLLM proxy.

        Yields text chunks as they arrive from the streaming response.

        Args:
            model: Model identifier (e.g., "openai/gpt-4", "anthropic/claude-3-sonnet")
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0.0-2.0). Defaults to 0.7.
            max_tokens: Maximum tokens in response. Defaults to None (unlimited).
            system_prompt: Optional system message to prepend to messages.

        Yields:
            Text chunks from the model response.

        Raises:
            Exception: If the request fails (API errors, connection errors, etc.)
        """
        # Prepend system prompt if provided
        request_messages = messages
        if system_prompt:
            request_messages = [
                {"role": "system", "content": system_prompt},
                *messages,
            ]

        try:
            stream = await self._client.chat.completions.create(
                model=model,
                messages=request_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"LiteLLM streaming error for model {model}: {str(e)}")
            raise

    async def get_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Get a non-streaming completion from LiteLLM proxy.

        Collects all chunks from the streaming response and returns the full text.

        Args:
            model: Model identifier (e.g., "openai/gpt-4")
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0.0-2.0). Defaults to 0.7.
            max_tokens: Maximum tokens in response. Defaults to None (unlimited).
            system_prompt: Optional system message to prepend to messages.

        Returns:
            Complete response text from the model.

        Raises:
            Exception: If the request fails.
        """
        response_text = ""
        async for chunk in self.stream_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        ):
            response_text += chunk

        return response_text

    async def close(self) -> None:
        """Close the underlying HTTP client connection."""
        await self._client.close()

    async def __aenter__(self) -> "LiteLLMClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


def create_llm_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: float = 60.0,
) -> LiteLLMClient:
    """Factory function to create a configured LiteLLM client.

    Args:
        api_key: LiteLLM API key. Defaults to LITELLM_API_KEY env var.
        base_url: LiteLLM proxy URL. Defaults to LITELLM_API_BASE env var.
        timeout: Request timeout in seconds. Defaults to 60.

    Returns:
        Configured LiteLLMClient instance.

    Raises:
        ValueError: If api_key is not provided or available from environment.
    """
    return LiteLLMClient(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
    )
