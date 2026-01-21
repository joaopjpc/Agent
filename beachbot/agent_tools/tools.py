"""Tools customizados usando agents.tool para interagir com Postgres."""
from __future__ import annotations

import datetime as dt
from typing import Any

from agents.tool import function_tool

from beachbot.storage import db as storage


def _session():
    if not storage.has_engine():
        raise RuntimeError("DATABASE_URL nao configurado; tools indisponiveis.")
    return storage.get_session()


@function_tool(name_override="registrar_aula_experimental")
def registrar_aula_experimental(
    nome: str,
    telefone: str,
    horario: str,
    nivel: str = "",
    instance_id: str | None = None,
) -> str:
    """
    Registra pedido de aula experimental no Postgres.
    - Cria/reutiliza cliente e conversa aberta.
    - status inicial: collecting.
    - horario é texto livre; armazena em notes para nao perder dado.
    """
    session = _session()
    try:
        client = storage.get_or_create_client(session, instance_id, telefone)
        convo = storage.get_or_create_open_conversation(session, client.id)
        now = dt.datetime.now(dt.timezone.utc)
        # Salva como mensagem de usuario para manter historico
        storage.save_message(
            session,
            convo.id,
            role="user",
            direction="in",
            text=f"[pedido_aula_experimental] nome={nome} telefone={telefone} horario={horario} nivel={nivel}",
            ts=now,
            wa_message_id=None,
        )
        # Cria registro de aula experimental
        record = storage.AulaExperimental(
            client_id=client.id,
            conversation_id=convo.id,
            status="collecting",
            name=nome,
            preferred_day=None,
            preferred_time=None,
            scheduled_at=None,
            notes=f"horario={horario}; nivel={nivel}",
            created_at=now,
            updated_at=now,
        )
        session.add(record)
        session.commit()
        return "Pedido de aula experimental registrado."
    finally:
        session.close()


@function_tool(name_override="confirmar_aula_experimental")
def confirmar_aula_experimental(telefone: str, instance_id: str | None = None) -> str:
    """
    Marca como scheduled o ultimo pedido de aula do cliente informado.
    """
    session = _session()
    try:
        client = storage.get_or_create_client(session, instance_id, telefone)
        rec = (
            session.query(storage.AulaExperimental)
            .filter(storage.AulaExperimental.client_id == client.id)
            .order_by(storage.AulaExperimental.id.desc())
            .first()
        )
        if not rec:
            return "Nenhum pedido encontrado para este telefone."
        rec.status = "scheduled"
        rec.updated_at = dt.datetime.now(dt.timezone.utc)
        session.add(rec)
        session.commit()
        return "Aula experimental marcada como scheduled."
    finally:
        session.close()
