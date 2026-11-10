import sys
import sqlite3
from datetime import datetime

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import DB_PATH

def exibir_painel_historico():
    print("\n" + "=" * 105)
    print("                      📊 PAINEL DE CONTROLE: AUDITORIA DE CANDIDATURAS ATS")
    print("=" * 105)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM candidaturas_historico")
        total = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as enviados FROM candidaturas_historico WHERE status = 'SUBMETIDO'")
        enviados = cursor.fetchone()["enviados"]
        
        cursor.execute("SELECT COUNT(*) as descartados FROM candidaturas_historico WHERE status = 'DESCARTADO_SCORE_BAIXO'")
        descartados = cursor.fetchone()["descartados"]
        
        cursor.execute("SELECT AVG(score_match) as media FROM candidaturas_historico")
        media_score = cursor.fetchone()["media"] or 0.0
        
        print(f"📈 Indicadores Consolidados:")
        print(f"   • Total de Vagas Rastreadas : {total}")
        print(f"   • Candidaturas Enviadas     : {enviados} ({round((enviados/total*100) if total else 0, 1)}% de conversão)")
        print(f"   • Vagas Descartadas (Score) : {descartados}")
        print(f"   • Score Médio de Aderência  : {round(media_score, 1)}%")
        print("-" * 105)
        
        cursor.execute("""
            SELECT id, plataforma, empresa, titulo_cargo, score_match, status, skills_match, data_processamento 
            FROM candidaturas_historico 
            ORDER BY id ASC
        """)
        registros = cursor.fetchall()
        
        formato = "{:<3} | {:<13} | {:<18} | {:<28} | {:<7} | {:<13}"
        print(formato.format("ID", "Plataforma", "Empresa", "Cargo", "Score", "Status"))
        print("-" * 105)
        
        for r in registros:
            status_simbolo = "✅ ENVIADO" if r["status"] == "SUBMETIDO" else "❌ SCORE BAIXO"
            cargo_curto = (r["titulo_cargo"][:25] + "...") if len(r["titulo_cargo"]) > 28 else r["titulo_cargo"]
            print(formato.format(
                r["id"],
                r["plataforma"][:13],
                r["empresa"][:18],
                cargo_curto,
                f"{r['score_match']}%",
                status_simbolo
            ))
            
    print("=" * 105 + "\n")

if __name__ == "__main__":
    exibir_painel_historico()
