# 02 · Pré-requisitos

**Nível:** iniciante · **Última atualização:** 14/08/2026

---

## Resumo em cinco linhas

Você precisa de: um terminal, saber navegar nele, e entender o que é um endereço IP.
Só isso é indispensável. Tudo o mais este curso ensina no caminho.

Se você já sabe abrir um terminal e sabe que `192.168.0.1` é um endereço de rede, pule para
[`03-instalacao.md`](03-instalacao.md).

---

## Conhecimento indispensável

Sem isto, o material trava. Com isto, ele flui.

### 1. Usar um terminal

Saber abrir um terminal, digitar um comando, ler a saída, e não entrar em pânico quando
aparecer texto vermelho.

Concretamente, você deve conseguir executar `ls`, `cd`, entender o que é um "diretório
atual", e saber que `|` liga a saída de um comando à entrada de outro.

- **Onde aprender (PT):** [Curso de Linux para iniciantes — Diolinux](https://www.youtube.com/@Diolinux) · [Linux Básico — Bóson Treinamentos](https://www.youtube.com/playlist?list=PLucm8g_ezqNoAkYKMK1MRHwtqAaOdW7f9)
- **Onde aprender (interativo, no navegador):** [linuxjourney.com](https://linuxjourney.com/) (EN, gratuito)
- **Tempo:** 3 a 6 horas para o suficiente.

### 2. Saber o que é um endereço IP

Não precisa saber sub-redes nem CIDR ainda. Precisa saber que:

- toda máquina na rede tem um número que a identifica (`192.168.0.15`, `10.0.0.7`);
- `127.0.0.1` é um endereço especial que significa "eu mesmo";
- endereços que começam com `192.168.`, `10.` ou `172.16–31.` são **privados** (rede interna);
- o resto é público (internet).

Se você sabe essas quatro coisas, está pronto. Se não sabe, são 40 minutos de leitura.

- **Onde aprender (PT):** [Endereçamento IP — Bóson Treinamentos](https://www.youtube.com/playlist?list=PLucm8g_ezqNrNucFEmMU3AsaEBoV4XsMs)
- **Tempo:** 1 hora.

### 3. Entender o que é um "processo"

Um programa em execução. Tem um número (PID), tem um dono (usuário), pode ser encerrado.

Isso importa porque **toda porta aberta pertence a um processo**, e a pergunta prática
número um do assunto é "quem abriu essa porta?".

- **Tempo:** 20 minutos. Rode `ps aux | head` e olhe as colunas. Já basta.

---

## Conhecimento que ajuda muito (mas não trava)

| Assunto | Por que ajuda | Onde aprender |
|---|---|---|
| **Modelo de camadas TCP/IP** | Entender onde a porta *vive* na pilha | O próprio [`12-onde-a-porta-vive.md`](12-onde-a-porta-vive.md) ensina do zero |
| **Noções de HTTP** | Metade dos exemplos são web | [`apis`](../apis/00-MAPA.md) nesta pasta |
| **Python básico** | O projeto-modelo é em Python | Não é obrigatório: ele roda sem você editar nada |
| **Docker** | Publicação de porta é o assunto do `20` | [`docker`](../docker/00-MAPA.md) nesta pasta |
| **Sistemas numéricos (hex, binário)** | O `/proc/net/tcp` grava tudo em hexadecimal | O `15` explica na hora |
| **Noções de segurança ofensiva** | Contexto do `17` e do `19` | [`ethical-hacking`](../ethical-hacking/00-MAPA.md) nesta pasta |

---

## Ambiente

### Mínimo absoluto

| Item | Requisito |
|---|---|
| Sistema operacional | Qualquer um: Linux, macOS ou Windows 10+ |
| Hardware | Qualquer coisa dos últimos 15 anos. Isso não usa CPU nem memória. |
| Disco | ~200 MB para todas as ferramentas do `03` (o Nmap sozinho leva ~30 MB) |
| Rede | Nenhuma! Tudo pode ser feito contra `127.0.0.1` |
| Conta em serviço | Nenhuma. Nada aqui exige cadastro. |
| Privilégio administrativo | **Recomendável, não obrigatório.** Ver abaixo. |

### Sobre precisar de `sudo` / administrador

Esta é a restrição real, e vale ser honesto sobre ela:

| O que você quer fazer | Precisa de privilégio? |
|---|---|
| Listar portas abertas | Não |
| Ver **qual processo** abriu cada porta (todos os usuários) | **Sim** |
| Varrer portas com `connect()` (`nmap -sT`) | Não |
| Varredura SYN, UDP, detecção de SO (`nmap -sS -sU -O`) | **Sim** |
| Capturar pacotes (`tcpdump`, Wireshark) | **Sim** (ou grupo `wireshark`) |
| Escutar em porta abaixo de 1024 | **Sim** (ou capability, ver `03`) |
| Ver regras de firewall | **Sim** |
| Rodar o projeto-modelo | Não |

**Sem `sudo` você faz uns 70 % do curso.** Os 30 % restantes ficam anotados — e onde não
foi possível executar, este material diz claramente que não foi.

### Se você não tem administrador na sua máquina

É a situação de muita gente em máquina corporativa. Rota:

1. Use uma **máquina virtual** — VirtualBox é gratuito e não exige admin no host em algumas
   configurações; se exigir, veja o item 2.
2. Use **WSL2** no Windows: você é root **dentro** dele, mesmo sem ser admin do Windows —
   desde que o WSL já esteja instalado.
3. Use um **container**: `docker run --rm -it --cap-add=NET_RAW --cap-add=NET_ADMIN ubuntu`
   te dá root dentro do container.
4. Use uma **VM na nuvem** de camada gratuita (Oracle Cloud Always Free, Google Cloud
   e-2-micro). Detalhes e preços no [`80-custos-e-licencas.md`](80-custos-e-licencas.md).
5. Use um **laboratório no navegador**: TryHackMe e Hack The Box têm salas de varredura
   sem instalar nada. Ver [`03-instalacao.md`](03-instalacao.md), seção "sem instalar nada".

---

## Tempo realista até cada nível

Estes números pressupõem uma pessoa que já tem os indispensáveis acima e estuda com as mãos,
não só lendo. São honestos, não otimistas.

| Nível | O que você consegue fazer | Tempo |
|---|---|---|
| **Funcional** | Listar portas, achar o processo dono, testar se uma porta responde | **3 a 5 horas** |
| **Confortável** | Diagnosticar os 4 erros clássicos sozinho, ler `nmap`, entender loopback vs. 0.0.0.0 | **15 a 25 horas** |
| **Competente** | Auditar uma frota, decidir o que fechar, entender NAT e container, ler captura de pacote | **60 a 100 horas** |
| **Profundo** | Explicar TIME_WAIT e esgotamento de porta efêmera, escrever ferramenta própria, ajustar sysctl com critério | **200 a 400 horas** |
| **Fronteira** | Contribuir com scanner, pesquisar varredura em escala de internet, trabalhar em pilha de rede | **anos** |

**Um aviso sobre o nível "funcional":** ele é rápido de alcançar e enganoso. Em 4 horas você
sabe rodar `ss -tulpn`. O erro é achar que isso é o assunto. O que separa profissional de
iniciante não é conhecer o comando — é saber **por que a resposta dele às vezes está
incompleta**, e é isso que leva as outras 20 horas.

---

## Rota de resgate — o que fazer se faltar um pré-requisito

| Se você… | Faça isto |
|---|---|
| Nunca abriu um terminal | Instale o Windows Terminal ou abra o Terminal do macOS. Passe 2 h no linuxjourney.com. Volte. |
| Não sabe o que é IP | Leia a seção 2 acima e rode `ip a` (Linux/macOS) ou `ipconfig` (Windows). Olhe seu próprio IP. Já basta para começar. |
| Não tem admin na máquina | Use WSL2, container ou VM na nuvem gratuita (ver acima). Não trave por causa disso. |
| Tem medo de "quebrar a rede" | Você não vai. Nada neste curso, até o `18`, modifica configuração. Listar e varrer são operações de leitura. Onde houver risco, este material avisa em negrito. |
| Está em máquina corporativa | **Leia o `03`, seção "rede corporativa", antes de rodar qualquer varredura.** Varrer a rede da empresa sem avisar aciona alertas e pode ser tratado como incidente — mesmo sendo você. |
| Não sabe Python e quer o projeto-modelo | Rode do jeito que está. Ele não pede que você programe. Ler o código com os comentários já ensina. |

---

## Aviso legal, antes de tudo

Isto não é rodapé. É pré-requisito.

**Varrer portas da sua própria máquina e da sua própria rede é administração normal.**
Varrer máquina de terceiro sem autorização é, no Brasil, potencialmente enquadrável no
**art. 154-A do Código Penal** (invasão de dispositivo informático, redação dada pela
Lei 14.155/2021), e viola o contrato de praticamente todo provedor de internet e de nuvem.

Três regras que valem para o curso inteiro:

1. **Alvo padrão é `127.0.0.1`.** Todo exemplo aqui funciona contra a própria máquina.
2. **Rede da empresa exige aviso.** Mesmo sendo o administrador dela. Varredura dispara
   IDS, e "eu estava estudando" é uma conversa ruim de se ter com o time de segurança
   depois do alerta, não antes.
3. **`scanme.nmap.org` existe** justamente para ser varrido — o projeto Nmap o mantém com
   autorização explícita para isso. É o único alvo público que este material recomenda,
   e mesmo assim: sem `-T5`, sem varrer as 65 535 portas repetidamente.

O enquadramento completo está em [`ethical-hacking`](../ethical-hacking/00-MAPA.md) nesta
mesma pasta, arquivo de ética e lei.

---

## Checklist antes de seguir

```bash
# 1. Tenho um terminal e ele responde
echo "ok"

# 2. Sei meu IP
ip a 2>/dev/null || ipconfig     # Linux/macOS || Windows

# 3. Tenho Python 3.10+ (para o projeto-modelo)
python3 --version

# 4. Sei se tenho privilégio administrativo
sudo -n true 2>/dev/null && echo "tenho sudo" || echo "sem sudo — sem problema, siga assim mesmo"
```

Se os quatro rodaram, siga para [`03-instalacao.md`](03-instalacao.md).

---

## Autoteste

1. Qual é o único conhecimento indispensável que, se faltar, realmente trava este curso?
2. Você não tem `sudo`. Quais três coisas do curso ficam fora do seu alcance? Qual a saída
   para cada uma?
3. Por que varrer a rede da sua própria empresa, sendo você o administrador, ainda exige
   avisar alguém antes?
4. Alguém diz "aprendi portas em uma tarde, é só rodar `netstat`". O que essa pessoa
   provavelmente **não** sabe ainda?
5. Você está num Windows corporativo sem privilégio de administrador. Enumere três formas de
   montar um ambiente de estudo mesmo assim.

---

*Próximo: [`03-instalacao.md`](03-instalacao.md) — o manual de campo.*
