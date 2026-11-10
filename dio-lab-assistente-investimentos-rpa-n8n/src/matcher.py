from decimal import Decimal
from typing import List
from .models import Cliente, Investimento, Recomendacao

INTROS = {
    "Conservador": "foco em segurança e preservação de capital",
    "Moderado": "equilíbrio entre segurança e rentabilidade",
    "Arrojado": "potencial de retorno elevado com maior exposição a risco",
}


class RecomendacaoMatcher:
    def cruzar(
        self, clientes: List[Cliente], investimentos: List[Investimento]
    ) -> List[Recomendacao]:
        resultado: List[Recomendacao] = []
        for cliente in clientes:
            do_perfil = [i for i in investimentos if i.perfil == cliente.perfil]
            compativeis = sorted(
                [i for i in do_perfil if cliente.saldo >= i.minimo],
                key=lambda x: x.minimo,
            )
            mensagem = self._gerar_mensagem(cliente, compativeis)
            resultado.append(
                Recomendacao(
                    cliente=cliente,
                    investimentos_recomendados=compativeis,
                    mensagem=mensagem,
                )
            )
        return resultado

    def _formatar_moeda(self, valor: Decimal) -> str:
        return f"R$ {valor:,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")

    def _gerar_mensagem(self, cliente: Cliente, compativeis: List[Investimento]) -> str:
        nome = cliente.nome
        perfil = cliente.perfil.value
        saldo_fmt = self._formatar_moeda(cliente.saldo)

        if not compativeis:
            return (
                f"Olá {nome}, identificamos seu perfil {perfil}, mas seu saldo atual "
                f"({saldo_fmt}) ainda não atinge o mínimo exigido para as opções "
                f"disponíveis. Recomendamos aguardar ou aportar valores adicionais."
            )

        produtos = "\n".join(
            f" • {i.produto} — rentabilidade {i.rentabilidade} (mín. {self._formatar_moeda(i.minimo)})"
            for i in compativeis
        )

        return (
            f"Olá {nome}, com base no seu perfil {perfil} ({INTROS.get(perfil, '')}) "
            f"e saldo de {saldo_fmt}, recomendamos:\n{produtos}"
        )
