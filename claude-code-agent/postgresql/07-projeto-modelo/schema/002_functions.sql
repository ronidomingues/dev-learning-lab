-- 002_functions.sql — lógica de negócio que faz sentido viver no banco.
--
-- Debate honesto (ver README): lógica no banco é atômica e à prova de "a aplicação esqueceu",
-- mas é invisível para quem lê só o código da aplicação. Aqui usamos funções para as regras
-- que se BENEFICIAM de rodar dentro da mesma transação, atômicas por natureza.

BEGIN;

-- ---------------------------------------------------------------------------
-- Emprestar um exemplar a um membro, com todas as regras verificadas.
-- Retorna o id do empréstimo criado, ou levanta um erro claro.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION emprestar(
    p_exemplar_id BIGINT,
    p_membro_id   BIGINT,
    p_dias        INTEGER DEFAULT 14
) RETURNS BIGINT
LANGUAGE plpgsql AS $$
DECLARE
    v_id           BIGINT;
    v_aposentado   BOOLEAN;
    v_membro_ativo BOOLEAN;
BEGIN
    -- Trava a linha do exemplar durante a transação: dois empréstimos simultâneos
    -- do mesmo exemplar serializam aqui, e o segundo verá o primeiro.
    SELECT aposentado INTO v_aposentado
    FROM exemplares WHERE id = p_exemplar_id FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'exemplar % não existe', p_exemplar_id
            USING ERRCODE = 'no_data_found';
    END IF;
    IF v_aposentado THEN
        RAISE EXCEPTION 'exemplar % está aposentado', p_exemplar_id;
    END IF;

    SELECT ativo INTO v_membro_ativo FROM membros WHERE id = p_membro_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'membro % não existe', p_membro_id;
    END IF;
    IF NOT v_membro_ativo THEN
        RAISE EXCEPTION 'membro % está inativo', p_membro_id;
    END IF;

    -- Se o exemplar já estiver emprestado, o índice único parcial rejeita o INSERT.
    -- Capturamos para dar uma mensagem melhor que o erro cru de constraint.
    BEGIN
        INSERT INTO emprestimos (exemplar_id, membro_id, vence_em)
        VALUES (p_exemplar_id, p_membro_id, current_date + p_dias)
        RETURNING id INTO v_id;
    EXCEPTION WHEN unique_violation THEN
        RAISE EXCEPTION 'exemplar % já está emprestado', p_exemplar_id
            USING ERRCODE = 'exclusion_violation';
    END;

    RETURN v_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- Devolver um exemplar. Retorna true se estava emprestado; false se não havia
-- empréstimo em aberto (idempotente: devolver duas vezes não quebra).
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION devolver(p_exemplar_id BIGINT)
RETURNS BOOLEAN
LANGUAGE plpgsql AS $$
DECLARE v_id BIGINT;
BEGIN
    UPDATE emprestimos
    SET devolvido_em = now()
    WHERE exemplar_id = p_exemplar_id AND devolvido_em IS NULL
    RETURNING id INTO v_id;

    RETURN FOUND;   -- true se atualizou alguma linha
END;
$$;

-- ---------------------------------------------------------------------------
-- Empréstimos vencidos e não devolvidos, com dias de atraso.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION emprestimos_atrasados()
RETURNS TABLE (
    emprestimo_id BIGINT,
    membro        TEXT,
    titulo        TEXT,
    vence_em      DATE,
    dias_atraso   INTEGER
)
LANGUAGE sql STABLE AS $$
    SELECT
        em.id,
        m.nome,
        l.titulo,
        em.vence_em,
        (current_date - em.vence_em)::int
    FROM emprestimos em
    JOIN membros    m ON m.id = em.membro_id
    JOIN exemplares e ON e.id = em.exemplar_id
    JOIN livros     l ON l.id = e.livro_id
    WHERE em.devolvido_em IS NULL
      AND em.vence_em < current_date
    ORDER BY em.vence_em;
$$;

COMMIT;
