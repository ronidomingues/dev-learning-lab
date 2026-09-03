# 10 · Fundamentos — o que é uma variável de ambiente, por dentro

`Nível: intermediário` · `Atualizado em: 14/08/2026`

Aqui as caixas-pretas do Bloco A são abertas. Ao final você saberá exatamente
**onde** o valor mora na memória, **quem** o copia, **quem** consegue lê-lo e
**por que** ele não persiste.

---

## 1. Definição formal

> **Ambiente** (*environment*) de um processo é um **vetor de strings**, terminado
> por um ponteiro nulo, no formato `NOME=valor`, que o kernel entrega ao processo
> no momento de sua criação e que fica acessível na memória do próprio processo.

Três consequências saem direto da definição, e todas importam:

1. **É um vetor de strings, não um mapa.** Não existe tipo. `PORT=3000` é a string
   `"3000"`. Não existe inteiro, booleano, lista ou nulo. Tudo o que parece tipo é
   conversão feita por você, do lado do programa. Daí o erro clássico
   `Boolean("false") === true`.
2. **É entregue na criação.** Não é consultado depois. Não há notificação de mudança.
   Um processo já em execução não descobre que alguém editou um arquivo.
3. **Fica na memória do processo.** Não é um arquivo, não é um serviço, não tem dono
   central. Cada processo tem a **sua cópia**.

Em C, o ambiente é literalmente o terceiro parâmetro do `main`:

```c
int main(int argc, char *argv[], char *envp[]);
/*                                ^^^^^^^^^^^ o ambiente: char*[] terminado em NULL */
```

E a variável global `environ`, declarada em `<unistd.h>`:

```c
extern char **environ;
```

Vejamos de perto:

```c
// ambiente.c — imprime o ambiente lendo a variável global do processo
#include <stdio.h>
#include <unistd.h>

extern char **environ;

int main(void) {
    for (char **p = environ; *p != NULL; p++) {
        printf("%s\n", *p);
    }
    return 0;
}
```

```bash
gcc ambiente.c -o ambiente && ./ambiente | head -3
# esperado: SHELL=/bin/bash
#           PWD=/home/voce
#           LANG=pt_BR.UTF-8
```

`printenv` é praticamente isso e nada mais.

---

## 2. Como o valor chega lá: `fork` e `execve`

Este é o mecanismo inteiro, e vale entendê-lo de verdade.

Quando o seu shell executa `node app.js`, acontece isto:

```
     shell (PID 1234)                          processo novo (PID 5678)
     ─────────────────                         ────────────────────────
     ambiente:                        fork()
       PATH=/usr/bin        ──────────────────►  CÓPIA EXATA do ambiente
       HOME=/home/voce                             PATH=/usr/bin
       MEU_NOME=Maria                              HOME=/home/voce
                                                   MEU_NOME=Maria
                                                          │
                                                          │ execve("/usr/bin/node",
                                                          │        ["node","app.js"],
                                                          │        envp)
                                                          ▼
                                                   o binário do Node substitui a
                                                   imagem do processo, MAS o envp
                                                   passado é preservado
```

A chamada de sistema é:

```c
int execve(const char *pathname, char *const argv[], char *const envp[]);
/*                                                   ^^^^^^^^^^^^^^^^^^ aqui */
```

**O ambiente é um argumento de `execve`.** Isso responde a maior parte das dúvidas
práticas do assunto:

| Pergunta | Resposta, derivada de `execve` |
|---|---|
| Por que `export X=1` não aparece em outro terminal? | o outro terminal é outro processo, criado antes; nunca recebeu esse `envp` |
| Por que editar `~/.bashrc` não afeta o terminal aberto? | o `envp` dele foi montado antes da edição |
| Por que preciso reiniciar o serviço depois de mudar o `EnvironmentFile`? | o systemd monta o `envp` na hora do `execve`; não há como mudar depois |
| Por que o processo filho herda tudo? | porque `fork` copia, e o padrão do `execve` é repassar |
| Por que não dá para "desdefinir" globalmente? | não existe "globalmente"; existe uma cópia por processo |
| Por que o valor não persiste em disco? | ele nunca esteve em disco |

Faça o experimento:

```bash
export TESTE=abc
bash                    # abre um shell FILHO
echo $TESTE             # abc  ← herdou
export TESTE=xyz
exit                    # volta ao shell PAI
echo $TESTE             # abc  ← a mudança do filho NÃO subiu
```

**A herança é de mão única, sempre.** Nenhum processo filho consegue alterar o
ambiente do pai. É por isso que `./script.sh` que faz `export` não muda o seu shell,
mas `source script.sh` muda — o `source` não cria processo, executa no shell atual.

---

## 3. Onde o ambiente mora na memória

No Linux, o ambiente fica no **topo da pilha (stack)** do processo, montado pelo
kernel durante o `execve`:

```
   endereços altos
  ┌──────────────────────────────┐
  │  strings do ambiente         │  "PATH=/usr/bin\0" "HOME=/home/voce\0" …
  │  strings dos argumentos      │  "node\0" "app.js\0"
  ├──────────────────────────────┤
  │  envp[]  → ponteiros         │  ─────► para as strings acima
  │  argv[]  → ponteiros         │
  │  argc                        │
  ├──────────────────────────────┤
  │  pilha (cresce para baixo)   │
  │            ↓                 │
  │                              │
  │            ↑                 │
  │  heap (cresce para cima)     │
  ├──────────────────────────────┤
  │  BSS / dados / código        │
  └──────────────────────────────┘
   endereços baixos
```

O kernel expõe isso em `/proc/<pid>/environ`:

```bash
cat /proc/self/environ | tr '\0' '\n' | head -3
# esperado: SHELL=/bin/bash
#           SESSION_MANAGER=local/…
#           QT_ACCESSIBILITY=1
```

Repare no `tr '\0' '\n'`: o arquivo usa **byte nulo** como separador, exatamente
como o vetor em memória.

> **Curiosidade que confirma a teoria:** `tr '\0' '\n' < /proc/self/environ` devolve
> **vazio**, enquanto `cat /proc/self/environ | tr …` funciona. Motivo: `/proc/self`
> aponta para o processo que **abre** o arquivo, e quem abre um redirecionamento `<`
> é o processo do `tr` — cujo ambiente, naquele instante, ainda não é o que você
> espera. Para inspecionar o shell atual, use `/proc/$$/environ`. Isto não é
> pegadinha: é a definição de "cada processo tem a sua cópia", aparecendo na prática.

### 🚨 A consequência de segurança mais importante do curso

```bash
sudo cat /proc/$(pgrep -f 'node src/app.mjs')/environ | tr '\0' '\n'
```

**Root lê o ambiente de qualquer processo.** E o próprio usuário lê o de seus
processos. Isso significa:

> **Variável de ambiente NÃO protege segredo contra quem já está na máquina com
> privilégio.** Ela protege contra: commit acidental, arquivo esquecido em disco,
> backup, cópia de imagem, e leitura por outro usuário sem privilégio.

Esse é um limite **estrutural**, não uma falha a corrigir. Quem precisa passar
desse limite precisa de outra classe de mecanismo — enclave, HSM, atestação —
tratada em [60-teoria-avancada.md](60-teoria-avancada.md).

Em contrapartida, `/proc/<pid>/environ` **congela o ambiente do `execve`**: em Linux,
alterações feitas em tempo de execução com `setenv()` **não aparecem** ali, porque o
kernel guarda apenas os limites da região original. Isso confunde muita gente na
depuração — o que o `printenv` de dentro do processo mostra e o que
`/proc/PID/environ` mostra podem divergir.

---

## 4. Escopo, ciclo de vida e as três armadilhas de escopo

```
                      ┌─────────────────────────────────────┐
                      │      systemd / init (PID 1)         │
                      │      ambiente mínimo                │
                      └──────────────┬──────────────────────┘
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
             ┌────────────┐   ┌────────────┐   ┌────────────┐
             │ sshd       │   │ nginx      │   │ minha-app  │
             │            │   │            │   │ + Environ- │
             │            │   │            │   │   mentFile │
             └─────┬──────┘   └────────────┘   └─────┬──────┘
                   ▼                                 ▼
             ┌────────────┐                   ┌────────────┐
             │ seu shell  │                   │ subprocess │
             │ + .bashrc  │                   │ herda TUDO │← ⚠️
             └─────┬──────┘                   └────────────┘
                   ▼
             ┌────────────┐
             │ node app   │
             └────────────┘
```

**Armadilha 1 — herança para subprocessos.** Se a sua aplicação executa
`child_process.spawn('convert', …)` ou `subprocess.run(['ffmpeg', …])`, esse
programa de terceiro recebe **todos** os seus segredos. Se ele tiver uma falha que
imprima o ambiente num relatório de erro, o segredo saiu.

```javascript
// ❌ o ImageMagick recebe DATABASE_URL, API_KEY, tudo
spawn('convert', [entrada, saida]);

// ✅ ambiente enxuto, só o necessário
spawn('convert', [entrada, saida], {
  env: { PATH: process.env.PATH, HOME: '/tmp', LANG: 'C' },
});
```

Em Python: `subprocess.run([...], env={"PATH": os.environ["PATH"]})`.

**Armadilha 2 — o ambiente do `cron` é quase vazio.** `cron` não lê `.bashrc`, não
lê `.profile`, e o `PATH` dele costuma ser só `/usr/bin:/bin`. É a causa nº 1 de
"funciona quando eu rodo à mão, não funciona no cron".

```cron
# ❌ vai falhar: 'node' não está no PATH do cron
0 3 * * * node /opt/app/backup.js

# ✅ caminho absoluto e ambiente explícito
0 3 * * * . /etc/minha-app/env && /usr/local/bin/node /opt/app/backup.js
```

**Armadilha 3 — a sessão SSH não é o serviço.** Você testa por SSH, funciona; o
serviço sobe pelo systemd, não funciona. São ambientes diferentes, montados por
processos pais diferentes. Sempre verifique com `/proc/PID/environ`, não com
`echo $VAR` na sua sessão.

---

## 5. As regras exatas de precedência

Quando o mesmo nome vem de várias fontes, esta é a ordem (da mais forte para a mais fraca):

```
1. definido no comando               VAR=x node app.js
2. herdado do processo pai           (export no shell, systemd, Docker -e, K8s env)
3. definido pelo código em runtime   process.env.VAR = 'y'    ← muda a cópia em memória
4. carregado de arquivo .env         --env-file, dotenv, load_dotenv
5. padrão embutido no código         process.env.VAR ?? 'z'
```

**Os níveis 4 e 5 só valem se os anteriores não tiverem definido nada** — e essa é a
propriedade que sustenta o curso inteiro. Verificado no
[04-como-comecar.md §5](04-como-comecar.md) e travado por teste no
[projeto-modelo](07-projeto-modelo/test/processo.test.mjs).

Todas as bibliotecas sérias têm uma opção para inverter isso (`override: true`,
`createMutable`), e a recomendação é: **não use**. Se você inverter, o `.env`
esquecido num servidor passa a **derrubar** a configuração de produção.

---

## 6. Limites concretos

Números que só aparecem quando você já está com problema:

| Limite | Valor típico (Linux) | Como bate |
|---|---|---|
| Tamanho total de `argv` + `envp` | `MAX_ARG_STRLEN` = 128 KiB por string; total ~2 MiB (`ulimit -s / 4`) | erro `E2BIG` / `Argument list too long` |
| Nome da variável | sem limite formal; use `[A-Z_][A-Z0-9_]*` | `export 2FA=1` é erro de sintaxe no bash |
| Valor | pode conter qualquer byte **exceto `\0`** | chave privada PEM cabe; binário puro não |
| Quantidade | limitada só pelo total | — |

```bash
getconf ARG_MAX
# esperado: 2097152 (2 MiB) em Linux x86_64 típico
```

Consequência prática: **certificado ou chave privada grande em variável de ambiente
é má ideia** — não pelo limite (cabe), mas porque a quebra de linha vira um pesadelo
de escape que se comporta diferente em cada carregador. **Use arquivo montado**
(padrão `_FILE`, ver [06-exemplos.md #7](06-exemplos.md)).

---

## 7. Case sensitivity: Unix vs. Windows

| | Unix (Linux, macOS, BSD) | Windows |
|---|---|---|
| Diferencia maiúscula de minúscula? | **sim**: `Path` ≠ `PATH` | **não**: `Path` = `PATH` = `path` |
| Separador do PATH | `:` | `;` |
| Herança | via `fork`/`execve` | via `CreateProcess` (bloco de ambiente) |
| Persistência para o usuário | não existe nativamente (usa-se arquivo de perfil) | **sim**, no Registro (`HKCU\Environment`) |
| Onde ficam | memória do processo | memória do processo **+ Registro** para os persistentes |

⚠️ Essa diferença quebra código real. Um contêiner Linux com `Database_Url` e código
que lê `DATABASE_URL` funciona na máquina Windows do desenvolvedor e falha em produção.
**Sempre MAIÚSCULAS**, sempre.

E em Windows, `setx` grava no Registro: o valor **persiste depois do reboot**, e vale
para **todos** os processos novos do usuário. É a única plataforma em que "variável
de ambiente" chega perto de significar "configuração persistente do sistema" — o que
torna o Windows nativo um lugar **pior** para guardar segredo, não melhor.

---

## 8. A regra dos cinco porquês: por que `NOME=valor` e nada mais?

**1. Por que variáveis de ambiente são só texto plano `NOME=valor`?**
Porque a interface do `execve` é `char *const envp[]` — um vetor de strings C.

**2. Por que a interface é um vetor de strings C?**
Porque foi assim que o Unix definiu, no Version 7 (1979), quando `environ` e
`execve` ganharam a forma atual.

**3. Por que definiram assim, e não com tipos ou estrutura?**
Por três razões documentadas na cultura do Unix da época:
- **memória**: um PDP-11 tinha 64 KiB de espaço de endereçamento por processo;
  um formato estruturado exigiria um parser em cada programa, e o texto plano
  exige zero;
- **independência de linguagem**: qualquer linguagem sabe ler uma string terminada
  em nulo, e nenhuma precisa concordar sobre o que é "inteiro" ou "lista";
- **filosofia de texto**: a regra "escreva programas que manipulem fluxos de texto,
  porque essa é a interface universal" — que Doug McIlroy formulou e que o resto do
  Unix segue.

**4. Por que não trocaram nos 45 anos seguintes?**
Compatibilidade binária. `execve` é a fronteira entre **todo** programa e **todo**
kernel Unix-like. Mudar a assinatura quebraria cada binário existente. É uma
**decisão histórica congelada** — e este é um ponto de parada legítimo dos cinco
porquês.

**5. Então o texto plano é a melhor solução, ou só a que sobrou?**
Opinião profissional, explicitamente minha e não consenso: é a que sobrou, e é
**boa o bastante** — mas o preço é real e você paga todo dia. A ausência de tipo
causa `Boolean("false") === true`. A ausência de esquema faz o `.env.example` ser
necessário. A ausência de estrutura faz gente serializar JSON dentro de variável
(o que funciona e é feio). Formatos melhores existem no nível da aplicação
(pydantic-settings, Viper, Spring `@ConfigurationProperties`) — e todos eles, no
fundo, **leem `NOME=valor` e convertem**. A camada de baixo não mudou.

---

## 9. O que é "segredo", formalmente

Vale precisar, porque a palavra é usada de forma frouxa.

> Um **segredo** é um dado cuja **utilidade depende de sua confidencialidade**.

Disso saem propriedades que orientam todo o resto do curso:

| Propriedade | Consequência prática |
|---|---|
| Perde valor ao ser conhecido | não existe "vazou mas está tudo bem"; existe "vazou, e agora o custo é X" |
| Não se pode "des-vazar" | a única resposta a um vazamento é **rotacionar**, nunca "apagar do Git" |
| Tem prazo de validade implícito | quanto mais tempo vive, maior a chance acumulada de vazar → rotação periódica |
| É copiável sem deixar rastro | por isso auditoria de **acesso** vale mais que auditoria de **posse** |
| Vale o que protege | o modelo de ameaça define o investimento, não o contrário |

E a taxonomia que você usará ao classificar as variáveis de um sistema:

| Tipo | Exemplo | Rotação | Se vazar |
|---|---|---|---|
| **Configuração pública** | `PORT`, `LOG_LEVEL` | — | nada |
| **Configuração sensível** | `DB_HOST` interno, nome de bucket | rara | facilita reconhecimento do atacante |
| **Credencial simétrica** | senha de banco, chave de API | trimestral | acesso direto |
| **Credencial assimétrica** | chave privada TLS, chave de assinatura | anual | personificação, forja |
| **Credencial derivada** | token OAuth, ticket de sessão | minutos/horas | janela curta |
| **Credencial dinâmica** | usuário de banco criado pelo Vault | 1 h ou menos | quase nada — expira sozinha |

A última linha é o destino da evolução do assunto: **o melhor segredo é o que
expira sozinho antes de o atacante conseguir usá-lo**. Ver
[45-rotacao-e-ciclo-de-vida.md](45-rotacao-e-ciclo-de-vida.md).

---

## Autoteste

1. Escreva a assinatura de `execve` e diga qual parâmetro carrega o ambiente.
2. Por que a alteração de ambiente feita por um processo filho não afeta o pai?
3. Explique, com base em `execve`, por que reiniciar o serviço é obrigatório depois de mudar o `EnvironmentFile`.
4. Quem consegue ler `/proc/<pid>/environ`? O que isso significa para o modelo de proteção?
5. Um processo faz `setenv("X","1")`. Isso aparece em `/proc/<pid>/environ` no Linux? Por quê?
6. Cite as cinco fontes de valor em ordem de precedência.
7. Por que passar chave privada PEM por variável de ambiente é má ideia, se ela cabe no limite?
8. Por que `Path` e `PATH` são a mesma variável no Windows e diferentes no Linux, e que bug real isso causa?
9. Dê o argumento de 1979 para o ambiente ser texto plano, e diga se ele ainda vale.
10. Por que "apagar o segredo do histórico do Git" não é uma resposta suficiente a um vazamento?

---

**Fontes:** `man 2 execve`, `man 7 environ`, `man proc` (Linux man-pages) ·
POSIX.1-2017 · consultados em 14/08/2026.

**Próximo:** [11-historia.md](11-historia.md) · Voltar ao [mapa](00-MAPA.md)
