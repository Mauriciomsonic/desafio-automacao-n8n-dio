import os
from datetime import datetime

# Configurações do Agendador (Scheduler)
HORA_INICIO = 10         # 10:00 (Início da janela de operação)
HORA_FIM = 18            # 18:00 (Fim da janela de operação)
INTERVALO_HORAS = 2      # Ciclos a cada 2 horas (10h, 12h, 14h, 16h e 18h)
HORARIOS_EXECUCAO = [10, 12, 14, 16, 18]  # Horários de disparo pontuais (Horário Local)
EXECUCAO_DIARIA = True   # Execução diária contínua
DIAS_UTEIS = [0, 1, 2, 3, 4]  # Preservado para regras e filtros de dias úteis legados
DIAS_SEMANA_AGENDAMENTO = [0, 1, 2, 3, 4, 5, 6]  # Diariamente (Segunda a Domingo)

# Critério de corte de compatibilidade ATS
SCORE_CORTE_MINIMO = 75.0  # %

# Caminhos de arquivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "candidaturas_test.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "curriculos_gerados")

# Perfil Profissional Consolidado do Maurício (Base de Fatos 100% Verídica)
# Abrange tanto a especialização em Machine Learning/IA quanto o sólido histórico em Infraestrutura, Cloud e DevOps
PERFIL_CANDIDATO = {
    "nome": "Maurício",
    "cidade_estado": "São Paulo, SP",
    "email": "mauricio.tech@exemplo.com",
    "linkedin": "linkedin.com/in/mauricio-tech-cloud",
    "github": "github.com/mauricio-dev",
    
    # Cargos em que possui histórico e elegibilidade comprovada
    "cargos_alvo": [
        "Machine Learning Engineer / IA",
        "Analista de Infraestrutura Cloud Sênior / Pleno",
        "DevOps Engineer / Especialista em Automação",
        "Analista de Sistemas / Suporte Especializado N3"
    ],
    
    "resumo_base": "Profissional de Tecnologia com mais de 6 anos de experiência consolidada em Infraestrutura de TI, Cloud Computing (AWS e Azure), automação DevOps e Engenharia de Machine Learning. Especialista em sustentação de ambientes de missão crítica, migrações para nuvem, orquestração de containers com Docker/Kubernetes e desenvolvimento de automações em Python, Bash e PowerShell. Histórico comprovado com dezenas de projetos de infraestrutura entregues com alta disponibilidade (SLA 99.9%), otimização de custos e conformidade técnica.",
    
    # Matriz completa de Hard Skills comprovadas
    "hard_skills": [
        # Cloud & Infraestrutura
        "AWS", "EC2", "S3", "RDS", "Lambda", "VPC",
        "Azure", "Azure AI", "Active Directory", "Azure AD",
        # DevOps & Conteinerização
        "Docker", "Kubernetes", "CI/CD", "Jenkins", "GitLab CI", "Terraform", "Ansible", "Git", "GitHub Actions",
        # Sistemas & Monitoramento
        "Linux", "RHEL", "Ubuntu", "CentOS", "Windows Server",
        "Prometheus", "Grafana", "Zabbix", "Nagios",
        # Redes & Segurança
        "TCP/IP", "DNS", "DHCP", "VPN", "Firewall",
        # Programação & Dados
        "Python", "FastAPI", "Pandas", "Scikit-Learn", "SQL", "Bash", "PowerShell", "TypeScript", "Prompt Engineering", "NotebookLM",
        # Governança
        "ITIL", "ITIL v4"
    ],
    
    # Histórico de Experiência Profissional Real
    "experiencias": [
        {
            "cargo": "Analista de Infraestrutura Cloud e Machine Learning",
            "empresa": "Tech Solutions & Projetos Corporativos",
            "periodo": "Jan/2022 - Presente",
            "conquistas": [
                "Liderou a migração de 100% da infraestrutura on-premise para AWS (EC2, S3, RDS), reduzindo custos operacionais em 35% (economia de ~R$ 20.000/mês).",
                "Implementou pipelines de CI/CD automatizados com Jenkins e GitLab CI, reduzindo o tempo de deploy de 2 horas para 10 minutos.",
                "Automatizou monitoramento centralizado com Prometheus e Grafana, reduzindo o MTTR (Mean Time to Recovery) em 60%.",
                "Desenvolveu pipelines de dados e consumo de APIs de IA Generativa com Python e Azure, com mais de 49 projetos documentados e versionados."
            ]
        },
        {
            "cargo": "Analista de Suporte e Infraestrutura N2 / N3",
            "empresa": "Serviços Corporativos de TI",
            "periodo": "Mar/2019 - Dez/2021",
            "conquistas": [
                "Gerenciou parque com mais de 500 servidores Linux (RHEL/Ubuntu/CentOS), mantendo SLA de disponibilidade em 99.9%.",
                "Lidou com projetos de migração de Active Directory local para Azure AD, impactando mais de 2.000 usuários sem downtime.",
                "Criou scripts em Bash e PowerShell para automação de rotinas de backup, auditoria de redes e conformidade de segurança."
            ]
        }
    ],
    
    "formacao": "Bacharelado em Ciência da Computação / Tecnologia da Informação",
    
    "certificacoes": [
        "AWS Certified Solutions Architect – Associate",
        "Microsoft Certified: Azure Fundamentals (AZ-900 / Azure AI)",
        "ITIL v4 Foundation",
        "Linux Professional Institute (LPIC-1)",
        "Formações e Bootcamps DIO: Machine Learning Engineer & Cloud DevOps"
    ]
}
