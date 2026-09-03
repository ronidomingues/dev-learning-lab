/**
 * Os schemas de entrada. UMA fonte da verdade.
 *
 * Estes mesmos objetos aparecem no openapi.yaml. Se você mudar aqui e esquecer lá,
 * o teste `contrato cobre todas as rotas` (test/api.test.js) reclama.
 */

const ANO_MAXIMO = new Date().getUTCFullYear() + 1;

/** ISBN-13 com ou sem hífens. */
const PADRAO_ISBN13 = '^97[89](-?\\d){10}$';

export const CriarLivro = {
  type: 'object',
  required: ['titulo', 'autor'],
  // Rejeitar campo desconhecido pega erro de digitação do cliente na hora,
  // em vez de ignorar em silêncio. O custo: adicionar campo novo exige atenção
  // à compatibilidade — ver 18-operacao-e-ciclo-de-vida.md §5.
  additionalProperties: false,
  properties: {
    titulo: { type: 'string', minLength: 1,  maxLength: 200 },
    autor:  { type: 'string', minLength: 1,  maxLength: 120 },
    ano:    { type: 'integer', minimum: 1450, maximum: ANO_MAXIMO },
    isbn:   { type: 'string', pattern: PADRAO_ISBN13 }
  }
};

/** PATCH: todos os campos opcionais, mas ao menos um precisa vir. */
export const AtualizarLivro = {
  type: 'object',
  additionalProperties: false,
  minProperties: 1,
  properties: {
    titulo: { type: 'string', minLength: 1,  maxLength: 200 },
    autor:  { type: 'string', minLength: 1,  maxLength: 120 },
    ano:    { type: 'integer', minimum: 1450, maximum: ANO_MAXIMO },
    isbn:   { type: 'string', pattern: PADRAO_ISBN13 }
  }
};

export const CriarEmprestimo = {
  type: 'object',
  required: ['livro_id', 'pessoa'],
  additionalProperties: false,
  properties: {
    livro_id: { type: 'string', format: 'uuid' },
    pessoa:   { type: 'string', minLength: 2, maxLength: 120 }
  }
};

export const ANO_MAXIMO_PERMITIDO = ANO_MAXIMO;
