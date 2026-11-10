"""
=============================================================================
Gerenciador & Agendador Contínuo do Caçador de Vagas ATS
Projeto: DIO Santander / TIVIT / AWS & Azure AI
=============================================================================
Comandos suportados:
  python gerenciador_vagas.py --executar         -> Roda o ciclo imediatamente
  python gerenciador_vagas.py --daemon           -> Executa continuamente nos slots 10h, 12h, 14h, 16h e 18h
  python gerenciador_vagas.py --adicionar-vaga   -> Adiciona interativamente uma nova vaga encontrada
  python gerenciador_vagas.py --historico        -> Exibe o resumo do banco de dados
  python gerenciador_vagas.py --abrir-dashboard  -> Abre o dashboard no navegador padrão
=============================================================================
"""

import os
import sys
import time
import json
import webbrowser
from datetime import datetime, timedelta

# Configura UTF-8 no Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import (
    HORA_INICIO, HORA_FIM, INTERVALO_HORAS, HORARIOS_EXECUCAO, BASE_DIR
)
from run_demo import executar_ciclo_teste, validar_janela_horario
from ver_historico import exibir_painel_historico

def calcular_segundos_ate_proximo_slot() -> int:
    """Calcula o tempo em segundos até o próximo slot (10h, 12h, 14h, 16h ou 18h)."""
    agora = datetime.now()
    hoje = agora.date()
    
    # Gera os datetimes dos slots de hoje
    slots_hoje = [datetime.combine(hoje, datetime.min.time()).replace(hour=h, minute=0, second=0) for h in HORARIOS_EXECUCAO]
    
    # Próximo slot hoje
    proximos = [s for s in slots_hoje if s > agora]
    
    if proximos:
        alvo = proximos[0]
    else:
        # Primeiro slot de amanhã (10:00)
        amanha = hoje + timedelta(days=1)
        alvo = datetime.combine(amanha, datetime.min.time()).replace(hour=HORARIOS_EXECUCAO[0], minute=0, second=0)
        
    delta = (alvo - agora).total_seconds()
    return max(int(delta), 1), alvo

def iniciar_daemon():
    """Inicia o daemon de agendamento contínuo a cada 2 horas nos slots 10h às 18h."""
    print("\n" + "=" * 80)
    print("⏰ AGENDADOR CONTÍNUO ATIVADO (DAEMON MODE)")
    print("=" * 80)
    print(f">> Janela de Execução: Diariamente entre {HORA_INICIO}:00 e {HORA_FIM}:00 (Fuso Local)")
    print(f">> Slots Autorizados : {', '.join([f'{h:02d}:00' for h in HORARIOS_EXECUCAO])}")
    print(">> Pressione CTRL+C para interromper o monitoramento.\n")
    
    try:
        while True:
            agora = datetime.now()
            hora_atual = agora.hour
            minuto_atual = agora.minute
            
            # Se coincide com um dos slots dentro de uma margem de 2 minutos
            if hora_atual in HORARIOS_EXECUCAO and minuto_atual <= 2:
                print(f"\n[🔔 ALARME DISPARADO] Horário programado atingido: {agora.strftime('%H:%M:%S')}")
                executar_ciclo_teste(ignorar_janela=False)
                # Aguarda 3 minutos para não re-executar no mesmo minuto
                time.sleep(180)
            else:
                segundos_espera, proximo_horario = calcular_segundos_ate_proximo_slot()
                print(f"[⏳ AGENDADOR EM ESPERA] Próximo disparo em: {proximo_horario.strftime('%d/%m/%Y às %H:%M:%S')} (em ~{segundos_espera // 60} minutos)")
                # Dorme em blocos de até 60 segundos para permitir interrupção suave
                tempo_sono = min(segundos_espera, 60)
                time.sleep(tempo_sono)
    except KeyboardInterrupt:
        print("\n\n[🛑 AGENDADOR INTERROMPIDO] Finalizado pelo usuário com sucesso.")

def adicionar_vaga_interativa(empresa: str, titulo: str, plataforma: str, url: str, obrigatorios: list, desejaveis: list):
    """Adiciona uma nova oportunidade ao arquivo de entrada para processamento."""
    caminho_entrada = os.path.join(BASE_DIR, "entrada_vagas.json")
    vagas_existentes = []
    
    if os.path.exists(caminho_entrada):
        try:
            with open(caminho_entrada, "r", encoding="utf-8") as f:
                vagas_existentes = json.load(f)
                if not isinstance(vagas_existentes, list):
                    vagas_existentes = []
        except Exception:
            vagas_existentes = []
            
    nova = {
        "empresa": empresa,
        "titulo": titulo,
        "plataforma": plataforma,
        "url": url,
        "requisitos_obrigatorios": obrigatorios,
        "requisitos_desejaveis": desejaveis
    }
    
    vagas_existentes.append(nova)
    
    with open(caminho_entrada, "w", encoding="utf-8") as f:
        json.dump(vagas_existentes, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Nova vaga registrada em entrada_vagas.json:")
    print(f"   • Empresa: {empresa}")
    print(f"   • Cargo  : {titulo}")
    print(f"   • Fonte  : {plataforma}")
    print(f"   • Total de novas vagas pendentes: {len(vagas_existentes)}")

def abrir_dashboard():
    """Abre o dashboard.html no navegador padrão."""
    caminho = os.path.join(BASE_DIR, "dashboard.html")
    if os.path.exists(caminho):
        print(f"\n🌐 Abrindo Dashboard no navegador: {caminho}")
        webbrowser.open(f"file:///{os.path.abspath(caminho)}")
    else:
        print(f"[!] Arquivo de dashboard não encontrado em {caminho}")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if "--daemon" in args:
        iniciar_daemon()
    elif "--historico" in args:
        exibir_painel_historico()
    elif "--abrir-dashboard" in args:
        abrir_dashboard()
    elif "--adicionar" in args or "--adicionar-vaga" in args:
        print("\n📝 Cadastro de Nova Oportunidade para Avaliação ATS:")
        emp = input("Empresa: ").strip() or "Empresa Exemplo"
        car = input("Cargo: ").strip() or "Especialista Cloud"
        plat = input("Plataforma (LinkedIn/Gupy/Indeed): ").strip() or "LinkedIn"
        url_vaga = input("URL da vaga: ").strip() or "https://linkedin.com/jobs/vaga-teste"
        req_obrig = [s.strip() for s in (input("Requisitos Obrigatórios (separados por vírgula): ") or "AWS, Linux, Docker").split(",") if s.strip()]
        req_desej = [s.strip() for s in (input("Requisitos Desejáveis (separados por vírgula): ") or "Python, Terraform").split(",") if s.strip()]
        adicionar_vaga_interativa(emp, car, plat, url_vaga, req_obrig, req_desej)
    else:
        # Padrão: roda o ciclo com verificação da janela
        print("💡 Dica: Use --daemon para rodar contínuo, --historico para relatório, ou --abrir-dashboard.")
        executar_ciclo_teste(ignorar_janela=True)
