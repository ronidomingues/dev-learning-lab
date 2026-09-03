# 19 · Anti-análise — a corrida armamentista

**Nível:** avançado · **Data:** 03/09/2026

Se ofuscação ([`18`](18-ofuscacao-e-packers.md)) esconde o *código*, anti-análise ataca as
*suas ferramentas*: detecta depurador, VM, sandbox, e muda de comportamento para te enganar.
Este é o jogo de gato e rato que define a análise de malware moderna. Para cada técnica há uma
contramedida — e para cada contramedida, uma contra-contramedida.

---

## 1. Anti-debugging — "estou sendo depurado?"

| Técnica | Como funciona | Contramedida |
|---|---|---|
| **`ptrace(TRACEME)`** (Linux) | Só um processo pode fazer `ptrace` num alvo; se o malware chama `ptrace(PTRACE_TRACEME)` e falha, há um debugger anexado | Patch da chamada; ou o debugger anexa depois; `set follow-fork` e forçar retorno 0 |
| **`IsDebuggerPresent` / PEB flag** (Windows) | Lê o flag `BeingDebugged` no PEB | Zerar o flag; plugins como ScyllaHide escondem o debugger |
| **Timing checks** (RDTSC) | Mede ciclos entre dois pontos; um breakpoint/step atrasa muito | Não fazer single-step na região; patch para retornar delta pequeno |
| **Breakpoint detection** | Procura o byte `0xCC` (INT3) no próprio código, ou checa DR0–DR7 | Usar *hardware breakpoints* (não alteram bytes); esconder registradores de debug |
| **`INT 2D` / exceções** | Comportamento de exceção difere sob debugger | Tratar/patched; conhecer o truque específico |
| **Self-checksumming** | O código soma seus próprios bytes; um breakpoint (0xCC) muda a soma → detecta patch/BP | Hardware breakpoints; corrigir o checksum após patch |

Ferramenta-chave no Windows: **ScyllaHide** (esconde a presença do depurador de dezenas de
checagens de uma vez). No Linux, patch das checagens ou Frida forçando os retornos.

---

## 2. Anti-VM / anti-sandbox — "estou num laboratório?"

Malware sofisticado se comporta bem quando percebe que está numa VM/sandbox (para não revelar
sua lógica maliciosa ao analista) e só ataca em máquinas "reais".

**Sinais que ele procura:**
- **Artefatos de VM:** drivers/serviços (`VBoxGuest`, `vmtoolsd`), endereços MAC de fabricantes
  de VM, strings de BIOS ("VirtualBox", "VMware"), dispositivos específicos.
- **Recursos "pequenos demais":** poucos núcleos, pouca RAM, disco pequeno, um só monitor —
  típico de sandbox descartável.
- **Falta de interação humana:** sem movimento de mouse, histórico vazio, poucos arquivos
  recentes, uptime baixo.
- **Sandboxes conhecidas:** nomes de usuário/host padrão (`sandbox`, `malware`, `cuckoo`), hooks
  de monitoramento na memória.

**Contramedidas do analista:**
- **"Endurecer" a VM:** renomear artefatos, aumentar recursos, simular atividade de usuário,
  MAC realista. Projetos como VMCloak/scripts de hardening fazem isso.
- **Bare-metal sandbox:** analisar em hardware real descartável (mais caro, mas anti-anti-VM).
- **Patch das checagens** identificadas estaticamente.
- **Análise estática** quando o dinâmico é envenenado — anti-VM não protege contra ler o código.

---

## 3. Anti-disassembly — enganar o desmontador

Explora a ambiguidade da desmontagem linear em x86 (instruções de tamanho variável):

- **Junk byte após salto incondicional:** um byte "lixo" logo após um `jmp` desalinha a
  varredura linear, que passa a decodificar instruções fantasmas. O fluxo real (recursivo)
  pula o byte. Ghidra/IDA (recursivos) resistem melhor que `objdump`.
- **Saltos para o meio de instruções:** o mesmo byte é o fim de uma instrução e o começo de
  outra, dependendo de onde você entra (*overlapping instructions*).
- **Chamadas que nunca retornam / `push`+`ret` como `jmp` disfarçado**: confundem a
  reconstrução do fluxo.

**Contramedida:** desmontadores recursivos, correção manual (marcar bytes como código/dados no
Ghidra: `Clear`/`Disassemble`), e execução dinâmica para revelar o fluxo real.

---

## 4. Automodificação e desempacotamento em estágios

Código que **reescreve a si mesmo** em runtime (a base de packers e de vários malwares):
- O estático vê só o estágio 1 (o desempacotador); o código real só existe **após** rodar.
- Contramedida: dinâmico. Breakpoint na transição, dump da memória, ou emulação para obter o
  estágio seguinte ([`18`](18-ofuscacao-e-packers.md)).

Multi-estágio moderno: um *dropper* baixa o *loader* que baixa o *payload*, cada um cifrado e
válido só em condições específicas (geografia, data, presença de um domínio). Reverter exige
reconstruir a cadeia inteira.

---

## 5. Anti-Frida / anti-hook (mobile e desktop)

Apps que se defendem de instrumentação:
- Detectam a presença do `frida-server` (portas, nomes de thread `gum-js-loop`, strings na
  memória), ou verificam a **integridade** de funções (um hook altera os primeiros bytes).
- Detectam root/jailbreak e *cert pinning* para impedir interceptação de tráfego.

**Contramedidas:** scripts anti-detecção do Frida, *gadget* embutido em vez de server,
reescrever os primeiros bytes de volta, patch estático do app (repackaging). É um subcampo
inteiro do RE mobile ([`23`](23-mobile-e-managed.md)).

---

## 6. O princípio que vence a corrida

Anti-análise **atrapalha, não impede**. Dois motivos estruturais:
1. **O código precisa rodar.** Toda checagem anti-debug/anti-VM é código que você pode ler
   estaticamente e neutralizar. Você sempre pode *patchar a checagem*.
2. **Você controla a máquina.** Num alvo do lado do cliente, o analista tem privilégio total:
   pode emular, instrumentar o kernel, usar hardware breakpoints, rodar bare-metal. O malware
   está no seu território.

Por isso a estratégia certa é **camadas**: quando o dinâmico é envenenado por anti-VM, caia no
estático; quando o estático é ofuscado, caia no dinâmico/emulação. O atacante da vez (você)
alterna a lente que o defensor não conseguiu envenenar. **Nenhum defensor envenena as duas ao
mesmo tempo sem quebrar o próprio programa.**

---

## 7. Ética e escopo

As mesmas técnicas de contornar anti-análise servem para **defender** (analisar o malware que
te ataca) e para **atacar** (burlar proteção legítima de software). Contornar proteção para
**pirataria** ou para desabilitar segurança de terceiros sem autorização é ilegal na maioria
das jurisdições e pode violar o DMCA §1201 (EUA) e cláusulas contratuais. Análise de malware
defensiva, pesquisa de segurança de boa-fé e trabalho sob contrato de pentest são os terrenos
legítimos. Ver o arquivo de custos/ética e [`10-fundamentos.md`](10-fundamentos.md).

---

## Autoteste

1. Explique a técnica `ptrace(PTRACE_TRACEME)` e como o analista a neutraliza.
2. Por que *hardware breakpoints* derrotam a detecção de `0xCC` e o self-checksumming?
3. Liste quatro sinais que um malware usa para decidir "estou numa VM/sandbox".
4. O que é anti-disassembly com "junk byte", e por que desmontadores recursivos resistem melhor?
5. Diante de um malware com forte anti-VM, qual lente de análise você prioriza e por quê?
6. Enuncie os dois motivos estruturais pelos quais anti-análise "atrapalha, mas não impede".
7. Onde passa a linha ética/legal ao contornar proteções anti-análise?
