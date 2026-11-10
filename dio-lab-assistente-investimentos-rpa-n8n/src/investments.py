import logging
from io import StringIO
from pathlib import Path
from typing import List
import pandas as pd
import requests

from .config import AppConfig
from .models import Investimento

logger = logging.getLogger(__name__)


class InvestimentosLoader:
    def __init__(self, config: AppConfig):
        self.config = config

    def carregar(self) -> List[Investimento]:
        logger.info("Carregando CSV de investimentos de %s", self.config.url_csv)
        base_dir = Path(__file__).resolve().parent.parent
        local_csv = base_dir / "docs" / "data.csv"

        texto_csv = ""

        # Verifica se a URL é placeholder ou arquivo local
        if not self.config.url_csv or "<" in self.config.url_csv or "seu-usuario" in self.config.url_csv:
            if local_csv.exists():
                logger.info("URL remota de CSV não configurada. Usando arquivo local: %s", local_csv)
                with open(local_csv, "r", encoding="utf-8-sig") as f:
                    texto_csv = f.read()
        elif not self.config.url_csv.startswith("http"):
            path_candidate = Path(self.config.url_csv)
            if path_candidate.exists():
                with open(path_candidate, "r", encoding="utf-8-sig") as f:
                    texto_csv = f.read()
            elif local_csv.exists():
                with open(local_csv, "r", encoding="utf-8-sig") as f:
                    texto_csv = f.read()

        if not texto_csv:
            try:
                resp = requests.get(self.config.url_csv, timeout=self.config.timeout_http)
                resp.raise_for_status()
                # Remove BOM UTF-8 se presente (\ufeff)
                texto_csv = resp.text.lstrip("\ufeff")
            except requests.RequestException as exc:
                if local_csv.exists():
                    logger.warning(
                        "Falha ao carregar CSV remoto (%s). Usando contingência local: %s",
                        exc, local_csv
                    )
                    with open(local_csv, "r", encoding="utf-8-sig") as f:
                        texto_csv = f.read()
                else:
                    raise RuntimeError(f"Falha ao carregar CSV: {exc}") from exc

        # Trata BOM se ainda estiver presente
        texto_csv = texto_csv.lstrip("\ufeff")
        df = pd.read_csv(StringIO(texto_csv))
        df.columns = [c.strip().lower() for c in df.columns]

        # Normaliza tipos
        df["minimo"] = pd.to_numeric(
            df["minimo"].astype(str).str.replace(r"[^\d]", "", regex=True),
            errors="coerce"
        )
        df = df.dropna(subset=["minimo"])
        df["rentabilidade"] = df["rentabilidade"].astype(str).str.strip()

        investimentos: List[Investimento] = []
        for _, row in df.iterrows():
            try:
                investimentos.append(Investimento(**row.to_dict()))
            except Exception as exc:
                logger.error("Investimento inválido: %s — erro: %s", row.to_dict(), exc)
                raise

        logger.info("%s investimentos carregados.", len(investimentos))
        return investimentos
