-- ============================================================================
-- 003-seed-cadastro.sql — Dados mestres (cadastro) da planta fictícia
--
-- Planta: unidade de resina alquídica em batelada.
--   Área 100 — reação        (T-101 tanque de carga, R-101 reator, P-301 bomba)
--   Área 200 — utilidades    (E-201 trocador de calor / água de resfriamento)
--   Área 400 — acabamento    (C-401 centrífuga)
--
-- A nomenclatura dos tags segue a ISA-5.1 (a norma que define os símbolos de
-- P&ID): primeira letra = grandeza medida, segunda = função do instrumento.
--   T I -101  →  Temperature Indicator, malha 101
--   P I -101  →  Pressure Indicator
--   F I -102  →  Flow Indicator
--   L I -101  →  Level Indicator
--   S I -101  →  Speed Indicator
--   A I -101  →  Analyzer Indicator (aqui, pH)
-- ============================================================================

INSERT INTO equipamento (equipamento_id, nome, tipo, area, capacidade_kg) VALUES
  ('T-101', 'Tanque de carga de matérias-primas', 'tanque',     '100', 20000.0),
  ('R-101', 'Reator de resina alquídica',          'reator',     '100',  6000.0),
  ('P-301', 'Bomba de transferência',              'bomba',      '100',   NULL),
  ('E-201', 'Trocador de calor — água gelada',     'trocador',   '200',   NULL),
  ('C-401', 'Centrífuga de acabamento',            'centrifuga', '400',  1500.0);

INSERT INTO tag
  (tag_id, equipamento_id, descricao, grandeza, unidade,
   lim_inf_op, lim_sup_op, lim_inf_alarme, lim_sup_alarme, periodo_s) VALUES
  -- Tags do reator: são estes que se ligam à batelada.
  ('TI-101', 'R-101', 'Temperatura da massa reacional', 'temperatura', 'degC',
     30.0, 190.0,   5.0, 195.0, 60),
  ('PI-101', 'R-101', 'Pressão no topo do reator',       'pressao',     'bar',
      0.3,   3.2,   0.1,   3.3, 60),
  ('LI-101', 'R-101', 'Nível do reator',                 'nivel',       '%',
      0.0,  90.0,  NULL,  95.0, 60),
  ('SI-101', 'R-101', 'Rotação do agitador',             'rotacao',     'rpm',
      0.0, 100.0,  NULL, 110.0, 60),
  ('AI-101', 'R-101', 'pH da massa reacional',           'ph',          'pH',
      4.5,   7.5,   4.5,   8.0, 60),
  ('FI-102', 'R-101', 'Vazão de alimentação T-101→R-101','vazao',       'kg/h',
      0.0, 8000.0, NULL, 9000.0, 60),
  -- Tags de utilidade: NÃO pertencem ao reator, e por isso não aparecem na
  -- view v_leitura_batelada. Isso é de propósito — ver o README.
  ('TI-201', 'E-201', 'Temperatura de saída da água',    'temperatura', 'degC',
     20.0,  45.0,  NULL,  50.0, 60),
  ('FI-201', 'E-201', 'Vazão de água de resfriamento',   'vazao',       'kg/h',
      0.0, 20000.0, 2000.0, NULL, 60);
