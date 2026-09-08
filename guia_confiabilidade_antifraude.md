# Guia de Confiabilidade & Protocolo de Defesa Antifraude (Fail-Closed)

Este documento estabelece a política técnica de segurança cibernética e triagem de legitimidade implementada no motor de automação N8N para proteção da identidade digital, dados pessoais e reputação do candidato **Mauricio Alves dos Santos**.

---

## 1. Princípio Fundamental: Filosofia *Fail-Closed*

Em engenharia de sistemas de missão crítica, qualquer componente cuja integridade não possa ser atestada documentalmente deve ser **bloqueado por padrão** (*fail-closed*). 

A automação nunca assume a boa-fé de anúncios de vagas. Toda oportunidade ingerida pelo pipeline é tratada como **não confiável** até que passe com sucesso por todos os gates determinísticos de validação.

---

## 2. Matriz de Red Flags (Critérios de Exclusão Sumária)

| Vetor de Risco | Indicador de Detecção | Ação no N8N | Risco Mitigado |
| :--- | :--- | :--- | :--- |
| **Cobrança Financeira** | Menções a "taxa de matrícula", "aquisição de treinamento", "exame admissional prévio por conta do candidato" ou chaves Pix/Crypto. | **Bloqueio Imediato** | Golpe financeiro direto. |
| **Solicitação Precoce de Dados Sensíveis** | Solicitação de CPF, RG, CNH, dados bancários, fotos de documentos ou senhas no primeiro contato. | **Bloqueio Imediato** | Furto de identidade e abertura de contas fraudulentas. |
| **Domínio de E-mail Desacoplado** | Empresas de médio/grande porte anunciando vagas corporativas utilizando provedores gratuitos (`@gmail.com`, `@hotmail.com`, `@yahoo.com`, etc.). | **Bloqueio Imediato** | Engenharia social e falsificação de identidade empresarial (phishing). |
| **Antiguidade de Domínio Suspeita** | Consulta WHOIS revelando que o domínio da empresa ou do portal foi registrado há menos de 30 dias. | **Bloqueio Imediato** | Infraestrutura temporária criada exclusivamente para golpes sazonais. |
| **Ausência de Registro Cadastral (CNPJ)** | Ausência de razão social, CNPJ inativo, baixado ou sem correspondência com a atividade econômica na Receita Federal. | **Descarte** | Empresa fantasma ou intermediário não autorizado. |
| **Incongruência Salarial & Falsa Urgência** | Promessa de remuneração astronômica para tarefas triviais aliada a gatilhos de escassez agressiva ("Início imediato", "Vagas esgotam hoje"). | **Descarte** | Esquemas de pirâmide, phishing de dados ou trabalho ilícito. |

---

## 3. Implementação Técnica do Filtro no N8N (Nó Code / JavaScript)

O snippet abaixo roda dentro do nó de validação do workflow N8N antes de qualquer processamento por modelos de Inteligência Artificial:

```javascript
// Nó N8N: Anti-Fraud Gate (Fail-Closed)
const item = $input.item.json;

// 1. Provedores de E-mail Gratuitos
const freeEmailDomains = [
  'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 
  'bol.com.br', 'uol.com.br', 'live.com', 'icloud.com'
];

// 2. Dicionário de Palavras de Risco Financeiro e Dados Sensíveis
const fraudPatterns = [
  /taxa\s+(de\s+)?(inscri[cç][aã]o|processo|sele[cç][aã]o|cadastro)/i,
  /pagar\s+(pelo\s+)?(curso|treinamento|exame)/i,
  /chave\s+pix|dep[oó]sito\s+banc[aá]rio/i,
  /envie\s+(foto\s+do\s+)?(documento|rg|cpf|cnh|cart[aã]o)/i,
  /renda\s+extra\s+di[aá]ria|ganhe\s+dinheiro\s+f[aá]cil/i
];

let isFraud = false;
let fraudReason = '';

// Checagem de Domínio
const contactEmail = item.contact_email || '';
const domain = contactEmail.split('@')[1];
if (domain && freeEmailDomains.includes(domain.toLowerCase())) {
  if (item.company_size !== 'Startup/Individual') {
    isFraud = true;
    fraudReason = `Domínio de e-mail gratuito (${domain}) em vaga corporativa`;
  }
}

// Checagem de Conteúdo Textual
const fullText = `${item.title} ${item.description} ${item.requirements}`.toLowerCase();
for (const pattern of fraudPatterns) {
  if (pattern.test(fullText)) {
    isFraud = true;
    fraudReason = `Gatilho de fraude detectado no texto: ${pattern.toString()}`;
    break;
  }
}

// Checagem de Idade de Domínio (WHOIS)
if (item.whois_age_days !== undefined && item.whois_age_days < 30) {
  isFraud = true;
  fraudReason = `Domínio corporativo registrado há menos de 30 dias (${item.whois_age_days} dias)`;
}

// Decisão Determinística Fail-Closed
if (isFraud) {
  return {
    json: {
      action: 'DISCARD_SECURITY_THREAT',
      job_id: item.id || item.job_uuid,
      company: item.company,
      title: item.title,
      reason: fraudReason,
      timestamp: new Date().toISOString()
    }
  };
}

// Vaga Aprovada no Gate de Segurança
return {
  json: {
    action: 'PROCEED_TO_MATCHER',
    ...item
  }
};
```

---

## 4. Matriz de Confusão e Isolamento de Falsos Positivos

Vagas de TI frequentemente contêm jargões ambíguos. Para evitar que o sistema confunda funções e gere ruído, o motor de segmentação aplica as seguintes regras de desambiguação:

1. **"Scheduler" vs "Agendamento Geral"**:
   - Vagas que utilizam "Scheduler" referindo-se a recepcionista ou agendador de consultas médicas são eliminadas instantaneamente pela ausência obrigatória da stack de TI (`Control-M`, `UC4`, `Batch`, `Mainframe`, `Cron`).
2. **"Operador de Produção" (Industrial vs TI)**:
   - O sistema filtra palavras como "chão de fábrica", "usinagem", "linha de montagem" ou "CNC", garantindo que apenas oportunidades de **Produção de TI / Ambientes Distribuídos** avancem para o cálculo de score.
3. **"Suporte N1/Helpdesk" vs "Suporte a Storage/Missão Crítica"**:
   - Vagas focadas apenas em periféricos e atendimento a usuário final são descartadas por estarem abaixo do limiar de senioridade de Mauricio Alves dos Santos.

---

## 5. Diretrizes de Conformidade com LGPD & Termos de Uso (ToS)

- **Minimização de Dados (Art. 6º, III, LGPD)**: O currículo transmitido contém apenas as informações estritamente necessárias para a avaliação profissional. Documentos civis (CPF, RG) jamais são trafegados ou expostos.
- **Transparência e Consentimento**: O envio de candidaturas é submetido ao controle humano (*Human-in-the-Loop* via notificação com botão de confirmação no Telegram), assegurando total ciência e soberania do titular sobre a destinação de seus dados.
- **Respeito aos Termos de Serviço**: O ecossistema prioriza APIs oficiais (Adzuna, Remotive, agregadores credenciados) com chaves de autenticação legítimas e rate limiting ético, sem sobrecarregar servidores de terceiros.
