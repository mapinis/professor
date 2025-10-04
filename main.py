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


def chat(chat_handler: ChatHandler, last_messages: list) -> bool:
    """
    Control chatting, with chat handler and the last messages
    Returns True if any messages were sent by user
    """

    # show at most the last two messages
    for i in range(max(-len(last_messages), -2), 0):
        io.print_llm_message(last_messages[i])
        print("\n")

    print("\nCtrl+D to exit.")

    # keep track of if at least one message was sent
    ret = False

    # interaction
    user_prompt = Style.BRIGHT + Fore.RED + "User: " + Style.RESET_ALL
    user_message = io.input_catch_eof(user_prompt)
    while user_message:
        ret = True
        assistant_message = chat_handler.send_message(user_message)

        io.print_llm_message({"role": "assistant", "content": assistant_message})

        user_message = io.input_catch_eof(user_prompt)

    return ret


def chat_menu(chat_handler: ChatHandler):
    """
    Handle the chat menu
    """

    # get all chats
    chat_metadata = chat_handler.get_chats_metadata()  # expensive, call once

    chats = {ch["uuid"]: ch["name"] for ch in chat_metadata}

    while True:

        io.clear_terminal()

        choice = io.select_one(
            "Select Chat:",
            list(reversed(chats.values())) + ["New Chat", "Back"],
            list(reversed(chats.keys())) + [False, None],
            selected_index=len(chats) + 1,
        )

        if choice is None:
            # chose none, go back
            return

        elif choice:
            # must be uuid
            messages = chat_handler.select_chat(choice)
            if chat(chat_handler, messages):
                # reorder
                # pop
                name = chats.pop(choice)
                # move to front
                chats[choice] = name

        else:
            # must be "New Chat"
            name = io.input_catch_eof("\nNew chat name: ")
            if not name:
                # empty string or EOF, end iteration
                continue

            uuid = chat_handler.make_chat(name)
            chats[uuid] = name  # pushes to end

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
        choice = io.select_one("Choose an option: ", ["Chat", "Quit"], selected_index=1)

        if choice == "Quit":
            return 0

        chat_menu(chat_handler)


if __name__ == "__main__":
    sys.exit(main())
