# 75 · Armadilhas — 30 erros clássicos e 9 mitos

**Nível:** todos · **Última atualização:** 14/08/2026

Cada armadilha traz: **o erro → por que persiste → como evitar**. O "por que persiste"
importa: quase todos esses erros sobrevivem porque *funcionam na maioria das vezes*, e falham
exatamente no caso que interessa.

---

## Erros de conceito

### 1. Achar que a porta é um lugar

**O erro:** tratar a porta como algo que "está lá" e pode ser aberta ou fechada como uma
válvula.

**Por que persiste:** a metáfora da "porta do prédio" é a primeira que todo mundo ouve, e
ela sugere permanência.

**Como evitar:** interiorize que **a porta só existe enquanto um processo a reservou**.
Você não fecha uma porta — você para de abri-la. A hierarquia é: desligue o serviço >
restrinja o `bind` > filtre.

### 2. Confundir porta com protocolo de aplicação

**O erro:** "a porta 80 está aberta, logo é um servidor web".

**Por que persiste:** é verdade em 95 % dos casos, e o `nmap` sem `-sV` reforça a ilusão ao
imprimir "http" ao lado do número.

**Como evitar:** o nome vem do `/etc/services`, uma tabela de convenções. Para saber de
verdade: `nmap -sV`, ou converse com o serviço.

### 3. Achar que TCP/80 e UDP/80 são a mesma porta

**O erro:** liberar "a porta 443" no firewall pensando que cobriu tudo.

**Por que persiste:** durante 30 anos, quase nada relevante usava UDP em porta de serviço
web. **Isso mudou com o HTTP/3.**

**Como evitar:** são espaços de numeração separados. Especifique sempre o transporte.
Teste: `curl --http3 -sS -o /dev/null -w '%{http_version}\n' https://cloudflare.com/` —
se der 2 em vez de 3, seu UDP/443 está bloqueado.

### 4. Achar que uma porta só suporta uma conexão

**O erro:** "como o servidor atende 50 mil clientes na 443?"

**Como evitar:** a exclusividade é da **quádrupla**, não da porta. O socket de escuta é um;
os sockets de conexão são milhares, todos com a mesma porta local.

### 5. Confundir a porta do switch com a porta TCP

**O erro:** "o switch tem 24 portas, então ele controla 24 conexões".

**Por que persiste:** homonímia pura, e ninguém desfaz.

**Como evitar:** em equipamento de rede, "porta" é o conector físico. Um switch de camada 2
não sabe o que é porta TCP.

---

## Erros de bind e configuração

### 6. `0.0.0.0` por padrão, sem pensar

**O erro:** deixar o serviço no padrão do framework, que costuma ser `0.0.0.0`.

**Por que persiste:** frameworks escolhem `0.0.0.0` para funcionar dentro de container. Fora
dele, ninguém troca de volta.

**Como evitar:** `ss -tulpn | grep -vE '127\.0\.0\.'` toda semana. Se a linha não tem
justificativa escrita, o bind está errado.

### 7. Achar que `127.0.0.1` cobre todo o loopback

**O erro:** testar `127.0.0.1:53` e concluir que não há DNS local.

**Por que persiste:** todo mundo escreve `127.0.0.1` e ninguém pensa no `/8`.

**Como evitar:** todo o `127.0.0.0/8` é loopback — 16 milhões de endereços. O
`systemd-resolved` usa `127.0.0.53`. Verificado nesta máquina.

### 8. Esquecer o IPv6

**O erro:** firewall e bind configurados só para IPv4, numa máquina com IPv6 ativo.

**Por que persiste:** o IPv6 "funciona sozinho" e não aparece nos comandos que as pessoas
decoraram.

**Como evitar:**

```bash
ss -tulpn | grep -E '\[::\]'
sudo ip6tables -L -n -v
```

Com o IPv6 passando de 50 % do tráfego em 2026, essa é uma das exposições mais comuns e
menos notadas.

### 9. Tratar `::ffff:127.0.0.1` como endereço exposto

**O erro:** script de auditoria que testa `ip == "127.0.0.1"` e classifica o IPv4-mapeado
como exposto.

**Por que persiste:** o formato só aparece quando há socket IPv6 aceitando IPv4, e o teste
ingênuo funciona até esse dia.

**Como evitar:** desembrulhe o prefixo `::ffff:` antes de comparar. O
[projeto-modelo](07-projeto-modelo/README.md) tinha exatamente esse defeito na primeira
versão — encontrado ao rodar contra esta máquina, corrigido, e coberto por dois testes.

### 10. Rodar o serviço como root só para usar porta baixa

**O erro:** `sudo node server.js` para escutar na 80.

**Por que persiste:** é o que resolve o `Permission denied` mais rápido.

**Como evitar:** quatro alternativas, no [`03-instalacao.md`](03-instalacao.md):
`setcap cap_net_bind_service`, ativação por socket do systemd,
`sysctl ip_unprivileged_port_start`, ou porta alta com proxy reverso na frente.

### 11. Escolher porta na faixa efêmera

**O erro:** escolher a 50000 "porque é dinâmica e ninguém usa".

**Por que persiste:** o RFC diz que 49152–65535 é dinâmica, e parece livre.

**Como evitar:** no Linux, a faixa efêmera é **32768–60999** (medido nesta máquina) — ela
**cobre** boa parte da faixa "dinâmica" do RFC. Um serviço ali pode colidir com uma porta
de origem. Use a faixa 1024–32767.

### 12. `EXPOSE` no Dockerfile achando que publica

**O erro:** `EXPOSE 80` e esperar que a porta esteja acessível.

**Como evitar:** `EXPOSE` é documentação. Só `-p` publica.

### 13. `-p 8080:80` em vez de `-p 127.0.0.1:8080:80`

**O erro:** publicar em todas as interfaces sem perceber.

**Por que persiste:** a forma curta é a que aparece em todo tutorial.

### 14. `containerPort` divergente do que o processo usa (Kubernetes)

**O erro:** manifesto diz 8080, processo escuta na 9090.

**Como evitar:** `containerPort` é informativo. Só o `targetPort` do Service importa.
Verifique com `kubectl get endpoints`.

---

## Erros de diagnóstico

### 15. Começar pelo firewall

**O erro:** "não responde" → mexer no firewall.

**Por que persiste:** firewall é a explicação mais interessante, e o passo 1 parece bobo
demais.

**Como evitar:** a ordem certa é: (0) o `ss` mostra `LISTEN`? (1) em qual IP? (2) responde
localmente? ... e só então firewall. O passo 0 resolve metade dos casos, em três segundos.

### 16. Testar com `curl` na mesma máquina e concluir que está no ar

**O erro:** `curl http://localhost:8080/` funciona → "o serviço está acessível".

**Como evitar:** esse teste não exercitou rede nenhuma. **A pergunta que fecha o
diagnóstico:** *"o `curl` rodou na mesma máquina que o serviço?"*

### 17. Não distinguir "recusada" de "timeout"

**O erro:** tratar as duas como "não funcionou".

**Como evitar:** recusada = chegou lá, ninguém escuta (rápido). Timeout = alguém descartou
(lento). São problemas em lugares diferentes. Medido: `after 0 ms` contra
`after 5000 milliseconds`.

### 18. Confiar só no `ss`

**O erro:** "o `ss` mostra `LISTEN`, então está acessível".

**Como evitar:** o `ss` não sabe de firewall, NAT, Security Group nem rota. Teste também de
fora.

### 19. Confiar só no `nmap`

**O erro:** "o `nmap` diz aberta, então há um serviço ali".

**Como evitar:** pode ser proxy, honeypot ou redirecionamento no kernel. O caso real deste
curso: 25 portas "abertas" contra 8 processos escutando.

### 20. Ignorar `Recv-Q` numa linha `LISTEN`

**O erro:** achar que `Recv-Q` são bytes.

**Como evitar:** em `LISTEN`, `Recv-Q` é a **fila de conexões prontas** e `Send-Q` é o
**backlog**. `Recv-Q` alto e preso = o processo não está chamando `accept()`. Diagnóstico
preciso, num comando.

### 21. Achar que `CLOSE_WAIT` é problema de rede

**O erro:** abrir chamado com o time de rede por causa de `CLOSE_WAIT` acumulando.

**Como evitar:** `CLOSE_WAIT` significa que **o seu código** não chamou `close()`. O kernel
não pode resolver sozinho. É o único estado que aponta o dedo para a aplicação.

### 22. `netstat -tulpn` no macOS

**O erro:** copiar o comando do Linux.

**Como evitar:** o `netstat` do BSD tem outras flags (`-p` é "protocolo", não "processo").
No macOS use `lsof -nP -iTCP -sTCP:LISTEN`.

### 23. Esquecer que `lsof` trunca o nome em 9 caracteres

**O erro:** ver `MainThrea` e não reconhecer o processo.

**Como evitar:** `lsof +c 0`.

### 24. Não usar `-n` no `ss`

**O erro:** deixar a ferramenta traduzir 22 para "ssh".

**Como evitar:** sem `-n`, você lê o que **deveria** estar ali, não o que está. E fica lento
por causa do DNS reverso.

---

## Erros de varredura

### 25. Varrer sem autorização

**O erro:** "é só um scan, não faz mal".

**Como evitar:** art. 154-A do Código Penal; contrato de todo provedor; e IDS corporativo
tratando como incidente. Avise por escrito, antes.

### 26. `-T5` achando que é melhor

**O erro:** usar a velocidade máxima para "ganhar tempo".

**Por que persiste:** parece óbvio que mais rápido é melhor.

**Como evitar:** `-T5` perde pacotes e reporta aberta como filtrada. Em rede local, `-T4`.
Contra a internet, `-T3` (o padrão) existe por um motivo. A documentação do Nmap é explícita.

### 27. Esquecer `-Pn` contra Windows e nuvem

**O erro:** `nmap` responde "Host seems down" e você acredita.

**Como evitar:** Windows bloqueia ICMP echo por padrão desde 2004; nuvens também. Use `-Pn`.

### 28. Varrer UDP como se fosse TCP

**O erro:** `nmap -sU -p-` e esperar terminar.

**Como evitar:** ausência de resposta em UDP não é conclusiva, e o alvo limita a taxa de
ICMP. Sonde poucas portas, com `-sV`.

### 29. Ler `open|filtered` como "aberta"

**O erro:** contar `open|filtered` no relatório como porta aberta.

**Como evitar:** significa **"não foi possível determinar"**. Reportar como aberta é falso
positivo; ignorar é falso negativo. Reporte como o que é, e diga por quê.

### 30. Relatório sem data, hora e ponto de origem

**O erro:** entregar a saída do `nmap` como se fosse verdade atemporal.

**Como evitar:** uma varredura é uma **medição**, válida naquele instante e daquele ponto de
vista. Sempre registre: alvo, data/hora, ferramenta e versão, técnica, origem — e **o que
não foi possível determinar**.

---

## Nove mitos

### Mito 1 — "Mudar o SSH da porta 22 deixa o servidor mais seguro"

**Falso como segurança, verdadeiro como higiene operacional.** Um `nmap -p-` acha em
segundos. O ganho real é que 99 % das tentativas automatizadas somem do log, o que torna as
tentativas reais **visíveis**. Faça — pelo motivo certo, e sem relaxar em chave, `fail2ban`
e atualização.

### Mito 2 — "Fechar todas as portas deixa a máquina segura"

Uma máquina sem porta aberta não presta serviço nenhum. E ela continua vulnerável pelo que
**inicia**: navegador, cliente de e-mail, atualizador. A maior parte do comprometimento hoje
entra por conexão de **saída**, não de entrada.

### Mito 3 — "Está numa rede privada, então está protegido"

Rede privada não é rede segura. Um notebook infectado, um container comprometido ou um
phishing bem-sucedido colocam o atacante **dentro**. É a premissa que o zero trust ataca.

### Mito 4 — "É criptografado, então ninguém vê a porta"

TLS cifra a carga útil. Cabeçalhos IP e TCP ficam em claro — **precisam** ficar, senão
nenhum roteador saberia rotear. A porta é sempre visível, mesmo com TLS 1.3 e ECH.

### Mito 5 — "Esconder o banner corrige a vulnerabilidade"

Reduz ruído de ataque automatizado. Não corrige nada. Se um relatório de auditoria apresenta
isso como *a* correção de um achado, o relatório está errado.

### Mito 6 — "`tcp_tw_recycle` resolve o TIME_WAIT"

**Foi REMOVIDO do kernel na versão 4.12, em 2017**, porque quebrava clientes atrás de NAT de
forma silenciosa e intermitente. Qualquer texto que ainda o recomende é anterior a 2017 —
use isso como teste de frescor do material que você está lendo.

### Mito 7 — "Porta alta é mais segura que porta baixa"

O número não confere propriedade nenhuma. A restrição de <1024 é uma convenção do Unix de
~1980, feita para um mundo de máquinas compartilhadas que não existe mais. Windows nunca a
teve.

### Mito 8 — "`nmap` mostrando `filtered` significa que não tem nada lá"

Significa que **não veio resposta**. Pode haver um serviço perfeitamente funcional atrás de
um firewall com `DROP` — que é, aliás, exatamente a configuração desejada.

### Mito 9 — "Ninguém vai achar meu servidor, ele não tem DNS"

Desde 2013 (ZMap, masscan), a IPv4 inteira é varrida em minutos, continuamente, por vários
atores. Em **IPv6** a afirmação recuperou algum valor — mas continua sendo camada adicional,
nunca controle único. Ver [`65-estado-da-arte.md`](65-estado-da-arte.md).

---

## Cartão de bolso — as cinco perguntas que resolvem quase tudo

```
1. ss -tulpn | grep :PORTA        →  existe LISTEN?
2. Em qual IP?                    →  127.0.0.1 ou 0.0.0.0?
3. Recusada ou timeout?           →  ninguém escuta, ou firewall?
4. O teste rodou de onde?         →  mesma máquina não testa rede
5. O que o kernel diz difere      →  NAT, proxy, redirecionamento
   do que a rede responde?
```

---

## Autoteste

1. Cite três erros desta lista que você já cometeu. Para cada um, qual pergunta o teria
   evitado?
2. Por que o mito do `tcp_tw_recycle` é útil como teste de frescor de material de rede?
3. "Fechar todas as portas deixa a máquina segura." Refute em duas frases.
4. Qual a diferença entre o erro 18 e o erro 19? Por que os dois existem?
5. Um relatório de varredura lista 40 portas `open|filtered` como abertas. Qual é o problema,
   e como o resultado deveria ser reportado?
6. Por que `-T5` pode piorar a qualidade da varredura?
7. Você vê `CLOSE_WAIT` crescendo em produção. Para qual time você abre o chamado, e por quê?
8. Qual é o único mito desta lista que, em 2026, tem alguma defesa técnica — e sob que
   condição exata?

---

*Próximo: [`80-custos-e-licencas.md`](80-custos-e-licencas.md).*
