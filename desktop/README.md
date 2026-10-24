# Aurora TV nativa (0.2)

Aplicação Qt/QML em janela própria, tela cheia, sem navegador e sem servidor HTTP.
Esta é a nova direção de desenvolvimento. A pasta web/ preserva o protótipo anterior.

## Desenvolvimento

Python 3.10–3.13 (3.12 recomendado). Em um ambiente virtual:

```
python -m pip install -r desktop/requirements.txt
python -m desktop.app
```

Use `--windowed` para uma janela. Setas navegam; para cima abre navegação do menu,
para baixo volta aos títulos. Enter assiste, F favorita, S busca, O importa pasta,
Esc volta e F11 alterna tela cheia. Mouse também funciona; duplo clique abre um título.
Os seletores de arquivo e controles de configurações ainda exigem mouse/teclado;
compatibilidade total com controle remoto físico permanece pendente.

A biblioteca importa MP4, MKV, WebM, MOV, AVI e M4V; os formatos efetivamente
reproduzíveis dependem dos codecs do Qt/FFmpeg. Importação ocorre em segundo plano,
limitada a 2.000 vídeos/10.000 diretórios. Não move nem envia os arquivos.
Favoritos e progresso ficam no diretório AppDataLocation do Qt, em library.json.
O player oferece faixas de áudio e legendas embutidas quando detectadas.
Biblioteca organiza os arquivos pelo nome; pôsteres, identificação de temporadas,
metadados externos e atualização automática de pastas ainda não foram implementados.

## Pacote para Windows

`.github/workflows/windows-app.yml` prepara build no Windows, testes e empacotamento
com PyInstaller. Quando publicado no GitHub, o workflow em main ou execução manual
gera o artefato AuroraTV-Windows. É um pacote portátil com AuroraTV.exe e _internal;
não é um instalador e não exige Python no computador de destino.
O workflow foi preparado, mas não executado nesta nuvem. Não há EXE Windows pronto.

## Validação realizada na nuvem Linux

- Sete testes de backend e persistência passaram.
- Inicialização QML passou em plataforma offscreen.
- Teste Qt de navegação, favorito, seleção da biblioteca, abertura de player e saída passou.
- Um vídeo MPEG-4 sintético local foi aberto e decodificado pelo FFmpeg do Qt.
- Não há dispositivo de som ou aceleração de vídeo nesta máquina: áudio audível e
  aceleração por hardware não foram validados.
- Windows real, pacote PyInstaller e conteúdo remoto não foram validados.
- Capturas reais da execução de teste estão em /workspace/aurora-artifacts.

O controle móvel do protótipo web não está conectado à interface nativa.
Rede, HDMI, energia, atualização de SO e firmware não são implementados pelo app.

Para repetir o teste de interface, instale também FFmpeg e execute na raiz:
`QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software python -m scripts.smoke_native`.
Opcional: AURORA_SCREENSHOT=/caminho/captura.png salva uma captura da tela inicial.
