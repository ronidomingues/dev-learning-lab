# 15 · Armadilhas e mitos

**Nível: todos** · Pode ser lido a qualquer momento.

Erros que se repetem década após década, e o folclore que os sustenta. Organizado por nível de gravidade — o primeiro grupo custa produtos inteiros, o último custa tardes.

---

# Parte I — Erros arquiteturais

## 1. Fazer SPA porque é o padrão

**O erro.** Um blog, um site institucional, uma documentação construídos como SPA. Bundle de 800 KB para exibir texto, SEO quebrado, tela branca em rede ruim.

**Por que acontece.** É o que o tutorial ensina, é o que a vaga pede, é o que o time já sabe. Ninguém pergunta se o problema pede isso.

**A correção.** A árvore de decisão do arquivo `07`, seção 11. Comece pelo mais estático que atenda o requisito.

**Como reconhecer que você caiu nele:** se o usuário típico visita uma ou duas páginas e vai embora, o modelo de "pagar caro na primeira visita para pagar zero depois" nunca se amortiza. Você pagou o custo e não colheu o benefício.

---

## 2. Tratar estado de servidor como estado de cliente

**O erro.** `useEffect` + `useState` + store global para dados que vivem no banco.

**A consequência.** Você escreveu um cache — sem TTL, sem invalidação, sem dedupe, sem revalidação, sem cancelamento, sem retry. Todos esses vão ser adicionados aos poucos, mal, ao longo de meses.

**A correção.** Arquivo `06`, seção 1. É a refatoração de maior retorno disponível na maioria das SPAs que já auditei.

---

## 3. Buscar dados dentro de componentes

**O erro.** Cada componente busca o que precisa no `useEffect`.

**A consequência.** Cascatas em série (arquivo `08`, seção 3). Uma tela que deveria carregar em 300 ms leva 1,8 s, e a causa não aparece em nenhum profiler de CPU — só na aba Network.

**A correção.** Loaders de rota. Declare os dados no nível da rota; dispare código e dados em paralelo.

---

## 4. Ignorar o carregamento inicial até ser tarde

**O erro.** Desenvolver em localhost com rede local e CPU de desktop. Descobrir na produção que o app leva 8 segundos num Android de entrada em 4G.

**A correção.** Throttling ativado desde o primeiro dia. Orçamento de bundle no CI desde o primeiro dia. Um dispositivo real barato na mesa da equipe.

---

## 5. Reinventar o navegador, mal

**O erro.** Modal, dropdown, tooltip, tabs, date picker feitos do zero. Cada um com acessibilidade quebrada, teclado incompleto e um bug de foco.

**A correção.** `<dialog>`, `<details>`, `popover`, `<input type="date">` para o que a plataforma já resolve. Radix, React Aria, Ark UI ou Headless UI para o resto. Esses componentes custaram anos-pessoa de trabalho especializado.

---

# Parte II — Erros de implementação

## 6. Os clássicos de roteamento

| Erro | Sintoma |
|---|---|
| Sem rewrite no servidor | recarregar `/sobre` dá 404 |
| Sem listener de `popstate` | botão voltar muda a URL e não a tela |
| Interceptar Ctrl+clique | não dá para abrir em nova aba |
| Não mover o foco | leitor de tela não anuncia nada |
| Não restaurar rolagem | voltar cai no topo de uma lista longa |
| Não cancelar navegação anterior | tela errada aparece após clique rápido |
| Filtros fora da URL | usuário não consegue compartilhar o link |
| `pushState` a cada tecla | botão voltar precisa de 40 cliques |

Checklist completo no arquivo `05`, seção 10.

---

## 7. `key={index}`

**O erro.** Usar o índice como chave em lista que reordena, filtra ou recebe inserções.

**A consequência.** Estado de componente vazando para o item errado, `<input>` com o texto do vizinho, foco perdido, animações reiniciando. Bugs que parecem aleatórios e são perfeitamente determinísticos.

**Explicação em** `13`, seção 2. Índice só é seguro em listas verdadeiramente estáticas.

---

## 8. Vazamentos de recursos

```js
// TODOS vazam se não forem limpos
useEffect(() => {
  const t = setInterval(tick, 1000);
  const obs = new ResizeObserver(cb); obs.observe(el);
  const ws = new WebSocket(url);
  addEventListener('resize', cb);

  return () => {                        // ← a limpeza não é opcional
    clearInterval(t); obs.disconnect(); ws.close(); removeEventListener('resize', cb);
  };
}, []);
```

Numa SPA a página **nunca recarrega**, então vazamentos se acumulam pela sessão inteira. Num MPA, cada navegação limpava tudo de graça. Sintoma típico: "o app fica lento depois de um tempo de uso" — e ninguém consegue reproduzir em 5 minutos de teste.

Diagnóstico: DevTools → Memory → comparar heap snapshots após navegar várias vezes entre as mesmas duas telas. Se os detached nodes crescem monotonicamente, você tem um vazamento.

---

## 9. Race conditions em requisições

```js
// clássico e sempre presente
useEffect(() => {
  fetch(`/api/busca?q=${termo}`).then(r => r.json()).then(setResultados);
}, [termo]);
// digite "abc" rápido: as respostas podem chegar fora de ordem.
// "ab" chega depois de "abc" e sobrescreve com o resultado errado.
```

Correção no arquivo `05`, seção 5 (token de geração + `AbortController`), ou simplesmente use uma biblioteca de consultas que já resolve isso.

---

## 10. Erros silenciosos

```js
fetch(url).then(r => r.json())          // 500 → tenta parsear HTML → erro obscuro
promessa.catch(() => {})                 // engoliu o erro; ninguém nunca vai saber
try { … } catch (e) { console.log(e) }   // console de produção não é monitoramento
```

Sem `if (!r.ok)`, sem fronteiras de erro, sem listeners globais e sem Sentry, você descobre os bugs pelo suporte — quando o usuário se dá ao trabalho de reclamar em vez de simplesmente ir embora.

---

# Parte III — Mitos

## 11. "SPA é mais rápida"

**Meia verdade, e a metade errada é a que importa.** A navegação subsequente é muito mais rápida. O **primeiro carregamento** é significativamente mais lento. Se o usuário típico vê duas páginas e sai, você entregou uma experiência pior.

## 12. "O Google renderiza JavaScript, então SEO está resolvido"

**Falso na prática.** Renderiza, mas com atraso de horas a dias, com orçamento limitado, e os outros rastreadores — inclusive os de LLMs, cada vez mais relevantes — majoritariamente não renderizam. Arquivo `10`, seção 1.

## 13. "Virtual DOM é rápido"

**Falso como enunciado.** VDOM é mais **lento** que manipulação direta e cirúrgica — é uma camada a mais. O que ele oferece é um **modelo de programação** que evita a categoria de bugs do jQuery, com desempenho suficientemente bom. Svelte e Solid provam que dá para ter o modelo declarativo sem o VDOM, e mais rápido. Arquivo `13`.

## 14. "Precisamos de Redux"

**Quase sempre falso em 2026.** A maior parte do que motivava Redux era estado de servidor, que hoje pertence a um cache de consultas. O que sobra costuma caber numa store de 20 linhas.

## 15. "TypeScript deixa o código seguro"

**Falso.** TypeScript verifica **o que você escreveu**, não o que chega pela rede. `const dados: Usuario = await r.json()` é uma **afirmação sem verificação nenhuma** — o `json()` retorna `any` e você mentiu para o compilador. Valide no limite do sistema com Zod, Valibot ou equivalente.

## 16. "Microfrontends resolvem escala"

**Raramente.** Eles resolvem um problema **organizacional** (times independentes com ciclos de release próprios), a um custo técnico alto: duplicação de dependências, estilos conflitantes, roteamento distribuído, versões divergentes do framework, depuração atravessando fronteiras. Se você tem um time, microfrontends são complexidade pura. **A Lei de Conway funciona nos dois sentidos** — não invente uma arquitetura distribuída para uma organização que não é distribuída.

## 17. "Precisamos ser offline-first"

**Quase sempre não.** Offline-first exige resolução de conflito, e conflito é um problema genuinamente difícil (arquivo `08`, seção 9). Se seus usuários estão em escritórios com Wi-Fi, você vai gastar meses para resolver um problema que eles não têm. Offline-first é para campo, logística, saúde em áreas remotas, aviação.

## 18. "Vamos otimizar depois"

**Meia verdade perigosa.** Micro-otimizações, sim — deixe para depois e meça. **Decisões arquiteturais, não.** Trocar CSR por SSR depois de dois anos de código é uma reescrita. Escolher a estratégia de renderização e o orçamento de performance é decisão de projeto, não de polimento.

## 19. "É só uma dependência"

**Falso.** Um pacote traz um grafo transitivo com dezenas de outros, cada um com autor, licença, cadeia de suprimentos e ciclo de vida próprios. Cada dependência é uma aposta de que o mantenedor continuará mantendo, e não será comprometido. Arquivo `11`, seção 7.

## 20. "Esse framework é mais rápido — olha o benchmark"

**Quase sempre irrelevante.** Benchmarks de framework medem renderização de listas grandes. Sua aplicação é limitada por rede, por bundle, por consulta de banco e por imagens — não por diffing. A diferença entre React e Solid num app real é tipicamente invisível ao lado de uma cascata de rede mal resolvida.

---

# Parte IV — Erros de processo

## 21. Escolher tecnologia pelo currículo

Adotar algo porque é novo, não porque resolve um problema seu. Você paga a curva de aprendizado, os bugs de imaturidade, a documentação escassa e o ecossistema pequeno — e ainda vai mantê-lo por anos.

## 22. Não medir

Otimizar por intuição. A intuição sobre performance web está errada com frequência notável, porque o gargalo raramente está onde o código parece complicado.

## 23. Testar só o caminho feliz

Erro de rede, resposta vazia, resposta gigante, 403, timeout, sessão expirada no meio do fluxo, clique duplo, conexão intermitente. Cada um é um estado que o usuário vai encontrar.

## 24. Não ter orçamento no CI

Sem `size-limit` e Lighthouse CI falhando o build, o bundle cresce sozinho e a performance regride semana a semana. Ninguém adiciona 300 KB de uma vez; adicionam-se 8 KB por PR.

## 25. Abstrair cedo demais

Um wrapper genérico sobre o roteador, uma camada de abstração sobre o `fetch`, um sistema de plugins — antes de existirem três casos concretos. A abstração errada custa mais que a duplicação que ela evitou, porque duplicação é fácil de desfazer e abstração errada é difícil.

---

## 26. Autoteste

1. Por que a SPA "não se amortiza" para um site de conteúdo?
2. O que exatamente você reescreve quando trata estado de servidor como estado de cliente?
3. Por que vazamentos de memória são mais graves em SPA que em MPA?
4. Por que "Virtual DOM é rápido" está errado como enunciado?
5. Por que TypeScript não protege dados vindos da rede?
6. Que problema microfrontends realmente resolvem, e a que custo?
7. Quais otimizações podem esperar e quais não podem?
8. Por que abstrair cedo é pior que duplicar?

---

**Anterior:** [14 — Estado da arte](14-estado-da-arte.md) · **Próximo:** [16 — Prática](16-pratica.md)
