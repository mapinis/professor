"""
Utility functions for getting inputs
"""

import os

import cutie
from colorama import Fore, Style


def input_catch_eof(prompt: str) -> str | None:
    """
    Normal input but returns None if Ctrl+D (EOF)
    """

    try:
        return input(prompt)
    except EOFError:
        return None


def select_one(
    question: str | None,
    options: list,
    values: list | None = None,
    selected_index: int = None,
) -> any:
    """
    Show the user a cutie dialogue to select one from the options
    If values is provided, |values| must = |options|,
        and the value of the chosen index is returned instead
    If question is None, no question is shown
    """

    if values:
        assert len(values) == len(options), "select_one values not length of options"

    if question:
        opts = [question] + options
        captions = [0]
    else:
        opts = options
        captions = None

    # prompt for the select (blocking)
    select_ind = cutie.select(
        options=opts,
        caption_indices=captions,
        confirm_on_select=False,
        selected_index=selected_index,
    )

    select_ind -= 1 if question else 0  # question adds to index

    if values:
        return values[select_ind]

    return options[select_ind]


def print_llm_message(message):
    """
    Prints an llm message, user or assistant
    Expects {"role": ..., "content": ...}

    User is red, assistant is blue, anything else (tools?) is green
    """

    assert message["role"], "message needs role field"
    assert message["content"], "message needs content"

    role_color = (
        Fore.RED
        if message["role"] == "user"
        else Fore.BLUE if message["role"] == "assistant" else Fore.GREEN
    )

    print(
        role_color
        + Style.BRIGHT
        + message["role"].capitalize()
        + ": "
        + Style.RESET_ALL
        + message["content"]
    )


def clear_terminal():
    """
    Clear the terminal contents
    """
    os.system("cls" if os.name == "nt" else "clear")


def print_welcome_message():
    """
    Print a welcome message, clearing terminal
    """

    clear_terminal()

    print("Hello, I'm your Professor. Ready to learn?\n")
