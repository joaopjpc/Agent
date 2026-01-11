"""CLI entrypoint for Smash Beach Tennis bot."""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from beachbot import db
from beachbot.network import build_network, run_turn

load_dotenv()

DATA_PATH = Path(__file__).parent / "data" / "data.sqlite"


def main() -> None:
    """Simple terminal chat loop with conversation history."""
    connection = db.init_db(DATA_PATH)
    network = build_network()
    messages: list[dict[str, str]] = []

    print("Smash Beach Tennis - Atendimento (digite 'sair' para encerrar)\n")

    while True:
        user_message = input("Voce: ").strip()
        if not user_message:
            continue
        if user_message.lower() in {"sair", "exit", "quit"}:
            print("Ate logo!")
            break

        db.log_message(connection, role="user", content=user_message)
        messages.append({"role": "user", "content": user_message})

        response = run_turn(network, messages)
        print(f"Bot: {response}")
        db.log_message(connection, role="assistant", content=response)
        messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
