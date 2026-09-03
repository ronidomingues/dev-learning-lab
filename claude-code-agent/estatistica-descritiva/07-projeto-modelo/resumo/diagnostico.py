"""A camada de honestidade: avisos sobre quando NÃO acreditar nas medidas.

Qualquer biblioteca calcula média e desvio padrão. O que este projeto tem de
diferente é este módulo: ele examina os dados e diz **quais medidas do
relatório não devem ser usadas** e por quê.

Cada aviso tem: gravidade, título, explicação e — obrigatoriamente — o que
fazer no lugar. Aviso que não diz o que fazer é ruído.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import medidas as M
from .formato import num, pct

__all__ = ["Aviso", "diagnosticar", "GRAVE", "ATENCAO", "NOTA"]

GRAVE = "GRAVE"
ATENCAO = "ATENÇÃO"
NOTA = "NOTA"

_ORDEM = {GRAVE: 0, ATENCAO: 1, NOTA: 2}


@dataclass
class Aviso:
    gravidade: str
    titulo: str
    detalhe: str
    acao: str

    def __str__(self):
        return f"[{self.gravidade}] {self.titulo}\n    {self.detalhe}\n    → {self.acao}"


def diagnosticar(valores, coluna=None):
    """Devolve a lista de avisos aplicáveis, do mais grave para o menos."""
    avisos = []
    n = len(valores)

    # ---------------------------------------------------- tamanho da amostra
    if n < 5:
        avisos.append(Aviso(
            GRAVE, f"amostra minúscula (n = {n})",
            "Com menos de 5 observações, praticamente nenhuma medida de "
            "dispersão ou forma é confiável; o intervalo de confiança fica "
            "largo a ponto de ser inútil.",
            "Relate os valores individuais em vez de resumi-los.",
        ))
    elif n < 30:
        avisos.append(Aviso(
            NOTA, f"amostra pequena (n = {n})",
            "Abaixo de ~30 observações o intervalo da média usa a t de "
            "Student, mais largo que a normal, e as medidas de forma "
            "(assimetria e curtose) têm erro padrão enorme.",
            "Este relatório já usa a t. Trate assimetria e curtose como "
            "indício, não como medição.",
        ))

    # -------------------------------------------------------- valores únicos
    distintos = len(set(valores))
    if distintos == 1:
        avisos.append(Aviso(
            GRAVE, "todos os valores são iguais",
            f"Todas as {n} observações valem {num(valores[0])}. Dispersão zero.",
            "Verifique se a coluna certa foi lida; dispersão zero em dado "
            "real quase sempre significa erro de extração.",
        ))
        return avisos
    if distintos <= 10 and n >= 30:
        avisos.append(Aviso(
            ATENCAO, f"poucos valores distintos ({distintos})",
            "Dados com pouquíssimos valores distintos costumam ser "
            "categóricos ou ordinais (nota de 1 a 5, escala Likert, "
            "contagem pequena) disfarçados de número.",
            "Se for escala ordinal, média e desvio padrão não têm "
            "significado definido: use mediana, moda e a distribuição de "
            "frequências.",
        ))

    if n < 3:
        return sorted(avisos, key=lambda a: _ORDEM[a.gravidade])

    media = M.media(valores)
    mediana = M.mediana(valores)
    dp = M.desvio_padrao(valores)
    todos_positivos = all(v > 0 for v in valores)

    # ------------------------------------------------------------ assimetria
    if mediana != 0:
        razao = media / mediana
        if razao > 1.2 or razao < 0.833:
            lado = "à direita" if razao > 1 else "à esquerda"
            avisos.append(Aviso(
                GRAVE, f"distribuição assimétrica {lado} (média/mediana = {num(razao)})",
                f"Média = {num(media)} e mediana = {num(mediana)}. Quando as "
                "duas divergem tanto, a média deixa de descrever o caso "
                "típico: ela é puxada pelos valores extremos.",
                "Relate a MEDIANA como valor típico. Use a média apenas se a "
                "pergunta for sobre o TOTAL (folha, faturamento, carga).",
            ))

    # --------------------------------------------------------- dispersão alta
    if todos_positivos and dp > media:
        avisos.append(Aviso(
            GRAVE, "desvio padrão maior que a média",
            f"DP = {num(dp)} contra média = {num(media)} (CV = {num(dp/media)}). "
            "Em dados estritamente positivos isso indica cauda pesada ou "
            "outliers dominantes.",
            "Considere escala logarítmica, ou relate mediana e IQR. "
            "Um intervalo média ± DP aqui incluiria valores negativos, "
            "que são impossíveis nesta variável.",
        ))

    # ------------------------------------------------- normalidade na prática
    cobertura = M.cobertura_1dp(valores)
    if n >= 20 and not (0.60 <= cobertura <= 0.76):
        avisos.append(Aviso(
            ATENCAO, f"a regra dos 68% não vale aqui (cobertura real: {pct(cobertura, 0)})",
            "Numa distribuição normal, ~68% das observações caem a menos de "
            f"1 desvio padrão da média. Aqui caem {pct(cobertura, 0)}.",
            "Não use 'média ± 2 DP' como faixa de 95%. Use percentis "
            "empíricos (p2,5 e p97,5), que não supõem formato nenhum.",
        ))

    # --------------------------------------------------------------- outliers
    q1, _, q3 = M.quartis(valores)
    faixa = q3 - q1
    if faixa > 0:
        lo, hi = q1 - 1.5 * faixa, q3 + 1.5 * faixa
        fora = [v for v in valores if v < lo or v > hi]
        if fora:
            prop = len(fora) / n
            grav = GRAVE if prop > 0.05 else ATENCAO
            avisos.append(Aviso(
                grav, f"{len(fora)} valor(es) fora da cerca de 1,5×IQR ({pct(prop)})",
                f"Cerca: [{num(lo)} ; {num(hi)}]. Extremos observados: "
                + ", ".join(num(v) for v in sorted(fora)[:5])
                + ("…" if len(fora) > 5 else ""),
                "A cerca marca CANDIDATOS, não erros. Investigue a origem de "
                "cada um antes de qualquer decisão; nunca remova por remover.",
            ))

    # --------------------------------------------------------- sinais suspeitos
    if any(v < 0 for v in valores) and any(v > 0 for v in valores):
        avisos.append(Aviso(
            NOTA, "há valores positivos e negativos",
            "O coeficiente de variação não tem interpretação quando a "
            "variável muda de sinal, e a média pode ficar perto de zero por "
            "cancelamento, inflando artificialmente o CV.",
            "Ignore o CV nesta coluna.",
        ))

    zeros = sum(1 for v in valores if v == 0)
    if zeros and zeros / n > 0.20:
        avisos.append(Aviso(
            ATENCAO, f"{zeros} zeros ({pct(zeros/n, 0)} dos dados)",
            "Excesso de zeros muitas vezes significa duas populações "
            "misturadas (quem não usou e quem usou) ou ausência codificada "
            "como zero.",
            "Verifique se zero significa 'nenhum' ou 'não medido'. Se forem "
            "duas populações, descreva-as separadamente.",
        ))

    # ------------------------------------------------------- arredondamento
    inteiros = sum(1 for v in valores if float(v).is_integer())
    if n >= 20 and inteiros == n:
        multiplos = [10, 5]
        for m in multiplos:
            k = sum(1 for v in valores if v % m == 0)
            if k / n > 0.8:
                avisos.append(Aviso(
                    NOTA, f"{pct(k/n, 0)} dos valores são múltiplos de {m}",
                    "Concentração em números redondos indica arredondamento "
                    "na coleta (heaping) — típico de idade autodeclarada, "
                    "estimativas de tempo e valores 'de cabeça'.",
                    "A precisão real dos dados é menor que a exibida; "
                    "arredonde os resultados de acordo.",
                ))
                break

    return sorted(avisos, key=lambda a: _ORDEM[a.gravidade])
