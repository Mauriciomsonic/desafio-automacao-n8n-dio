/**
 * =========================================================================
 * JAVASCRIPT MODULAR: BANNER DE HISTÓRICO (ÚLTIMOS 20 DIAS) & TICKET
 * =========================================================================
 */

let historico20DiasData = [];
let ticketSelecionadoAtual = null;

// Gera a série temporal realista de 20 dias retroativos a partir de Hoje (new Date())
function gerarSerieTemporal20Dias() {
  const agora = new Date();
  const serie = [];
  const diasDaSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

  // Vagas mockadas realistas para os payloads de auditoria
  const empresasPool = [
    'Instituição Financeira / Missão Crítica',
    'Telecom & Cloud Infrastructure',
    'Tech Modernization Hub',
    'Kyndryl / IBM Alliance',
    'B3 Brasil Bolsa Balcão',
    'Santander Tecnologia',
    'TIVIT Terceirização de TI',
    'Stefanini Global IT'
  ];

  const cargosPool = [
    'Scheduler Sênior / Especialista Control-M',
    'Analista de Suporte Storage & TSM SR',
    'Engenheiro de Confiabilidade (SRE) & Workload',
    'Arquiteto de Automação de Workloads',
    'Analista de Produção de TI e Batch SR'
  ];

  for (let i = 19; i >= 0; i--) {
    const dataAlvo = new Date(agora.getTime() - (i * 24 * 60 * 60 * 1000));
    const diaNum = dataAlvo.getDate().toString().padStart(2, '0');
    const mesNum = (dataAlvo.getMonth() + 1).toString().padStart(2, '0');
    const anoNum = dataAlvo.getFullYear();
    const dataFormatada = `${diaNum}/${mesNum}/${anoNum}`;
    const diaSemanaIndex = dataAlvo.getDay();
    const diaSemanaNome = diasDaSemana[diaSemanaIndex];
    const isFimDeSemana = diaSemanaIndex === 0 || diaSemanaIndex === 6;

    // Regras de simulação para a série
    let status = 'SUCCESS';
    let motivo = 'Execução perfeita do pipeline agendado';
    let duracaoSegundos = (1.2 + Math.random() * 0.95).toFixed(3);
    let ingeridos = 0;
    let antifraudeSeguros = 0;
    let scoreAlto = 0;
    let despachados = 0;

    // Simulando 1 falha pontual (há 5 dias atrás) e 1 alerta antifraude (há 11 dias atrás)
    if (i === 5 && !isFimDeSemana) {
      status = 'FAILED';
      motivo = 'Falha de conexão externa: Timeout 504 no endpoint de busca de vagas';
      duracaoSegundos = '5.012';
      ingeridos = 0;
      antifraudeSeguros = 0;
      scoreAlto = 0;
      despachados = 0;
    } else if (i === 11 && !isFimDeSemana) {
      status = 'WARNING';
      motivo = '2 tentativas de golpe descartadas com sucesso pelo Gate Antifraude';
      duracaoSegundos = (2.2 + Math.random() * 0.4).toFixed(3);
      ingeridos = 14;
      antifraudeSeguros = 12; // 2 bloqueadas
      scoreAlto = 3;
      despachados = 3;
    } else if (isFimDeSemana) {
      status = 'WEEKEND';
      motivo = 'Janela de manutenção / Fim de semana (sem agendamento automático)';
      duracaoSegundos = '0.000';
      ingeridos = 0;
      antifraudeSeguros = 0;
      scoreAlto = 0;
      despachados = 0;
    } else {
      // Dia útil com sucesso
      ingeridos = Math.floor(8 + Math.random() * 6);
      const fraudes = Math.random() > 0.65 ? 1 : 0;
      antifraudeSeguros = ingeridos - fraudes;
      scoreAlto = Math.floor(2 + Math.random() * 3);
      despachados = scoreAlto;
    }

    const runId = `#RUN-${anoNum}${mesNum}${diaNum}-N8N-${Math.floor(1000 + Math.random() * 8999)}`;
    const horaInicio = `10:00:0${Math.floor(1 + Math.random() * 5)}.${Math.floor(100 + Math.random() * 899)}`;
    const horaFim = `10:00:0${Math.floor(6 + Math.random() * 3)}.${Math.floor(100 + Math.random() * 899)}`;

    serie.push({
      indice: 19 - i,
      data: dataAlvo,
      dataFormatada: dataFormatada,
      diaSemana: diaSemanaNome,
      diaNum: diaNum,
      isFimDeSemana: isFimDeSemana,
      status: status,
      motivo: motivo,
      runId: runId,
      timestampInicio: `${dataFormatada} ${horaInicio} BRT`,
      timestampFim: `${dataFormatada} ${horaFim} BRT`,
      duracao: `${duracaoSegundos}s`,
      ingeridos: ingeridos,
      antifraude: antifraudeSeguros,
      scoreAlto: scoreAlto,
      despachados: despachados,
      vagasAprovadas: Array.from({ length: scoreAlto }, (_, idx) => ({
        cargo: cargosPool[idx % cargosPool.length],
        empresa: empresasPool[(idx + i) % empresasPool.length],
        score: Math.floor(75 + Math.random() * 23),
        status: 'Candidatura Preparada (STAR ATS)'
      }))
    });
  }

  return serie;
}

// Inicializa o Banner e calcula KPIs dos 20 dias
function initHistoricalBanner() {
  historico20DiasData = gerarSerieTemporal20Dias();

  // 1. Atualizar label da janela de 20 dias
  const primeiroDia = historico20DiasData[0].dataFormatada;
  const ultimoDia = historico20DiasData[historico20DiasData.length - 1].dataFormatada;
  const labelJanela = document.getElementById('labelJanela20Dias');
  if (labelJanela) {
    labelJanela.textContent = `${primeiroDia} a ${ultimoDia} (20 dias)`;
  }

  // 2. Calcular KPIs
  const diasUteis = historico20DiasData.filter(d => !d.isFimDeSemana);
  const totalEsperadas = diasUteis.length;
  const sucessos = diasUteis.filter(d => d.status === 'SUCCESS' || d.status === 'WARNING').length;
  const falhas = diasUteis.filter(d => d.status === 'FAILED').length;
  const taxaSucesso = ((sucessos / totalEsperadas) * 100).toFixed(1);

  let somaDuracao = 0;
  let countComDuracao = 0;
  let totalVagas = 0;
  let totalScoreAlto = 0;
  let totalAntifraudeBloqueadas = 0;

  historico20DiasData.forEach(d => {
    if (d.status !== 'WEEKEND' && d.status !== 'FAILED') {
      somaDuracao += parseFloat(d.duracao);
      countComDuracao++;
    }
    totalVagas += d.ingeridos;
    totalScoreAlto += d.scoreAlto;
    totalAntifraudeBloqueadas += (d.ingeridos - d.antifraude);
  });

  const mediaDuracao = countComDuracao > 0 ? (somaDuracao / countComDuracao).toFixed(2) : '1.84';

  // Atualizar elementos do DOM
  const elExecRealizadas = document.getElementById('kpiExecucoesRealizadas');
  if (elExecRealizadas) elExecRealizadas.textContent = sucessos;

  const elTaxaSucesso = document.getElementById('kpiTaxaSucesso');
  if (elTaxaSucesso) elTaxaSucesso.textContent = `${taxaSucesso}%`;

  const elSucessosCount = document.getElementById('kpiSucessosCount');
  if (elSucessosCount) elSucessosCount.textContent = `${sucessos} Sucessos`;

  const elFalhasCount = document.getElementById('kpiFalhasCount');
  if (elFalhasCount) elFalhasCount.textContent = `${falhas} Falha`;

  const elTempoMedio = document.getElementById('kpiTempoMedio');
  if (elTempoMedio) elTempoMedio.textContent = `${mediaDuracao}s`;

  const elVagasProcessadas = document.getElementById('kpiVagasProcessadas');
  if (elVagasProcessadas) elVagasProcessadas.textContent = totalVagas;

  // 3. Renderizar Grid da Timeline dos 20 Dias
  renderizarTimelineGrid();

  // 4. Selecionar por padrão o dia mais recente (Hoje)
  selecionarDiaTimeline(historico20DiasData.length - 1);
}

// Renderiza os 20 cards/blocos da Timeline Interativa
function renderizarTimelineGrid() {
  const container = document.getElementById('gridTimeline20Dias');
  if (!container) return;

  container.innerHTML = '';

  historico20DiasData.forEach((item, index) => {
    let pillCor = 'status-pill-success';
    let statusLabel = 'Sucesso';

    if (item.status === 'FAILED') {
      pillCor = 'status-pill-failed';
      statusLabel = 'Falha';
    } else if (item.status === 'WARNING') {
      pillCor = 'status-pill-warning';
      statusLabel = 'Aviso Antifraude';
    } else if (item.status === 'WEEKEND') {
      pillCor = 'status-pill-weekend';
      statusLabel = 'Fim de Semana';
    }

    const card = document.createElement('div');
    card.className = 'timeline-day-card glass-card rounded-xl p-2.5 flex flex-col items-center justify-between border border-white/[0.06] text-center';
    card.id = `timelineCard-${index}`;
    card.setAttribute('title', `${item.dataFormatada} (${item.diaSemana}): ${statusLabel} • ${item.duracao}`);
    card.onclick = () => selecionarDiaTimeline(index);

    card.innerHTML = `
      <span class="text-[9px] text-[#9AA1AC] uppercase font-semibold">${item.diaSemana}</span>
      <span class="text-xs font-mono font-bold text-white my-1">${item.diaNum}</span>
      <span class="w-2 h-2 rounded-full ${pillCor}"></span>
    `;

    container.appendChild(card);
  });
}

// Seleciona um dia na timeline e atualiza o componente de Ticket
function selecionarDiaTimeline(index) {
  // Remove ativo anterior
  document.querySelectorAll('.timeline-day-card').forEach(c => c.classList.remove('active-day'));

  const cardAtivo = document.getElementById(`timelineCard-${index}`);
  if (cardAtivo) cardAtivo.classList.add('active-day');

  const ticket = historico20DiasData[index];
  ticketSelecionadoAtual = ticket;

  // Atualizar Card de Ticket
  const elRunId = document.getElementById('ticketRunId');
  if (elRunId) elRunId.textContent = ticket.runId;

  const elSubtitulo = document.getElementById('ticketSubtitulo');
  if (elSubtitulo) elSubtitulo.textContent = ticket.motivo;

  const elStatusBadge = document.getElementById('ticketBadgeStatus');
  const elStatusTexto = document.getElementById('ticketBadgeTexto');

  if (elStatusBadge && elStatusTexto) {
    if (ticket.status === 'SUCCESS') {
      elStatusBadge.className = 'px-2.5 py-0.5 rounded-full bg-[#22D3A5]/10 border border-[#22D3A5]/25 text-[#22D3A5] text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5';
      elStatusTexto.textContent = 'SUCESSO (PASS)';
    } else if (ticket.status === 'WARNING') {
      elStatusBadge.className = 'px-2.5 py-0.5 rounded-full bg-amber-400/10 border border-amber-400/25 text-amber-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5';
      elStatusTexto.textContent = 'ALERTA (ANTIFRAUDE)';
    } else if (ticket.status === 'FAILED') {
      elStatusBadge.className = 'px-2.5 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/25 text-rose-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5';
      elStatusTexto.textContent = 'FALHA (TIMEOUT)';
    } else {
      elStatusBadge.className = 'px-2.5 py-0.5 rounded-full bg-white/10 border border-white/20 text-[#9AA1AC] text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5';
      elStatusTexto.textContent = 'OFF-PEAK (SÁB/DOM)';
    }
  }

  // Atualizar Metadados
  const elInicio = document.getElementById('ticketTimestampInicio');
  if (elInicio) elInicio.textContent = ticket.timestampInicio;

  const elFim = document.getElementById('ticketTimestampFim');
  if (elFim) elFim.textContent = ticket.timestampFim;

  const elDuracao = document.getElementById('ticketDuracao');
  if (elDuracao) elDuracao.textContent = `${ticket.duracao} (${(parseFloat(ticket.duracao)/60).toFixed(2)}m)`;

  // Atualizar Checkpoints
  const elIngeridos = document.getElementById('ticketIngeridos');
  if (elIngeridos) elIngeridos.textContent = ticket.ingeridos;

  const elAntifraude = document.getElementById('ticketAntifraude');
  if (elAntifraude) elAntifraude.textContent = ticket.antifraude;

  const elScoreAlto = document.getElementById('ticketScoreAlto');
  if (elScoreAlto) elScoreAlto.textContent = ticket.scoreAlto;

  const elDespachados = document.getElementById('ticketDespachados');
  if (elDespachados) elDespachados.textContent = ticket.despachados;
}

// Funções do Modal de Payload
function abrirModalPayloadTicket() {
  if (!ticketSelecionadoAtual) return;
  const modal = document.getElementById('modalPayloadTicket');
  if (!modal) return;

  const elSub = document.getElementById('modalPayloadSubtitulo');
  if (elSub) elSub.textContent = `Run ID: ${ticketSelecionadoAtual.runId} • Data: ${ticketSelecionadoAtual.dataFormatada}`;

  trocarAbaPayload('json');
  modal.classList.remove('hidden');
}

function fecharModalPayloadTicket() {
  const modal = document.getElementById('modalPayloadTicket');
  if (modal) modal.classList.add('hidden');
}

function trocarAbaPayload(aba) {
  const container = document.getElementById('conteudoAbaPayload');
  if (!container || !ticketSelecionadoAtual) return;

  const btnJson = document.getElementById('tabBtnJson');
  const btnGates = document.getElementById('tabBtnGates');
  const btnVagas = document.getElementById('tabBtnVagas');

  // Reset classes
  [btnJson, btnGates, btnVagas].forEach(b => {
    if (b) {
      b.classList.replace('border-[#22D3A5]', 'border-transparent');
      b.classList.replace('text-[#22D3A5]', 'text-[#9AA1AC]');
    }
  });

  if (aba === 'json') {
    if (btnJson) {
      btnJson.classList.replace('border-transparent', 'border-[#22D3A5]');
      btnJson.classList.replace('text-[#9AA1AC]', 'text-[#22D3A5]');
    }
    const payloadCompleto = {
      pipeline_execution_id: ticketSelecionadoAtual.runId,
      trigger: "n8n-nodes-base.scheduleTrigger (Cron 08h Seg-Sex)",
      timestamps: {
        started_at: ticketSelecionadoAtual.timestampInicio,
        stopped_at: ticketSelecionadoAtual.timestampFim,
        duration_ms: Math.round(parseFloat(ticketSelecionadoAtual.duracao) * 1000)
      },
      integrity_verification: {
        status: ticketSelecionadoAtual.status,
        diagnostic: ticketSelecionadoAtual.motivo,
        items_ingested: ticketSelecionadoAtual.ingeridos,
        antifraud_safe: ticketSelecionadoAtual.antifraude,
        antifraud_blocked: ticketSelecionadoAtual.ingeridos - ticketSelecionadoAtual.antifraude,
        semantic_high_matches: ticketSelecionadoAtual.scoreAlto,
        dispatched_applications: ticketSelecionadoAtual.despachados
      },
      audit_telemetry: {
        operator: "Mauricio Alves dos Santos (Scheduler SR)",
        sha256_checkpoint: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        governance_compliance: "LGPD Art. 6 + ToS API"
      }
    };
    container.innerHTML = `<pre class="whitespace-pre-wrap select-all">${JSON.stringify(payloadCompleto, null, 2)}</pre>`;
  } else if (aba === 'gates') {
    if (btnGates) {
      btnGates.classList.replace('border-transparent', 'border-[#22D3A5]');
      btnGates.classList.replace('text-[#9AA1AC]', 'text-[#22D3A5]');
    }
    container.innerHTML = `
      <div class="space-y-4 font-sans text-xs">
        <div class="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between">
          <div>
            <div class="font-bold text-white">Gate 1: Ingestão HTTP APIs Oficiais</div>
            <div class="text-[#9AA1AC] text-[11px] mt-0.5">Captura multicanal com rate limiting ético</div>
          </div>
          <span class="text-[#22D3A5] font-mono font-bold">${ticketSelecionadoAtual.ingeridos} itens</span>
        </div>

        <div class="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between">
          <div>
            <div class="font-bold text-white">Gate 2: Filtro Antifraude (Fail-Closed)</div>
            <div class="text-[#9AA1AC] text-[11px] mt-0.5">Bloqueio de taxas, e-mails gratuitos e domínios &lt; 30 dias</div>
          </div>
          <span class="text-emerald-400 font-mono font-bold">${ticketSelecionadoAtual.antifraude} aprovados / ${ticketSelecionadoAtual.ingeridos - ticketSelecionadoAtual.antifraude} bloqueados</span>
        </div>

        <div class="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between">
          <div>
            <div class="font-bold text-white">Gate 3: Motor Semântico & Pydantic</div>
            <div class="text-[#9AA1AC] text-[11px] mt-0.5">Cruzamento ponderado 70/30 (Missão Crítica + Nuvem/IA)</div>
          </div>
          <span class="text-sky-400 font-mono font-bold">${ticketSelecionadoAtual.scoreAlto} com score ≥70%</span>
        </div>

        <div class="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between">
          <div>
            <div class="font-bold text-white">Gate 4: Human-in-the-Loop & Dispatcher</div>
            <div class="text-[#9AA1AC] text-[11px] mt-0.5">Confirmação de envio via Telegram Bot e registro imutável</div>
          </div>
          <span class="text-purple-400 font-mono font-bold">${ticketSelecionadoAtual.despachados} despachados</span>
        </div>
      </div>
    `;
  } else if (aba === 'vagas') {
    if (btnVagas) {
      btnVagas.classList.replace('border-transparent', 'border-[#22D3A5]');
      btnVagas.classList.replace('text-[#9AA1AC]', 'text-[#22D3A5]');
    }
    if (ticketSelecionadoAtual.vagasAprovadas.length === 0) {
      container.innerHTML = '<div class="p-4 text-center text-[#9AA1AC]">Nenhuma vaga prioritária selecionada neste ciclo.</div>';
    } else {
      let cardsHtml = '<div class="space-y-3 font-sans">';
      ticketSelecionadoAtual.vagasAprovadas.forEach(v => {
        cardsHtml += `
          <div class="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between">
            <div>
              <div class="font-bold text-white text-xs">${v.cargo}</div>
              <div class="text-[#9AA1AC] text-[11px]">${v.empresa}</div>
            </div>
            <div class="text-right">
              <span class="px-2 py-0.5 rounded-full bg-[#22D3A5]/10 text-[#22D3A5] font-mono font-bold text-xs">${v.score}%</span>
              <div class="text-[10px] text-emerald-400 mt-0.5">${v.status}</div>
            </div>
          </div>
        `;
      });
      cardsHtml += '</div>';
      container.innerHTML = cardsHtml;
    }
  }
}

function copiarTicketId() {
  if (!ticketSelecionadoAtual) return;
  navigator.clipboard.writeText(ticketSelecionadoAtual.runId).then(() => {
    alert(`Run ID copiado: ${ticketSelecionadoAtual.runId}`);
  });
}

function copiarAuditSummary() {
  if (!ticketSelecionadoAtual) return;
  const summary = `Ticket: ${ticketSelecionadoAtual.runId}
Data: ${ticketSelecionadoAtual.timestampInicio}
Status: ${ticketSelecionadoAtual.status}
Duração: ${ticketSelecionadoAtual.duracao}
Vagas Ingeridas: ${ticketSelecionadoAtual.ingeridos}
Score >= 70%: ${ticketSelecionadoAtual.scoreAlto}`;
  navigator.clipboard.writeText(summary).then(() => {
    alert('Sumário do Ticket copiado para a Área de Transferência!');
  });
}

function copiarJsonModal() {
  const container = document.getElementById('conteudoAbaPayload');
  if (!container) return;
  navigator.clipboard.writeText(container.innerText).then(() => {
    const btn = document.getElementById('btnCopiarModalJson');
    if (btn) {
      btn.innerText = 'Copiado!';
      setTimeout(() => { btn.innerText = 'Copiar JSON'; }, 2000);
    }
  });
}

// Auto-inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  initHistoricalBanner();
});
