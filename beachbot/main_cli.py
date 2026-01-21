"""CLI entrypoint for Smash Beach Tennis bot (Postgres-only)."""
from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv

from beachbot.core.handler import create_handler

load_dotenv()


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
    """Simple terminal chat loop with Postgres persistente."""
    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL nao definido. Configure Postgres antes de rodar o CLI.")
        sys.exit(1)

    triage_mode = _select_triage_mode()
    handler = create_handler(triage_mode=triage_mode)

    print("Smash Beach Tennis - Atendimento (digite 'sair' para encerrar)\n")

    while True:
        user_message = input("Voce: ").strip()
        if not user_message:
            continue
        if user_message.lower() in {"sair", "exit", "quit"}:
            print("Ate logo!")
            break

        response = await handler.handle_message(
            sender="cli",
            text=user_message,
            history=None,
        )
        print(f"Bot: {response}")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
