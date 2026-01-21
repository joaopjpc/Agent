"""Cliente para enviar mensagens via Evolution API (não oficial do WhatsApp)."""
# Basicamente faço um post simples para o endpoint correto da API REST do Evolution
# e a Evolution cuida do resto (autenticação, fila, etc) e envia a mensagem via WhatsApp.

from __future__ import annotations

import logging
from typing import Any

import httpx


logger = logging.getLogger(__name__)


class EvolutionClient:
    """Cliente mínimo para envio de mensagens de texto."""

    def __init__( 
        self,
        base_url: str,
        apikey: str,
        instance: str,
        *,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/") 
        self.apikey = apikey
        self.instance = instance
        self.timeout = timeout

    async def send_text(self, number: str, text: str, delay: int = 1) -> dict[str, Any]:
        """Envia mensagem de texto para um número via Evolution API."""
        url = f"{self.base_url}/message/sendText/{self.instance}"
        payload = {"number": number, "text": text, "delay": delay}

        logger.info("Evolution request: url=%s payload=%s", url, payload)

        # Envia a mensagem usando o cliente HTTP
        async with httpx.AsyncClient(timeout=self.timeout) as client: 
            response = await client.post(url, headers={"apikey": self.apikey}, json=payload)
            logger.info("Evolution response: status=%s body=%s", response.status_code, response.text)
            if response.status_code >= 400:
                logger.error(
                    "Evolution response error: status=%s body=%s",
                    response.status_code,
                    response.text,
                )
            response.raise_for_status()
            return response.json()
