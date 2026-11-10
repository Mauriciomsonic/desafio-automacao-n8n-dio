import os
import re
from typing import Dict, List, Tuple
from config import PERFIL_CANDIDATO, OUTPUT_DIR

# Tabela de normalização semântica de sinônimos técnicos
SINONIMOS_MAP = {
    # Cloud & Infra
    "azure ml": "azure ai",
    "azure openai": "azure ai",
    "azure services": "azure ai",
    "azure machine learning": "azure ai",
    "active directory": "active directory",
    "ad": "active directory",
    "azure ad": "azure ad",
    "rhel": "linux",
    "red hat": "linux",
    "centos": "linux",
    "ubuntu": "linux",
    "windows": "windows server",
    "win server": "windows server",
    # DevOps & Automação
    "k8s": "kubernetes",
    "conteinerização": "docker",
    "containers": "docker",
    "github actions": "ci/cd",
    "gitlab ci": "ci/cd",
    "pipelines ci/cd": "ci/cd",
    "pipelines": "ci/cd",
    "iac": "terraform",
    "infraestrutura como código": "terraform",
    # IA & Programação
    "prompt eng.": "prompt engineering",
    "prompt eng": "prompt engineering",
    "genai": "prompt engineering",
    "ia generativa": "prompt engineering",
    "llm": "prompt engineering",
    "rest api": "fastapi",
    "apis rest": "fastapi",
    "apis": "fastapi",
    "postgres": "sql",
    "postgresql": "sql",
    "mysql": "sql",
    "banco de dados relacional": "sql",
    "itil v4": "itil",
    "itil foundation": "itil"
}

def normalizar_termo(termo: str) -> str:
    """Normaliza grafias e sinônimos para o padrão canônico da base de habilidades."""
    t = termo.lower().strip()
    return SINONIMOS_MAP.get(t, t)

def sanitizar_dados_pessoais(texto: str) -> str:
    """
    Sanitização rigorosa de dados sensíveis (PII) conforme a LGPD.
    Remove CPFs, RGs e dados de identificação antes de qualquer exportação.
    """
    texto = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "[CPF_PROTEGIDO_LGPD]", texto)
    texto = re.sub(r"\b\d{2}\.?\d{3}\.?\d{3}-?[0-9xX]\b", "[RG_PROTEGIDO_LGPD]", texto)
    return texto

def analisar_compatibilidade(vaga: Dict) -> Tuple[float, List[str], List[str], Dict]:
    """
    Motor semântico refinado com ponderação de requisitos (70% Obrigatórios / 30% Desejáveis).
    Reconhece o repertório completo: Cloud, Infraestrutura, DevOps, Suporte N3 e Machine Learning.
    """
    skills_candidato_raw = [s.lower().strip() for s in PERFIL_CANDIDATO["hard_skills"]]
    skills_candidato_norm = set([normalizar_termo(s) for s in skills_candidato_raw] + skills_candidato_raw)

    req_obrigatorios = [r.strip() for r in vaga.get("requisitos_obrigatorios", vaga.get("requisitos_chave", []))]
    req_desejaveis = [r.strip() for r in vaga.get("requisitos_desejaveis", [])]

    match_obrigatorios = []
    gaps_obrigatorios = []

    for req in req_obrigatorios:
        req_norm = normalizar_termo(req)
        match_found = False
        for s in skills_candidato_norm:
            if s == req_norm or s in req_norm or req_norm in s:
                match_obrigatorios.append(req.title())
                match_found = True
                break
        if not match_found:
            gaps_obrigatorios.append(req.title())

    match_desejaveis = []
    gaps_desejaveis = []

    for req in req_desejaveis:
        req_norm = normalizar_termo(req)
        match_found = False
        for s in skills_candidato_norm:
            if s == req_norm or s in req_norm or req_norm in s:
                match_desejaveis.append(req.title())
                match_found = True
                break
        if not match_found:
            gaps_desejaveis.append(req.title())

    # Cálculo Ponderado 70/30
    pct_obrigatorios = (len(match_obrigatorios) / len(req_obrigatorios)) if req_obrigatorios else 1.0
    pct_desejaveis = (len(match_desejaveis) / len(req_desejaveis)) if req_desejaveis else 1.0

    if req_desejaveis:
        score_total = (pct_obrigatorios * 70.0) + (pct_desejaveis * 30.0)
    else:
        score_total = pct_obrigatorios * 100.0

    score_total = round(min(100.0, max(0.0, score_total)), 1)
    skills_em_comum = list(set(match_obrigatorios + match_desejaveis))
    gaps_totais = list(set(gaps_obrigatorios + gaps_desejaveis))

    detalhes = {
        "score_obrigatorio": round(pct_obrigatorios * 100, 1),
        "score_desejavel": round(pct_desejaveis * 100, 1) if req_desejaveis else None,
        "match_obrigatorios": match_obrigatorios,
        "gaps_obrigatorios": gaps_obrigatorios,
        "match_desejaveis": match_desejaveis,
        "gaps_desejaveis": gaps_desejaveis,
    }

    return score_total, skills_em_comum, gaps_totais, detalhes

def gerar_curriculo_ats(vaga: Dict, skills_em_comum: List[str]) -> str:
    """
    Gera currículo adaptado para o domínio específico da vaga:
    - Se vaga for de Infraestrutura/Cloud: ressalta migrações AWS/Azure, Linux, servidores e redes.
    - Se vaga for de DevOps/SRE: ressalta CI/CD, Docker, Kubernetes, Terraform, automação.
    - Se vaga for de ML/IA: ressalta Python, Azure AI, pipelines de dados e IA Generativa.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cand = PERFIL_CANDIDATO
    empresa = vaga["empresa"]
    cargo_vaga = vaga["titulo"]
    cargo_lower = cargo_vaga.lower()

    # Reordena competências para colocar as com match primeiro
    todas_skills = list(cand["hard_skills"])
    skills_ordenadas = sorted(
        todas_skills,
        key=lambda s: any(m.lower() in s.lower() for m in skills_em_comum),
        reverse=True
    )
    skills_formatadas = " • ".join(skills_ordenadas)

    # Calibração contextual do Resumo conforme a área da vaga
    if any(k in cargo_lower for k in ["infra", "cloud", "suporte", "sistemas", "redes"]):
        resumo_calibrado = (
            f"Profissional sênior de Tecnologia com sólida trajetória em Infraestrutura Cloud (AWS e Azure), "
            f"administração de servidores Linux/Windows e sustentação de ambientes de missão crítica. "
            f"Comprovada experiência em migrações para nuvem, redução de custos de infraestrutura e automação com Bash e Python. "
            f"Certificado AWS Solutions Architect Associate e ITIL v4."
        )
    elif any(k in cargo_lower for k in ["devops", "sre", "automação", "plataforma"]):
        resumo_calibrado = (
            f"Especialista em Engenharia DevOps e Automação Cloud com ampla vivência na criação de pipelines CI/CD "
            f"(Jenkins, GitLab CI), orquestração de containers com Docker e Kubernetes e provisionamento de Infraestrutura como Código (Terraform). "
            f"Foco em redução de tempos de deploy, aumento de confiabilidade de sistemas e observabilidade contínua."
        )
    else:
        resumo_calibrado = cand["resumo_base"]

    linhas = [
        f"{cand['nome'].upper()}",
        f"{cand['cidade_estado']} | {cand['email']}",
        f"{cand['linkedin']} | {cand['github']}",
        "",
        "OBJETIVO PROFISSIONAL",
        f"Atuação estratégica como {cargo_vaga} na {empresa}, aplicando sólida bagagem técnica com foco em alta disponibilidade, automação e eficiência operacional.",
        "",
        "RESUMO DE QUALIFICAÇÕES",
        f"{resumo_calibrado}",
        "",
        "HABILIDADES TÉCNICAS E COMPETÊNCIAS",
        f"{skills_formatadas}",
        "",
        "EXPERIÊNCIA PROFISSIONAL",
    ]

    # Bullets de experiências priorizados por relevância à vaga
    for exp in cand["experiencias"]:
        linhas.append(f"{exp['cargo']} — {exp['empresa']}")
        linhas.append(f"Período: {exp['periodo']}")
        
        # Ordena conquistas dando preferência àquelas que citam stacks da vaga
        conquistas_ordenadas = sorted(
            exp["conquistas"],
            key=lambda c: any(s.lower() in c.lower() for s in skills_em_comum),
            reverse=True
        )
        for c in conquistas_ordenadas:
            linhas.append(f"• {c}")
        linhas.append("")

    linhas.extend([
        "CERTIFICAÇÕES PROFISSIONAIS",
    ])
    for cert in cand["certificacoes"]:
        linhas.append(f"• {cert}")

    linhas.extend([
        "",
        "FORMAÇÃO ACADÊMICA",
        f"• {cand['formacao']}",
        "",
        "IDIOMAS",
        "• Português: Nativo",
        "• Inglês: Técnico / Avançado para Leitura, Documentação e Conversação",
        ""
    ])

    conteudo_completo = "\n".join(linhas)
    conteudo_sanitizado = sanitizar_dados_pessoais(conteudo_completo)

    # Gera nome de arquivo seguro para Windows/Linux
    empresa_limpa = re.sub(r"[^\w\-]", "_", empresa)
    cargo_limpo = re.sub(r"[^\w\-]", "_", cargo_vaga)
    nome_arquivo = f"CV_ATS_{empresa_limpa}_{cargo_limpo}.txt"
    caminho_final = os.path.join(OUTPUT_DIR, nome_arquivo)

    with open(caminho_final, "w", encoding="utf-8") as f:
        f.write(conteudo_sanitizado)

    return caminho_final
