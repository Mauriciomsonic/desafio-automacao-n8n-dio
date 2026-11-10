import sqlite3
import hashlib
import csv
import json
import os
from typing import Optional, List, Dict
from config import DB_PATH

def inicializar_banco():
    """Cria a tabela e índices de histórico de candidaturas se não existirem."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidaturas_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_hash TEXT UNIQUE NOT NULL,
                plataforma TEXT NOT NULL,
                empresa TEXT NOT NULL,
                titulo_cargo TEXT NOT NULL,
                url_vaga TEXT NOT NULL,
                score_match REAL NOT NULL,
                status TEXT NOT NULL,
                caminho_cv TEXT,
                skills_match TEXT,
                skills_gaps TEXT,
                data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Adiciona colunas novas caso a tabela venha de versão anterior
        try:
            cursor.execute("ALTER TABLE candidaturas_historico ADD COLUMN skills_match TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE candidaturas_historico ADD COLUMN skills_gaps TEXT")
        except sqlite3.OperationalError:
            pass

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_hash ON candidaturas_historico(job_hash)")
        conn.commit()

def gerar_hash_vaga(empresa: str, titulo: str, url: str) -> str:
    """Gera um hash SHA-256 único e determinístico para a vaga."""
    chave = f"{empresa.lower().strip()}||{titulo.lower().strip()}||{url.strip()}"
    return hashlib.sha256(chave.encode("utf-8")).hexdigest()

def vaga_ja_processada(job_hash: str) -> bool:
    """Verifica se a vaga já foi processada anteriormente no banco de dados."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM candidaturas_historico WHERE job_hash = ?", (job_hash,))
        return cursor.fetchone() is not None

def registrar_candidatura(
    job_hash: str,
    plataforma: str,
    empresa: str,
    titulo: str,
    url: str,
    score: float,
    status: str,
    caminho_cv: Optional[str] = None,
    skills_match: Optional[List[str]] = None,
    skills_gaps: Optional[List[str]] = None
):
    """Registra uma candidatura processada com auditoria completa de skills."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        match_str = ", ".join(skills_match) if skills_match else ""
        gaps_str = ", ".join(skills_gaps) if skills_gaps else ""

        cursor.execute("""
            INSERT INTO candidaturas_historico 
            (job_hash, plataforma, empresa, titulo_cargo, url_vaga, score_match, status, caminho_cv, skills_match, skills_gaps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (job_hash, plataforma, empresa, titulo, url, score, status, caminho_cv, match_str, gaps_str))
        conn.commit()

def listar_historico() -> List[Dict]:
    """Retorna todas as candidaturas registradas no banco."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidaturas_historico ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]

def exportar_relatorio_csv(caminho_csv: str) -> str:
    """Exporta o histórico completo para formato CSV legível no Excel."""
    registros = listar_historico()
    if not registros:
        return ""

    campos = ["id", "data_processamento", "plataforma", "empresa", "titulo_cargo", "score_match", "status", "skills_match", "skills_gaps", "url_vaga"]
    
    with open(caminho_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for r in registros:
            writer.writerow(r)
            
    return caminho_csv

def exportar_relatorio_json(caminho_json: str) -> str:
    """Exporta o histórico completo para formato JSON para integração com o Dashboard."""
    registros = listar_historico()
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=2, ensure_ascii=False)
    return caminho_json
