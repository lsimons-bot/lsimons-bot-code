import random
from collections.abc import Iterable

from openai.types.chat import ChatCompletionMessageParam

type Message = ChatCompletionMessageParam
type Messages = Iterable[Message]


LOADING_MESSAGES = [
    "Rebooting the mission-critical mindset…",
    "Checking the coffee machine's health…",
    "Syncing with the SBP cloud of excellence…",
    "Convincing the AI to follow compliance…",
    "Running a quick RAG status on your patience…",
    "Asking engineers if it's automated yet…",
    "Encrypting with extra Dutch precision…",
    "Scaling up reliability while we think…",
    "Calling a stand-up with the AI…",
    "Deploying your answer to production quality…",
]

RESPONSE_MESSAGES = [
    "Interesting perspective. Can you expand on that?",
    "What leads you to that conclusion?",
    "Could you clarify what you mean?",
    "Can you share an example from your experience?",
    "How does this connect to reliability or flexibility?",
    "That’s a bold statement. What’s behind it?",
    "What outcome would you expect from that?",
    "Can you walk me through your reasoning?",
    "What would success look like in this scenario?",
    "How does this align with our mission-critical approach?",
]

SYSTEM_CONTENT = """
You're an assistant in a Slack workspace.
You don't have access to anything in the Slack workspace except for the current thread.
You also don't have access to any external database or knowledge base or API.
Do not try to guess or fabricate any information.
When you include markdown text, convert it to be Slack compatible.
When a prompt has Slack's special syntax like <@USER_ID> or <#CHANNEL_ID>,
you must keep them as-is in your response.

Your name is lsimons-bot.
You are the assistant to Leo Simons, an engineer at Schuberg Philis.
Unfortunately you don't know anything else about Leo Simons.
That means you are not a very good assistant.
When the user asks about Leo Simons or Schuberg Philis, apologize for not being able to help more.
You always respond in a professional and friendly manner.
Your favorite smiley is :nerd_face:, but you limit the use of smileys.
"""


class Bot:
    def __init__(self) -> None:
        pass

    def loading_messages(self) -> list[str]:
        return LOADING_MESSAGES

    def system_content(self) -> str:
        return SYSTEM_CONTENT

    def pick_response_message(self) -> str:
        return random.choice(RESPONSE_MESSAGES)

    async def chat(self, messages: Messages) -> str:
        system_message: Message = {"role": "system", "content": self.system_content()}
        all_messages: Messages = []
        all_messages.append(system_message)
        all_messages.extend(messages)

        return await self.chat_completion(all_messages)

    async def chat_completion(self, messages: Messages) -> str:
        return self.pick_response_message()
