"""Configuracao de rede para o AtendentePro."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from agents import Runner
from atendentepro.network import create_standard_network


def build_network() -> Any:
    """Cria a rede do AtendentePro usando templates locais."""
    return create_standard_network(
        templates_root=Path(__file__).parent,
        client="escolinha_beach",
        include_escalation=True,
        include_feedback=False,
        include_confirmation=False,
        include_answer=False,
    )


def run_turn(network: Any, messages: list[dict[str, str]]) -> str:
    """Envia a conversa ao agente de triagem via Runner (assincrono) e retorna texto."""
    result = asyncio.run(Runner.run(network.triage, messages))
    if hasattr(result, "final_output"):
        return result.final_output
    if hasattr(result, "text"):
        return result.text
    return str(result)
