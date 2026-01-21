"""Utilitarios para extrair mensagens do webhook MESSAGES_UPSERT da Evolution API."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ParsedMessage:
    """Representa os campos essenciais de uma mensagem recebida."""

    sender: Optional[str]
    text: str
    message_id: Optional[str] = None
    instance_id: Optional[str] = None


def parse_messages_upsert(payload: Any) -> Optional[ParsedMessage]:
    """
    Extrai sender/text/message_id/instance_id de payloads MESSAGES_UPSERT.

    A Evolution API pode entregar formatos ligeiramente diferentes (lista de mensagens
    em data.messages ou objeto unico em data). O parser eh tolerante e retorna None
    para nao interromper o webhook.
    """
    if not isinstance(payload, dict):
        logger.warning("Payload do webhook nao eh um objeto JSON")
        return None

    event = payload.get("event")
    if event is not None:
        event_norm = str(event).lower()
        if event_norm not in {"messages_upsert", "messages.upsert", "messages-upsert", "messages"}:
            return None

    instance_id: Optional[str] = (
        payload.get("instanceId") or payload.get("instance_id") or payload.get("instance")
    )

    containers: list[dict[str, Any]] = []
    data = payload.get("data")
    if isinstance(data, dict):
        containers.append(data)
    containers.insert(0, payload)

    skipped_from_me = False
    for container in containers:
        parsed, skipped = _parse_container(container, instance_id)
        skipped_from_me = skipped_from_me or skipped
        if parsed:
            return parsed

    if skipped_from_me:
        return None

    logger.warning(
        "Nao foi possivel localizar mensagens no payload MESSAGES_UPSERT",
        extra={"top_level_keys": list(payload.keys())},
    )
    return None


def _parse_container(container: Any, instance_id: Optional[str]) -> tuple[Optional[ParsedMessage], bool]:
    if not isinstance(container, dict):
        return None, False

    skipped_from_me = False
    messages = container.get("messages")
    if isinstance(messages, list):
        for message_entry in messages:
            parsed, skipped = _parse_message_entry(message_entry, instance_id)
            skipped_from_me = skipped_from_me or skipped
            if parsed:
                return parsed, skipped_from_me

    parsed, skipped = _parse_message_entry(container, instance_id)
    return parsed, skipped_from_me or skipped


def _parse_message_entry(entry: Any, instance_id: Optional[str]) -> tuple[Optional[ParsedMessage], bool]:
    if not isinstance(entry, dict):
        return None, False

    key = entry.get("key") or entry.get("msgKey") or {}
    if not isinstance(key, dict):
        key = {}

    from_me = bool(key.get("fromMe")) or bool(entry.get("fromMe"))
    if from_me:
        return None, True

    # Evolution 2.3.0: quando remoteJid termina com @lid, senderPn traz o JID real.
    remote_jid = key.get("remoteJid") or entry.get("remoteJid")
    sender_pn = key.get("senderPn") or entry.get("senderPn")
    sender_lid = key.get("senderLid") or entry.get("senderLid")
    participant = key.get("participant")
    fallback_from = entry.get("from")

    # Prioridade: se for LID, tenta senderPn/participant primeiro; caso normal, remoteJid primeiro.
    sender_candidates = []
    remote_is_lid = isinstance(remote_jid, str) and remote_jid.lower().endswith("@lid")
    if remote_is_lid:
        if sender_pn:
            sender_candidates.append(sender_pn)
        if sender_lid:
            sender_candidates.append(sender_lid)
        if participant:
            sender_candidates.append(participant)
        if remote_jid:
            sender_candidates.append(remote_jid)
        if fallback_from:
            sender_candidates.append(fallback_from)
    else:
        if remote_jid:
            sender_candidates.append(remote_jid)
        if participant:
            sender_candidates.append(participant)
        if fallback_from:
            sender_candidates.append(fallback_from)

    message_id = (
        key.get("id")
        or key.get("idMessage")
        or key.get("messageId")
        or entry.get("id")
        or entry.get("message_id")
    )

    message_body = entry.get("message")
    text = _extract_text_from_message(message_body)
    if not text:
        # Algumas integracoes trazem o texto direto no objeto
        text = entry.get("text") or entry.get("body") or entry.get("messageText")

    if text:
        text = text.strip()

    sender: Optional[str] = None
    for candidate in sender_candidates:
        normalized = _normalize_sender(candidate)
        if normalized:
            sender = normalized
            break

    if text:
        return ParsedMessage(sender=sender, text=text, message_id=message_id, instance_id=instance_id), False

    return None, False


def _normalize_sender(sender_raw: Any) -> Optional[str]:
    if sender_raw is None:
        return None

    sender_str = str(sender_raw).strip()
    if not sender_str:
        return None

    sender_lower = sender_str.lower()

    # Rejeita LID ou domínios não WhatsApp
    if sender_lower.endswith("@lid"):
        return None

    allowed_domains = ("@s.whatsapp.net", "@c.us", "@g.us")
    if any(sender_lower.endswith(dom) for dom in allowed_domains):
        return sender_str

    # Fallback apenas para números puros (sem domínio)
    digits_only = re.sub(r"\D+", "", sender_str)
    if not digits_only:
        return None
    if not digits_only.startswith("55"):
        return None
    return digits_only


def _extract_text_from_message(message: Any) -> Optional[str]:
    if not isinstance(message, dict):
        return None

    # Desembrulha formatos que aninham a mensagem em campos "message"
    for wrapper in ("ephemeralMessage", "viewOnceMessage", "viewOnceMessageV2", "deviceSentMessage"):
        wrapper_body = message.get(wrapper)
        if isinstance(wrapper_body, dict):
            nested = wrapper_body.get("message") or wrapper_body
            nested_text = _extract_text_from_message(nested)
            if nested_text:
                return nested_text

    if "conversation" in message:
        return message.get("conversation")

    extended = message.get("extendedTextMessage")
    if isinstance(extended, dict) and extended.get("text"):
        return extended.get("text")

    image_msg = message.get("imageMessage")
    if isinstance(image_msg, dict):
        caption = image_msg.get("caption")
        if caption:
            return caption

    video_msg = message.get("videoMessage")
    if isinstance(video_msg, dict):
        caption = video_msg.get("caption") or video_msg.get("title")
        if caption:
            return caption

    doc_msg = message.get("documentMessage")
    if isinstance(doc_msg, dict):
        caption = doc_msg.get("caption") or doc_msg.get("title")
        if caption:
            return caption

    buttons_resp = message.get("buttonsResponseMessage")
    if isinstance(buttons_resp, dict):
        text = buttons_resp.get("selectedDisplayText") or buttons_resp.get("selectedButtonId") or buttons_resp.get("selectedId")
        if text:
            return text

    template_resp = message.get("templateButtonReplyMessage")
    if isinstance(template_resp, dict):
        text = template_resp.get("selectedDisplayText") or template_resp.get("selectedId")
        if text:
            return text

    list_resp = message.get("listResponseMessage")
    if isinstance(list_resp, dict):
        single = list_resp.get("singleSelectReply")
        if isinstance(single, dict):
            title = single.get("title") or single.get("selectedRowId")
            if title:
                return title

    interactive_resp = message.get("interactiveResponseMessage")
    if isinstance(interactive_resp, dict):
        native_flow = interactive_resp.get("nativeFlowResponseMessage")
        if isinstance(native_flow, dict):
            for key in ("buttonsResponseMessage", "listResponseMessage"):
                nested = native_flow.get(key)
                if isinstance(nested, dict):
                    text = _extract_text_from_message({key: nested})
                    if text:
                        return text
        body = interactive_resp.get("body")
        if isinstance(body, str) and body:
            return body

    text_msg = message.get("textMessage")
    if isinstance(text_msg, dict) and text_msg.get("text"):
        return text_msg.get("text")

    return None
