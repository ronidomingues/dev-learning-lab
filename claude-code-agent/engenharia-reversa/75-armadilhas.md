# 75 · Armadilhas, mitos e más práticas

**Nível:** todos · **Data:** 03/09/2026

O que faz o iniciante perder horas — e o que o veterano evita no automático. Erros de técnica,
mitos que atrapalham, e más práticas que persistem. Ler isto **antes** economiza semanas.

---

## Parte 1 — Erros técnicos clássicos

### 1. Confiar cegamente no descompilador
O pseudo-C é uma **interpretação**, não a verdade. Ele erra tipos, funde variáveis, inventa
nomes e às vezes mente sobre o fluxo. **Correção:** quando algo não faz sentido, desça ao
assembly — ele é o que a CPU executa ([`14`](14-analise-estatica.md)).

### 2. Ignorar que `-O2` muda tudo
Testar seus alvos só em `-O0` e travar diante de código otimizado real. O compilador funde
funções (inline), desenrola laços, troca `%` por multiplicação mágica, elimina variáveis.
**Correção:** treine também com `-O2`/`-Os` e reconheça os padrões de otimização.

### 3. Confundir sintaxe AT&T e Intel
Ler `mov %eax, %ebx` como "move eax para ebx" quando em AT&T é o contrário. **Correção:**
padronize **Intel** em todas as ferramentas (`-M intel`, `set disassembly-flavor intel`).

### 4. Esquecer o ASLR ao depurar
Anotar um endereço de uma execução e ele "não existir" na próxima. **Correção:** entenda o
*slide* de ASLR; use `vmmap`; desabilite ASLR no laboratório para endereços estáveis
([`13`](13-formatos-de-binario.md)).

### 5. Confundir endereço de arquivo com endereço de memória
O offset no arquivo ≠ o endereço virtual em execução (imagebase, relocação). **Correção:** saiba
converter; o Ghidra mostra endereços virtuais, `objdump`/hex mostram offsets de arquivo.

### 6. Ler assembly linha a linha
Tentar entender cada instrução em vez de reconhecer **padrões** (prólogo, chamada+checagem,
laço, acesso a array). **Correção:** leia em blocos; use o CFG; deixe o descompilador com o
detalhe e foque na estrutura.

### 7. Não usar o binário como oráculo
Teorizar no papel quando um `break` + `set $rax=1` confirmaria em 5 segundos. **Correção:**
teste hipóteses executando; a resposta está a um breakpoint de distância.

### 8. Errar na aritmética de ponteiros/offsets de struct
Somar tamanhos ignorando **padding/alinhamento** e remontar a struct errada. **Correção:**
respeite o alinhamento; confirme offsets no assembly ([`17`](17-estruturas-de-dados-no-binario.md)).

### 9. Analisar malware sem isolamento
Rodar uma amostra "só para ver" na máquina de trabalho. **Correção:** VM descartável, rede
simulada, snapshots — sempre ([`15`](15-analise-dinamica.md), [`20`](20-analise-de-malware.md)).

### 10. Ignorar anti-análise e concluir errado
Um malware detecta a VM e se comporta bem; você conclui "é benigno". **Correção:** desconfie de
comportamento "limpo demais"; combine estático + dinâmico + VM endurecida ([`19`](19-anti-analise.md)).

### 11. Desmontagem linear tomada como verdade
`objdump` desalinha após dados no meio do código e você analisa lixo. **Correção:** use
desmontador recursivo (Ghidra/IDA/r2); corrija marcações de código/dados à mão.

### 12. Não anotar / recomeçar do zero
Reverter uma função, entender, fechar sem renomear nada, e reabrir amanhã perdido. **Correção:**
**anote sempre** (renomeie, tipe, comente); um projeto Ghidra bem anotado é seu código-fonte
reconstruído e reutilizável.

---

## Parte 2 — Mitos

| Mito | Realidade |
|---|---|
| "Descompilar devolve o código-fonte original" | Devolve *comportamento equivalente*; nomes/comentários/tipos se perderam para sempre ([`10`](10-fundamentos.md)) |
| "Ofuscação torna o código seguro" | Torna mais **caro** de reverter; nunca impede. Tudo que roda no cliente é recuperável |
| "Preciso ser gênio da matemática" | Precisa de paciência e método. A matemática pesada é para automação de fronteira, não para o dia a dia |
| "IA (LLM) já reverte tudo sozinha" | Acelera e alucina; é assistente, não oráculo. Sempre conferir ([`65`](65-estado-da-arte.md)) |
| "IDA Pro é obrigatória" | Ghidra (grátis) cobre 90%+ do trabalho. IDA é conforto/nicho, não requisito |
| "RE é ilegal" | Depende do quê, por quê e onde. Muitos usos são protegidos (segurança, interoperabilidade); pirataria não |
| "Binário stripped é impossível de entender" | Só mais trabalhoso; símbolos dinâmicos, strings e comportamento continuam entregando muito |
| "Se compila, minha descompilação está certa" | Compilar ≠ equivalente. Verifique o *comportamento*, não só a sintaxe |
| "Assembly é a mesma coisa em toda CPU" | x86, ARM, MIPS diferem em registradores, chamada e semântica. A *intuição* transfere; os detalhes não |
| "Um packer forte protege para sempre" | Compra tempo. O código se desempacota em memória para rodar — e ali você o dumpa ([`18`](18-ofuscacao-e-packers.md)) |

---

## Parte 3 — Más práticas que persistem

- **Colar comandos de tutorial sem entender** (`sudo` em tudo, desabilitar proteções às cegas).
  Você aprende o *quê* e não o *porquê*, e trava no primeiro caso diferente.
- **Perseguir a ferramenta perfeita** em vez de dominar uma. Ghidra + GDB + Python resolvem
  quase tudo; troque de ferramenta por necessidade, não por modismo.
- **Não versionar/registrar o trabalho.** Sem *writeups* e sem salvar projetos anotados, cada
  análise recomeça do zero e o aprendizado não acumula.
- **Pular a fundação** (assembly, formatos, convenções) e viver "no descompilador". Funciona até
  o dia em que o descompilador falha — e ele falha justamente nos casos interessantes.
- **Ignorar a lei e a ética** "porque é só estudo". Escolha alvos legítimos; documente
  autorização; pratique divulgação responsável ([`21`](21-vulnerabilidades.md)).
- **Automatizar cedo demais.** Escrever um script angr elaborado antes de entender o alvo à mão.
  Entenda primeiro; automatize o que se repete depois.

---

## O anti-padrão mestre

Quase todo erro acima é uma variação de **um só**: *tratar uma abstração conveniente como se
fosse a verdade* — o pseudo-C como o fonte, a ferramenta como o entendimento, a IA como o
oráculo, o comportamento observado como o comportamento total. A disciplina central do RE é
lembrar que **o binário é a única verdade**, e toda camada acima dele é uma hipótese a
confirmar.

---

## Autoteste

1. Qual é o "anti-padrão mestre" do qual quase todos os erros derivam? Dê dois exemplos.
2. Por que treinar só com `-O0` é uma armadilha, e o que fazer a respeito?
3. Desminta: "ofuscação torna o código seguro". Onde exatamente ela falha?
4. Um malware parece benigno na sua análise dinâmica. Que armadilha você deve considerar?
5. Cite dois mitos sobre ferramentas (IDA/IA) e a realidade de cada um.
6. Por que "anotar sempre" no Ghidra não é preciosismo, mas produtividade?
7. Qual má prática de aprendizado impede o conhecimento de *acumular* entre análises?
