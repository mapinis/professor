"""
Chat functions:
  - Interacting with anthropic api
  - Reading chat data
  - Writing chat data
"""

import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

# get system prompt
with open("./llm/prompts/system.txt", mode="r", encoding="utf-8") as f:
    system_prompt = f.read()

# will later support writing to file, reading from file, and multiple chats
messages: list[anthropic.types.MessageParam] = []


def chat(user_message: str):
    """
    Chat with the assistant
    Writes stream to stdout
    """

    messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        max_tokens=512,
        model="claude-sonnet-4-20250514",
        messages=messages,
        system=system_prompt,
    )

    assert response.content[0].text, response

    assistant_message = response.content[0].text
    print(assistant_message)

    messages.append({"role": "assistant", "content": assistant_message})
