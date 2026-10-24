# Arquitetura e decisões

A primeira fatia usa Python stdlib para transporte LAN e HTML/CSS/JavaScript sem framework para apresentação. A interface do navegador é uma camada do futuro sistema, não substitui sozinha o SO. Não há kernel próprio ou integração privilegiada nesta versão.

- `smartbox/server.py`: runtime de desenvolvimento, catálogo autorizado inicial, pareamento e fila limitada de comandos. Processo único, tokens efêmeros.
- `web/app.js`: navegação espacial, estado de tela, catálogo, reprodução e persistência local.
- `web/remote.js`: controle móvel autenticado, reconexão e busca.
- `web/style.css`: identidade visual e layout adaptável.
- `tests/`: testes de integração HTTP sem pacotes externos.

Próxima separação: extrair catálogo/provedores, player, persistência e adaptadores de hardware dos módulos iniciais. Provedores devem declarar disponibilidade, licença e capacidades; nenhum serviço deve presumir acesso a um catálogo comercial.

Para Linux físico, avaliar mpv/Kodi e DRM/KMS ou navegador quiosque conforme GPU, drivers e memória. Rede pode usar NetworkManager via D-Bus, áudio PipeWire e energia logind, com serviço de privilégios mínimos e autorização explícita. Nenhum desses adaptadores está conectado agora. Android requer outra camada de integração nativa; não assumir que uma imagem Linux genérica inicializa em SoCs ARM de TV Box.

Atualizações assinadas, rollback, watchdog, backup/restauração, armazenamento indexado, logs estruturados e descoberta mDNS precisam de implementação antes de uso como appliance. Esta versão não modifica partições nem fornece comandos de flash.
