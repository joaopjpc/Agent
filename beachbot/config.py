"""Carrega configurações do ambiente para o bot Smash BT."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Configurações necessárias para integrar com Evolution API."""

    evolution_base_url: str
    evolution_apikey: str
    evolution_instance: str


def _require_env(name: str) -> str:
    """Lê variável obrigatória, disparando erro quando ausente."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Variável de ambiente obrigatória ausente: {name}")
    return value


def load_settings() -> Settings:
    """Cria objeto Settings a partir das variáveis de ambiente."""
    apikey = os.getenv("EVOLUTION_APIKEY") or os.getenv("EVOLUTION_TOKEN")
    if not apikey:
        raise ValueError("Variável de ambiente obrigatória ausente: EVOLUTION_APIKEY ou EVOLUTION_TOKEN")

    return Settings(
        evolution_base_url=_require_env("EVOLUTION_BASE_URL"),
        evolution_apikey=apikey,
        evolution_instance=_require_env("EVOLUTION_INSTANCE"),
    )
