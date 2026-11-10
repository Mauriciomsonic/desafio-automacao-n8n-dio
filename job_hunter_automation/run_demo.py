import os
import sys
import re
import json
from datetime import datetime

# Garante suporte a UTF-8 no terminal Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import (
    HORA_INICIO, HORA_FIM, INTERVALO_HORAS, HORARIOS_EXECUCAO, EXECUCAO_DIARIA,
    DIAS_UTEIS, SCORE_CORTE_MINIMO, OUTPUT_DIR, BASE_DIR
)
from db_manager import (
    inicializar_banco, gerar_hash_vaga, vaga_ja_processada,
    registrar_candidatura, listar_historico, exportar_relatorio_csv, exportar_relatorio_json
)
from ats_engine import analisar_compatibilidade, gerar_curriculo_ats
from gmail_watcher import obter_vagas_do_gmail
from jev_suitability import avaliar_vaga_com_jev
from audio_notifier import tocar_efeito_sonoro_ciclo

def validar_janela_horario(agora: datetime = None, apenas_slots_exatos: bool = False) -> bool:
    """
    Verifica se o momento atual (fuso horário local) está dentro do ciclo de execução
    permitido: diariamente entre 10h e 18h a cada 2 horas (10h, 12h, 14h, 16h e 18h).
    Preserva as regras de segurança e o bloqueio de disparo fora desse período.
    """
    if agora is None:
        agora = datetime.now()
    
    hora_atual = agora.hour
    no_periodo = HORA_INICIO <= hora_atual <= HORA_FIM
    
    if apenas_slots_exatos:
        return no_periodo and (hora_atual in HORARIOS_EXECUCAO)
    
    return no_periodo

def atualizar_dashboard_com_dados_reais(registros):
    """Injeta os dados reais do banco SQLite diretamente nos arquivos dashboard.html."""
    if not registros:
        print("[!] Nenhum registro encontrado para sincronizar no dashboard.")
        return
        
    caminhos_dashboard = [
        os.path.join(BASE_DIR, "dashboard.html"),
        os.path.join(BASE_DIR, "dashboard", "index.html"),
        r"C:\Users\rodri\.gemini\antigravity\brain\79562a11-f46e-407b-bb41-031575585e44\dashboard.html"
    ]
    
    # Formata registros para o modelo esperado pelo frontend
    vagas_formatadas = []
    for idx, r in enumerate(registros, start=1):
        skills_raw = r.get("skills_match")
        if isinstance(skills_raw, str):
            skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
        elif isinstance(skills_raw, list):
            skills = skills_raw
        else:
            skills = []
            
        gaps_raw = r.get("skills_gaps")
        if isinstance(gaps_raw, str):
            gaps = [g.strip() for g in gaps_raw.split(",") if g.strip()]
        elif isinstance(gaps_raw, list):
            gaps = gaps_raw
        else:
            gaps = []

        score_val = r.get("score_match")
        if score_val is None:
            score_val = r.get("score", 0)
            
        vagas_formatadas.append({
            "id": r.get("id", idx),
            "empresa": r.get("empresa") or "Confidencial",
            "cargo": r.get("titulo_cargo") or r.get("cargo") or "Oportunidade",
            "plataforma": r.get("plataforma") or "Web / ATS",
            "score": int(round(float(score_val))),
            "status": r.get("status") or ("SUBMETIDO" if float(score_val) >= 75 else "DESCARTADO_SCORE_BAIXO"),
            "skills": skills,
            "gaps": gaps
        })
        
    bloco_js = "let vagasDB = " + json.dumps(vagas_formatadas, ensure_ascii=False, indent=6) + ";"
    padrao_regex = re.compile(r'(const|let)\s+vagasDB\s*=\s*\[.*?\];', re.DOTALL)
    
    for caminho in caminhos_dashboard:
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                
                if padrao_regex.search(conteudo):
                    novo_conteudo = padrao_regex.sub(bloco_js, conteudo, count=1)
                    with open(caminho, "w", encoding="utf-8") as f:
                        f.write(novo_conteudo)
                    print(f"   [OK] Dashboard sincronizado: {os.path.basename(caminho)} ({len(vagas_formatadas)} vagas)")
                elif "let vagasAtuais = [...vagasIniciais];" in conteudo:
                    script_injecao = f"\n    vagasAtuais = {json.dumps(vagas_formatadas, ensure_ascii=False)};"
                    novo_conteudo = conteudo.replace("let vagasAtuais = [...vagasIniciais];", "let vagasAtuais = [...vagasIniciais];" + script_injecao)
                    with open(caminho, "w", encoding="utf-8") as f:
                        f.write(novo_conteudo)
                    print(f"   [OK] Dashboard legado sincronizado: {os.path.basename(caminho)}")
                else:
                    print(f"   [AVISO] Ponto de injeção 'vagasDB' não localizado em {caminho}")
            except Exception as e:
                print(f"   [ERRO] Falha ao sincronizar dashboard em {caminho}: {e}")

def executar_ciclo_teste(ignorar_janela: bool = True):
    print("\n" + "=" * 85)
    print(">> EXECUTANDO PIPELINE REFINADO DO ROBO CACADOR DE VAGAS (ATS ENGINE v2)")
    print("=" * 85)
    
    agora = datetime.now()
    dentro_da_janela = validar_janela_horario(agora)
    
    slots_str = ", ".join([f"{h:02d}:00" for h in HORARIOS_EXECUCAO])
    print(f">> Timestamp Atual: {agora.strftime('%d/%m/%Y %H:%M:%S')} ({agora.strftime('%A')} - Fuso Horário Local)")
    print(f">> Janela Permitida: Diariamente, a cada 2 horas entre {HORA_INICIO}:00 e {HORA_FIM}:00 (Slots: {slots_str})")
    
    if dentro_da_janela:
        print(f"[OK] Status da Janela: DENTRO DO HORARIO DE EXECUCAO PERMITIDO (10h-18h).")
    else:
        print(f"[AVISO] Status da Janela: FORA DO HORARIO PERMITIDO (Permitido: 10h as 18h nos slots {slots_str}).")
        if not ignorar_janela:
            print(f"[STOP] Execucao suspensa com seguranca fora do horario de operacao. Proxima janela: {slots_str}.")
            return

    # 1. Inicializa o Banco de Dados
    inicializar_banco()
    
    # 2. Leitura de Alertas de Vagas
    print("\n>> Etapa 1: Varrendo e-mails e alertas de vagas (Gmail)...")
    vagas = obter_vagas_do_gmail(modo_teste=True)
    print(f"   Encontradas {len(vagas)} oportunidades nos alertas.")
    
    # 3. Processamento com Motor Ponderado
    print("\n>> Etapa 2: Processamento, Deduplicacao por Hash e Scoring Ponderado (70/30)...")
    
    aprovadas = 0
    duplicadas = 0
    rejeitadas = 0
    
    for i, vaga in enumerate(vagas, start=1):
        empresa = vaga["empresa"]
        titulo = vaga["titulo"]
        url = vaga["url"]
        plataforma = vaga["plataforma"]
        
        job_hash = gerar_hash_vaga(empresa, titulo, url)
        
        print(f"\n--- [Vaga {i}/{len(vagas)}] {titulo} @ {empresa} ({plataforma}) ---")
        
        # Teste de Idempotencia
        if vaga_ja_processada(job_hash):
            print(f"   [DEDUPLICACAO ATIVADA]: Vaga ja processada em ciclo anterior.")
            print(f"   Hash {job_hash[:16]}... localizado no SQLite. Envio duplicado cancelado.")
            duplicadas += 1
            continue
            
        # Analise Semantica Ponderada (70% Obrigatorios / 30% Desejaveis)
        score, skills_match, gaps, detalhes = analisar_compatibilidade(vaga)
        
        # Validacao Complementar com o Modelo TypeSafe JEV
        avaliacao_jev = avaliar_vaga_com_jev(vaga, score, skills_match)
        print(f"   Score ATS Ponderado: {score}% (Corte minimo: {SCORE_CORTE_MINIMO}%)")
        print(f"   🤖 Decisao JEV ({avaliacao_jev['provedor']}): {avaliacao_jev['decisao']} | Seguranca: {avaliacao_jev['status_seguranca']} (Confianca: {int(avaliacao_jev['confianca']*100)}%)")
        print(f"   • Score Obrigatorios (70%): {detalhes['score_obrigatorio']}%")
        if detalhes['score_desejavel'] is not None:
            print(f"   • Score Desejaveis   (30%): {detalhes['score_desejavel']}%")
        print(f"   🎯 Skills em comum: {', '.join(skills_match) if skills_match else 'Nenhuma'}")
        
        if gaps:
            print(f"   ⚠️ Gaps no perfil : {', '.join(gaps)}")
            
        if score >= SCORE_CORTE_MINIMO:
            # Gera curriculo ATS-proof
            caminho_cv = gerar_curriculo_ats(vaga, skills_match)
            print(f"   [APROVADA]: Score atingido.")
            print(f"   Curriculo ATS internacional gerado: {os.path.basename(caminho_cv)}")
            print(f"   Candidatura registrada com sucesso!")
            
            registrar_candidatura(
                job_hash=job_hash,
                plataforma=plataforma,
                empresa=empresa,
                titulo=titulo,
                url=url,
                score=score,
                status="SUBMETIDO",
                caminho_cv=caminho_cv,
                skills_match=skills_match,
                skills_gaps=gaps
            )
            aprovadas += 1
        else:
            print(f"   [DESCARTADA]: Score insuficiente ({score}%). Nenhuma habilidade fabricada.")
            registrar_candidatura(
                job_hash=job_hash,
                plataforma=plataforma,
                empresa=empresa,
                titulo=titulo,
                url=url,
                score=score,
                status="DESCARTADO_SCORE_BAIXO",
                caminho_cv=None,
                skills_match=skills_match,
                skills_gaps=gaps
            )
            rejeitadas += 1

    # 4. Exportacao de Relatorios
    caminho_csv = os.path.join(BASE_DIR, "relatorio_candidaturas.csv")
    caminho_json = os.path.join(BASE_DIR, "relatorio_candidaturas.json")
    exportar_relatorio_csv(caminho_csv)
    exportar_relatorio_json(caminho_json)
    
    # 5. Sincronizacao automatica com o Dashboard
    registros_completos = listar_historico()
    atualizar_dashboard_com_dados_reais(registros_completos)
    
    # Resumo Executivo
    print("\n" + "=" * 85)
    print("RELATORIO EXECUTIVO DO CICLO DE EXECUCAO")
    print("=" * 85)
    print(f"• Total de alertas avaliados    : {len(vagas)}")
    print(f"• Novas candidaturas enviadas   : {aprovadas}")
    print(f"• Tentativas duplicadas puladas : {duplicadas} (100% de protecao)")
    print(f"• Vagas descartadas por score   : {rejeitadas}")
    print(f"• Relatorio CSV para Excel      : {caminho_csv}")
    print(f"• Relatorio JSON para Dashboard : {caminho_json}")
    print(f"• Diretorio de Curriculos ATS   : {OUTPUT_DIR}")
    print("=" * 85)
    
    # 6. Efeito Sonoro Exclusivo do Ciclo (Exatamente uma vez por execução, 100% assíncrono)
    run_id_atual = f"RUN-{agora.strftime('%Y%m%d%H%M')}"
    if tocar_efeito_sonoro_ciclo(run_id=run_id_atual):
        print(f"🔔 [FEEDBACK SONORO] Efeito sonoro emitido para o ciclo ({run_id_atual}).")
    print("=" * 85 + "\n")

if __name__ == "__main__":
    executar_ciclo_teste(ignorar_janela=True)
