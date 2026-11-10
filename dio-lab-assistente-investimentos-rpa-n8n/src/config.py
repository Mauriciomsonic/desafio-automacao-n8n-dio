import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Carrega .env do diretório raiz se existir
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class AppConfig:
    url_clientes: str
    url_csv: str
    webhook_n8n: str
    timeout_http: int = 15
    max_retries: int = 3
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "AppConfig":
        base_dir = Path(__file__).resolve().parent.parent
        default_local_html = str(base_dir / "docs" / "index.html")
        default_local_csv = str(base_dir / "docs" / "data.csv")

        return cls(
            url_clientes=os.getenv(
                "URL_CLIENTES",
                "https://<seu-usuario>.github.io/dio-lab-assistente-investimentos-rpa-n8n/",
            ),
            url_csv=os.getenv(
                "URL_CSV",
                "https://<seu-usuario>.github.io/dio-lab-assistente-investimentos-rpa-n8n/data.csv",
            ),
            webhook_n8n=os.getenv(
                "WEBHOOK_N8N",
                "https://<seu-n8n>.n8n.cloud/webhook/assistente-investimentos",
            ),
            timeout_http=int(os.getenv("TIMEOUT_HTTP", "15")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
