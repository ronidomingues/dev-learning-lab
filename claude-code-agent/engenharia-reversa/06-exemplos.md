# 06 · Exemplos — 12 casos, do trivial ao de produção

**Nível:** intermediário · **Data:** 03/09/2026

Cada exemplo segue **problema → solução → explicação**. Todo código é completo e executável.
Compile os alvos com o `gcc` do [`03-instalacao.md`](03-instalacao.md). Sintaxe de assembly:
Intel (`objdump -M intel`).

> Convenção deste arquivo: `$` é o seu shell; `(gdb)` e `[0x...]>` são prompts de ferramenta.

---

## 1. Achar uma senha em texto claro

**Problema:** um programa pede senha; descubra-a sem o fonte.
```bash
cat > ex1.c <<'EOF'
#include <stdio.h>
#include <string.h>
int main(int c, char**v){ return (c==2 && !strcmp(v[1],"hunter2")) ? puts("OK") : puts("NO"); }
EOF
gcc -O0 -o ex1 ex1.c
```
**Solução:**
```bash
strings ex1 | grep -v '^/' | grep -E '^[a-z0-9]{5,}$'
# hunter2
./ex1 hunter2   # OK
```
**Explicação:** literais de string vão para `.rodata` e sobrevivem à compilação. `strings` é
sempre o primeiro tiro. Custa nada e resolve o caso ingênuo.

---

## 2. Entender uma comparação numérica

**Problema:** qual número o programa aceita?
```bash
cat > ex2.c <<'EOF'
#include <stdlib.h>
#include <stdio.h>
int main(int c,char**v){ if(c==2 && atoi(v[1])*3+7==2026){puts("OK");return 0;} puts("NO");return 1;}
EOF
gcc -O0 -o ex2 ex2.c
objdump -d -M intel ex2 | grep -E 'imul|add|cmp' | head
```
**Solução:** o assembly mostra `imul eax, eax, 3`, `add eax, 7`, `cmp eax, 0x7ea`
(`0x7ea` = 2026). Resolva a equação: `n*3+7=2026 → n=673`.
```bash
./ex2 673   # OK
```
**Explicação:** constantes aparecem como *imediatos* em hex. `0x7ea = 2026`. Reverter é
resolver a equação que o assembly descreve.

---

## 3. Reverter um XOR de byte único (senha oculta)

**Problema:** `strings` não mostra a senha. Veja o projeto-modelo
([`07-projeto-modelo/SOLUCAO.md`](07-projeto-modelo/SOLUCAO.md)) para o caso completo.
```bash
python3 -c "print(bytes(b^0x42 for b in bytes.fromhex('052a2b263023102326233027')).decode())"
# GhidraRadare
```
**Explicação:** XOR é reversível (`p = c ^ k`). A chave `0x42` está no próprio código
(`xor eax, 0x42`) e o dado cifrado, na `.rodata`. Ofuscação, não criptografia.

---

## 4. Ler argumentos de função no GDB (a convenção de chamada)

**Problema:** descobrir o que é passado a `strcmp` sem ler todo o assembly.
```bash
gcc -O0 -o ex1b ex1.c   # reusa o ex1.c
gdb -q ex1b
```
```gdb
(gdb) set disassembly-flavor intel
(gdb) break strcmp
(gdb) run chute
(gdb) x/s $rdi      # 1º arg: a sua entrada -> "chute"
(gdb) x/s $rsi      # 2º arg: a senha esperada -> "hunter2"
```
**Explicação:** na convenção **System V x86-64**, os 6 primeiros argumentos inteiros/ponteiro
vão em **RDI, RSI, RDX, RCX, R8, R9**, nessa ordem. Parar num `strcmp`/`memcmp` e ler RSI é
o truque mais rentável do RE dinâmico ([`16`](16-a-pilha-e-convencoes.md)).

---

## 5. Patch: fazer o programa "sempre aceitar"

**Problema:** desbloquear o `ex1` sem saber a senha, modificando o binário.
```bash
r2 -w ex1        # abre para escrita
```
```
[0x0]> aaa
[0x0]> s main
[0x0]> pdf                 # ache o 'jne'/'je' que decide OK vs NO
[0x0]> s 0x<endereco_do_call_strcmp_test>
[0x0]> "wa mov eax, 0"     # força strcmp "igual" (retorno 0) OU inverta o salto
[0x0]> q
```
**Solução mais simples** (inverter o salto): localize o `jne` após o `test eax,eax` e troque
por `je` (ou NOP-out). Depois `./ex1 qualquercoisa` imprime `OK`.
**Explicação:** o binário é editável. Quebra de proteção local é, no fundo, achar **o byte da
decisão** e virá-lo. Também mostra por que proteção do lado do cliente é frágil.

---

## 6. Descompilar no Ghidra headless (automação)

**Problema:** extrair o pseudocódigo de uma função sem abrir a GUI.
```python
# ListarC.py  (rode com analyzeHeadless ... -postScript ListarC.py)
from ghidra.app.decompiler import DecompInterface
di = DecompInterface(); di.openProgram(currentProgram)
fm = currentProgram.getFunctionManager()
for f in fm.getFunctions(True):
    if f.getName() == "main":
        res = di.decompileFunction(f, 60, monitor)
        print(res.getDecompiledFunction().getC())
```
```bash
$GHIDRA/support/analyzeHeadless /tmp/p P -import ./ex2 -postScript ListarC.py -deleteProject
```
**Explicação:** o modo headless é como se coloca RE em pipeline/CI — triagem de milhares de
binários, geração de relatórios, diffing de versões.

---

## 7. Desmontar bytes crus com Capstone (Python)

**Problema:** você tem só alguns bytes (de um dump de rede, um shellcode) e quer o assembly.
```python
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
code = b"\x55\x48\x89\xe5\x31\xc0\x5d\xc3"   # push rbp; mov rbp,rsp; xor eax,eax; pop rbp; ret
md = Cs(CS_ARCH_X86, CS_MODE_64)
for ins in md.disasm(code, 0x1000):
    print(f"0x{ins.address:x}:  {ins.mnemonic}\t{ins.op_str}")
```
Saída:
```
0x1000:  push rbp
0x1001:  mov  rbp, rsp
0x1004:  xor  eax, eax
0x1006:  pop  rbp
0x1007:  ret
```
**Explicação:** Capstone é o motor de desmontagem por trás de meia indústria. `xor eax,eax`
é o idioma universal de "zerar" — reconheça-o de imediato.

---

## 8. Identificar e desempacotar um binário com UPX

**Problema:** `strings` só mostra lixo e "UPX!"; o programa está *packed*.
```bash
# criar um alvo empacotado:
gcc -O2 -o ex8 ex2.c && upx -9 ex8 2>/dev/null || echo "instale upx (03-instalacao)"
file ex8               # menciona "UPX compressed"
upx -d -o ex8_orig ex8 # descompacta
objdump -d -M intel ex8_orig | head
```
**Explicação:** um **packer** comprime/cifra o código e o restaura em memória ao rodar. UPX é
o único packer com desempacotamento *oficial* (`upx -d`). Packers de malware não são tão
gentis — você desempacota rodando até o *OEP* (ponto de entrada original) e fazendo dump
([`18-ofuscacao-e-packers.md`](18-ofuscacao-e-packers.md)).

---

## 9. Rastrear syscalls para entender o comportamento

**Problema:** o que este programa faz com o sistema (arquivos, rede)?
```bash
cat > ex9.c <<'EOF'
#include <stdio.h>
int main(){ FILE*f=fopen("/etc/hostname","r"); char b[64]; if(f){fgets(b,64,f);printf("%s",b);fclose(f);} return 0;}
EOF
gcc -o ex9 ex9.c
strace -e trace=openat,read,write ./ex9
```
Você vê `openat(AT_FDCWD, "/etc/hostname", O_RDONLY)` — o programa lê o hostname. Nenhuma
linha de assembly foi necessária.
**Explicação:** para *malware triage*, `strace`/`ltrace` (numa VM isolada!) revelam intenção
em segundos: que arquivos toca, para onde se conecta, o que executa.

---

## 10. Interceptar uma função com Frida (sem recompilar)

**Problema:** vazar a senha esperada de um binário vivo, sem patch e sem GDB.
```bash
gcc -O0 -o ex10 ex1.c
cat > hook.js <<'EOF'
Interceptor.attach(Module.getExportByName(null, 'strcmp'), {
  onEnter(args){ console.log('strcmp:', args[0].readCString(), '<>', args[1].readCString()); }
});
EOF
frida -l hook.js -f ./ex10 qualquer 2>/dev/null
# strcmp: qualquer <> hunter2
```
**Explicação:** Frida injeta JS no processo. Em apps Android/iOS reais, é assim que se
contornam checagens de root/jailbreak, se leem chaves e se automatizam testes de segurança.

---

## 11. Caso de produção — interoperabilidade de formato de arquivo

**Contexto real:** durante anos, abrir `.doc`/`.xls` fora do Microsoft Office exigia
**reverter o formato binário OLE2/BIFF**, não documentado publicamente. Projetos como
**LibreOffice/OpenOffice** e a lib **Apache POI** foram construídos analisando os bytes de
arquivos reais e a lógica do próprio Office.

**Como se faz (esqueleto com LIEF/pyelftools-style em Python puro sobre um formato próprio):**
```python
import struct
# Ler um cabeçalho binário desconhecido: hipótese -> validar contra muitos arquivos.
with open("amostra.bin","rb") as f:
    magic, versao, n_registros = struct.unpack("<4sHI", f.read(10))
print(magic, versao, n_registros)   # compare entre dezenas de arquivos para achar o padrão
```
**Método:** (1) colete muitos arquivos de exemplo; (2) compare regiões que mudam vs. fixas;
(3) formule hipóteses de campo (`offset`, `tamanho`, `contagem`); (4) valide escrevendo um
parser e conferindo contra o programa original. **Legalidade:** interoperabilidade é o uso
mais protegido de RE — a Diretiva 2009/24/CE da UE a autoriza explicitamente
(ver ética/custos e [`10-fundamentos.md`](10-fundamentos.md)).

---

## 12. Caso de produção — análise de um serial/keygen de licença

**Contexto real:** software com verificação de licença **local** (offline). O analista
reverte a rotina de validação e descobre a *fórmula* que separa serial válido de inválido —
como no nível 3 do projeto-modelo, mas com aritmética real.

**O que se procura no descompilador:**
```c
// pseudocódigo típico recuperado de um validador real
int valido(char *serial){
    if (strlen(serial) != 20) return 0;
    unsigned h = 0x1505;                 // semente (aqui, a do hash djb2)
    for (int i=0; i<16; i++) h = h*33 + serial[i];
    return (h & 0xffff) == checksum_dos_ultimos_4_digitos(serial);
}
```
Reconhecer `h*33` + semente `0x1505` grita **djb2** (um hash conhecido). Aí você escreve um
gerador que produz seriais cujo hash bate — um **keygen**.

**A lição profissional (e a linha ética):** entender a fórmula é *engenharia*; **gerar e
distribuir chaves para pirataria é crime** na maioria das jurisdições e viola a EULA. O mesmo
conhecimento serve para o fabricante *provar* que seu esquema é fraco e trocá-lo por
**assinatura criptográfica** (RSA/ECDSA), que não é falsificável só com o binário. Faça pelo
lado da defesa; se for ofensivo, que seja sob contrato de pentest autorizado.

---

## Autoteste

1. Ordene por custo (mais barato primeiro): Ghidra, `strings`, `strace`, GDB. Quando escalar
   de um para o outro?
2. No ex2, como `0x7ea` no assembly virou "o programa aceita 673"?
3. Por que parar num `strcmp`/`memcmp` no GDB e ler RSI é tão eficiente?
4. Qual a diferença, técnica e legal, entre o exemplo 11 (interoperabilidade) e o 12 (keygen)?
5. O que é um packer, e por que `upx -d` funciona para UPX mas não para um packer de malware?
6. Escreva o hook Frida mínimo para logar as chamadas a `memcmp` de um binário.
7. No exemplo 5, quais são as **duas** formas de "sempre aceitar", e qual altera menos bytes?
