# Exercício — Armazenamento

> **Tente antes de olhar.**

## Enunciado

### Parte A — decidir

Para o **CFTV do quarto** (MotionEye, já em produção) e para o **FlixARD**,
classifique cada item como *volume nomeado*, *bind mount* ou *tmpfs*, e
justifique em uma frase:

1. Gravações de vídeo do MotionEye
2. Arquivo de configuração do MotionEye (`motioneye.conf`)
3. Banco de dados de usuários do FlixARD
4. Biblioteca de filmes e séries do FlixARD
5. Thumbnails gerados pelo FlixARD
6. Cache de sessão do Redis
7. Certificados TLS do Caddy
8. `/tmp` de uma API com `read_only: true`

### Parte B — investigar

9. Um colega diz que perdeu o banco ao rodar `docker compose down`. Como você
   descobre se havia volume configurado, e como evita que se repita?

10. Depois de meses de testes, `docker system df` mostra 14 GB em *Local
    Volumes* com 92% reclaimable. Como investigar **antes** de apagar?

### Parte C — escrever

11. Escreva o trecho de `compose.yaml` do MotionEye para CFTV com:
    - gravações em `/srv/cftv/gravacoes` no host
    - configuração versionada no git, montada read-only
    - acesso à câmera USB em `/dev/video0`
    - interface web só no loopback do host

---
---
---

# SOLUÇÃO COMENTADA

## Parte A

| # | Item | Escolha | Justificativa |
|---|---|---|---|
| 1 | Gravações do MotionEye | **bind mount** | você assiste, arquiva e apaga esses vídeos por fora do Docker |
| 2 | `motioneye.conf` | **bind mount de arquivo**, `:ro` | versionado no git; montar o **arquivo**, nunca o diretório |
| 3 | Banco do FlixARD | **volume nomeado** | ninguém abre arquivo interno do Postgres na mão |
| 4 | Biblioteca de mídia | **bind mount**, `:ro` | você copia filme para lá com rsync/Samba |
| 5 | Thumbnails | **volume nomeado** | artefato derivado, regenerável |
| 6 | Cache do Redis | **nenhum** | é cache; com `--save ""` não escreve em disco |
| 7 | Certificados do Caddy | **volume nomeado** | o Caddy gerencia sozinho; só não pode ser efêmero (senão reemite e bate no limite do Let's Encrypt) |
| 8 | `/tmp` de app read-only | **tmpfs** | efêmero por definição, e em RAM é mais rápido |

O item 7 tem uma pegadinha: parece que "certificado é arquivo, quero ver" — mas
você nunca edita um certificado na mão. Se for efêmero, porém, o Caddy reemite a
cada restart e o Let's Encrypt tem limite de 5 emissões por domínio por semana.
Volume nomeado é a resposta.

O item 6 também: a tentação é dar um volume ao Redis "por segurança". Se é
cache, persistir só cria obrigação de gerenciar disco sem ganho.

## Parte B

### 9. Investigar a perda do banco

```bash
# Havia volume declarado?
grep -A5 'volumes:' compose.yaml
docker compose config | grep -A10 'volumes:'

# O volume ainda existe?
docker volume ls | grep <nome-do-projeto>

# Se existe, para onde apontava?
docker volume inspect <nome>
```

Três causas possíveis, em ordem de probabilidade:

1. **Não havia volume.** Os dados estavam na camada de escrita e o `down`
   (que remove containers) os levou junto. Sem volta.
2. **Rodou `down -v`.** O `-v` apaga volumes. Sem volta.
3. **O volume existe, mas o serviço subiu com outro nome de projeto.** Volumes
   são prefixados pelo nome do projeto (o diretório, por padrão). Renomear a
   pasta cria um conjunto novo de volumes e "os dados somem" — mas estão lá:

```bash
docker volume ls
# projeto-antigo_pgdata     <- os dados estão aqui
# projeto-novo_pgdata       <- vazio, é o que está em uso
```

**Prevenção:**

```yaml
name: flixard        # fixa o nome do projeto, imune a renomear a pasta

services:
  db:
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

E backup automático, como no
[sistema financeiro](../08-projeto-aplicado/compose-sistema-financeiro.md).

### 10. Investigar 14 GB antes de apagar

**Nunca** rode `docker volume prune` direto. Investigue:

```bash
# 1) Detalhe por volume, com tamanho
docker system df -v

# 2) Quais estão órfãos
docker volume ls -f dangling=true

# 3) Para cada suspeito, ver o que tem dentro (sem sudo, via container)
docker run --rm -v <nome-do-volume>:/dados:ro alpine sh -c "du -sh /dados && ls -la /dados"

# 4) Quem usa cada volume
docker ps -a --format '{{.Names}}' | while read c; do
  echo "== $c"; docker inspect "$c" --format '{{range .Mounts}}{{.Name}} {{end}}'
done
```

O passo 3 é o essencial: um volume "órfão" pode conter o banco de um projeto que
você não está rodando **agora**, mas vai rodar semana que vem.

Só depois:

```bash
docker volume rm <nome-especifico>     # cirúrgico, um por vez
```

Em geral, o maior consumidor é o **build cache**, não os volumes — e esse é
seguro de limpar:

```bash
docker builder prune
```

## Parte C — MotionEye para CFTV

```yaml
name: cftv

services:
  motioneye:
    image: ccrisan/motioneye:master-amd64
    container_name: motioneye

    ports:
      # Interface web só no loopback. O acesso externo passa por proxy
      # reverso com TLS e autenticação — nunca exposto direto na LAN.
      - "127.0.0.1:8765:8765"

    volumes:
      # 1) Gravações: BIND MOUNT. É o dado que você assiste e arquiva.
      #    Vídeo enche disco rápido: monte aqui um disco dedicado.
      - /srv/cftv/gravacoes:/var/lib/motioneye

      # 2) Configuração: BIND MOUNT DE ARQUIVO, read-only.
      #    Montar o diretório /etc/motioneye esconderia os outros
      #    arquivos que a imagem traz e o serviço não subiria.
      - ./config/motioneye.conf:/etc/motioneye/motioneye.conf:ro

      # 3) Fuso horário do host: sem isso, o carimbo de data/hora da
      #    gravação sai em UTC — péssimo para quem revê imagem de segurança.
      - /etc/localtime:/etc/localtime:ro

    devices:
      # Passa a câmera USB para dentro do container.
      - /dev/video0:/dev/video0

    restart: unless-stopped

    # Câmera + transcode consomem CPU. Sem limite, o CFTV pode
    # degradar o resto do servidor.
    deploy:
      resources:
        limits:
          cpus: "1.5"
          memory: 1g

    healthcheck:
      test: ["CMD-SHELL", "wget -q --spider http://127.0.0.1:8765/ || exit 1"]
      interval: 60s
      timeout: 10s
      start_period: 30s
      retries: 3
```

### Decisões que valem comentário

**`devices:` e não `privileged: true`.** Muito tutorial de câmera manda usar
`privileged: true`, que dá ao container acesso a **todos** os dispositivos e
praticamente elimina o isolamento. `devices:` concede só `/dev/video0`. Se
precisar de mais de uma câmera, liste cada uma.

**Gravações em bind mount, num disco dedicado.** Vídeo 24/7 enche disco em
semanas. Em volume nomeado, você encheria a partição do sistema (onde vive
`/var/lib/docker`) e derrubaria **todos** os containers da máquina, não só o
CFTV. Bind mount para um disco separado isola o risco.

**`/etc/localtime` read-only.** Detalhe pequeno com consequência real: sem ele,
o carimbo das gravações fica em UTC. Em imagem de segurança, horário errado
compromete o valor do registro.

**Interface no loopback.** MotionEye é uma interface administrativa com acesso a
câmera dentro da sua casa. Expor na LAN é convite. E lembre-se de que
`ufw deny 8765` **não** protege, porque as regras de iptables do Docker são
avaliadas antes das do UFW — o prefixo `127.0.0.1:` é o que realmente resolve.

> **Nota:** a tag `ccrisan/motioneye:master-amd64` é a mais usada da comunidade,
> mas o projeto original teve manutenção intermitente. Como você já roda
> MotionEye em produção, mantenha **a imagem que já funciona** e confira a tag
> antes de mudar. Não troque uma coisa que funciona por causa de um exercício.

---
[← bind mount vs volume](bind-mount-vs-volume.md) · [módulo 05: redes →](../05-redes/bridge-host-none.md) · [índice](../00-indice.md)
