# 75 · Armadilhas — erros clássicos, mitos e por que persistem

`Nível: todos` · `Última atualização: 12/08/2026`

Os erros que quase todo mundo comete, os mitos que quase todo mundo acredita, e — o mais
importante — **por que** eles persistem apesar de todos avisarem. Ler isto poupa meses.

---

## Parte A · Erros de iniciante (técnicos)

**1. Pular a enumeração.** O erro mãe. "Nenhum exploit funciona" quase sempre significa "não
enumerei o suficiente". 80% do trabalho é a fase 2. O achado está na saída que você não leu.
*Persiste porque* enumerar é chato e exploração é emocionante — o incentivo psicológico engana.

**2. Escanear só as portas padrão.** `-p-` existe por um motivo. O serviço vulnerável mora na
porta 8081, não na 80. *Persiste porque* scan completo é lento e a pressa vence.

**3. Não rodar com `sudo`.** `-sS`, `-O`, `-sU` viram silenciosamente scans piores sem root.
Você tira conclusão de dado incompleto. *Persiste porque* o nmap não grita o suficiente.

**4. Copiar exploit sem ler.** Roda contra você mesmo, não funciona, ou tem backdoor. **Sempre
leia o código antes de executar.** *Persiste porque* ler código dá trabalho e "funcionou no
vídeo".

**5. Não verificar se o ataque funcionou.** Metade dos "não funcionou" é "funcionou e a pessoa
não olhou". Depois de todo ataque: `id`, `whoami`, cheque o status. *Persiste porque* a pessoa
espera um efeito dramático que nem sempre acontece.

**6. Esquecer de estabilizar o shell.** Trabalhar num shell "burro" onde `Ctrl+C` mata tudo e
não há setas. Custa 15 segundos estabilizar ([`05`](05-manual-de-uso.md) §8). *Persiste porque*
não se sabe que dá para melhorar.

**7. Não anotar.** Você acha o caminho, fecha o terminal, e no dia seguinte não lembra o passo
exato. Refaz tudo. *Persiste porque* anotar parece perda de tempo — até você perder o acesso.

**8. Confundir "não achei" com "não existe".** Ferramenta que não reporta nada não prova
ausência ([`60`](60-teoria-avancada.md) §1). *Persiste porque* dá conforto acreditar no scanner.

## Parte B · Erros de carreira e de método

**9. Colecionar cursos sem praticar.** Sabe falar, não sabe fazer. 1h de laboratório > 4h de
vídeo. *Persiste porque* vídeo dá sensação de progresso sem o desconforto de travar.

**10. Paralisia da certificação perfeita.** 8 meses escolhendo entre OSCP e CPTS em vez de
estudar. *Persiste porque* pesquisar é mais fácil que fazer, e parece produtivo.

**11. Ignorar o lado defensivo.** Quem nunca defendeu ataca raso. Passar por SOC/blue te faz
melhor atacante ([`25`](25-carreira-passo-a-passo.md)). *Persiste porque* "blue é chato" é um
preconceito comum e errado.

**12. Menosprezar o relatório.** A parte que o cliente paga é a que iniciantes acham
burocracia ([`24`](24-relatorio-e-comunicacao.md)). *Persiste porque* a recompensa emocional
está no achado, não na escrita.

**13. Menosprezar os fundamentos.** Pular redes/TCP para ir ao exploit. Trava no primeiro alvo
diferente do tutorial. *Persiste porque* fundamento é lento e exploit é recompensa rápida.

**14. Não escrever inglês/leitura.** Limita o material a 10% do que existe. *Persiste porque*
começar dói e o custo do adiamento é invisível.

## Parte C · Mitos que precisam morrer

**15. "Hacker digita rápido e entra em 30 segundos."** Mito de filme. O ataque de 30 segundos
veio de 3 semanas de recon. *Persiste porque* a mídia vende isso há 40 anos.

**16. "Existe uma ferramenta que acha tudo."** Scanner acha o conhecido genérico. Falha de
lógica de negócio, IDOR, nenhum scanner acha bem ([`18`](18-seguranca-web.md) §11). *Persiste
porque* fornecedores de scanner vendem essa fantasia.

**17. "Kali é para usar como sistema principal."** Kali é ferramenta de trabalho, roda com
privilégio largo, quebra. Não é SO de vida ([`03`](03-instalacao.md) §2). *Persiste porque*
tutoriais de YouTube sugerem o contrário.

**18. "Preciso ser gênio de matemática."** Precisa de teimosia e método. Cripto avançada é uma
especialidade, não o campo. *Persiste porque* intimida e afasta gente boa.

**19. "Mais ferramentas = melhor hacker."** O bom pentester domina poucas ferramentas
profundamente e entende o que elas fazem. *Persiste porque* instalar ferramenta é mais fácil
que aprender.

**20. "0-day é o que importa."** A maioria dos ataques reais usa n-day e configuração errada
([`10`](10-fundamentos.md) §4). *Persiste porque* 0-day é glamouroso e n-day é sem graça.

**21. "Bug bounty é dinheiro fácil e rápido."** É renda muito variável; a maioria ganha pouco no
começo ([`80`](80-custos-e-licencas.md)). *Persiste porque* os casos de sucesso viralizam e os
milhares que ganham zero não postam.

**22. "Certificação garante emprego."** Abre porta; portfólio prova competência
([`25`](25-carreira-passo-a-passo.md)). *Persiste porque* certificado é um caminho claro e
comprável, e clareza vende.

## Parte D · Erros éticos e legais (os que acabam com carreiras)

**23. "Só um pouquinho fora do escopo."** Escopo é lei, não sugestão ([`12`](12-etica-lei-e-contrato.md)).
Achado fora do escopo não é pago e pode virar processo. *Persiste porque* a curiosidade e o
"achado bom demais para ignorar" vencem a disciplina.

**24. "Achei a falha, vou avisar a empresa" (sem autorização).** Confissão por escrito de acesso
indevido. *Persiste porque* parece a coisa "do bem" a fazer — e a lei não vê intenção.

**25. "Guardo o dump do cliente para o portfólio."** Quebra de NDA e LGPD; vazamento depois.
*Persiste porque* o troféu é tentador e o risco parece abstrato — até o vazamento.

## Por que os erros persistem — o padrão comum

Note o fio condutor: quase todo erro persiste porque **a recompensa imediata desalinha do valor
real**. Enumerar é chato mas paga; hackear é emocionante mas raro. Relatório é trabalhoso mas é
o produto; achado é divertido mas é meio caminho. Vídeo dá sensação de progresso; laboratório
dá progresso com desconforto.

Quem entende esse desalinhamento e escolhe conscientemente o valor real sobre a recompensa
imediata **já está à frente da maioria** — não por talento, mas por método. É a vantagem mais
acessível da profissão.

---

## Autoteste

1. Qual é "o erro mãe" do iniciante, e por que ele persiste?
2. Por que "não achei" não é "não existe"? (relacione com [`60`](60-teoria-avancada.md))
3. Por que Kali não deve ser seu sistema operacional principal?
4. Desminta o mito "existe uma ferramenta que acha tudo".
5. Por que 0-day é supervalorizado por iniciantes frente a n-day?
6. Por que avisar uma empresa de uma falha achada sem autorização é perigoso?
7. Qual é o "fio condutor" que explica por que quase todos os erros persistem?
8. Como esse entendimento vira uma vantagem de carreira?
