"""Valida o parsing de payloads MESSAGES_UPSERT da Evolution API."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from beachbot.webhook.parsing import parse_messages_upsert  # noqa: E402

SAMPLES = ROOT / "samples"


def _load_sample(filename: str) -> dict:
    path = SAMPLES / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_parsed(
    filename: str,
    expected_sender: str,
    expected_text: str,
    expected_message_id: str,
    expected_instance_id: str,
) -> None:
    payload = _load_sample(filename)
    parsed = parse_messages_upsert(payload)
    assert parsed, f"Falha ao parsear {filename}"
    assert parsed.sender == expected_sender, f"sender inesperado em {filename}: {parsed.sender}"
    assert parsed.text == expected_text, f"text inesperado em {filename}: {parsed.text}"
    assert parsed.message_id == expected_message_id, f"message_id inesperado em {filename}: {parsed.message_id}"
    assert parsed.instance_id == expected_instance_id, f"instance_id inesperado em {filename}: {parsed.instance_id}"
    print(f"[ok] {filename} -> sender={parsed.sender} text='{parsed.text}' id={parsed.message_id} instance={parsed.instance_id}")


def _assert_ignored(filename: str, reason: str) -> None:
    payload = _load_sample(filename)
    parsed = parse_messages_upsert(payload)
    assert parsed is None, f"Esperava ignorar {filename} ({reason})"
    print(f"[ok] {filename} ignorado ({reason})")


def main() -> None:
    _assert_parsed(
        "messages_upsert_conversation.json",
        expected_sender="5521973641659",
        expected_text="Oi, quero saber mais",
        expected_message_id="BAE599990001",
        expected_instance_id="demo-instance",
    )
    _assert_parsed(
        "messages_upsert_extended_text.json",
        expected_sender="5521973641659",
        expected_text="Quero aula experimental gratuita",
        expected_message_id="XYZ123",
        expected_instance_id="demo-instance",
    )
    _assert_parsed(
        "messages_upsert_buttons_response.json",
        expected_sender="5521973641659",
        expected_text="Agendar aula experimental",
        expected_message_id="BTN-123",
        expected_instance_id="demo-instance",
    )
    _assert_ignored("messages_upsert_from_me.json", reason="fromMe True")
    _assert_ignored("messages_other_event.json", reason="evento diferente")


if __name__ == "__main__":
    main()
