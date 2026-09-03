// Erros de domínio com código estável. O código é o que o HTTP mapeia;
// a mensagem é para humanos e pode mudar sem quebrar cliente nenhum.
export class ErroDominio extends Error {
  constructor(codigo, mensagem, status = 400) {
    super(mensagem);
    this.name = "ErroDominio";
    this.codigo = codigo;
    this.status = status;
  }
}

export const erroValidacao = (msg) => new ErroDominio("validacao", msg, 400);
export const erroSlugEmUso = (slug) => new ErroDominio("slug_em_uso", `o apelido "${slug}" já existe`, 409);
export const erroNaoEncontrado = () => new ErroDominio("nao_encontrado", "link não encontrado", 404);
export const erroLimite = (retryAfter) => {
  const e = new ErroDominio("limite_excedido", "muitas requisições", 429);
  e.retryAfter = retryAfter;
  return e;
};
