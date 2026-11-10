#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TypeSafe AI - Validador de Suitability e Confiança com o Modelo Jev
Projeto: Assistente de Investimentos com RPA e N8N (DIO Santander)
=============================================================================
Este script utiliza o modelo flagship System One 'jev-1.13' da TypeSafe para:
1. Analisar a carteira de clientes extraída pelo RPA.
2. Fazer perguntas tipadas (Choice, Score, Noul) sobre conformidade e risco.
3. Aplicar o padrão 'Confidence-Gated Routing':
   - Confiança >= 0.85: Aprovado para despacho automático.
   - Confiança < 0.85: Sinalizado para revisão de um consultor humano.
=============================================================================
"""

import os
import sys
import json
from pathlib import Path

# Configura UTF-8 no terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

import requests

# Função nativa para carregar .env sem depender de pacotes externos
def carregar_chave_env() -> str:
    # 1. Tenta variável de ambiente do sistema
    key = os.getenv("TYPESAFE_API_KEY", "").strip()
    if key and key != "ts_sua_chave_aqui":
        return key

    # 2. Tenta ler o arquivo .env no diretório atual e no diretório pai
    candidatos = [
        Path(".env"),
        Path(__file__).resolve().parent.parent / ".env",
        Path.cwd() / ".env"
    ]
    for p in candidatos:
        if p.exists():
            try:
                for linha in p.read_text(encoding="utf-8").splitlines():
                    linha = linha.strip()
                    if not linha or linha.startswith("#"):
                        continue
                    if "TYPESAFE_API_KEY=" in linha:
                        val = linha.split("TYPESAFE_API_KEY=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
                    elif linha.startswith("apikey_") or linha.startswith("ts_"):
                        return linha
            except Exception:
                pass
    return ""

API_KEY = carregar_chave_env()

# Carrega base de clientes do HTML ou de arquivo
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"

# Endpoint oficial da API TypeSafe
TYPESAFE_API_URL = "https://api.typesafe.ai/v1/evaluate"


def carregar_clientes_amostra() -> list:
    """
    Retorna a lista de clientes para validação do Jev.
    """
    return [
        {
            "id": "CLI-1001",
            "nome": "Carlos Eduardo Silva",
            "saldo": 1500.00,
            "perfil": "Conservador",
            "ativo_recomendado": "CDB Liquidez Diária (Mín: R$ 1.000, 12.5% a.a.)"
        },
        {
            "id": "CLI-1002",
            "nome": "Mariana Rios de Souza",
            "saldo": 15000.00,
            "perfil": "Moderado",
            "ativo_recomendado": "Fundo Multimercado (Mín: R$ 5.000, 16.0% a.a.)"
        },
        {
            "id": "CLI-1003",
            "nome": "Rodrigo Mendes Prado",
            "saldo": 25000.00,
            "perfil": "Arrojado",
            "ativo_recomendado": "Ações ETF e Criptoativos (Rendimento Variável)"
        },
        {
            "id": "CLI-1004",
            "nome": "Ana Paula Albuquerque",
            "saldo": 350.00,
            "perfil": "Conservador",
            "ativo_recomendado": "Poupança / Reserva de Liquidez (Mín: R$ 100)"
        }
    ]


def avaliar_com_jev(cliente: dict, api_key: str) -> dict:
    """
    Envia o contexto do cliente para o modelo Jev da TypeSafe AI.
    """
    state_context = f"""
    DADOS DO CLIENTE:
    Nome: {cliente['nome']} (ID: {cliente['id']})
    Saldo Disponível: R$ {cliente['saldo']:,.2f}
    Perfil de Investidor Declarado: {cliente['perfil']}
    Ativo Selecionado pelo Algoritmo: {cliente['ativo_recomendado']}
    """

    payload = {
        "model": "jev-1.13",
        "state": state_context.strip(),
        "questions": {
            "conformidade_suitability": {
                "type": "choice",
                "question": "A recomendação de produto está compatível com as regras de suitability do perfil?",
                "options": [
                    {"id": "conforme", "description": "Ativo 100% alinhado à tolerância de risco e patrimônio"},
                    {"id": "risco_excessivo", "description": "Ativo apresenta risco superior ao aceito pelo perfil"},
                    {"id": "subalocacao", "description": "Risco excessivamente baixo para o potencial do investidor"}
                ]
            },
            "grau_aderencia": {
                "type": "score",
                "question": "Qual o grau de eficiência do aporte em relação ao saldo em conta?",
                "levels": [
                    {"score": 1, "description": "Aporte compromete mais de 90% do saldo líquido"},
                    {"score": 2, "description": "Aporte consome entre 50% e 90% do saldo líquido"},
                    {"score": 3, "description": "Aporte equilibrado, preservando capital para diversificação"}
                ]
            },
            "aprovacao_automatica": {
                "type": "noul",
                "question": "Este portfólio pode ser despachado de forma 100% autônoma sem passar por revisão humana?"
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(TYPESAFE_API_URL, json=payload, headers=headers, timeout=12)
    response.raise_for_status()
    return response.json()


def main():
    print("=" * 70)
    print("🛡️ TYPESAFE AI — AVALIADOR DE SUITABILITY COM MODELO JEV (SYSTEM ONE)")
    print("=" * 70)

    if not API_KEY or API_KEY == "ts_sua_chave_aqui":
        print("\n❌ Chave da TypeSafe não configurada!")
        print("Para configurar:")
        print("1. Defina a variável de ambiente:  $env:TYPESAFE_API_KEY = 'sua_chave'")
        print("2. Ou insira a chave no arquivo: .env na raiz do projeto")
        print("\nExemplo de chamada que será executada:")
        print("  Model: jev-1.13")
        print("  Primitives: Choice (Suitability), Score (Aderência), Noul (Auto-Aprovação)")
        sys.exit(1)

    print(f"[*] Chave detectada: {API_KEY[:6]}...{API_KEY[-4:]}")
    print("[*] Conectando ao modelo Jev (jev-1.13)...")

    clientes = carregar_clientes_amostra()
    print(f"[*] Processando {len(clientes)} investidores da carteira...\n")

    for c in clientes:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"👤 Cliente: {c['nome']} [{c['id']}] | Saldo: R$ {c['saldo']:,.2f} | Perfil: {c['perfil']}")
        print(f"📌 Ativo Proposto: {c['ativo_recomendado']}")

        try:
            res = avaliar_com_jev(c, API_KEY)
            confianca = res.get("confidence", 0.0)
            respostas = res.get("answers", {})

            decisao_suitability = respostas.get("conformidade_suitability", {}).get("value", "N/A")
            score_aderencia = respostas.get("grau_aderencia", {}).get("value", 0)
            p_auto = respostas.get("aprovacao_automatica", {}).get("probability", 0.0)

            print(f"🔍 Decisão Jev: {decisao_suitability.upper()} (Score: {score_aderencia}/3)")
            print(f"📊 Probabilidade de Aprovação Direta: {p_auto:.1%}")
            print(f"🎯 Índice de Confiança do Modelo: {confianca:.1%}")

            # Padrão Confidence-Gated Routing
            if confianca >= 0.85 and decisao_suitability == "conforme":
                print("✅ AÇÃO: [DISPARO IMEDIATO] Aprovado com alta confiança pelo Jev.")
            else:
                print("⚠️ AÇÃO: [ROTEAMENTO PARA REVISÃO] Confiança ou adequação requer assessor humano.")

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao consultar API TypeSafe: {e}")

    print("\n" + "=" * 70)
    print("✅ Avaliação com TypeSafe Jev finalizada com sucesso!")


if __name__ == "__main__":
    main()
