# 15 · Análise dinâmica — executar e observar

**Nível:** intermediário · **Data:** 03/09/2026

Análise **dinâmica** é rodar o programa e observá-lo por dentro. Ela responde o que o estático
não sabe: **valores concretos** de tempo de execução, qual caminho é realmente tomado, e
desfaz "de graça" ofuscação e packing (o programa se desembaralha para rodar, e você olha).
O custo: você vê só os caminhos que aciona, e executar código hostil exige **isolamento**.

---

## 1. As três formas de análise dinâmica

| Forma | O que faz | Ferramentas |
|---|---|---|
| **Depuração** | Pausa a execução, inspeciona/edita registradores e memória, passo a passo | GDB (+pwndbg/GEF), x64dbg, LLDB, WinDbg |
| **Tracing** | Registra eventos (syscalls, chamadas de lib, instruções) sem parar | strace, ltrace, `ftrace`, DynamoRIO |
| **Instrumentação** | Injeta código no processo vivo para interceptar/alterar | Frida, Pin, Valgrind, eBPF |

Comece sempre pelo **mais barato** (tracing) e desça para depuração quando precisar de detalhe.

---

## 2. Depuração com GDB — o núcleo

### O ciclo
```gdb
break funcao        # onde parar
run [args]          # inicia
# ...parou...
info registers      # estado
x/s $rdi            # inspeciona memória/argumentos
stepi / nexti       # avança instrução (into/over)
finish              # roda até retornar
continue            # segue até o próximo break
```

### Breakpoints que vão além do básico
- **Por endereço:** `break *0x401149` (útil em binário stripped, sem nomes).
- **Condicional:** `break funcao if $rdi == 0` — para só quando a condição bate. Economiza horas.
- **Watchpoint:** `watch var` / `watch *0x4040` — para quando **um valor de memória muda**.
  Perfeito para achar "quem sobrescreveu isto?".
- **Catchpoint:** `catch syscall connect` — para numa syscall específica.

### Ver e alterar o mundo
```gdb
x/16xb $rsp         # 16 bytes da pilha em hex
x/8i $rip           # próximas 8 instruções
telescope $rsp      # (pwndbg) pilha "desenrolada" seguindo ponteiros
set $rax = 1        # força um valor (ex.: fingir que uma checagem passou)
set {int}0x4040 = 42
jump *0x401200      # desvia a execução (pular uma checagem)
```

**O truque mais poderoso:** parar antes de uma decisão e **forçar o resultado**. Chegou num
`test eax,eax; je erro` e você quer o outro caminho? `set $eax = 1` (ou 0) e siga. É análise
dinâmica virando *manipulação* — a fronteira com o patching.

---

## 3. Tracing — o reconhecimento barato

### strace (syscalls = interação com o SO)
```bash
strace -f -e trace=file,network,process ./BIN
```
Mostra tudo que o programa pede ao kernel: arquivos abertos, conexões, processos criados. Para
**triagem de malware** (numa VM!), é a foto mais rápida da intenção: "abre isto, conecta ali,
executa aquilo".

### ltrace (chamadas de biblioteca)
```bash
ltrace -e 'strcmp+strncmp+memcmp' ./BIN senha
```
Vê as chamadas a funções de bibliotecas — inclusive as comparações de senha, com os argumentos.
Muitas vezes **resolve um crackme sozinho**: você lê a senha esperada passando pelo `strcmp`.

---

## 4. Instrumentação com Frida — reescrever o comportamento ao vivo

Frida injeta JavaScript no processo. Você intercepta qualquer função, lê/altera argumentos e
retornos, sem recompilar nem parar o programa.

```javascript
// Logar e FORÇAR uma verificação de licença a retornar "válido"
const alvo = Module.getExportByName(null, 'verifica_licenca');
Interceptor.attach(alvo, {
  onEnter(args) { this.serial = args[0].readCString(); },
  onLeave(retval) {
    console.log('verifica_licenca("' + this.serial + '") =', retval, '-> forcando 1');
    retval.replace(1);   // sempre "válido"
  }
});
```
Usos reais: contornar checagens de root/jailbreak e *cert pinning* em apps móveis (em pentest
autorizado), extrair chaves de criptografia no momento em que são usadas, mapear qual função
faz o quê chamando `Stalker` (trace de instruções). É a ferramenta que domina o RE mobile
([`23`](23-mobile-e-managed.md)).

---

## 5. Emulação — rodar sem a máquina/SO alvo

Às vezes você não pode rodar o binário nativamente: é de outra arquitetura (firmware ARM/MIPS
num PC x86), ou você quer isolar **uma função** e executá-la com entradas controladas.

| Ferramenta | Para quê |
|---|---|
| **QEMU (user-mode)** | Rodar um binário ARM/MIPS no seu x86 (`qemu-arm ./bin_arm`) |
| **QEMU (system)** | Emular a máquina inteira (firmware, um SO) |
| **Unicorn** | Emular *trechos* de código em Python — "rode esta função com RDI=0x10" |
| **Qiling** | Framework sobre Unicorn: emula syscalls/SO, roda binários isolados |
| **angr** | Execução simbólica *e* concreta; explora caminhos ([`60`](60-teoria-avancada.md)) |

Emulação com Unicorn é ideal para **desofuscar**: você executa a rotina de decriptação embutida
no malware, alimentando os bytes cifrados, e lê o resultado — sem rodar o malware inteiro.

---

## 6. Anti-debug: por que às vezes "não para"

Programas hostis detectam depuradores e mudam de comportamento (travam, mentem, se apagam).
Técnicas comuns: `ptrace(PTRACE_TRACEME)` (Linux — se já está sendo *traced*, falha),
`IsDebuggerPresent`/`CheckRemoteDebuggerPresent` (Windows), medir tempo entre instruções
(um breakpoint atrasa), procurar `0xCC` (o byte do breakpoint) no próprio código.

Contramedidas: rodar sob um depurador que esconde sua presença, *patch* das checagens, ou
Frida para forçar as funções de detecção a retornarem "não há debugger". Assunto inteiro em
[`19-anti-analise.md`](19-anti-analise.md).

---

## 7. Laboratório seguro (obrigatório para malware)

Executar código desconhecido é executar código possivelmente hostil. **Regras não-negociáveis:**
- **VM descartável** com *snapshot* — você reverte ao estado limpo após cada amostra.
- **Rede isolada** ou simulada (**INetSim**/**FakeNet**) para o malware "achar" que tem
  internet sem tocar a real; nunca na sua LAN.
- **Sem pastas compartilhadas** montadas com a máquina hospedeira durante a execução.
- **Distro pronta:** REMnux (análise) + uma VM Windows com FLARE VM (execução), em rede só entre elas.
- Ciente de que malware avançado **detecta VM** e se comporta bem para enganar você
  ([`19`](19-anti-analise.md), [`20`](20-analise-de-malware.md)).

---

## 8. Estático × dinâmico — quando usar qual

| Situação | Prefira |
|---|---|
| Código hostil que você não quer executar | Estático |
| Precisa saber um valor de runtime (chave, offset calculado) | Dinâmico |
| Packer/ofuscação (o programa se desembaralha ao rodar) | Dinâmico (dump após unpack) |
| Mapear todos os caminhos possíveis | Estático (+ simbólico) |
| Confirmar rapidamente uma hipótese | Dinâmico (breakpoint + observar) |
| Um crackme simples | ltrace/Frida primeiro; often resolve na hora |

Na prática: **os dois, alternando**. Estático mapeia; dinâmico confirma e desbloqueia.

---

## Autoteste

1. Cite as três formas de análise dinâmica e um exemplo de ferramenta de cada.
2. O que um **watchpoint** faz, e para que problema ele é a ferramenta ideal?
3. Você parou num `test eax,eax; je erro` e quer o outro caminho. Dê duas formas de forçar isso no GDB.
4. Por que `ltrace` frequentemente resolve um crackme sem abrir o descompilador?
5. Escreva o esqueleto de um hook Frida que força uma função a retornar 1.
6. Quando você usaria **emulação** em vez de rodar o binário nativamente? Dê dois casos.
7. Liste três regras não-negociáveis do laboratório de análise de malware e por quê.
8. Um malware "não para" no seu GDB e se encerra sozinho. O que provavelmente está acontecendo?
