# 06 · Exercícios — do reproduzir ao investigar

`Nível: iniciante → pesquisa` · `Atualizado em: 19/08/2026`

Quatro níveis. Faça na ordem: cada um pressupõe o anterior.
Todos os comandos assumem que você está em `08-projeto-espacial/` com o ambiente
do [`requirements.txt`](requirements.txt) instalado.

---

## Nível 1 · Reproduzir (2 h)

Objetivo: confirmar que tudo funciona e que você sabe ler a saída.

**1.1** Rode a suíte e confirme 56 testes OK.

```bash
python -m unittest discover -s tests -v
```

**1.2** Reproduza os quatro pipelines e confira, um a um, os números da
[tabela-resumo do `04`](04-resultados-e-validacao.md#7--tabela-resumo-da-validação).

**1.3** Calcule à mão, com calculadora, e confirme contra o programa:
- a potência de ruído de um sistema com T_sys = 45 K e B = 250 MHz;
- o atraso de dispersão para DM = 120, entre 1200 e 1500 MHz;
- o desvio Doppler em banda Ka (32 GHz) para 15 km/s.

**1.4** Gere as figuras e explique, por escrito, o que cada uma mostra:

```bash
python -m cosmos pulsar --figuras saida/
python -m cosmos enlace --figuras saida/
```

**1.5** Na cascata (`cascata.png`), identifique visualmente a curva de dispersão.
Ela é mais inclinada em que ponta da banda? Por quê?

---

## Nível 2 · Variar e prever (4 h)

Objetivo: **prever antes de rodar**. Escreva sua previsão, depois execute.

**2.1** Sem rodar, preveja a SNR se a duração passar de 60 s para 15 s. Verifique:

```bash
python -m cosmos pulsar --duracao 15
```

**2.2** Idem para 16 canais em vez de 64. Compare com a previsão √n — e leia a
[§6 do `04`](04-resultados-e-validacao.md) antes de concluir que o código está errado.

**2.3** Encontre empiricamente a **amplitude mínima detectável** (limiar de 8 σ)
com os parâmetros padrão. Faça uma bissecção com `--amplitude`.

**2.4** Rode com `--dm 200` mantendo 64 canais. O que o programa avisa?
Confirme com `python -m cosmos dispersao --dm 200`. Quantos canais seriam
necessários para esse DM?

**2.5** Aumente a grade de DM para passo 0,5 (`--dm-passo 0.5`). O melhor DM fica
mais perto de 50? E o que acontece com o número de tentativas independentes e com
o limiar exigido? Há um custo em refinar a grade — descreva-o.

**2.6** No enlace, encontre o limiar de SNR para M = 1, 2, 4, 8, 16 períodos.
Trace a curva. Ela segue √M? Justifique com a §6 do [`02`](02-a-fisica-do-sinal.md).

---

## Nível 3 · Estender o código (10–20 h)

Objetivo: escrever código novo que se integra ao existente, com teste.

**3.1 · Busca 2-D (DM × período).**
O `buscar_dm` fixa o período e o `buscar_periodo` fixa o DM. Implemente
`buscar_2d` que varre os dois e devolve o plano completo. Meça o custo em função
do tamanho das grades e confirme que ele é o produto. Gere um mapa de calor.

**3.2 · Excisão de RFI.**
Acrescente ao sintetizador uma opção de injetar interferência:
(a) banda estreita e persistente (uma linha horizontal na cascata);
(b) banda larga e impulsiva (uma linha vertical).
Depois implemente a defesa: mascarar canais cuja variância seja anômala
(critério robusto, com mediana e MAD) e zerar amostras de tempo saturadas.
**Meça quanto a SNR se recupera.** Este exercício é o mais próximo do trabalho
real de quem opera um radiotelescópio.

**3.3 · Interpolação do pico de DM.**
Ajuste uma parábola aos três pontos em torno do máximo da curva SNR × DM e
devolva o DM com barra de erro. Compare com o valor verdadeiro em 20 realizações
e verifique se o erro estimado é honesto (o verdadeiro cai dentro da barra em
~68 % dos casos?).

**3.4 · Filtro casado em fase.**
O `snr_perfil` usa o **pico** de um bin. Implemente a alternativa correta:
correlacionar o perfil com um modelo do formato do pulso (filtro casado) e usar o
máximo dessa correlação. Isso deve recuperar parte dos ~10 % de déficit
identificados na [§6 do `04`](04-resultados-e-validacao.md). Meça.

**3.5 · Aquisição coerente.**
Implemente `adquirir_coerente`, que soma os **complexos** em vez dos módulos.
Mostre com um experimento em que caso ela ganha (Doppler bem estimado) e em que
caso ela **perde feio** para a não coerente (Doppler residual de alguns hertz).

**3.6 · Rastreamento em malha fechada.**
Substitua a estimativa em bloco de `estimar_deriva` por um PLL de segunda ordem
que rastreia continuamente. Compare o erro de frequência ao longo do tempo entre
os dois métodos, com uma rampa Doppler realista.

**3.7 · Dedispersão coerente.**
Implemente a versão que corrige a **fase** no domínio da frequência, num sinal
complexo de banda base, e mostre que ela não sofre o borrão intracanal. Compare
com a incoerente para um DM alto e canais largos. É o exercício mais difícil da
lista e o mais próximo de pesquisa.

---

## Nível 4 · Investigar (aberto)

Objetivo: fazer o que não tem resposta no fim do livro.

**4.1 · Dados reais de pulsar.**
Baixe parâmetros do **ATNF Pulsar Catalogue** e alimente o simulador com P e DM
de pulsares verdadeiros (por exemplo, o B0329+54, brilhante e clássico). Que
tempo de integração seria necessário para detectá-lo com um radiotelescópio
amador de 3 m? Use a equação do radiômetro e seja honesto sobre as hipóteses.

**4.2 · O piso do estimador.**
A [§6 do `04`](04-resultados-e-validacao.md) mediu piso de 3,22 σ para 64 bins de
fase. **Derive a expressão teórica** do valor esperado do máximo de n amostras
gaussianas (dica: estatística de valores extremos, distribuição de Gumbel) e
compare com a medida para n = 16, 32, 64, 128, 256. O acordo é bom?

**4.3 · Quanto custa uma busca de verdade.**
Estime o custo computacional de varrer 5 000 DMs sobre 1 hora de dados do CHIME
(16 384 canais, 1 ms). Quantas operações? Quanto tempo numa CPU? E por que se usa
FPGA? Compare com o custo do `plano_dm_tempo` deste projeto, extrapolado.

**4.4 · Ruído não gaussiano.**
Substitua o ruído gaussiano por uma distribuição de cauda pesada (t de Student
com poucos graus de liberdade). Meça como a taxa de falso alarme **real** se
afasta da prevista pela teoria gaussiana do `deteccao.py`. Quanto de sigma a mais
seria preciso exigir para manter a mesma taxa? Este é o motivo prático de as
buscas reais exigirem 8–10 σ.

**4.5 · Injeção cega.**
Peça a alguém que rode o sintetizador com parâmetros secretos (ou nenhum sinal!)
e lhe entregue só o arquivo. Você consegue recuperar P e DM sem saber a resposta —
e consegue dizer **"não há sinal"** quando não há? A segunda parte é a mais
difícil, e é o teste que colaborações reais aplicam a si mesmas.

**4.6 · Um sinal artificial.**
Se uma civilização quisesse ser encontrada, que sinal enviaria? Argumente em
termos do que este projeto ensina: banda estreita (ganho por integração
coerente) ou banda larga com código (ganho por correlação)? Que suposições cada
escolha faz sobre o receptor? Compare com a estratégia real do SETI e do Breakthrough
Listen.

---

## Como saber que você aprendeu

Você entendeu este projeto se conseguir, sem consultar:

- [ ] explicar por que a SNR cresce com √N, e citar quatro formas diferentes de
      obter esse N nos quatro pipelines;
- [ ] estimar o tempo de telescópio necessário para uma observação, à mão;
- [ ] explicar como um atraso de chegada vira uma medida de distância;
- [ ] dizer por que um candidato com melhor DM igual a zero é suspeito;
- [ ] explicar por que "5 sigma" pode não significar nada;
- [ ] dizer onde está o fator ½ da rampa Doppler e o que acontece sem ele;
- [ ] explicar por que se soma módulos e não complexos na aquisição a frio;
- [ ] descrever o que é uma injeção cega e por que ela existe.

---

## Se travar

| Sintoma | Onde olhar |
|---|---|
| não entendi a física | [`02-a-fisica-do-sinal.md`](02-a-fisica-do-sinal.md) |
| não entendi uma linha de código | [`03-o-codigo-linha-a-linha.md`](03-o-codigo-linha-a-linha.md) |
| meu número não bate | [`04-resultados-e-validacao.md`](04-resultados-e-validacao.md), tabela final |
| falta base de DSP | [`../00-MAPA.md`](../00-MAPA.md) — capítulos 10 a 20 |
| falta a matemática | [`../12-matematica-do-zero.md`](../12-matematica-do-zero.md) |
