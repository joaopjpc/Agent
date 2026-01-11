"""Tools customizados usando agents.tool para interagir com o SQLite."""
from __future__ import annotations

import sqlite3
from typing import Any

from agents.tool import function_tool

from beachbot import db

_CONNECTION: sqlite3.Connection | None = None


def set_connection(connection: sqlite3.Connection) -> None:
    """Define a conexao do SQLite para uso pelas tools."""
    global _CONNECTION
    _CONNECTION = connection


def _require_connection() -> sqlite3.Connection:
    if _CONNECTION is None:
        raise ValueError("Conexao do banco nao configurada.")
    return _CONNECTION


@function_tool(name_override="registrar_aula_experimental")
def registrar_aula_experimental(
    nome: str,
    telefone: str,
    horario: str,
    nivel: str,
) -> str:
    """Registra pedido de aula experimental com status confirmacao_pendente."""
    conn = _require_connection()
    db.registrar_aula_experimental(
        conn,
        nome=nome,
        telefone=telefone,
        horario_escolhido=horario,
        nivel_aluno=nivel,
        status="confirmacao_pendente",
    )
    return "Pedido registrado no banco com status confirmacao_pendente."


@function_tool(name_override="confirmar_aula_experimental")
def confirmar_aula_experimental(telefone: str) -> str:
    """Marca como confirmada a ultima aula pendente para o telefone informado."""
    conn = _require_connection()
    updated = db.confirmar_aula_experimental(conn, telefone)
    if updated:
        return "Aula experimental confirmada."
    return "Nenhuma aula pendente encontrada para este telefone."
