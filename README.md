# Nova versão: aplicativo nativo

A versão Qt/QML está em [desktop/README.md](desktop/README.md). Ela abre em janela própria, sem navegador. O workflow de Windows está preparado, mas o EXE ainda precisa ser gerado e testado no GitHub Actions. As instruções abaixo pertencem ao protótipo web anterior.

# Aurora TV

Primeira versão funcional de uma central de mídia para computador, base para um ambiente Linux em modo quiosque. Não é uma imagem de sistema operacional nem firmware para TV Box.

## Executar no computador

Requer Python 3.10+ e navegador atual. Não há dependências Python externas.

```sh
cd laura-conteudos
python -m smartbox.server
```

No Windows, use `py -3 -m smartbox.server` se `python` não estiver disponível. Abra no navegador o endereço **completo** impresso no terminal: ele contém a credencial da tela da TV. Não compartilhe esse endereço. Para encerrar o servidor: Ctrl+C.

Para usar o celular na mesma rede:

```sh
python -m smartbox.server --host 0.0.0.0 --port 8080
```

Na TV, abra o endereço impresso substituindo `0.0.0.0` pelo IP local do computador. Na TV vá a Configurações → Exibir código. No celular abra `http://IP-DO-COMPUTADOR:8080/remote.html` e digite o código. No Windows permita a porta 8080 **somente na rede privada**. O código dura cinco minutos, tem uso único e limite de tentativas. O controle reconecta enquanto o servidor mantém o token; reiniciar o servidor exige novo pareamento.

Use apenas em LAN confiável: este servidor de desenvolvimento usa HTTP sem criptografia. Não exponha a porta na internet. Para implantação final são necessários HTTPS, armazenamento e revogação de dispositivos, proteção persistente contra abuso e serviço de produção. A descoberta automática/mDNS e instalação como PWA ainda não foram implementadas; o acesso nesta versão é pelo IP.

## O que testar

- Setas navegam entre elementos; Enter seleciona, Esc volta, Home abre o início.
- Catálogo → detalhes → assistir; reprodução e controles nativos do navegador.
- Espaço pausa, setas esquerda/direita avançam dez segundos durante reprodução.
- Favoritos e progresso persistem no navegador; “Continuar assistindo” retoma o ponto salvo.
- Biblioteca abre arquivo local sem upload. Para legendas, selecione um arquivo WebVTT no player.
- No celular: direção, OK, voltar, início, play/pause, busca e volume do player.
- Configurações mostram explicitamente capacidades indisponíveis; não alteram rede, HDMI ou energia do computador.

Os dois vídeos de demonstração são projetos abertos da Blender Foundation, com fonte/licença nos detalhes; Sintel é um trailer. Não há scraping, canais FAST ou séries integrados. Fontes externas podem falhar e a interface informa indisponibilidade. Codecs, áudio múltiplo e aceleração dependem do navegador; seleção de faixa de áudio ainda não foi implementada. A arte da interface é procedural, não são pôsteres oficiais. Favoritos e histórico de arquivos locais exigem selecionar o arquivo novamente após recarregar.

## Validação automatizada

```sh
python -m unittest discover -s tests -v
node --check web/app.js
node --check web/remote.js
```

Os testes exercitam HTTP real, catálogo, isolamento da credencial da TV, pareamento, comando de busca, estado de reprodução, limite de tentativas, origem e código de uso único. Não validam decodificação de vídeo nem navegação visual.

Veja [máquina virtual](docs/VM.md), [arquitetura](docs/ARCHITECTURE.md) e [estado de implementação](docs/STATUS.md).
