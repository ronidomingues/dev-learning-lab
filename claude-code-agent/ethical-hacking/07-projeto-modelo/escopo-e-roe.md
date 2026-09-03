# Escopo e Regras de Engajamento (RoE) — LEIA ANTES DE TUDO

> Este documento simula a autorização que, num trabalho real, **precede** qualquer teste.
> Sem um documento como este, assinado, testar é crime (art. 154-A do Código Penal). Ver
> [`12-etica-lei-e-contrato.md`](../12-etica-lei-e-contrato.md).

---

## 1. Autorização

A **LojaExemplo Ltda.** (fictícia) autoriza **[seu nome]** a realizar um teste de invasão na
aplicação abaixo, entre **12/08/2026 e 19/08/2026**, das 09h às 18h.

Signatários (num trabalho real, com nome, cargo e assinatura de quem tem **autoridade** para
autorizar — dono do sistema, não o gerente de TI qualquer):

- Contratante: _______________________ (representante legal da LojaExemplo)
- Executante: _______________________ (você)

## 2. Escopo — o que PODE ser testado

| Ativo | Endereço | Incluído? |
|---|---|---|
| Aplicação web de teste | `http://127.0.0.1:3000` | ✅ Sim |
| Arquivo de dados da app | `usuarios.db.json` (local) | ✅ Sim |

## 3. Fora de escopo — o que NÃO pode

- Qualquer outro host, IP ou domínio. Se algo interessante apontar para fora do escopo,
  **pare e reporte** — não siga.
- Ataques de negação de serviço (DoS) e testes de carga.
- Engenharia social contra pessoas reais.
- Exfiltração de dados reais além do mínimo necessário para provar a falha.

## 4. Regras de engajamento

- **Janela:** só dentro do horário acordado.
- **Prova, não dano:** demonstrar impacto com o mínimo. Se achar IDOR, provar com 2 contas
  de teste — **não** varrer a base inteira.
- **Sem alterar/destruir dados:** nada de `DROP TABLE`, apagar ou modificar registros reais.
- **Contato de emergência:** se algo quebrar a app ou você achar sinal de invasão real
  prévia, ligar para _____________ imediatamente e parar.
- **Dados sensíveis achados** (senhas, PII): registrar a existência, **não** copiar em massa,
  tratar com confidencialidade, e destruir cópias após entregar o relatório.

## 5. Entregáveis

- Relatório executivo + técnico (ver [`relatorio/relatorio-exemplo.md`](relatorio/relatorio-exemplo.md)).
- Passos de reprodução para cada achado.
- Uma sessão de *retest* após as correções.

## 6. Confidencialidade

Todo achado é confidencial. Nada é divulgado publicamente sem autorização escrita do
contratante — nem em rede social, nem em write-up, nem em portfólio (a não ser anonimizado e
com permissão).

---

**Checklist antes do primeiro comando:**

- [ ] Este documento está preenchido e (num caso real) assinado por quem tem autoridade.
- [ ] Eu sei exatamente qual endereço está no escopo e qual não está.
- [ ] Eu sei o que **não** posso fazer (DoS, alterar dados, sair do escopo).
- [ ] Eu tenho um contato de emergência.
- [ ] Só agora vou para [`pentest/roteiro.md`](pentest/roteiro.md).
