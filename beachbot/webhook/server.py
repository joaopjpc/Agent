"""Servidor FastAPI com health check e webhook para Evolution API."""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Awaitable, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from beachbot.config import Settings, load_settings
from beachbot.core.handler import MessageHandler, create_handler
from beachbot.evolution_client import EvolutionClient
from beachbot.webhook.parsing import ParsedMessage, parse_messages_upsert
from beachbot.utils.redact import mask_phone

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

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


async def _process_message(parsed: ParsedMessage) -> None:
    """Processa mensagem e envia resposta do bot sem bloquear o webhook."""
    handler: Optional[MessageHandler] = getattr(app.state, "handler", None)
    if handler is None:
        logger.warning(
            "Handler nao inicializado; resposta nao enviada",
            extra={"sender_masked": mask_phone(parsed.sender), "message_id": parsed.message_id},
        )
        return

    reply_text = await handler.handle_message(
        parsed.sender,
        parsed.text,
        message_id=parsed.message_id,
        instance_id=parsed.instance_id,
    )

    if reply_text is None:
        logger.info(
            "Nenhuma resposta enviada (buffer aguardando)",
            extra={
                "sender_masked": mask_phone(parsed.sender),
                "message_id": parsed.message_id,
                "instance_id": parsed.instance_id,
            },
        )
        return
    if reply_text == "":
        logger.warning(
            "Resposta vazia nao enviada",
            extra={
                "sender_masked": mask_phone(parsed.sender),
                "message_id": parsed.message_id,
                "instance_id": parsed.instance_id,
            },
        )
        return

    if evolution_client is None:
        logger.warning(
            "Evolution client nao configurado; resposta nao enviada",
            extra={"sender_masked": mask_phone(parsed.sender), "message_id": parsed.message_id},
        )
        return

    text_len = len(reply_text)
    preview = reply_text[:60]
    if text_len > 60:
        preview += "..."

    try:
        await evolution_client.send_text(parsed.sender, reply_text)
        logger.info(
            "Resposta enviada via Evolution",
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
            "Falha ao enviar resposta via Evolution",
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


@app.on_event("startup")
async def startup() -> None:
    """Inicializa a rede do bot uma unica vez."""
    triage_mode = os.getenv("TRIAGE_MODE", "prompt")
    app.state.handler = create_handler(triage_mode=triage_mode)


@app.on_event("shutdown")
async def shutdown() -> None:
    """Limpa referencias em shutdown."""
    if hasattr(app.state, "handler"):
        app.state.handler = None


async def _handle_webhook(request: Request) -> JSONResponse:
    """Processa o webhook (rota base ou com sufixo de evento)."""
    raw_body = await request.body()
    body_size = len(raw_body)

    # Loga um preview bruto do payload para facilitar debug de formato
    try:
        body_preview = raw_body[:500].decode("utf-8", errors="replace")
    except Exception:
        body_preview = str(raw_body[:500])

    logger.debug("Payload bruto recebido: %s", body_preview)

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

        # Dispara processamento sem bloquear a resposta do webhook
        _fire_and_forget(_process_message(parsed_message))
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


@app.post("/webhook")
async def webhook(request: Request) -> JSONResponse:
    """Rota base do webhook (Evolution sem sufixo de evento)."""
    return await _handle_webhook(request)


@app.post("/webhook/{event_path}")
async def webhook_event(event_path: str, request: Request) -> JSONResponse:
    """Rota para Evolution com 'Webhook by Events' habilitado (ex.: /webhook/messages-upsert)."""
    return await _handle_webhook(request)
