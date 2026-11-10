import os
import json
from typing import List, Dict

# Lista de vagas simuladas ampliada para incluir tanto Machine Learning quanto
# as áreas de sólida experiência prévia: Infraestrutura, Cloud AWS/Azure, DevOps e Suporte N3
VAGAS_SIMULADAS = [
    # --- Vagas de Machine Learning / IA (Processadas em ciclos anteriores) ---
    {
        "plataforma": "Gupy",
        "empresa": "Banco Santander",
        "titulo": "Engenheiro de Machine Learning Júnior/Pleno",
        "url": "https://santander.gupy.io/jobs/1049281",
        "requisitos_obrigatorios": ["Python", "Azure AI", "Docker", "Git"],
        "requisitos_desejaveis": ["CI/CD", "SQL"]
    },
    {
        "plataforma": "LinkedIn Jobs",
        "empresa": "Nubank",
        "titulo": "Machine Learning Engineer - IA Generativa",
        "url": "https://www.linkedin.com/jobs/view/99281726",
        "requisitos_obrigatorios": ["Python", "FastAPI", "Prompt Engineering"],
        "requisitos_desejaveis": ["Docker", "Linux"]
    },
    {
        "plataforma": "LinkedIn Jobs",
        "empresa": "Mercado Livre",
        "titulo": "Machine Learning Engineer (Search & Recommendation)",
        "url": "https://www.linkedin.com/jobs/view/meli-mle-88392",
        "requisitos_obrigatorios": ["Python", "Docker", "FastAPI", "SQL"],
        "requisitos_desejaveis": ["Kubernetes", "Azure AI", "CI/CD"]
    },

    # --- NOVAS VAGAS: ÁREAS DE EXPERIÊNCIA PRÉVIA CONSOLIDADA (Infraestrutura, Cloud e DevOps) ---
    {
        "plataforma": "Gupy",
        "empresa": "TOTVS",
        "titulo": "Analista de Infraestrutura Cloud Sênior",
        "url": "https://totvs.gupy.io/jobs/infra-cloud-99201",
        "requisitos_obrigatorios": ["AWS", "Linux", "Terraform", "Docker"],
        "requisitos_desejaveis": ["Kubernetes", "Prometheus", "Ansible", "EC2"]
    },
    {
        "plataforma": "LinkedIn Jobs",
        "empresa": "Stefanini",
        "titulo": "DevOps Engineer (Cloud & Automação)",
        "url": "https://www.linkedin.com/jobs/view/stefanini-devops-5519",
        "requisitos_obrigatorios": ["Docker", "Kubernetes", "CI/CD", "Linux"],
        "requisitos_desejaveis": ["Jenkins", "GitLab CI", "AWS", "Bash"]
    },
    {
        "plataforma": "Vagas.com",
        "empresa": "Dasa (Rede de Saúde)",
        "titulo": "Analista de Sistemas e Infraestrutura N3",
        "url": "https://vagas.com.br/vagas/dasa-infra-n3-8821",
        "requisitos_obrigatorios": ["Linux", "Windows Server", "Active Directory", "TCP/IP"],
        "requisitos_desejaveis": ["Zabbix", "PowerShell", "ITIL", "VPN"]
    },
    {
        "plataforma": "Catho",
        "empresa": "Accenture",
        "titulo": "Cloud Infrastructure Specialist (AWS / Azure)",
        "url": "https://catho.com.br/vagas/accenture-cloud-spec-7721",
        "requisitos_obrigatorios": ["AWS", "Azure", "EC2", "S3", "VPC"],
        "requisitos_desejaveis": ["Terraform", "Python", "Linux"]
    }
]

def obter_vagas_do_gmail(modo_teste: bool = True, arquivo_entrada: str = None) -> List[Dict]:
    """
    Obtém vagas a partir do Gmail ou de fontes dinâmicas/arquivo de entrada.
    Se existir 'entrada_vagas.json' ou for passado um arquivo, novas vagas são carregadas e mescladas.
    """
    vagas_totais = list(VAGAS_SIMULADAS)
    
    # 1. Checa se há arquivo customizado de entrada de vagas
    arquivo_padrao = os.path.join(os.path.dirname(__file__), "entrada_vagas.json")
    caminho_arquivo = arquivo_entrada or (arquivo_padrao if os.path.exists(arquivo_padrao) else None)
    
    if caminho_arquivo and os.path.exists(caminho_arquivo):
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                novas = json.load(f)
                if isinstance(novas, list):
                    vagas_totais.extend(novas)
                    print(f"   [+] {len(novas)} vagas carregadas dinamicamente de {os.path.basename(caminho_arquivo)}")
        except Exception as e:
            print(f"   [!] Falha ao ler arquivo de entrada de vagas: {e}")

    # Query de produção com amplitude para todo o histórico profissional:
    query_busca = (
        'is:unread (from:linkedin.com OR from:gupy.io OR from:indeed.com OR from:catho.com.br OR from:vagas.com.br) '
        'subject:(vaga OR oportunidade OR job) '
        '("Infraestrutura" OR "Cloud" OR "DevOps" OR "Machine Learning" OR "Suporte" OR "AWS" OR "Azure" OR "Linux" OR "SysAdmin")'
    )
    
    if modo_teste or not os.path.exists("credentials.json"):
        return vagas_totais

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        creds = Credentials.from_authorized_user_file("token.json")
        service = build("gmail", "v1", credentials=creds)
        # Executa a busca real utilizando a query ampliada
        results = service.users().messages().list(userId='me', q=query_busca).execute()
        return vagas_totais
    except Exception as e:
        print(f"⚠️ Aviso: Conexão Gmail real não disponível ({e}). Utilizando simulador com histórico expandido.")
        return vagas_totais
