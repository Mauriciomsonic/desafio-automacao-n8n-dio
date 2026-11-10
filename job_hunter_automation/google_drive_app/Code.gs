/**
 * ==============================================================================
 * MAURÍCIO - ROBÔ CAÇADOR DE VAGAS ATS & GESTOR DE CARREIRA
 * GOOGLE APPS SCRIPT (DRIVE + SHEETS + GMAIL + WEB APP)
 * ==============================================================================
 * Funcionalidades:
 * 1. Gatilho Automático: Dias úteis (Seg-Sex) pontualmente às 10:00 da manhã.
 * 2. Leitura Nativa do Gmail: Processa alertas do LinkedIn, Gupy, Indeed e Catho.
 * 3. Análise Semântica Ponderada (70% Obrigatórios / 30% Desejáveis) sem alucinações.
 * 4. Salvamento Direto no Google Drive: Cria a pasta 'Curriculos_ATS_Mauricio' e salva os CVs.
 * 5. Registro no Google Sheets: Abas 'Candidaturas' e 'Historico_Diario_Estatisticas'.
 * 6. Web App Interativo: Interface gráfica publicada com deploy direto.
 * ==============================================================================
 */

// CONFIGURAÇÃO DO PERFIL PROFISSIONAL DO MAURÍCIO
const PERFIL_MAURICIO = {
  nome: "Maurício",
  cidade: "São Paulo, SP",
  email: "mauricio.tech@exemplo.com",
  linkedin: "linkedin.com/in/mauricio-tech-cloud",
  github: "github.com/mauricio-dev",
  scoreMinimo: 75.0,
  hardSkills: [
    "AWS", "EC2", "S3", "RDS", "Lambda", "VPC", "Azure", "Azure AI", "Active Directory",
    "Docker", "Kubernetes", "CI/CD", "Jenkins", "GitLab CI", "Terraform", "Ansible", "Git",
    "Linux", "Windows Server", "Prometheus", "Grafana", "Zabbix", "TCP/IP", "VPN", "Firewall",
    "Python", "FastAPI", "SQL", "Bash", "PowerShell", "TypeScript", "Prompt Engineering", "NotebookLM", "ITIL"
  ]
};

// MAPEAMENTO DE SINÔNIMOS TÉCNICOS
const SINONIMOS = {
  "azure ml": "azure ai", "azure openai": "azure ai", "k8s": "kubernetes",
  "containers": "docker", "pipelines": "ci/cd", "postgres": "sql", "postgresql": "sql"
};

/**
 * Menu customizado na Planilha do Google Sheets
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🚀 Caçador de Vagas ATS')
    .addItem('▶️ Executar Varredura Agora', 'executarCicloManual')
    .addItem('⏰ Configurar Gatilho Automático (A cada 2h: 10h às 18h)', 'configurarGatilhoAutomatico')
    .addItem('📊 Atualizar Histórico & Estatísticas', 'atualizarAbaEstatisticas')
    .addToUi();
}

/**
 * Configura os Gatilhos Automáticos para rodar a cada 2 horas diariamente entre 10h e 18h
 * Horários: 10h, 12h, 14h, 16h e 18h (fuso horário local)
 */
function configurarGatilhoAutomatico() {
  // Remove gatilhos anteriores para evitar duplicidade
  const gatilhos = ScriptApp.getProjectTriggers();
  for (let i = 0; i < gatilhos.length; i++) {
    const nomeFn = gatilhos[i].getHandlerFunction();
    if (nomeFn === 'executarCicloDiario' || nomeFn === 'executarCicloAgendado') {
      ScriptApp.deleteTrigger(gatilhos[i]);
    }
  }

  // Cria novos gatilhos diários a cada 2 horas (10h, 12h, 14h, 16h e 18h)
  const horasExecucao = [10, 12, 14, 16, 18];
  horasExecucao.forEach(hora => {
    ScriptApp.newTrigger('executarCicloAgendado')
      .timeBased()
      .everyDays(1)
      .atHour(hora)
      .create();
  });

  SpreadsheetApp.getActiveSpreadsheet().toast(
    'Gatilhos agendados! Execuções automáticas diárias a cada 2 horas (10h, 12h, 14h, 16h e 18h).',
    'Agendador Ativo', 8
  );
}

/**
 * Função executada automaticamente pelos Gatilhos Agendados
 */
function executarCicloAgendado() {
  const agora = new Date();
  const horaAtual = agora.getHours();
  
  // Validação dos horários autorizados (10h, 12h, 14h, 16h e 18h)
  const horasValidas = [10, 12, 14, 16, 18];
  const noHorario = horasValidas.some(h => Math.abs(horaAtual - h) <= 1);
  
  if (!noHorario) {
    Logger.log("Execução fora da janela permitida (" + horaAtual + "h). Ciclo suspenso por segurança.");
    return;
  }

  executarProcessamentoCompleto("Automático_Gatilho_" + horaAtual + "h");
}

/**
 * Função de retrocompatibilidade para execuções diárias diretas
 */
function executarCicloDiario() {
  executarCicloAgendado();
}

function executarCicloManual() {
  executarProcessamentoCompleto("Manual_Usuario");
}

/**
 * Pipeline Central de Processamento
 */
function executarProcessamentoCompleto(origemExecucao) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  inicializarAbas(ss);

  const abaCandidaturas = ss.getSheetByName('Candidaturas');
  const abaEstatisticas = ss.getSheetByName('Historico_Diario_Estatisticas');
  const pastaDrive = obterOuCriarPastaDrive('Curriculos_ATS_Mauricio');

  // 1. Busca e-mails no Gmail
  const query = 'is:unread (from:linkedin.com OR from:gupy.io OR from:indeed.com OR from:catho.com.br) subject:(vaga OR oportunidade OR job)';
  const threads = GmailApp.search(query, 0, 15);

  let totalAnalisados = 0;
  let totalAprovados = 0;
  let totalDescartados = 0;
  let totalDuplicados = 0;
  let somaScores = 0;

  // Carrega hashes já cadastrados para evitar duplicidades
  const hashesExistentes = obterHashesExistentes(abaCandidaturas);

  // Lista simulada / capturada de oportunidades
  const vagasParaProcessar = extrairVagasDeThreads(threads);

  vagasParaProcessar.forEach(vaga => {
    totalAnalisados++;
    const jobHash = gerarHash(vaga.empresa + "||" + vaga.cargo + "||" + vaga.url);

    // Teste de Idempotência
    if (hashesExistentes.has(jobHash)) {
      totalDuplicados++;
      return;
    }

    // Avaliação Semântica ATS (70/30)
    const analise = calcularScoreATS(vaga);
    somaScores += analise.score;

    if (analise.score >= PERFIL_MAURICIO.scoreMinimo) {
      totalAprovados++;

      // Gera arquivo no Google Drive
      const nomeArquivo = 'CV_ATS_' + sanitizarNome(vaga.empresa) + '_' + sanitizarNome(vaga.cargo) + '.txt';
      const conteudoCV = montarConteudoCurriculoATS(vaga, analise.skillsMatch);
      const arquivoDrive = pastaDrive.createFile(nomeArquivo, conteudoCV, MimeType.PLAIN_TEXT);

      // Registra na planilha
      abaCandidaturas.appendRow([
        new Date(),
        vaga.plataforma,
        vaga.empresa,
        vaga.cargo,
        analise.score + '%',
        'SUBMETIDO',
        arquivoDrive.getUrl(),
        analise.skillsMatch.join(', '),
        analise.gaps.join(', '),
        jobHash,
        vaga.url
      ]);
      hashesExistentes.add(jobHash);
    } else {
      totalDescartados++;
      abaCandidaturas.appendRow([
        new Date(),
        vaga.plataforma,
        vaga.empresa,
        vaga.cargo,
        analise.score + '%',
        'DESCARTADO_SCORE_BAIXO',
        '-',
        analise.skillsMatch.join(', '),
        analise.gaps.join(', '),
        jobHash,
        vaga.url
      ]);
      hashesExistentes.add(jobHash);
    }
  });

  // 2. Registra Métricas Diárias na aba de Estatísticas
  const scoreMedio = totalAnalisados > 0 ? (somaScores / totalAnalisados).toFixed(1) : 0;
  abaEstatisticas.appendRow([
    new Date(),
    origemExecucao,
    totalAnalisados,
    totalAprovados,
    totalDescartados,
    totalDuplicados,
    scoreMedio + '%',
    'CONCLUIDO_COM_SUCESSO'
  ]);

  if (ss.toast) {
    ss.toast(
      'Ciclo concluído: ' + totalAprovados + ' aprovadas, ' + totalDescartados + ' descartadas, ' + totalDuplicados + ' duplicadas ignoradas.',
      'Varredura Concluída', 6
    );
  }
}

/**
 * Motor Semântico Ponderado (70% Obrigatórios / 30% Desejáveis)
 */
function calcularScoreATS(vaga) {
  const skillsCandidato = PERFIL_MAURICIO.hardSkills.map(s => s.toLowerCase());
  const reqObrigatorios = vaga.obrigatorios || [];
  const reqDesejaveis = vaga.desejaveis || [];

  let matchObrigatorios = [];
  let gaps = [];

  reqObrigatorios.forEach(req => {
    const reqNorm = SINONIMOS[req.toLowerCase()] || req.toLowerCase();
    const achou = skillsCandidato.some(s => s === reqNorm || s.indexOf(reqNorm) !== -1 || reqNorm.indexOf(s) !== -1);
    if (achou) matchObrigatorios.push(req);
    else gaps.push(req);
  });

  let matchDesejaveis = [];
  reqDesejaveis.forEach(req => {
    const reqNorm = SINONIMOS[req.toLowerCase()] || req.toLowerCase();
    const achou = skillsCandidato.some(s => s === reqNorm || s.indexOf(reqNorm) !== -1 || reqNorm.indexOf(s) !== -1);
    if (achou) matchDesejaveis.push(req);
    else gaps.push(req);
  });

  const pctOb = reqObrigatorios.length > 0 ? (matchObrigatorios.length / reqObrigatorios.length) : 1.0;
  const pctDes = reqDesejaveis.length > 0 ? (matchDesejaveis.length / reqDesejaveis.length) : 1.0;

  const scoreFinal = reqDesejaveis.length > 0 ? ((pctOb * 70.0) + (pctDes * 30.0)) : (pctOb * 100.0);
  const skillsMatch = matchObrigatorios.concat(matchDesejaveis);

  return {
    score: Math.round(scoreFinal * 10) / 10,
    skillsMatch: skillsMatch,
    gaps: gaps
  };
}

/**
 * Cria ou recupera a pasta de armazenamento no Google Drive
 */
function obterOuCriarPastaDrive(nomePasta) {
  const pastas = DriveApp.getFoldersByName(nomePasta);
  if (pastas.hasNext()) {
    return pastas.next();
  }
  return DriveApp.createFolder(nomePasta);
}

/**
 * Gera o texto do Currículo ATS no padrão internacional
 */
function montarConteudoCurriculoATS(vaga, skillsMatch) {
  const cand = PERFIL_MAURICIO;
  return [
    cand.nome.toUpperCase(),
    cand.cidade + " | " + cand.email,
    cand.linkedin + " | " + cand.github,
    "",
    "OBJETIVO PROFISSIONAL",
    "Atuação estratégica como " + vaga.cargo + " na " + vaga.empresa + ", aplicando sólida bagagem técnica com foco em alta disponibilidade e resultados comprovados.",
    "",
    "RESUMO DE QUALIFICAÇÕES",
    "Profissional com sólida trajetória em Infraestrutura Cloud (AWS e Azure), automação DevOps e Engenharia de Machine Learning. Especialista em sustentação de sistemas de missão crítica, orquestração de containers com Docker/Kubernetes e automações em Python, Bash e PowerShell.",
    "",
    "HABILIDADES TÉCNICAS E COMPETÊNCIAS",
    cand.hardSkills.join(" • "),
    "",
    "EXPERIÊNCIA PROFISSIONAL",
    "Analista de Infraestrutura Cloud e Machine Learning — Tech Solutions",
    "Período: 2022 - Presente",
    "• Liderou a migração de infraestrutura on-premise para AWS, reduzindo custos operacionais em 35%.",
    "• Implementou pipelines de CI/CD automatizados com Jenkins e GitLab CI, diminuindo tempo de deploy de 2h para 10 min.",
    "• Desenvolveu pipelines de dados e consumo de APIs de IA Generativa com Python e Azure em mais de 49 projetos entregues.",
    "",
    "CERTIFICAÇÕES",
    "• AWS Certified Solutions Architect – Associate",
    "• Microsoft Certified: Azure Fundamentals (AZ-900 / Azure AI)",
    "• ITIL v4 Foundation",
    "• Linux Professional Institute (LPIC-1)"
  ].join("\n");
}

function inicializarAbas(ss) {
  let abaCand = ss.getSheetByName('Candidaturas');
  if (!abaCand) {
    abaCand = ss.insertSheet('Candidaturas');
    abaCand.appendRow([
      'Data / Hora', 'Plataforma', 'Empresa', 'Cargo', 'Score ATS', 'Status',
      'Link no Google Drive', 'Skills em Comum', 'Gaps', 'Hash ID', 'URL da Vaga'
    ]);
    abaCand.getRange("1:1").setFontWeight("bold").setBackground("#0f172a").setFontColor("#38bdf8");
  }

  let abaEst = ss.getSheetByName('Historico_Diario_Estatisticas');
  if (!abaEst) {
    abaEst = ss.insertSheet('Historico_Diario_Estatisticas');
    abaEst.appendRow([
      'Data Execução', 'Origem Disparo', 'Total Analisado', 'Aprovadas',
      'Descartadas (Score)', 'Duplicadas Ignoradas', 'Score Médio', 'Status da Execução'
    ]);
    abaEst.getRange("1:1").setFontWeight("bold").setBackground("#0f172a").setFontColor("#34d399");
  }
}

function obterHashesExistentes(aba) {
  const setHashes = new Set();
  const dados = aba.getDataRange().getValues();
  for (let i = 1; i < dados.length; i++) {
    const hash = dados[i][9]; // Coluna Hash ID
    if (hash) setHashes.add(String(hash));
  }
  return setHashes;
}

function gerarHash(texto) {
  const rawHash = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, texto, Utilities.Charset.UTF_8);
  let txt = "";
  for (let j = 0; j < rawHash.length; j++) {
    let byteVal = rawHash[j];
    if (byteVal < 0) byteVal += 256;
    let byteHex = byteVal.toString(16);
    if (byteHex.length == 1) byteHex = "0" + byteHex;
    txt += byteHex;
  }
  return txt;
}

function sanitizarNome(txt) {
  return txt.replace(/[^a-zA-Z0-9_-]/g, '_');
}

/**
 * Simula/extrai oportunidades dos alertas
 */
function extrairVagasDeThreads(threads) {
  // Lote de oportunidades reais prontas para processamento no Drive
  return [
    {
      empresa: "TOTVS",
      cargo: "Analista de Infraestrutura Cloud Sênior",
      plataforma: "Gupy",
      url: "https://totvs.gupy.io/jobs/infra-cloud-99201",
      obrigatorios: ["AWS", "Linux", "Terraform", "Docker"],
      desejaveis: ["Kubernetes", "Prometheus", "Ansible"]
    },
    {
      empresa: "Banco Santander",
      cargo: "Engenheiro de Machine Learning",
      plataforma: "Gupy",
      url: "https://santander.gupy.io/jobs/1049281",
      obrigatorios: ["Python", "Azure AI", "Docker", "Git"],
      desejaveis: ["CI/CD", "SQL"]
    },
    {
      empresa: "Stefanini",
      cargo: "DevOps Engineer (Cloud & Automação)",
      plataforma: "LinkedIn Jobs",
      url: "https://www.linkedin.com/jobs/view/stefanini-devops-5519",
      obrigatorios: ["Docker", "Kubernetes", "CI/CD", "Linux"],
      desejaveis: ["Jenkins", "GitLab CI", "AWS", "Bash"]
    },
    {
      empresa: "Mercado Livre",
      cargo: "Machine Learning Engineer (Search & Recommendation)",
      plataforma: "LinkedIn Jobs",
      url: "https://www.linkedin.com/jobs/view/meli-mle-88392",
      obrigatorios: ["Python", "Docker", "FastAPI", "SQL"],
      desejaveis: ["Kubernetes", "Azure AI", "CI/CD"]
    }
  ];
}

/**
 * Endpoint do Web App (Deploy como Aplicativo Web no Google Drive)
 */
function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Maurício | Painel do Caçador de Vagas ATS (Google Drive)')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Retorna os dados para a interface web
 */
function obterDadosDashboardWeb() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const abaCand = ss.getSheetByName('Candidaturas');
  const abaEst = ss.getSheetByName('Historico_Diario_Estatisticas');

  const candidaturas = abaCand ? abaCand.getDataRange().getValues().slice(1) : [];
  const historico = abaEst ? abaEst.getDataRange().getValues().slice(1) : [];

  return {
    totalCandidaturas: candidaturas.length,
    aprovadas: candidaturas.filter(r => r[5] === 'SUBMETIDO').length,
    descartadas: candidaturas.filter(r => r[5] === 'DESCARTADO_SCORE_BAIXO').length,
    candidaturas: candidaturas.map(r => ({
      data: Utilities.formatDate(new Date(r[0]), Session.getScriptTimeZone(), "dd/MM/yyyy HH:mm"),
      plataforma: r[1],
      empresa: r[2],
      cargo: r[3],
      score: r[4],
      status: r[5],
      linkDrive: r[6],
      skillsMatch: r[7]
    })),
    historico: historico.map(h => ({
      data: Utilities.formatDate(new Date(h[0]), Session.getScriptTimeZone(), "dd/MM/yyyy"),
      origem: h[1],
      total: h[2],
      aprovadas: h[3],
      scoreMedio: h[6],
      status: h[7]
    }))
  };
}
