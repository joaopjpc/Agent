"""Servidor FastAPI com health check e webhook para Evolution API."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from beachbot.config import Settings, load_settings
from beachbot.evolution_client import EvolutionClient
from beachbot.webhook.parsing import ParsedMessage, parse_messages_upsert
from beachbot.utils.redact import mask_phone

logger = logging.getLogger(__name__)

app = FastAPI(title="Smash BT Webhook", version="0.1.0")

try:
    settings: Optional[Settings] = load_settings()
    evolution_client: Optional[EvolutionClient] = EvolutionClient(
        settings.evolution_base_url,
        settings.evolution_apikey,
        settings.evolution_instance,
    )
except Exception as exc:  # noqa: BLE001
    logger.warning("Configuracao incompleta do Evolution API: %s", exc)
    settings = None
    evolution_client = None


def _fire_and_forget(coro: Awaitable[None]) -> None:
    """Executa corrotina sem bloquear, logando excecoes."""
    task = asyncio.create_task(coro)

    def _log_exceptions(task_obj: asyncio.Task) -> None:
        try:
            task_obj.result()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Erro em tarefa async do webhook", exc_info=exc)

    task.add_done_callback(_log_exceptions)


async def _send_echo_message(parsed: ParsedMessage) -> None:
    """Envia resposta padrao sem bloquear o webhook."""
    if evolution_client is None:
        logger.warning(
            "Evolution client nao configurado; echo nao enviado",
            extra={
                "sender_masked": mask_phone(parsed.sender),
                "message_id": parsed.message_id,
                "instance_id": parsed.instance_id,
            },
        )
        return

    text_len = len(parsed.text)
    if text_len == 0:
        return

    preview = parsed.text[:60]
    if text_len > 60:
        preview += "..."

    try:
        await evolution_client.send_text(parsed.sender, f"Recebi: {parsed.text}")
        logger.info(
            "Echo enviado via Evolution",
            extra={
                "sender_masked": mask_phone(parsed.sender),
                "message_id": parsed.message_id,
                "text_len": text_len,
                "text_preview": preview,
                "instance_id": parsed.instance_id,
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "Falha ao enviar echo via Evolution",
            exc_info=exc,
            extra={
                "sender_masked": mask_phone(parsed.sender),
                "message_id": parsed.message_id,
                "text_len": text_len,
                "text_preview": preview,
                "instance_id": parsed.instance_id,
            },
        )


@app.get("/health")
async def health() -> dict[str, bool]:
    """Endpoint simples de verificacao de saude."""
    return {"ok": True}


@app.post("/webhook")
async def webhook(request: Request) -> JSONResponse:
    """Aceita payload JSON, tenta parsear a mensagem e responde rapidamente."""
    raw_body = await request.body()
    body_size = len(raw_body)
    try:
        payload: Any = await request.json()
        json_parsed = True
    except Exception:
        payload = None
        json_parsed = False

    parsed_message: Optional[ParsedMessage] = parse_messages_upsert(payload) if payload else None

    if parsed_message:
        text_len = len(parsed_message.text)
        preview = parsed_message.text[:60]
        if text_len > 60:
            preview += "..."

        logger.info(
            "Mensagem recebida do WhatsApp",
            extra={
                "path": str(request.url.path),
                "bytes": body_size,
                "json_parsed": json_parsed,
                "sender_masked": mask_phone(parsed_message.sender),
                "message_id": parsed_message.message_id,
                "text_len": text_len,
                "text_preview": preview,
                "instance_id": parsed_message.instance_id,
            },
        )

        # Dispara envio de echo sem bloquear a resposta do webhook
        _fire_and_forget(_send_echo_message(parsed_message))
    else:
        instance_id = None
        if isinstance(payload, dict):
            instance_id = payload.get("instanceId") or payload.get("instance_id")

        logger.warning(
            "Payload de webhook nao parseado",
            extra={
                "path": str(request.url.path),
                "bytes": body_size,
                "json_parsed": json_parsed,
                "instance_id": instance_id,
            },
        )

    return JSONResponse({"ok": True})
