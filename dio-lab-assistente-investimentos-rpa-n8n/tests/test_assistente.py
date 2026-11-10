import unittest
from decimal import Decimal
from pathlib import Path

from src.models import Cliente, PerfilInvestidor, Investimento, Recomendacao
from src.matcher import RecomendacaoMatcher
from src.config import AppConfig
from src.extractor import ClienteExtractor
from src.investments import InvestimentosLoader


class TestAssistenteInvestimentos(unittest.TestCase):
    def test_parse_saldo_variados(self):
        """Valida que o parsing monetário brasileiro não quebra com múltiplos formatos."""
        c1 = Cliente(nome="Teste 1", saldo="R$ 1.234,56", perfil=PerfilInvestidor.CONSERVADOR)
        self.assertEqual(c1.saldo, Decimal("1234.56"))

        c2 = Cliente(nome="Teste 2", saldo="R$ 1.234.567,89", perfil=PerfilInvestidor.MODERADO)
        self.assertEqual(c2.saldo, Decimal("1234567.89"))

        c3 = Cliente(nome="Teste 3", saldo=5000, perfil=PerfilInvestidor.ARROJADO)
        self.assertEqual(c3.saldo, Decimal("5000"))

        c4 = Cliente(nome="Teste 4", saldo="R$ 350,00", perfil=PerfilInvestidor.CONSERVADOR)
        self.assertEqual(c4.saldo, Decimal("350.00"))

    def test_matcher_filtro_perfil_e_saldo(self):
        """Valida a regra de elegibilidade: saldo >= minimo e ordenação por mínimo crescente."""
        investimentos = [
            Investimento(perfil=PerfilInvestidor.CONSERVADOR, produto="Poupança", minimo=100, rentabilidade="6.2%"),
            Investimento(perfil=PerfilInvestidor.CONSERVADOR, produto="Tesouro Selic", minimo=500, rentabilidade="13.0%"),
            Investimento(perfil=PerfilInvestidor.CONSERVADOR, produto="CDB Liquidez Diária", minimo=1000, rentabilidade="12.5%"),
            Investimento(perfil=PerfilInvestidor.MODERADO, produto="CDB Prefixado", minimo=1000, rentabilidade="14.0%"),
        ]

        matcher = RecomendacaoMatcher()

        # Cliente com saldo R$ 800 só pode receber Poupança (100) e Selic (500), mas NÃO CDB (1000)
        cliente = Cliente(nome="Ana Silva", saldo="R$ 800,00", perfil=PerfilInvestidor.CONSERVADOR)
        recs = matcher.cruzar([cliente], investimentos)

        self.assertEqual(len(recs), 1)
        compativeis = recs[0].investimentos_recomendados
        self.assertEqual(len(compativeis), 2)
        self.assertEqual(compativeis[0].produto, "Poupança")
        self.assertEqual(compativeis[1].produto, "Tesouro Selic")
        self.assertIn("Poupança", recs[0].mensagem)
        self.assertIn("Tesouro Selic", recs[0].mensagem)
        self.assertNotIn("CDB Liquidez Diária", recs[0].mensagem)

    def test_matcher_saldo_insuficiente_fallback(self):
        """Valida o fallback de saldo insuficiente quando cliente não atinge nenhum produto."""
        investimentos = [
            Investimento(perfil=PerfilInvestidor.CONSERVADOR, produto="CDB", minimo=1000, rentabilidade="12.0%")
        ]
        cliente = Cliente(nome="João", saldo="R$ 150,00", perfil=PerfilInvestidor.CONSERVADOR)
        matcher = RecomendacaoMatcher()
        recs = matcher.cruzar([cliente], investimentos)

        self.assertEqual(len(recs), 1)
        self.assertEqual(len(recs[0].investimentos_recomendados), 0)
        self.assertIn("ainda não atinge o mínimo exigido", recs[0].mensagem)

    def test_extractor_local_e_investments_local(self):
        """Valida que os loaders conseguem extrair da base do projeto localmente."""
        config = AppConfig.from_env()
        extractor = ClienteExtractor(config)
        clientes = extractor.extrair()
        self.assertGreaterEqual(len(clientes), 6)

        loader = InvestimentosLoader(config)
        investimentos = loader.carregar()
        self.assertEqual(len(investimentos), 9)


if __name__ == "__main__":
    unittest.main()
