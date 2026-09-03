# 05 · Manual de uso — referência das ferramentas

**Nível:** intermediário · **Data:** 03/09/2026 · organizado **por tarefa**, para consulta rápida.

Esta é a folha de cola do dia a dia. Não decore — consulte. Cada seção resolve *uma
pergunta prática*. Comandos testados em Ubuntu 22.04 (binutils 2.38, GDB 12.1, radare2 6.2.0,
Frida 17.17.0).

---

## Tarefa: "o que é este arquivo?"

| Comando | O que responde |
|---|---|
| `file BIN` | Formato (ELF/PE/Mach-O), arquitetura, 32/64, stripped, ligação estática/dinâmica |
| `strings -n 6 BIN` | Textos legíveis de ≥6 chars (senhas, URLs, mensagens) |
| `strings -e l BIN` | Strings UTF-16LE (comuns em binários Windows) |
| `xxd BIN \| head` | Bytes iniciais em hex (ver a "assinatura mágica": `7f 45 4c 46` = ELF) |
| `nm BIN` | Símbolos (nomes de funções/variáveis) — só se *not stripped* |
| `nm -D BIN` | Símbolos dinâmicos (funções importadas de bibliotecas) |
| `readelf -h BIN` | Cabeçalho ELF: tipo, arch, ponto de entrada |
| `readelf -d BIN` | Dependências dinâmicas (bibliotecas `.so` necessárias) |
| `checksec --file=BIN` | Proteções: NX, PIE, RELRO, canário de pilha, Fortify (vem com pwntools) |
| `capa BIN` | Capacidades de alto nível ("cria arquivo", "conexão HTTP") — flare-capa |

**Padrão de abertura de um alvo desconhecido:**
```bash
file BIN; echo ---; checksec --file=BIN; echo ---; strings -n 8 BIN | head -40; echo ---; nm -D BIN
```

---

## Tarefa: "mostre o assembly / as seções"

### objdump (binutils)
| Comando | Uso |
|---|---|
| `objdump -d BIN` | Desmontar seções executáveis (sintaxe AT&T por padrão) |
| `objdump -d -M intel BIN` | Desmontar em **sintaxe Intel** (mais legível para muitos) |
| `objdump -d --start-address=0x1149 --stop-address=0x1190 BIN` | Só um intervalo |
| `objdump -s -j .rodata BIN` | Dump hex de uma seção (ex.: dados constantes) |
| `objdump -h BIN` | Lista as seções e seus tamanhos/endereços |
| `objdump -R BIN` | Relocações dinâmicas (o que a PLT/GOT resolve) |
| `objdump -T BIN` | Tabela de símbolos dinâmicos |

Extrair uma função inteira:
```bash
objdump -d -M intel BIN | sed -n '/<nome_da_funcao>:/,/^$/p'
```

---

## Tarefa: "depurar rodando" — GDB (com pwndbg/GEF)

### Controle de execução
| Comando | Abreviação | Faz |
|---|---|---|
| `run [args]` | `r` | Inicia o programa |
| `start` | | Roda e para em `main` |
| `break *0x1149` / `break funcao` | `b` | Breakpoint por endereço ou nome |
| `continue` | `c` | Continua até o próximo breakpoint |
| `stepi` / `nexti` | `si`/`ni` | Um passo de **instrução** (into / over) |
| `step` / `next` | `s`/`n` | Um passo de **linha C** (se houver símbolos) |
| `finish` | | Roda até a função atual retornar |
| `tbreak` | | Breakpoint temporário (dispara uma vez) |

### Inspecionar
| Comando | Faz |
|---|---|
| `info registers` / `i r` | Todos os registradores |
| `p/x $rdi` | Imprime um registrador em hex |
| `x/s $rdi` | Lê a **string** apontada por RDI |
| `x/16xb $rsp` | 16 bytes em hex a partir de RSP (topo da pilha) |
| `x/8i $rip` | Próximas 8 instruções a partir de RIP |
| `x/4gx $rbp-0x20` | 4 valores de 8 bytes ("giant") a partir de um offset |
| `bt` | Backtrace (pilha de chamadas) |
| `set $rax = 1` | **Alterar** um registrador (forçar um caminho) |
| `set {int}0x4040 = 0x2a` | Escrever na memória |

### Atalhos que só quem usa há anos conhece
- `layout asm` / `layout regs` (GDB TUI) mostra código e registradores lado a lado.
- Com **pwndbg**: `vmmap` (mapa de memória), `telescope $rsp` (pilha "desenrolada" seguindo
  ponteiros), `heap`/`bins` (estado do alocador), `checksec`, `nearpc`.
- Rodar em lote (sem interação): `gdb -q -batch -ex 'b main' -ex run -ex 'x/s $rdi' BIN`.
- **Desabilitar ASLR** para endereços estáveis durante o estudo: `set disable-randomization on`
  (é o padrão do GDB) ou rodar via `setarch -R`.

---

## Tarefa: "análise + depuração num só lugar" — radare2 / rizin

`r2` é modal e tem curva íngreme; a recompensa é fazer tudo sem sair do teclado. (rizin usa
quase os mesmos comandos.)

### Abrir e analisar
```bash
r2 -A BIN         # abre e roda a análise (aa) automaticamente
r2 -d BIN         # abre em modo debug
r2 -w BIN         # abre para ESCRITA (patching)
```

### Comandos essenciais (dentro do r2)
| Comando | Faz |
|---|---|
| `aaa` | Análise completa (funções, strings, refs) |
| `afl` | Lista funções encontradas |
| `s main` / `s sym.checar` | "Seek": vai para um endereço/símbolo |
| `pdf` | Print Disassembly Function (desmonta a função atual) |
| `pdc` | Pseudo-descompilação (aproximada) |
| `iz` / `izz` | Strings na seção de dados / no arquivo todo |
| `ii` | Imports; `is` símbolos; `ie` entrypoints |
| `axt sym.foo` | Quem referencia `foo` (cross-references) |
| `VV` | Modo **grafo** de fluxo de controle (visual) |
| `V` | Modo visual (setas movem; `p` alterna painéis) |
| `db 0x1149` / `dc` / `ds` | Breakpoint / continuar / step (modo debug) |
| `dr` | Registradores (modo debug) |
| `wx 9090` @ `0x1170` | Escrever bytes (patch: dois NOPs) no endereço |
| `wa jmp 0x1200` @ `0x1170` | Escrever uma **instrução** (assembler embutido) |

**Regra de sobrevivência do r2:** `?` mostra ajuda de qualquer prefixo. `p?`, `a?`, `d?`.
Saia com `q`. A GUI **Cutter** expõe o mesmo motor com menos dor.

---

## Tarefa: "descompilar para pseudo-C"

| Ferramenta | Como | Nota |
|---|---|---|
| **Ghidra** (GUI) | Import → analisar → clicar na função → painel *Decompile* | Grátis, excelente, o padrão do curso |
| **Ghidra headless** | `support/analyzeHeadless PROJ_DIR Proj -import BIN -postScript Script.py` | Automação em lote/CI |
| **IDA Free** (GUI) | Abrir → `F5` sobre a função | Decompiler x86/x64 na nuvem |
| **radare2** | `pdc` / plugin `r2dec` (`pdd`) / `r2ghidra` (`pdg`) | `pdg` roda o descompilador do Ghidra dentro do r2 |
| **Dogbolt** (web) | Enviar binário em dogbolt.org | Compara Ghidra/angr/RetDec/BinaryNinja lado a lado |

Ghidra em **modo headless** (roda um script Python sobre um binário, sem abrir janela):
```bash
$GHIDRA/support/analyzeHeadless /tmp/proj MeuProj -import ./BIN \
  -postScript ListarFuncoes.py -deleteProject
```

---

## Tarefa: "ver o que o programa chama enquanto roda"

| Comando | Mostra |
|---|---|
| `strace ./BIN` | **Chamadas de sistema** (open, read, connect, execve…) |
| `strace -f -e trace=network ./BIN` | Só syscalls de rede, seguindo filhos (`-f`) |
| `ltrace ./BIN` | **Chamadas de biblioteca** (strcmp, malloc, printf…) |
| `ltrace -e 'str*' ./BIN` | Só funções que casam com o padrão |
| `frida-trace -i 'strcmp' ./BIN` | Instrumenta chamadas a `strcmp` ao vivo (edita os handlers JS gerados) |

`strace`/`ltrace` são a forma **mais barata** de entender o comportamento externo de um
programa antes de mergulhar no assembly. Comece por eles.

---

## Tarefa: "instrumentar / modificar em tempo de execução" — Frida

Frida injeta JavaScript num processo vivo. Poderosíssimo em Android/iOS/desktop.

```bash
frida-ps -U                 # lista processos (USB: dispositivo Android)
frida-trace -i 'open*' ./BIN
```
Script mínimo que intercepta `strcmp` e mostra os argumentos:
```javascript
// salve como hook.js; rode: frida -l hook.js ./BIN
Interceptor.attach(Module.getExportByName(null, 'strcmp'), {
  onEnter(args) {
    console.log('strcmp("' + args[0].readCString() + '", "' + args[1].readCString() + '")');
  }
});
```
Uso típico em RE: **ler a senha esperada** que o programa passa a uma comparação, ou
**forçar** uma função a retornar "sucesso" (`onLeave(retval){ retval.replace(1); }`).

---

## Tarefa: "modificar o binário permanentemente" (patching)

| Como | Ferramenta |
|---|---|
| Trocar bytes num offset | `radare2 -w`, depois `s ADDR; wx BYTES` — ou um editor hex (`xxd`/`hexedit`) |
| Substituir uma instrução | r2: `wa nop` / `wa jmp ADDR` no endereço |
| "Anular" um teste (NOP-out) | Substituir o salto condicional por `90 90...` (NOP) ou invertê-lo |
| Editar cabeçalhos/seções | **LIEF** (Python) — adiciona/edita segmentos, imports |
| Mudar interpretador/rpath ELF | `patchelf --set-interpreter ... BIN` |

Exemplo clássico ("sempre concede acesso"): achar o `je`/`jne` que decide, e invertê-lo ou
NOP-á-lo. Feito com cuidado no laboratório do [`70-pratica.md`](70-pratica.md).

---

## Tarefa: "automatizar em Python"

| Biblioteca | Para quê | Exemplo de 1 linha |
|---|---|---|
| **Capstone** | Desmontar bytes → instruções | `for i in Cs(CS_ARCH_X86,CS_MODE_64).disasm(code,0): print(i.mnemonic,i.op_str)` |
| **Keystone** | Montar (assembler): texto → bytes | `Ks(KS_ARCH_X86,KS_MODE_64).asm("xor rax,rax")` |
| **pwntools** | CTF/exploração, I/O com processos | `p = process('./BIN'); p.sendline(b'A'*40)` |
| **pyelftools / LIEF** | Ler/editar ELF/PE/Mach-O | `ELFFile(open('BIN','rb')).get_section_by_name('.text')` |
| **angr** | Execução simbólica (achar entrada que chega num ponto) | ver [`60-teoria-avancada.md`](60-teoria-avancada.md) |
| **ropper / ROPgadget** | Achar gadgets ROP | `ropper -f BIN --search 'pop rdi'` |
| **Unicorn** | Emular trechos de código isoladamente | útil para "rodar" uma função sem o programa todo |

---

## Sintaxe AT&T × Intel (a confusão nº 1 do iniciante)

O mesmo assembly, duas notações. **Sentido dos operandos é invertido.**

| | AT&T (objdump/GDB padrão) | Intel (IDA/Ghidra/`-M intel`) |
|---|---|---|
| Mover 5 para RAX | `mov $0x5, %rax` | `mov rax, 5` |
| Ordem | `origem, destino` | `destino, origem` |
| Registrador | prefixo `%` | sem prefixo |
| Imediato | prefixo `$` | sem prefixo |
| Memória | `-0x8(%rbp)` | `[rbp-0x8]` |

**Recomendação:** para RE, use **Intel** — é a notação dos descompiladores e da maioria dos
livros. `objdump -M intel`, e no GDB `set disassembly-flavor intel`.

---

## Marcados como obsoletos (não perca tempo)

- **Jython no Ghidra** → substituído por **PyGhidra** (Python 3). Só instale Jython se herdar
  scripts antigos.
- **`gdb` sem plugin** para RE sério → use **pwndbg** ou **GEF**.
- **OllyDbg** (Windows, 32-bit, sem manutenção) → use **x64dbg**.
- **IDA como única opção** → o **Ghidra** cobre 90% do trabalho de graça.

---

## Autoteste

1. Você recebe um binário desconhecido. Escreva a sequência de 4 comandos que roda primeiro,
   e o que cada um responde.
2. Qual a diferença entre `strace` e `ltrace`, e qual usar para ver uma conexão de rede?
3. No GDB, como você lê a string apontada pelo 1º argumento de uma função onde parou?
4. Traduza para Intel: `mov $0x2a, %eax`. Qual o valor movido, em decimal?
5. No radare2, qual a sequência para abrir com análise, listar funções, ir para `main` e
   desmontá-la?
6. Como você faria um programa "sempre conceder acesso" sem ter o código-fonte? Cite duas vias.
7. Qual descompilador você usaria sem instalar nada, e como compararia vários de uma vez?
