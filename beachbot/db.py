"""Persistencia SQLite para conversas, aulas experimentais e tickets de atendimento humano."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


SCHEMA = (
    "CREATE TABLE IF NOT EXISTS conversas ("
    "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  role TEXT NOT NULL,"
    "  content TEXT NOT NULL,"
    "  user_phone TEXT,"
    "  session TEXT,"
    "  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    ");",
    "CREATE TABLE IF NOT EXISTS clientes ("
    "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  telefone TEXT NOT NULL UNIQUE,"
    "  nome TEXT NOT NULL,"
    "  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    ");",
    "CREATE TABLE IF NOT EXISTS aulas_experimentais ("
    "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  nome TEXT NOT NULL,"
    "  telefone TEXT NOT NULL,"
    "  horario_escolhido TEXT NOT NULL,"
    "  nivel_aluno TEXT NOT NULL,"
    "  status TEXT NOT NULL DEFAULT 'confirmacao_pendente',"
    "  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    ");",
)


def init_db(path: Path) -> sqlite3.Connection:
    """Cria o arquivo do banco SQLite e as tabelas necessarias."""
    connection = sqlite3.connect(path)
    for statement in SCHEMA:
        connection.execute(statement)
    connection.commit()
    return connection


def log_message(
    connection: sqlite3.Connection,
    role: str,
    content: str,
    user_phone: str | None = None,
    session: str | None = None,
) -> None:
    """Armazena uma mensagem no historico da conversa, com opcional telefone e session."""
    connection.execute(
        "INSERT INTO conversas (role, content, user_phone, session) VALUES (?, ?, ?, ?)",
        (role, content, user_phone, session),
    )
    connection.commit()


def registrar_aula_experimental(
    connection: sqlite3.Connection,
    nome: str,
    telefone: str,
    horario_escolhido: str,
    nivel_aluno: str,
    status: str = "confirmacao_pendente",
) -> None:
    """Persiste um pedido de aula experimental."""
    if status not in {"confirmada", "confirmacao_pendente"}:
        raise ValueError("status invalido para aula experimental.")
    connection.execute(
        "INSERT INTO aulas_experimentais (nome, telefone, horario_escolhido, nivel_aluno, status) VALUES (?, ?, ?, ?, ?)",
        (nome, telefone, horario_escolhido, nivel_aluno, status),
    )
    connection.commit()


def confirmar_aula_experimental(connection: sqlite3.Connection, telefone: str) -> bool:
    """Marca como confirmada a aula experimental mais recente para o telefone."""
    cursor = connection.execute(
        "SELECT id FROM aulas_experimentais WHERE telefone = ? ORDER BY id DESC LIMIT 1",
        (telefone,),
    )
    row = cursor.fetchone()
    if not row:
        return False
    (latest_id,) = row
    connection.execute(
        "UPDATE aulas_experimentais SET status = 'confirmada' WHERE id = ?",
        (latest_id,),
    )
    connection.commit()
    return True

