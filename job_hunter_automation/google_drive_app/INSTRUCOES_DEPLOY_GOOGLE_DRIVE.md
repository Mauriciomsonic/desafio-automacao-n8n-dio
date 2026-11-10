# 🚀 Guia de Implantação: Robô Caçador de Vagas ATS no Google Drive & Sheets

Este guia permite instalar o aplicativo nativo diretamente no seu **Google Drive**, integrado ao **Gmail** e **Google Sheets**, configurado para rodar **em dias úteis às 10:00 da manhã**, com **histórico diário**, **estatísticas de conversão** e **painel web (Web App)**.

---

## 📋 Passo a Passo de Instalação (Tempo estimado: 2 minutos)

### Passo 1: Criar a Planilha no Google Drive
1. Acesse o seu Google Drive ou digite no navegador: [sheets.new](https://sheets.new)
2. Renomeie a planilha para: `Robô Caçador de Vagas ATS - Maurício`

### Passo 2: Abrir o Editor de Scripts (Google Apps Script)
1. No menu superior da planilha, clique em: **Extensões** > **Apps Script**.
2. Uma nova aba será aberta com o editor de código.

### Passo 3: Colar o Código do Aplicativo
1. No arquivo `Código.gs` (ou `Code.gs`) que já vem aberto, apague tudo e cole o conteúdo completo do arquivo:
   👉 [`google_drive_app/Code.gs`](./Code.gs)
2. Clique no botão **`+`** (Adicionar arquivo) ao lado de "Arquivos" > selecione **HTML**.
3. Dê o nome exato de `Index` (o Google criará `Index.html`).
4. Apague o conteúdo padrão e cole o código do arquivo:
   👉 [`google_drive_app/Index.html`](./Index.html)
5. Clique no ícone de disquete **💾 Salvar projeto** (ou `Ctrl + S`).

---

## ⏰ Passo 4: Ativar o Gatilho Automático (Dias Úteis às 10h)

Você tem duas formas simples de ativar o agendamento:

### Forma 1 (Pelo Menu da Própria Planilha):
1. Volte para a aba da planilha no navegador e dê um **F5 (atualizar página)**.
2. Um novo menu aparecerá no topo: **`🚀 Caçador de Vagas ATS`**.
3. Clique em: **`⏰ Configurar Gatilho Automático (Dias Úteis às 10h)`**.
4. Na primeira vez, o Google solicitará permissão de acesso (Gmail e Drive da sua conta). Clique em *Avançado > Acessar (não seguro)* e confirme.
5. Pronto! O gatilho diário das 10h está oficialmente ativo na nuvem do Google.

### Forma 2 (Direto pelo Editor do Apps Script):
1. No editor do Apps Script, selecione a função `configurarGatilhoAutomatico` no menu seletor e clique em **Executar**.

---

## 🌐 Passo 5: Fazer o Deploy como Aplicativo Web (Web App)

1. No canto superior direito do editor do Apps Script, clique em **Implantar** > **Nova implantação**.
2. Clique na engrenagem ao lado de "Selecionar tipo" e escolha **Aplicativo da Web**.
3. Preencha:
   * **Descrição:** `Caçador de Vagas ATS - Painel Web`
   * **Executar como:** `Eu (seu e-mail)`
   * **Quem tem acesso:** `Somente eu` (ou qualquer pessoa com o link, se preferir)
4. Clique em **Implantar**.
5. O Google gerará uma **URL do aplicativo da Web**. Copie esse link e salve nos favoritos do seu navegador ou no celular!

---

## 📊 Estrutura Criada Automaticamente no seu Google Drive

1. **Pasta no Google Drive:**
   * Uma pasta chamada `Curriculos_ATS_Mauricio` é criada automaticamente no seu Drive, guardando cada currículo `.txt` gerado e aprovado com score $\ge 75\%$.
2. **Aba `Candidaturas`:**
   * Registra cada vaga analisada, plataforma, empresa, cargo, score, skills que deram match, gaps e o **link direto do arquivo no Google Drive**.
3. **Aba `Historico_Diario_Estatisticas`:**
   * Registra o log de cada dia útil às 10:00: total de alertas lidos no Gmail, taxa de aprovação e score médio do dia.
4. **Proteção Anti-Spam:**
   * A coluna `Hash ID` com criptografia SHA-256 garante que nenhuma vaga receberá mais de uma candidatura, mesmo que novos e-mails cheguem para ela.
