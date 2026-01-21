"""Script simples para testar envio de texto via Evolution API."""
from __future__ import annotations

import argparse
import asyncio

from beachbot.config import load_settings
from beachbot.evolution_client import EvolutionClient


async def main() -> None:
    """Executa envio de mensagem de texto para um número informado."""
    parser = argparse.ArgumentParser(description="Teste de envio via Evolution API")
    parser.add_argument("number", help="Número de destino (somente dígitos, ex: 5599999999999)")
    parser.add_argument(
        "--text",
        default="Teste de envio do Smash BT",
        help="Texto a enviar (opcional)",
    )
    args = parser.parse_args()

    settings = load_settings()
    client = EvolutionClient(
        settings.evolution_base_url,
        settings.evolution_apikey,
        settings.evolution_instance,
    )

    response = await client.send_text(args.number, args.text)
    print("Resposta Evolution:", response)


if __name__ == "__main__":
    asyncio.run(main())
