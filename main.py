"""
Main file for PROFESSOR
Mark Apinis
"""

import sys
from dotenv import load_dotenv
from colorama import Style, Fore

from llm.chat import ChatHandler
import utils.io as io

load_dotenv()


def chat(chat_handler: ChatHandler, last_messages: list):
    """
    Control chatting, with chat handler and the last messages
    """

    # show at most the last two messages
    for i in range(max(-len(last_messages), -2), 0):
        io.print_llm_message(last_messages[i])
        print("\n")

    print("\nCtrl+D to exit.")

    # interaction
    user_prompt = Style.BRIGHT + Fore.RED + "User: " + Style.RESET_ALL
    user_message = io.input_catch_eof(user_prompt)
    while user_message:
        assistant_message = chat_handler.send_message(user_message)

        io.print_llm_message({"role": "assistant", "content": assistant_message})

        user_message = io.input_catch_eof(user_prompt)


def chat_menu(chat_handler: ChatHandler):
    """
    Handle the chat menu
    """

    # get all chats
    chats = chat_handler.get_chats_metadata()  # expensive, call once

    uuids = [ch["uuid"] for ch in chats]
    names = [ch["name"] for ch in chats]

    while True:

        io.clear_terminal()

        choice = io.select_one(
            "Select Chat:",
            names + ["New Chat", "Back"],
            uuids + [False, None],
            selected_index=len(uuids),
        )

        if choice is None:
            # chose none, go back
            return

        elif choice:
            # must be uuid
            messages = chat_handler.select_chat(choice)
            chat(chat_handler, messages)

        else:
            # must be "New Chat"
            name = io.input_catch_eof("\nNew chat name: ")
            if not name:
                # empty string or EOF, end iteration
                continue

            uuid = chat_handler.make_chat(name)
            uuids.insert(0, uuid)
            names.insert(0, name)

            # already selected
            chat(chat_handler, [])


def main() -> int:
    """
    App logic, returns exit code
    """

    chat_handler = ChatHandler()

    # main menu
    while True:
        io.print_welcome_message()
        choice = io.select_one("Choose an option: ", ["Chat", "Quit"], selected_index=0)

        if choice == "Quit":
            return 0

        chat_menu(chat_handler)


if __name__ == "__main__":
    sys.exit(main())
