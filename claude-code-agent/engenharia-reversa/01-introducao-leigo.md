# 01 · O que é Engenharia Reversa (para quem nunca ouviu falar)

**Nível:** iniciante · zero jargão · **Data:** 03/09/2026

---

## Comece pela imagem

Imagine que alguém te entrega **um bolo pronto** e pede: *"descubra a receita"*.

Você não tem a receita. Você tem só o resultado final: um bolo. Mas você pode provar,
cheirar, cortar em fatias, olhar a textura, separar as camadas, mandar um pedaço pro
laboratório medir açúcar e gordura. Aos poucos, você reconstrói uma receita que produz
**um bolo igual** — mesmo sem nunca ter visto a original.

Isso é **engenharia reversa**: partir de um produto acabado e caminhar *para trás* até
entender como ele foi feito e por que funciona.

A palavra "reversa" é o oposto de **engenharia normal (direta)**, que vai da ideia ao
produto: você tem a receita → faz o bolo. A engenharia reversa vai do produto à ideia:
você tem o bolo → recupera a receita.

> **Definição informal.** Engenharia reversa é o processo de examinar algo já construído
> para descobrir sua estrutura, seu funcionamento e as decisões de projeto por trás dele —
> sem ter acesso aos planos originais.

Isso vale para qualquer coisa: um relógio mecânico, um motor de carro, uma molécula de
remédio, um chip. **Neste curso, o "bolo" é um programa de computador** — um arquivo
executável — e a "receita" é o código-fonte e a lógica que o programador escreveu.

---

## Por que um programa precisa ser "revertido"?

Aqui está o detalhe que assusta o iniciante e que é a base de tudo:

**O programa que você executa não é o programa que o programador escreveu.**

O programador escreve um texto legível, em uma linguagem como C, chamado **código-fonte**:

```c
int somar(int a, int b) {
    return a + b;
}
```

Mas o computador não entende isso. Um programa chamado **compilador** traduz esse texto
para **código de máquina**: uma sequência de números que o processador executa
diretamente. Depois dessa tradução, o texto legível **é jogado fora**. O que sobra e é
distribuído — o arquivo `.exe` no Windows, o executável no Linux, o app no celular — é só
a versão em números.

Se você abrir esse arquivo num editor de texto, vê lixo:

```
7f 45 4c 46 02 01 01 00 00 00 00 00 55 48 89 e5 01 f7 89 f8 5d c3 ...
```

Aqueles `55 48 89 e5 01 f7 89 f8 5d c3` **são** a função `somar` acima. Mesma lógica,
forma ilegível. O nome `somar`, os nomes `a` e `b`, os comentários — tudo sumiu na tradução.

**Engenharia reversa de software é o trabalho de olhar esses números e reconstruir o que
o programa faz.** Não o texto original exato (esse não volta), mas uma compreensão
equivalente: "ah, essa parte pega dois números e soma".

### A analogia mais honesta: o relógio lacrado

Imagine um relógio de pulso **soldado, sem parafusos, que você não pode abrir sem
destruir**. Você quer saber como ele funciona. Pode:

- **Observar de fora** enquanto ele anda (que ponteiro se move, quando, em que ritmo);
- **Fazer um raio-X** para ver as engrenagens sem abrir;
- **Dar corda e cronometrar** para descobrir a relação entre as peças.

Na engenharia reversa de software esses três correspondem, respectivamente, a:

- **análise dinâmica** — rodar o programa e observar seu comportamento;
- **análise estática** — examinar o arquivo parado, sem executá-lo (o "raio-X");
- **instrumentação** — modificar o programa para que ele conte o que está fazendo.

Você vai aprender os três. (Definições formais em [`14-analise-estatica.md`](14-analise-estatica.md)
e [`15-analise-dinamica.md`](15-analise-dinamica.md).)

---

## Para que serve, na vida real

Engenharia reversa não é um truque de hacker de filme. É uma disciplina de engenharia com
usos legítimos e diários:

| Onde aparece | O que se faz | Exemplo concreto |
|---|---|---|
| **Segurança / antivírus** | Analisar um vírus para saber o que ele faz e como detê-lo | A empresa de antivírus reverte um ransomware para achar a falha que permite recuperar arquivos sem pagar |
| **Pesquisa de vulnerabilidades** | Achar falhas em programas sem ter o código | Descobrir que um roteador aceita uma senha secreta de fábrica |
| **Interoperabilidade** | Fazer um programa conversar com outro fechado | O LibreOffice consegue abrir arquivos `.docx` porque alguém reverteu o formato da Microsoft |
| **Compatibilidade / preservação** | Manter vivo software antigo cujo fabricante sumiu | Emuladores de videogames antigos; reviver um sistema bancário legado sem fonte |
| **Auditoria** | Verificar se um programa faz *só* o que promete | Confirmar que um app "de lanterna" não está roubando sua lista de contatos |
| **Diagnóstico** | Entender por que um sistema sem fonte quebra | Uma fábrica cujo software de controle de máquina travou e o fornecedor faliu |
| **Forense digital** | Reconstruir o que aconteceu num crime digital | Provar que um programa exfiltrou dados de uma empresa |

E, sim, também há o lado sombrio: **pirataria** (remover a proteção de licença de um
programa pago), **cheating** em jogos, e criação de malware. Este curso ensina a técnica —
que é a mesma para o bem e para o mal — e é claro sobre a lei (veja a seção final).

---

## "Mas isso não é ilegal?"

Depende **do quê você reverte, por quê, e onde você mora.** Resumo honesto (detalhes e
fontes na parte de ética/custos):

- **Reverter algo que é seu, ou feito para ser estudado** (crackmes, este curso, seu
  próprio código): **livre, sempre.** É o campo de treino legítimo.
- **Reverter para segurança e interoperabilidade**: **protegido por lei em muitos países.**
  Nos EUA há isenções específicas no DMCA §1201 para pesquisa de segurança de boa-fé
  (regra de 2024). Na União Europeia, a Diretiva 2009/24/CE permite descompilação para
  interoperabilidade. No **Brasil, a Lei 9.609/98 (Lei do Software) é omissa** sobre
  engenharia reversa — não proíbe explicitamente, mas também não protege como a lei europeia.
- **Reverter para pirataria** (quebrar licença de software pago para não pagar) ou
  **distribuir a versão quebrada**: **ilegal** na maioria das jurisdições, inclusive Brasil.
- **Contratos e EULAs** frequentemente proíbem engenharia reversa. Isso é uma restrição
  *contratual*, não penal — mas viola o acordo e pode gerar processo civil.

A regra de bolso deste curso: **estude a técnica em alvos que você tem direito de analisar.**
Há um mundo inteiro de crackmes, CTFs e binários abertos feitos exatamente para isso.

---

## O que a engenharia reversa **não** é

Desfazer mitos cedo economiza frustração:

- **Não é "descompilar e ter o código-fonte de volta".** Nomes, comentários e a estrutura
  original se perdem na compilação e **não voltam**. Um descompilador reconstrói *algo
  equivalente e legível*, não o original. (Por quê exatamente? Ver [`10-fundamentos.md`](10-fundamentos.md).)
- **Não é instantâneo nem automático.** Ferramentas modernas ajudam muito, mas reverter um
  programa grande é trabalho humano, lento, de detetive. Um malware sério pode levar
  semanas.
- **Não exige gênio, exige paciência e método.** É uma habilidade que se treina, como
  aprender um idioma. O idioma aqui é o **assembly** — a linguagem do processador.
- **Não é sempre possível quebrar proteções.** Alguns esquemas (criptografia bem-feita,
  código que roda em hardware seguro) são, na prática, impenetráveis. Reverter revela a
  *forma* da proteção, não garante *vencê-la*.

---

## Como este curso vai te levar lá

Você vai seguir exatamente o caminho do detetive:

1. **Entender como o "bolo" é feito** — como código vira binário ([`10`](10-fundamentos.md)).
2. **Aprender a linguagem do processador** — assembly x86-64 e ARM64 ([`12`](12-arquitetura-e-assembly.md)).
3. **Conhecer a embalagem** — os formatos ELF/PE/Mach-O ([`13`](13-formatos-de-binario.md)).
4. **Pegar as ferramentas** — Ghidra, GDB, radare2 e cia. ([`03`](03-instalacao.md), [`05`](05-manual-de-uso.md)).
5. **Reverter de verdade** — estática, dinâmica, exemplos, projeto ([`14`](14-analise-estatica.md)–[`07`](07-projeto-modelo/)).
6. **Enfrentar defesas** — ofuscação, anti-debug, packers ([`18`](18-ofuscacao-e-packers.md), [`19`](19-anti-analise.md)).
7. **Aplicar** — malware, vulns, firmware, mobile ([`20`](20-analise-de-malware.md)–[`23`](23-mobile-e-managed.md)).
8. **Chegar à fronteira** — teoria e IA que reverte binários ([`60`](60-teoria-avancada.md), [`65`](65-estado-da-arte.md)).

Se você só quer **sentir** como é antes de mergulhar, pule para
[`04-como-comecar.md`](04-como-comecar.md): em quinze minutos você reverte sua primeira
função. Mas volte aqui — a fundação importa.

---

## Autoteste

1. Explique, sem usar a palavra "código", por que um programa executável precisa ser
   "revertido" em vez de simplesmente lido.
2. O que **exatamente** se perde quando o código-fonte é compilado, e por isso não volta?
3. Dê um exemplo legítimo de engenharia reversa que beneficia diretamente um usuário comum.
4. Qual a diferença entre análise estática e análise dinâmica, na analogia do relógio lacrado?
5. Verdadeiro ou falso: "descompilar sempre devolve o código-fonte original". Justifique.
6. No Brasil, a Lei do Software proíbe engenharia reversa? Responda com precisão.
7. Cite duas coisas que a engenharia reversa **não** é, e por que o mito existe.

> Respostas conferíveis ao longo dos arquivos [`10`](10-fundamentos.md), [`14`](14-analise-estatica.md)
> e [`15`](15-analise-dinamica.md). Próximo passo: [`02-pre-requisitos.md`](02-pre-requisitos.md).
