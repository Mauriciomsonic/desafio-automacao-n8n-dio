# 📦 Guia Passo a Passo: Publicação na Hostinger (projetohandmadetemplates.online)

## Passo a Passo no hPanel:
1. Acesse https://hpanel.hostinger.com e selecione projetohandmadetemplates.online.
2. Abra o Gerenciador de Arquivos (File Manager) e entre na pasta public_html.
3. Envie os arquivos da pasta dist/ (index.html, .htaccess e assets/).
4. Extraia diretamente na raiz de public_html.
5. Em Segurança > SSL, ative o SSL Let's Encrypt gratuito e marque "Forçar HTTPS".

## Google Cloud Console OAuth:
No projeto gen-lang-client-0400885777, adicione em Origens JavaScript autorizadas:
- https://projetohandmadetemplates.online
- https://www.projetohandmadetemplates.online
