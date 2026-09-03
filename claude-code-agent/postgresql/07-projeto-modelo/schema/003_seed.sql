-- 003_seed.sql — dados de exemplo, para o banco não nascer vazio.
-- Roda depois do 001 e 002. Idempotente: limpa antes (as tabelas foram recriadas no 001).

BEGIN;

INSERT INTO autores (nome, nascimento) VALUES
    ('Machado de Assis', '1839-06-21'),
    ('Clarice Lispector', '1920-12-10'),
    ('Graciliano Ramos',  '1892-10-27');

INSERT INTO livros (isbn, titulo, ano, dados) VALUES
    ('978-8535910663', 'Dom Casmurro',        1899, '{"genero":"romance","idioma":"pt"}'),
    ('978-8520925157', 'A Hora da Estrela',   1977, '{"genero":"novela","idioma":"pt"}'),
    (NULL,             'Vidas Secas',         1938, '{"genero":"romance","idioma":"pt"}'),
    ('978-8535914849', 'Memórias Póstumas',   1881, '{"genero":"romance","idioma":"pt"}');

-- Ligações livro–autor (usando subconsultas para não depender dos ids gerados)
INSERT INTO livros_autores (livro_id, autor_id)
SELECT l.id, a.id FROM livros l, autores a
WHERE (l.titulo = 'Dom Casmurro'      AND a.nome = 'Machado de Assis')
   OR (l.titulo = 'Memórias Póstumas' AND a.nome = 'Machado de Assis')
   OR (l.titulo = 'A Hora da Estrela' AND a.nome = 'Clarice Lispector')
   OR (l.titulo = 'Vidas Secas'       AND a.nome = 'Graciliano Ramos');

-- Exemplares físicos (alguns títulos têm mais de uma cópia)
INSERT INTO exemplares (livro_id, codigo)
SELECT l.id, 'BIB-' || lpad((row_number() OVER ())::text, 6, '0')
FROM livros l
CROSS JOIN generate_series(1, 2) AS copia;   -- 2 exemplares por livro

INSERT INTO membros (nome, email) VALUES
    ('Ana Souza',   'ana@exemplo.com'),
    ('Bruno Lima',  'bruno@exemplo.com'),
    ('Carla Nunes', 'carla@exemplo.com');

COMMIT;
