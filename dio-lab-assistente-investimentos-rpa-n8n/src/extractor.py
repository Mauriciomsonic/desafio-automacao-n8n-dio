import logging
import time
from pathlib import Path
from typing import List
import requests
from bs4 import BeautifulSoup

from .config import AppConfig
from .models import Cliente

logger = logging.getLogger(__name__)


class ClienteExtractor:
    def __init__(self, config: AppConfig):
        self.config = config

    def extrair(self) -> List[Cliente]:
        html = self._fetch_com_retry(self.config.url_clientes)
        return self._parse_html(html)

    def _fetch_com_retry(self, url: str) -> str:
        # Fallback para arquivo local caso a URL seja template ou arquivo local
        base_dir = Path(__file__).resolve().parent.parent
        local_html = base_dir / "docs" / "index.html"

        if not url or "<" in url or "seu-usuario" in url:
            if local_html.exists():
                logger.info("URL remota não configurada. Usando arquivo local: %s", local_html)
                with open(local_html, "r", encoding="utf-8") as f:
                    return f.read()

        if not url.startswith("http"):
            path_candidate = Path(url)
            if path_candidate.exists():
                with open(path_candidate, "r", encoding="utf-8") as f:
                    return f.read()
            elif local_html.exists():
                with open(local_html, "r", encoding="utf-8") as f:
                    return f.read()

        # Requisição HTTP com retry e backoff exponencial
        for tentativa in range(1, self.config.max_retries + 1):
            try:
                logger.info("Buscando página de clientes (tentativa %s)...", tentativa)
                resp = requests.get(url, timeout=self.config.timeout_http)
                resp.raise_for_status()
                resp.encoding = "utf-8"
                return resp.text
            except requests.RequestException as exc:
                logger.warning("Falha na tentativa %s: %s", tentativa, exc)
                if tentativa == self.config.max_retries:
                    if local_html.exists():
                        logger.warning(
                            "Todas as tentativas falharam para %s. Recorrendo ao arquivo local de contingência: %s",
                            url, local_html
                        )
                        with open(local_html, "r", encoding="utf-8") as f:
                            return f.read()
                    raise RuntimeError(
                        f"Não foi possível acessar {url} após {self.config.max_retries} tentativas"
                    ) from exc
                time.sleep(2 ** (tentativa - 1))

        return ""

    def _parse_html(self, html: str) -> List[Cliente]:
        soup = BeautifulSoup(html, "html.parser")
        tabela = soup.find("table")
        if not tabela:
            raise ValueError("Elemento <table> não encontrado na página.")

        # Suporta detecção de cabeçalhos via thead ou primeira linha
        th_elements = tabela.find_all("th")
        if th_elements:
            raw_headers = [th.get_text(strip=True) for th in th_elements]
        else:
            first_tr = tabela.find("tr")
            if not first_tr:
                raise ValueError("Nenhuma linha de cabeçalho encontrada na tabela.")
            raw_headers = [td.get_text(strip=True) for td in first_tr.find_all(["th", "td"])]

        # Normaliza e mapeia cabeçalhos para os campos do schema Cliente
        headers = []
        for h in raw_headers:
            h_clean = h.lower().replace(" ", "_").replace("-", "")
            if "saldo" in h_clean:
                headers.append("saldo")
            elif "perfil" in h_clean:
                headers.append("perfil")
            elif "email" in h_clean or "e_mail" in h_clean:
                headers.append("email")
            elif "nome" in h_clean:
                headers.append("nome")
            else:
                headers.append(h_clean)

        logger.info("Cabeçalhos detectados e mapeados: %s", headers)

        # Suporta tabela com ou sem <tbody>
        body = tabela.find("tbody")
        if body:
            linhas = body.find_all("tr")
        else:
            todas_linhas = tabela.find_all("tr")
            linhas = todas_linhas[1:] if th_elements or len(todas_linhas) > 1 else todas_linhas

        clientes: List[Cliente] = []
        for idx, row in enumerate(linhas, start=1):
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) != len(headers) or not any(cols):
                logger.debug("Ignorando linha %s (vazia ou malformada)", idx)
                continue

            raw = dict(zip(headers, cols))
            try:
                cliente = Cliente(**raw)
                clientes.append(cliente)
            except Exception as exc:
                logger.error("Linha %s inválida: %s — erro: %s", idx, raw, exc)
                raise ValueError(f"Dados do cliente na linha {idx} são inválidos: {exc}") from exc

        logger.info("%s clientes extraídos com sucesso.", len(clientes))
        return clientes
