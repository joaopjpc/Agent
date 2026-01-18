"""CLI entrypoint for Smash Beach Tennis bot."""
from __future__ import annotations

import asyncio

from dotenv import load_dotenv

from beachbot import db
from beachbot.core.handler import create_handler

load_dotenv()

DATA_PATH = db.DEFAULT_DB_PATH


def _select_triage_mode() -> str:
    print("Modo de triage: [1] padrao (yaml) [2] prompt custom")
    choice = input("Escolha 1 ou 2 (Enter = 2): ").strip()
    if choice == "1":
        return "yaml"
    if choice in {"", "2"}:
        return "prompt"
    print("Opcao invalida, usando prompt custom.")
    return "prompt"


async def main_async() -> None:
    """Simple terminal chat loop with conversation history."""
    connection = db.init_db(DATA_PATH)
    triage_mode = _select_triage_mode()
    handler = create_handler(triage_mode=triage_mode)
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
        response = await handler.handle_message(
            sender="cli",
            text=user_message,
            history=messages,
        )
        print(f"Bot: {response}")
        db.log_message(connection, role="assistant", content=response)
        # handler já atualiza o histórico passado


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
