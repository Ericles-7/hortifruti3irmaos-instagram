# Publicação automática

Uma tarefa agendada do Claude roda todo dia às **6h53, 11h53, 16h53 e 17h53** (horário de Uiraúna), com um reforço 25 min depois (**7h18, 12h18, 17h18 e 18h18**) para cobrir atraso ou falha, e publica no @hortifruti3irmaos_uirauna o que estiver vencido em `agenda/fila.json`. A publicação usa o conector Windsor.ai, na conta do Instagram `17841446253151662`.

## Arquivos

- `fila.json`: tudo o que está programado (data, hora, tipo, imagens, legenda e status).
- `gerar_fila.py`: gera a fila. As legendas dos carrosséis e o rodízio dos stories estão nele.
- `postar.py`: usado pela tarefa para listar o que está pendente e marcar o que já foi publicado.

## Passo a passo de cada execução

1. Atualizar o branch `claude/instagram-hortifruti-arts-xtrq1r`.
2. Rodar `python3 agenda/postar.py pendentes`. A saída lista as postagens `pendente` cujo horário chegou há **no máximo 90 min**. Passou disso, o post perde a hora e não sai (por exemplo, um "bom dia" à noite). Se a lista vier vazia, encerrar.
3. Publicar cada item da lista no Windsor.ai (`connector: instagram`, `account: 17841446253151662`):
   - `story` → ação `create_story`, com `image_url` = `urls[0]` (ou `video_url`, se o story for vídeo).
   - `carrossel` → ação `create_carousel_post`, com `image_urls` = `urls` e `caption` = `legenda`.
   - `reel` → ação `create_video_post`, com `video_url`, `cover_url`, `caption` = `legenda` e `share_to_feed` = true.
4. Registrar o resultado:
   - Se deu certo: `python3 agenda/postar.py marcar <id> publicado <media_id>`.
   - Se falhou: `python3 agenda/postar.py marcar <id> erro "<mensagem>"`. Não tentar de novo na mesma execução.
5. Fazer o commit de `agenda/fila.json` e o push para o mesmo branch.

Regras:
- Publicar só o que está na fila.
- Nunca publicar um item de outro dia.
- Nunca publicar duas vezes o mesmo `id`.

## Como mudar a programação

- **Trocar uma legenda, uma data ou acrescentar posts:** editar `gerar_fila.py` e rodar `python3 agenda/gerar_fila.py`. Os itens já publicados continuam marcados como publicados.
- **Novas artes:** as imagens e os vídeos publicados ficam no repositório **público** `Ericles-7/hortifruti3irmaos-midia` (branch `main`), com os mesmos caminhos usados na fila. Enviar o arquivo para lá antes do horário do post. Este repositório pode ser privado, porque o Instagram só baixa do repositório de mídia.
- **Pausar um item:** trocar o `status` dele para `pausado` em `fila.json`.
- **Reels e stories em vídeo:** o vídeo vai para `reels/` no repositório de mídia e é programado em `REELS` ou `STORIES_VIDEO`, dentro de `gerar_fila.py`, com o `commit` do repositório de mídia que trouxe o vídeo. O vídeo é servido pelo jsDelivr, fixado nesse commit, porque o raw do GitHub entrega `.mp4` sem o tipo de vídeo. A capa vai pelo raw do GitHub, como as imagens. O vídeo precisa ter menos de 20 MB.
