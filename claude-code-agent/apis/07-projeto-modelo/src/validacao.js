/**
 * Validador de um subconjunto do JSON Schema (draft 2020-12).
 *
 * Em produção, use Ajv: é completo, rápido e compila o schema para JavaScript.
 * Este validador existe para o projeto ser executável sem `npm install`, e para
 * você ver que "validação por schema" não é mágica.
 *
 * Cobre: type, required, additionalProperties, properties, enum, const,
 *        minLength, maxLength, pattern, format(date|date-time), minimum,
 *        maximum, minItems, maxItems, items, nullable.
 */

const FORMATOS = {
  'date':      /^\d{4}-\d{2}-\d{2}$/,
  'date-time': /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/,
  'uuid':      /^[0-9a-f]{8}-[0-9a-f]{4}-[1-9a-f][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
};

function tipoDe(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  if (Number.isInteger(v)) return 'integer';
  return typeof v;
}

/**
 * @returns {Array<{campo: string, motivo: string}>} lista vazia se válido
 */
export function validar(dados, esquema, caminho = '') {
  const erros = [];
  const rotulo = caminho || '(raiz)';
  const filho = c => (caminho ? `${caminho}.${c}` : c);

  if (esquema.nullable && dados === null) return erros;

  // --- type ---
  if (esquema.type) {
    const tipos = Array.isArray(esquema.type) ? esquema.type : [esquema.type];
    const real = tipoDe(dados);
    // "integer" também satisfaz "number"
    const casa = tipos.some(t => t === real || (t === 'number' && real === 'integer'));
    if (!casa) {
      erros.push({ campo: rotulo, motivo: `deve ser ${tipos.join(' ou ')}, veio ${real}` });
      return erros;   // sem o tipo certo, as demais regras não fazem sentido
    }
  }

  // --- const / enum ---
  if ('const' in esquema && dados !== esquema.const) {
    erros.push({ campo: rotulo, motivo: `deve ser exatamente ${JSON.stringify(esquema.const)}` });
  }
  if (esquema.enum && !esquema.enum.includes(dados)) {
    erros.push({ campo: rotulo, motivo: `deve ser um de: ${esquema.enum.join(', ')}` });
  }

  // --- object ---
  if (tipoDe(dados) === 'object') {
    for (const obrigatorio of esquema.required ?? []) {
      if (dados[obrigatorio] === undefined) {
        erros.push({ campo: filho(obrigatorio), motivo: 'campo obrigatório' });
      }
    }
    if (esquema.additionalProperties === false) {
      for (const chave of Object.keys(dados)) {
        if (!esquema.properties?.[chave]) {
          erros.push({ campo: filho(chave), motivo: 'campo não reconhecido' });
        }
      }
    }
    for (const [chave, sub] of Object.entries(esquema.properties ?? {})) {
      if (dados[chave] !== undefined) {
        erros.push(...validar(dados[chave], sub, filho(chave)));
      }
    }
  }

  // --- string ---
  if (typeof dados === 'string') {
    if (esquema.minLength != null && dados.length < esquema.minLength) {
      erros.push({ campo: rotulo, motivo: `mínimo de ${esquema.minLength} caractere(s)` });
    }
    if (esquema.maxLength != null && dados.length > esquema.maxLength) {
      erros.push({ campo: rotulo, motivo: `máximo de ${esquema.maxLength} caracteres` });
    }
    if (esquema.pattern && !new RegExp(esquema.pattern).test(dados)) {
      erros.push({ campo: rotulo, motivo: 'formato inválido' });
    }
    if (esquema.format && FORMATOS[esquema.format] && !FORMATOS[esquema.format].test(dados)) {
      erros.push({ campo: rotulo, motivo: `deve estar no formato ${esquema.format}` });
    }
  }

  // --- number / integer ---
  if (typeof dados === 'number') {
    if (esquema.minimum != null && dados < esquema.minimum) {
      erros.push({ campo: rotulo, motivo: `mínimo ${esquema.minimum}` });
    }
    if (esquema.maximum != null && dados > esquema.maximum) {
      erros.push({ campo: rotulo, motivo: `máximo ${esquema.maximum}` });
    }
  }

  // --- array ---
  if (Array.isArray(dados)) {
    if (esquema.minItems != null && dados.length < esquema.minItems) {
      erros.push({ campo: rotulo, motivo: `mínimo de ${esquema.minItems} item(ns)` });
    }
    if (esquema.maxItems != null && dados.length > esquema.maxItems) {
      erros.push({ campo: rotulo, motivo: `máximo de ${esquema.maxItems} itens` });
    }
    if (esquema.items) {
      dados.forEach((item, i) => erros.push(...validar(item, esquema.items, `${caminho}[${i}]`)));
    }
  }

  return erros;
}
