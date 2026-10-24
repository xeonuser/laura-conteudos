# Build Windows publicado

O workflow 40051051571 concluiu com sucesso: sete testes, inicialização QML,
empacotamento PyInstaller, inicialização do EXE empacotado e publicação do ZIP.
Download público: https://github.com/xeonuser/laura-conteudos/releases/download/teste-windows-40051051571/AuroraTV-Windows.zip

O pacote tem 161.630.710 bytes. A disponibilidade foi confirmada com HTTP 200.
Ainda não foi validado em computador Windows físico. Os registros anteriores
abaixo descrevem o estado antes desta compilação.

---

# Atualização: versão nativa 0.2

Foi criada aplicação Qt/QML em desktop/, com player QtMultimedia, importação de pasta, favoritos e retomada. Sete testes passaram. Inicialização e interação Qt foram verificadas em Linux offscreen. O workflow de Windows foi preparado, mas ainda não executado; nenhum EXE foi produzido ou validado. O controle móvel da versão web não está conectado ao aplicativo nativo. Consulte desktop/README.md para detalhes.

---

# Estado da primeira entrega

1. Arquitetura: definida para desenvolvimento no computador; destino físico pendente de identificação.
2. Interface: implementada com arte procedural, catálogo inicial e detalhes.
3. Entrada: teclado e comandos do controle móvel implementados; controle IR/CEC não integrado.
4. Mídia: player do navegador, arquivo local, WebVTT, favoritos e histórico implementados. Séries, TV ao vivo e áudio múltiplo pendentes.
5. Configurações: informações do navegador e restauração local implementadas; rede, áudio físico, HDMI, energia e atualizações explicitamente indisponíveis.
6. Celular: controle web, pareamento e reconexão implementados. PWA offline e descoberta automática pendentes.
7. VM: roteiro disponível; nenhuma VM Windows/VirtualBox foi executada na nuvem.
8. Hardware: bloqueado até identificação e plano de recuperação. Nenhuma imagem de instalação produzida.

Testes executados e limitações adicionais são registrados no relatório da entrega. Esta é uma base funcional, não o sistema completo solicitado.

## Validação nesta nuvem

- Quatro testes de integração HTTP passaram, incluindo entrega do HTML.
- Verificação de sintaxe dos dois arquivos JavaScript passou com Node 24.
- Teste de navegador não executado: Chromium ausente e download em cdn.playwright.dev recusado pela política de rede (403).
- Reprodução remota, codecs, navegação visual, uso por celular físico e VM continuam sem validação neste ambiente.
