# Teste em Windows com VM Linux

Roteiro de preparação; não foi executado neste ambiente de nuvem.

1. Instale VirtualBox e crie uma VM x86_64 com Linux desktop mantido (por exemplo Debian com XFCE). Comece com 2 CPUs, 2 GB de RAM e disco dinâmico de 16 GB. Isso não é uma meta de consumo da TV Box.
2. Instale Python 3, navegador Firefox/Chromium e Git pelo gerenciador oficial da distribuição. Copie este projeto para a VM ou clone o repositório após publicar os arquivos.
3. Execute os comandos do README. Abra o endereço com token no navegador da VM. Use F11 para tela cheia. Isso testa a camada de apresentação, sem substituir o desktop.
4. Para celular, use rede em modo bridge e confirme o IP da VM. Se a rede não permitir bridge, configure encaminhamento TCP da porta 8080 em NAT e use o IP do Windows no celular. Restrinja o firewall à rede privada.
5. Teste vídeo remoto e um MP4 local, retomada, busca, pareamento, perda/retorno de Wi-Fi e reinício do servidor. Registre SO, navegador, codec e passos em caso de falha. Aceleração de vídeo na VM não prova aceleração na TV Box.
6. Valide o servidor com `/api/health`; use console e aba Network do navegador para diagnosticar falhas. Não publique logs com tokens de sessão.

QEMU é alternativa: use uma VM desktop x86_64 com rede bridge ou `hostfwd=tcp::8080-:8080`. Não há imagem bootável pronta nesta entrega.

Para o futuro quiosque: autologin em usuário sem privilégios, sessão gráfica mínima e inicialização supervisionada do backend e navegador. Implementar somente após validar a distribuição e o navegador escolhidos. Processos de nuvem não sobrevivem à publicação; execute novamente o comando do README.

## Hardware físico antes de qualquer imagem

Recolher modelo exato e revisão da placa, SoC, arquitetura, RAM, eMMC/NAND, Wi-Fi, Bluetooth, GPU, bootloader e firmware atual. Preparar backup verificável, imagem oficial de recuperação e método de recuperação validado. Não fazer flash, desbloquear bootloader ou alterar partições nesta etapa.
