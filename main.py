"""
Main file for PROFESSOR
Mark Apinis
"""

from llm.chat import chat


def main():
    """
    App logic
    """

    while True:
        message = input("User message: ")
        chat(message)


if __name__ == "__main__":
    main()
