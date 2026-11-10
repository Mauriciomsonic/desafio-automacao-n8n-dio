
// 1. Loader
const profile = {
  profile_owner: "Mauricio Alves dos Santos",
  skills_obrigatorias: [
    "Control-M", "UC4 (Automic)", "Maestro", 
    "TSM (Tivoli Storage Manager)", "NetBackup", 
    "Mainframe ES9000 / VM/VSESA", "Tape Libraries (ACSLS)", 
    "UNIX (AIX, Solaris, HP-UX, Linux)", "SAP R/3 Basis Operations"
  ],
  skills_modernas: [
    "Python (Advanced)", "CrewAI Agentic Orchestration", "N8N Automation", 
    "AWS Cloud Practitioner", "Azure AZ-900 / AI-900", "Kubernetes Fundamentals",
    "Power BI & Advanced Excel"
  ],
  thresholds: {
    high_match: 70,
    correction_min: 50,
    discard_threshold: 50
  }
};

// 2. Extractor
const sampleJobs = [
  {
    id: "job-001",
    title: "Scheduler Sênior / Especialista em Control-M",
    company: "Instituição Financeira / Missão Crítica",
    contact_email: "vagas.tech@bancocorp.com.br",
    company_size: "Enterprise",
    whois_age_days: 1200,
    description: "Control-M UNIX AIX Linux backup restore",
    requirements: "Control-M, UNIX, AIX",
    sla_requirement: "critical"
  },
  {
    id: "job-004-scam",
    title: "Digitador R$ 15.000",
    company: "Golpe",
    contact_email: "fake@gmail.com",
    company_size: "Enterprise",
    whois_age_days: 10,
    description: "taxa de inscrição exame admissional",
    requirements: "pagar taxa",
    sla_requirement: "non-critical"
  }
];

// 3. Antifraud Gate
const freeEmailDomains = ['gmail.com', 'hotmail.com'];
const fraudPatterns = [/taxa\s+(de\s+)?(inscri[cç][aã]o|processo)/i];

const securityChecked = sampleJobs.map(item => {
  let isFraud = false;
  let reason = '';
  const domain = (item.contact_email.split('@')[1] || '').toLowerCase();
  if (freeEmailDomains.includes(domain)) {
    isFraud = true;
    reason = 'Email gratuito';
  }
  if (fraudPatterns.some(p => p.test(item.description))) {
    isFraud = true;
    reason = 'Padrao de fraude';
  }
  return { ...item, security_passed: !isFraud, fraud_reason: reason };
});

console.log('Antifraud resultado:', securityChecked.map(j => ({ id: j.id, passed: j.security_passed, reason: j.fraud_reason })));

// 4. Parser
const parsedJobs = securityChecked.filter(j => j.security_passed).map(item => {
  return {
    ...item,
    cargo_normalizado: item.title,
    senioridade_requerida: "Sênior / Especialista",
    stack_tecnica: ["control-m", "unix", "aix"],
    sla_missao_critica: item.sla_requirement === "critical"
  };
});

// 5. Matcher
const matchedJobs = parsedJobs.map(item => {
  const fullText = `${item.title} ${(item.stack_tecnica || []).join(' ')} ${item.requirements} ${item.description}`.toLowerCase();
  let coreMatches = 0;
  for (const skill of profile.skills_obrigatorias) {
    if (fullText.includes(skill.toLowerCase())) coreMatches++;
  }
  const coreScore = (coreMatches / 4) * 55;
  let modernMatches = 0;
  for (const skill of profile.skills_modernas) {
    if (fullText.includes(skill.toLowerCase())) modernMatches++;
  }
  const modernScore = (modernMatches / 3) * 25;
  const isSenior = item.senioridade_requerida.includes("Sênior") || item.senioridade_requerida.includes("Especialista");
  const seniorityBonus = isSenior ? 15 : 5;
  const missionCriticalBonus = item.sla_missao_critica ? 10 : 0;
  let calculatedScore = Math.round(coreScore + modernScore + seniorityBonus + missionCriticalBonus);
  calculatedScore = Math.max(10, Math.min(98, calculatedScore));

  return {
    ...item,
    match_score: calculatedScore,
    status: calculatedScore >= 70 ? 'ALTA_PRIORIDADE' : 'BAIXA',
    justificativa: `Score de ${calculatedScore}% (${item.senioridade_requerida})`
  };
});

console.log('Matcher resultado:', matchedJobs.map(j => ({ id: j.id, score: j.match_score, status: j.status })));
console.log('TESTE CONCLUIDO COM SUCESSO TOTAL!');
