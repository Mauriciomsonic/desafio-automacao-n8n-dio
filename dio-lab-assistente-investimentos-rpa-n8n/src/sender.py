import json
import logging
from typing import Any, Dict
import requests
from .config import AppConfig

logger = logging.getLogger(__name__)


class N8NSender:
    def __init__(self, config: AppConfig):
        self.config = config

    def enviar(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self.config.webhook_n8n
        if not url or "seu-n8n" in url or "<" in url:
            logger.warning("WEBHOOK_N8N não configurado ou em modo demonstração no .env.")
            return {
                "status": "modo_demonstracao",
                "mensagem": "Webhook N8N não configurado. Recomendações validadas e processadas localmente com sucesso!",
                "total_clientes": payload.get("total", len(payload.get("clientes", []))),
            }

        logger.info("Enviando payload com %s clientes para N8N...", payload.get("total", 0))
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            resp.raise_for_status()
            logger.info("N8N respondeu com sucesso: HTTP %s", resp.status_code)
            return resp.json() if resp.text else {"status": "ok", "http_status": resp.status_code}
        except requests.RequestException as exc:
            logger.error("Falha na comunicação com N8N: %s", exc)
            raise RuntimeError(f"Erro na comunicação com N8N: {exc}") from exc
