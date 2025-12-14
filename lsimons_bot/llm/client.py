import logging
from collections.abc import Iterable

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

logger = logging.getLogger(__name__)


class LLMClient:
    client: AsyncOpenAI
    model: str

    def __init__(self, base_url: str, api_key: str, model: str = "gpt-4") -> None:
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    async def chat_completion(
        self,
        messages: Iterable[ChatCompletionMessageParam],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        logger.debug(">> LLMClient.chat_completion(%s)", messages)
        content = ""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
        except Exception as e:
            logger.error("Error communicating with LLM: %s", e)
            content = f"Error communicating with LLM: {e}"

        logger.debug("<< LLMClient.chat_completion('%s')", content)
        return content
