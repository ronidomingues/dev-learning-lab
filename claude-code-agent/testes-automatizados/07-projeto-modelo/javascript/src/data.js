/**
 * Datas de calendário como texto ISO-8601 (`"2026-08-12"`).
 *
 * Por que não usar `Date` direto? Cinco porquês, até a parada legítima:
 *
 * 1. Por que não `new Date("2026-08-12")`? Porque isso é interpretado como
 *    **meia-noite UTC**, mas `getDate()` devolve o dia no fuso **local**.
 *    Em São Paulo (UTC-3), `new Date("2026-08-12").getDate()` dá **11**.
 * 2. Por que a especificação faz isso? Porque `Date` é um instante (milissegundos
 *    desde 1970), não uma data de calendário. "12 de agosto" não é um instante.
 * 3. Por que `Date` só sabe instantes? Porque foi copiada às pressas da
 *    `java.util.Date` do Java 1.0 em maio de 1995, em dez dias de trabalho de
 *    Brendan Eich — decisão histórica documentada, nunca corrigida por
 *    compatibilidade retroativa da web.
 * 4. Por que não corrigiram? Porque mudar o comportamento de `Date` quebraria
 *    uma fração incalculável dos sites existentes. A web não versiona.
 * 5. E a solução oficial? A proposta **Temporal** (`Temporal.PlainDate`), que
 *    resolve exatamente isso. Em 12/08/2026 ela ainda não está disponível no
 *    Node 24 (`typeof Temporal === "undefined"`), então este módulo existe.
 *
 * Enquanto Temporal não chegar: guardamos texto ISO e fazemos a aritmética em
 * UTC explícito. Ordem lexicográfica de `"AAAA-MM-DD"` == ordem cronológica,
 * o que dá comparação e ordenação de graça.
 */

const FORMATO = /^(\d{4})-(\d{2})-(\d{2})$/;

export class DataInvalida extends Error {
  constructor(mensagem) {
    super(mensagem);
    this.name = 'DataInvalida';
  }
}

/** Valida e normaliza uma data ISO. Devolve a própria string. */
export function data(iso) {
  const casa = FORMATO.exec(iso);
  if (!casa) throw new DataInvalida(`data fora do formato AAAA-MM-DD: ${iso}`);
  const [, ano, mes, dia] = casa.map(Number);
  const utc = new Date(Date.UTC(ano, mes - 1, dia));
  // Detecta datas impossíveis como "2026-02-30", que o Date "conserta" em silêncio.
  if (
    utc.getUTCFullYear() !== ano ||
    utc.getUTCMonth() !== mes - 1 ||
    utc.getUTCDate() !== dia
  ) {
    throw new DataInvalida(`data inexistente no calendário: ${iso}`);
  }
  return iso;
}

/** Sempre UTC — nunca `new Date(iso)` sem hora, nunca `getDate()`. */
function paraUtc(iso) {
  const [ano, mes, dia] = data(iso).split('-').map(Number);
  return Date.UTC(ano, mes - 1, dia);
}

const UM_DIA = 86_400_000;

export function somarDias(iso, dias) {
  if (!Number.isInteger(dias)) throw new DataInvalida('dias deve ser inteiro');
  const d = new Date(paraUtc(iso) + dias * UM_DIA);
  const mes = String(d.getUTCMonth() + 1).padStart(2, '0');
  const dia = String(d.getUTCDate()).padStart(2, '0');
  return `${d.getUTCFullYear()}-${mes}-${dia}`;
}

export function diferencaEmDias(a, b) {
  return Math.round((paraUtc(a) - paraUtc(b)) / UM_DIA);
}

/** -1, 0 ou 1. Como ISO ordena lexicograficamente, dá para comparar direto. */
export function comparar(a, b) {
  data(a);
  data(b);
  return a < b ? -1 : a > b ? 1 : 0;
}

export function formatarBr(iso) {
  const [ano, mes, dia] = data(iso).split('-');
  return `${dia}/${mes}/${ano}`;
}
