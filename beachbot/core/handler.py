"""Orquestra a interacao entre o webhook/CLI e a rede AtendentePro."""
from __future__ import annotations

import logging
from typing import Any, Optional

from beachbot.network import build_network, run_turn_async
from beachbot.utils.redact import mask_phone

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "Tive um problema aqui, ja ja um atendente te responde."


class HandlerError(Exception):
    """Erro ao processar mensagem pelo bot."""


class MessageHandler:
    """Encapsula a rede do AtendentePro e processa mensagens."""

    def __init__(self, network: Any, *, fallback_message: str = FALLBACK_MESSAGE) -> None:
        self.network = network
        self.fallback_message = fallback_message

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
    ) -> str:
        """
        Processa texto de usuario e retorna resposta do bot.

        Se ocorrer erro, devolve fallback amigavel (sem levantar excecao).
        O histórico (se fornecido) é atualizado in-place com os turnos.
        """
        if not text:
            return self.fallback_message

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
