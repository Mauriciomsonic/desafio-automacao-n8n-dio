import json
import logging
import sys
from pathlib import Path

# Suporte a execução tanto via "python -m src.extrair_clientes" quanto "python src/extrair_clientes.py"
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.config import AppConfig
    from src.extractor import ClienteExtractor
    from src.investments import InvestimentosLoader
    from src.matcher import RecomendacaoMatcher
    from src.sender import N8NSender
else:
    from .config import AppConfig
    from .extractor import ClienteExtractor
    from .investments import InvestimentosLoader
    from .matcher import RecomendacaoMatcher
    from .sender import N8NSender


def configurar_logging(nivel: str):
    logging.basicConfig(
        level=getattr(logging, nivel.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    config = AppConfig.from_env()
    configurar_logging(config.log_level)
    logger = logging.getLogger("assistente_investimentos")

    try:
        logger.info("Iniciando pipeline do Assistente de Investimentos...")
        clientes = ClienteExtractor(config).extrair()
        investimentos = InvestimentosLoader(config).carregar()
        recomendacoes = RecomendacaoMatcher().cruzar(clientes, investimentos)

        logger.info("=" * 60)
        for r in recomendacoes:
            logger.info("\n%s", r.mensagem)
        logger.info("=" * 60)

        payload = {
            "clientes": [rec.model_dump(mode="json") for rec in recomendacoes],
            "total": len(recomendacoes),
        }

        resposta_n8n = N8NSender(config).enviar(payload)
        logger.info(
            "Resultado da Integração N8N:\n%s",
            json.dumps(resposta_n8n, indent=2, ensure_ascii=False),
        )
        logger.info("Pipeline concluído com sucesso!")
    except Exception as exc:
        logger.exception("Pipeline falhou: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
