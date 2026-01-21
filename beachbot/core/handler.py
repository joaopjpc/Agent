"""Orquestra a interacao entre o webhook/CLI e a rede AtendentePro."""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

from beachbot.network import build_network, run_turn_async
from beachbot.utils.redact import mask_phone

try:
    from beachbot.storage import db as storage
except Exception:  # noqa: BLE001
    storage = None

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "Tive um problema aqui, ja ja um atendente te responde."


class HandlerError(Exception):
    """Erro ao processar mensagem pelo bot."""


class MessageHandler:
    """Encapsula a rede do AtendentePro e processa mensagens."""

    def __init__(self, network: Any, *, fallback_message: str = FALLBACK_MESSAGE) -> None:
        self.network = network
        self.fallback_message = fallback_message
        self.storage_enabled = bool(os.getenv("DATABASE_URL")) and storage is not None and storage.has_engine()

    @classmethod
    def create(cls, *, triage_mode: str = "prompt", fallback_message: str = FALLBACK_MESSAGE) -> "MessageHandler":
        network = build_network(triage_mode=triage_mode)
        return cls(network, fallback_message=fallback_message)

    async def handle_message(
        self,
        sender: str,
        text: str,
        *,
        message_id: Optional[str] = None,
        instance_id: Optional[str] = None,
        history: Optional[list[dict[str, str]]] = None,
    ) -> Optional[str]:
        """
        Processa texto de usuario e retorna resposta do bot.

        Se ocorrer erro, devolve fallback amigavel (sem levantar excecao).
        O histórico (se fornecido) é atualizado in-place com os turnos.
        """
        if not text:
            return self.fallback_message

        # Se storage estiver habilitado, persiste no Postgres e usa historico do banco.
        if self.storage_enabled and storage is not None:
            ts_msg = datetime.now(timezone.utc)
            convo_id: Optional[int] = None
            client_id: Optional[int] = None
            try:
                # Sessao A: persiste a mensagem de entrada
                session_a = storage.get_session()
                try:
                    client = storage.get_or_create_client(session_a, instance_id, sender, ts=ts_msg)
                    client_id = client.id
                    convo = storage.get_or_create_open_conversation(session_a, client.id, ts=ts_msg)
                    convo_id = convo.id
                    storage.save_message(
                        session_a,
                        convo.id,
                        role="user",
                        direction="in",
                        text=text,
                        ts=ts_msg,
                        wa_message_id=message_id,
                    )
                finally:
                    session_a.close()

                # Aguarda janela de 15s para agrupar mensagens subsequentes (sem sessao aberta)
                await asyncio.sleep(15)

                # Sessao B: verifica se chegou mensagem mais recente e responde
                session_b = storage.get_session()
                try:
                    last_activity = (
                        session_b.query(storage.Conversation.last_activity_at)
                        .filter(storage.Conversation.id == convo_id)
                        .scalar()
                    )
                    if last_activity and last_activity > ts_msg:
                        return None

                    history_messages = storage.fetch_last_messages(session_b, convo_id, limit=20)
                    reply = await run_turn_async(self.network, history_messages)
                    storage.save_message(
                        session_b,
                        convo_id,
                        role="assistant",
                        direction="out",
                        text=reply,
                        ts=datetime.now(timezone.utc),
                        wa_message_id=None,
                    )
                    if client_id is not None:
                        storage.touch_client_last_seen(session_b, client_id, datetime.now(timezone.utc))
                    return reply
                finally:
                    session_b.close()
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "Erro ao processar mensagem com persistencia",
                    exc_info=exc,
                    extra={"sender_masked": mask_phone(sender), "message_id": message_id, "instance_id": instance_id},
                )
                return self.fallback_message

        # Sem storage: usa historico em memoria (CLI/legado)
        messages = list(history or [])
        messages.append({"role": "user", "content": text})

        try:
            reply = await run_turn_async(self.network, messages)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Erro ao gerar resposta do bot",
                exc_info=exc,
                extra={"sender_masked": mask_phone(sender), "message_id": message_id, "instance_id": instance_id},
            )
            return self.fallback_message

        if history is not None:
            messages.append({"role": "assistant", "content": reply})
            history[:] = messages

        return reply


def create_handler(*, triage_mode: str = "prompt", fallback_message: str = FALLBACK_MESSAGE) -> MessageHandler:
    """Conveniencia para criar handler padrao."""
    return MessageHandler.create(triage_mode=triage_mode, fallback_message=fallback_message)
