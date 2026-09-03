#!/usr/bin/env node
// Valida a configuração de Claude Code deste repositório e roda a suíte.
//
// Por que isto existe: configuração de agente é código que ninguém compila.
// Um JSON com vírgula sobrando, um hook sem bit de execução ou um caminho errado
// falham em silêncio no meio de uma sessão — e você culpa o modelo.
// Este script transforma esse silêncio em erro.
//
// Zero dependências. Uso: npm run verificar

import { readFileSync, existsSync, accessSync, constants, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const problemas = [];
const oks = [];

const erro = (m) => problemas.push(m);
const ok = (m) => oks.push(m);

// ---------------------------------------------------------------- 1. arquivos
const OBRIGATORIOS = [
  'CLAUDE.md',
  '.claude/settings.json',
  '.claude/rules/testes.md',
  '.claude/agents/revisor-api.md',
  '.claude/skills/novo-endpoint/SKILL.md',
  '.claude/skills/checar-tudo/SKILL.md',
  '.claude/commands/rotas.md',
  'src/tarefas.js',
  'src/servidor.js',
];
for (const rel of OBRIGATORIOS) {
  if (existsSync(join(RAIZ, rel))) ok(`arquivo presente: ${rel}`);
  else erro(`arquivo ausente: ${rel}`);
}

// ------------------------------------------------------- 2. settings.json é JSON
let settings = null;
try {
  settings = JSON.parse(readFileSync(join(RAIZ, '.claude/settings.json'), 'utf8'));
  ok('.claude/settings.json é JSON válido');
} catch (e) {
  erro(`.claude/settings.json não é JSON válido: ${e.message}`);
}

// -------------------------------------- 3. hooks: caminho existe e é executável
if (settings?.hooks) {
  let total = 0;
  for (const [evento, grupos] of Object.entries(settings.hooks)) {
    for (const grupo of grupos) {
      for (const h of grupo.hooks ?? []) {
        if (h.type !== 'command') continue;
        total++;
        const caminho = h.command.replace('${CLAUDE_PROJECT_DIR}', RAIZ);
        if (!existsSync(caminho)) {
          erro(`hook ${evento}: arquivo não existe → ${h.command}`);
          continue;
        }
        try {
          accessSync(caminho, constants.X_OK);
        } catch {
          erro(`hook ${evento}: sem bit de execução → chmod +x ${h.command}`);
        }
        if (!readFileSync(caminho, 'utf8').startsWith('#!')) {
          erro(`hook ${evento}: falta shebang (#!/usr/bin/env bash) → ${h.command}`);
        }
      }
    }
  }
  ok(`${total} hook(s) de comando verificados`);
} else {
  erro('nenhum hook configurado em .claude/settings.json');
}

// ------------------------------- 4. permissões: deny não pode ser anulado por allow
const perm = settings?.permissions ?? {};
for (const regra of perm.deny ?? []) {
  if ((perm.allow ?? []).includes(regra)) {
    erro(`regra "${regra}" aparece em allow E deny — deny vence, mas o allow engana quem lê`);
  }
}
if ((perm.deny ?? []).length === 0) erro('permissions.deny está vazio: nada protegido');
else ok(`${perm.deny.length} regra(s) de negação ativa(s)`);

// --------------------------------------- 5. frontmatter de agentes e skills
function lerFrontmatter(caminho) {
  const texto = readFileSync(caminho, 'utf8');
  if (!texto.startsWith('---')) return null;
  const fim = texto.indexOf('\n---', 3);
  if (fim === -1) return null;
  const campos = {};
  for (const linha of texto.slice(4, fim).split('\n')) {
    const m = linha.match(/^([a-zA-Z_-]+):\s*(.*)$/);
    if (m) campos[m[1]] = m[2].trim();
  }
  return campos;
}

const dirAgentes = join(RAIZ, '.claude/agents');
if (existsSync(dirAgentes)) {
  for (const arq of readdirSync(dirAgentes).filter((f) => f.endsWith('.md'))) {
    const fm = lerFrontmatter(join(dirAgentes, arq));
    if (!fm) { erro(`agente ${arq}: sem frontmatter YAML`); continue; }
    for (const obrigatorio of ['name', 'description']) {
      if (!fm[obrigatorio]) erro(`agente ${arq}: falta o campo "${obrigatorio}"`);
    }
    if (fm.name?.includes(':')) erro(`agente ${arq}: "name" não pode conter ":"`);
    if (fm.name && !/^[a-z0-9-]+$/.test(fm.name)) {
      erro(`agente ${arq}: "name" deve ser minúsculas e hífens (achado: ${fm.name})`);
    }
    ok(`agente válido: ${fm.name ?? arq}`);
  }
}

const dirSkills = join(RAIZ, '.claude/skills');
if (existsSync(dirSkills)) {
  for (const pasta of readdirSync(dirSkills)) {
    const caminho = join(dirSkills, pasta, 'SKILL.md');
    if (!existsSync(caminho)) { erro(`skill ${pasta}: falta SKILL.md`); continue; }
    const fm = lerFrontmatter(caminho);
    if (!fm?.description) erro(`skill ${pasta}: falta "description" (o Claude usa isso para decidir quando usá-la)`);
    else ok(`skill válida: ${fm.name ?? pasta}`);
  }
}

// ------------------------------------------------- 6. CLAUDE.md tem tamanho sadio
const claudeMd = readFileSync(join(RAIZ, 'CLAUDE.md'), 'utf8').split('\n').length;
if (claudeMd > 200) erro(`CLAUDE.md tem ${claudeMd} linhas; acima de 200 a aderência cai — mova detalhe para skills ou rules`);
else ok(`CLAUDE.md com ${claudeMd} linhas (limite recomendado: 200)`);

// -------------------------------------------------------------- 7. suíte de testes
let testesOk = false;
let resumoTestes = '';
try {
  const saida = execFileSync('node', ['--test'], { cwd: RAIZ, encoding: 'utf8', stdio: 'pipe' });
  const passaram = saida.match(/^# pass (\d+)$/m)?.[1] ?? saida.match(/pass (\d+)/)?.[1] ?? '?';
  const falharam = saida.match(/^# fail (\d+)$/m)?.[1] ?? saida.match(/fail (\d+)/)?.[1] ?? '?';
  resumoTestes = `${passaram} passaram, ${falharam} falharam`;
  testesOk = falharam === '0';
} catch (e) {
  resumoTestes = 'a suíte falhou';
  const saida = `${e.stdout ?? ''}`;
  const falharam = saida.match(/fail (\d+)/)?.[1];
  if (falharam) resumoTestes = `${falharam} teste(s) falhando`;
}
if (testesOk) ok(`testes: ${resumoTestes}`);
else erro(`testes: ${resumoTestes}`);

// ------------------------------------------------------------------- relatório
console.log('\n=== Verificação da configuração de Claude Code ===\n');
for (const m of oks) console.log(`  ok   ${m}`);
if (problemas.length) {
  console.log('');
  for (const m of problemas) console.log(`  ERRO ${m}`);
}
console.log(
  `\n${oks.length} verificação(ões) ok, ${problemas.length} problema(s).\n`,
);
process.exit(problemas.length === 0 ? 0 : 1);
