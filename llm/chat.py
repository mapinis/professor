"""
Files that holds the ChatHandler class
- read chat files
- write chat files
- use the anthropic api to send messages
"""

import os
from uuid import uuid4
from pathlib import Path
from datetime import datetime

import anthropic

from utils.files import read_json, write_json


class ChatHandler:
    """
    Handle chat messages, including reading and writing old messages
            Expects each chat to be in messages_dir/{uuid}.json
        With the schema:
        {
            "name": <name>,
            "time": <timestamp> (last time written to)
            "messages": [
                {
                    "role": ...,
                    "content": ...,
                },
                ...
            ]
        }
    """

    def __init__(self):

        # set up client
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self._client = anthropic.Anthropic(api_key=api_key)

        # get system prompt
        with open("./llm/prompts/system.txt", mode="r", encoding="utf-8") as f:
            self._system_prompt = f.read()

        # create data/messages if it does not exist
        self._messages_dir = Path("./data/messages")
        os.makedirs(self._messages_dir, exist_ok=True)

        self._chat_dictionary = self._load_chat_dictionary()

        # message state
        self._selected_chat: str | None = (
            None  # invariant: self._selected_chat in self._chat_dictionary
        )
        self._selected_messages: list[anthropic.types.MessageParam] = []

    def _load_chat_dictionary(self) -> dict[str, dict]:
        """
        Loads the chat metadata into a uuid -> metadata dict
        """

        ids = [
            filename[:-5]
            for filename in os.listdir(self._messages_dir)
            if filename[-5:] == ".json"
        ]

        # load raw string information
        chat_dictionary = {
            chat_id: read_json(
                self._messages_dir / f"{chat_id}.json", "{name: .name, time: .time}"
            )
            for chat_id in ids
        }

        # convert date strings to datetime objects
        for chat_id in chat_dictionary:
            chat_dictionary[chat_id]["time"] = datetime.fromisoformat(
                chat_dictionary[chat_id]["time"]
            )

        return chat_dictionary

    def _load_chat_messages(self, chat_id: str) -> list[anthropic.types.MessageParam]:
        """
        Loads the chat messages from the appropriate file
        """

        return read_json(self._messages_dir / f"{chat_id}.json", ".messages")

    def get_chats_metadata(self) -> list[dict]:
        """
        Get a list of chats metadata objects, with the schema:
        {
            "uuid": ...,
            "name": ...,
            "time": ...,
        }
        Returns list sorted by timestamp
        """

        chats = []
        for chat_id, metadata in self._chat_dictionary.items():
            chats.append({**metadata, "uuid": chat_id})

        return sorted(chats, key=lambda ch: ch["time"])

    def select_chat(self, chat_id: str) -> list[anthropic.types.MessageParam]:
        """
        Select the chat_id, loading the messages into current_messages
        Raises an error if chat_id is not in the chat_dictionary
        Returns message historu
        """

        if chat_id not in self._chat_dictionary:
            raise ValueError(f"{chat_id} not a valid chat id")

        self._selected_chat = chat_id
        self._selected_messages = self._load_chat_messages(chat_id)

        return self._selected_messages

    def make_chat(self, name: str) -> str:
        """
        Make a new chat with this name and selects it
        Updates state but does not create file until a message is sent
        Returns unique chat id
        """

        chat_id = uuid4()

        self._chat_dictionary[chat_id] = {"name": name, "time": datetime.now()}

        self._selected_chat = chat_id
        self._selected_messages = []

        return chat_id

    def send_message(self, user_message: str) -> str:
        """
        Chat with the assistant using provided user message
        Returns assistant message
        Updates the most recent chat usage and updates file
        Raises AssertionError if no chat is selected
        """

        # TODO: tool support

        # check that chat is selected
        assert self._selected_chat, "Cannot send message when no chat is selected"

        # add latest user message
        self._selected_messages.append({"role": "user", "content": user_message})

        # generate response
        response = self._client.messages.create(
            max_tokens=512,
            model="claude-sonnet-4-5-20250929",
            messages=self._selected_messages,
            system=self._system_prompt,
        )

        # make sure the response is good
        assert response.content[0].text, response

        # extract message
        assistant_message = response.content[0].text

        # update _selected_messages
        self._selected_messages.append(
            {"role": "assistant", "content": assistant_message}
        )

        # update metadata
        metadata = self._chat_dictionary[self._selected_chat]
        metadata["time"] = datetime.now()

        # write to file
        write_json(
            self._messages_dir / f"{self._selected_chat}.json",
            {
                "name": metadata["name"],
                "time": metadata["time"].isoformat(),
                "messages": self._selected_messages,
            },
        )

        # return
        return assistant_message
