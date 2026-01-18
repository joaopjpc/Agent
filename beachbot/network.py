"""Configuracao de rede para o AtendentePro."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Literal

from agents import Runner
from atendentepro.agents import create_triage_agent
from atendentepro.guardrails import get_guardrails_for_agent
from atendentepro.network import create_standard_network


TRIAGE_INSTRUCTIONS_PATH = Path(__file__).parent / "config" / "triage_instructions.md"


def _load_triage_instructions() -> str:
    return TRIAGE_INSTRUCTIONS_PATH.read_text(encoding="utf-8").strip()


def _replace_triage(network: Any) -> None:
    custom_prompt = _load_triage_instructions()
    custom_triage = create_triage_agent(
        keywords_text="",
        custom_instructions=custom_prompt,
        guardrails=get_guardrails_for_agent("Triage Agent", Path(__file__).parent),
    )

    old_triage = network.triage
    custom_triage.handoffs = old_triage.handoffs if old_triage else [] 
    network.triage = custom_triage

    if old_triage:
        for agent in network.get_all_agents():
            if agent is custom_triage:
                continue
            agent.handoffs = [
                custom_triage if handoff is old_triage else handoff
                for handoff in agent.handoffs
            ]


TriageMode = Literal["prompt", "yaml"]


def build_network(*, triage_mode: TriageMode = "prompt") -> Any:
    """Cria a rede do AtendentePro usando templates locais."""
    if triage_mode not in {"prompt", "yaml"}:
        raise ValueError(f"Unsupported triage_mode: {triage_mode}")
    network = create_standard_network(
        templates_root=Path(__file__).parent,
        client="config",
        escalation_channels=(
            "Apenas mantenha-se atento no WhatsApp. "
            "Ja contactamos um atendente humano que ira atende-lo em breve."
        ),
        include_feedback=False,
        include_confirmation=False,
        include_answer=False,
    )

    if triage_mode == "prompt":
        _replace_triage(network)
    return network


async def run_turn_async(network: Any, messages: list[dict[str, str]]) -> str:
    """Executa uma rodada de conversa de forma assincrona."""
    result = await Runner.run(network.triage, messages)
    if hasattr(result, "final_output"):
        return result.final_output
    if hasattr(result, "text"):
        return result.text
    return str(result)


def run_turn(network: Any, messages: list[dict[str, str]]) -> str:
    """Executa uma rodada de conversa de forma sincrona (compatibilidade CLI antiga)."""
    return asyncio.run(run_turn_async(network, messages))
