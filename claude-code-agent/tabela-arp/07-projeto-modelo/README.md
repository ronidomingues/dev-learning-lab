# Projeto-modelo · `arpinspect`

> Um inspetor da tabela ARP/vizinhos, **executável, completo e sem dependências**, que lê a
> tabela real do sistema, identifica o fabricante de cada dispositivo pelo MAC e **detecta
> anomalias** — inclusive a assinatura de um ataque de ARP spoofing.
>
> **Nível:** intermediário · **Requisitos:** Python 3.8+ · **Root:** não é necessário (só lê)

Este projeto existe para transformar os capítulos [01](../01-introducao-leigo.md),
[12](../12-anatomia-do-pacote.md) e [18-seguranca](../18-seguranca.md) em código que você
roda. Não é um trecho: é uma ferramenta inteira, com testes, tratamento de erro, saída para
humano e para máquina, e um modo de auditoria usável em CI.

---

## O que ele faz

1. **Lê** a tabela real: no Linux via `ip -j neigh show` (JSON) com *fallback* textual; em
   macOS/BSD/Windows via `arp -a`.
2. **Enriquece** cada MAC com o fabricante, consultando a base OUI pública do IEEE (usa a que o
   `nmap` embute, ou `oui.txt` do pacote `ieee-data`, ou uma que você passar).
3. **Detecta**:
   - **um IP com dois MACs** → assinatura clássica de *ARP spoofing* / IP em disputa;
   - **um MAC servindo muitos IPs** → roteador, *proxy ARP*, ou host se passando por vários;
   - **entradas FAILED/INCOMPLETE** → hosts mortos ou varredura em curso;
   - **MAC localmente administrado/aleatório** (bit `0x02`) → privacidade de Wi-Fi ou spoof;
   - **o gateway** → e sugere fixá-lo como `PERMANENT` (defesa do [18](../18-seguranca.md)).
4. **Resume** a rede por estado e por fabricante.

---

## Como rodar

```bash
cd 07-projeto-modelo

# inspecionar a máquina atual (a saída abaixo é real, desta máquina)
python3 arpinspect.py

# analisar uma captura salva, sem tocar na rede
python3 arpinspect.py --file exemplo-spoofing.txt

# saída JSON, para integrar com outra ferramenta
python3 arpinspect.py --json

# modo auditoria para CI: sai com código 1 se houver anomalia REAL
python3 arpinspect.py --file exemplo-spoofing.txt --check ; echo "exit=$?"

# base OUI alternativa
python3 arpinspect.py --oui /usr/share/nmap/nmap-mac-prefixes
```

Gerar uma captura para analisar depois (offline):
```bash
ip neigh show > minha-rede.txt        # Linux
arp -a        > minha-rede.txt        # macOS/Windows
python3 arpinspect.py --file minha-rede.txt
```

---

## Saída real (máquina de escrita, 14/08/2026)

```
════════════════════════════════════════════════════════════════════
 INSPETOR DA TABELA ARP / VIZINHOS
════════════════════════════════════════════════════════════════════
 gateway padrão: 10.209.0.1
 entradas: 14   estados: {'FAILED': 3, 'STALE': 8, 'REACHABLE': 3}
────────────────────────────────────────────────────────────────────
 IP              MAC                 ESTADO      FABRICANTE
────────────────────────────────────────────────────────────────────
>10.209.0.1      6c:31:0e:..:..:..   REACHABLE   Cisco Systems
 10.209.0.195    58:38:79:..:..:..   STALE       Ricoh Company
 10.209.1.31     00:50:56:..:..:..   REACHABLE   VMware
 10.209.1.101    10:bf:48:..:..:..   STALE       Asustek Computer
!10.209.1.102    —                   FAILED      (sem MAC)
 10.209.2.134    d0:94:66:..:..:..   STALE       Dell
 ...
```
*(os 3 últimos octetos dos MAC foram mascarados no README por privacidade; ver aviso em
[01](../01-introducao-leigo.md) §4. Ao rodar na sua máquina, aparecem completos.)*

E contra o arquivo de spoofing de exemplo (fabricado para o exercício):
```
 • IP 10.0.0.1 aparece com MACs diferentes ['aa:bb:cc:00:00:01', 'de:ad:be:ef:00:99']
   -> possível ARP spoofing ou IP em disputa
 • MAC 00:50:56:11:22:33 (VMware) responde por 4 IPs
   -> roteador, proxy ARP, ou host se passando por vários
```

---

## Estrutura

```
07-projeto-modelo/
├── README.md              # este arquivo
├── arpinspect.py          # a ferramenta (uma só, ~330 linhas, comentada)
├── test_arpinspect.py     # 19 testes (unittest, zero dependências)
└── exemplo-spoofing.txt   # captura fabricada com 2 anomalias plantadas
```

---

## O que cada decisão de projeto ensina

- **Ler `ip -j neigh` (JSON) com fallback textual.** Ensina a nunca depender de parsing frágil
  quando existe saída estruturada — e a degradar com elegância quando ela falta. É o padrão de
  toda automação de rede séria.
- **Normalizar o MAC** (`AA-BB`, `aa:bb`, `a:b:c:1:2:3` do macOS → forma canônica) antes de
  comparar. Ensina por que "comparar strings de MAC" ingenuamente gera falsos negativos — o
  mesmo endereço tem várias grafias.
- **O bit localmente-administrado (`0x02`).** Ensina que MAC **não** é imutável: telefones e
  notebooks modernos usam MAC aleatório por privacidade, e o bit `0x02` os denuncia. É também
  como um atacante esconde o fabricante.
- **Detectar IP↔MAC inconsistente**, não IP duplicado ingênuo. Ensina a assinatura **real** de
  spoofing: o perigo é *um IP com dois MACs* (alguém se passando pelo gateway), não *dois IPs
  com um MAC* (que é normal — uma máquina com vários IPs, ou um roteador).
- **Separar anomalia `[info]` de anomalia real** e refletir isso no **código de saída** do
  `--check`. Ensina o padrão de ferramenta de CI: ruído informativo não pode reprovar o
  *pipeline*; só o que é acionável.
- **Tratamento de erro real:** `subprocess` com `timeout` e `FileNotFoundError`; arquivos lidos
  com `errors="replace"`; base OUI ausente não quebra, só degrada o campo fabricante para `?`.
  Ensina o que tutoriais omitem: o caminho de falha é metade do programa.
- **Testes que incluem o caminho feliz E o de ataque.** O teste `test_rede_saudavel...` garante
  que a ferramenta **não** grita lobo numa rede limpa — tão importante quanto detectar o
  ataque. Falso positivo mata uma ferramenta de segurança.

---

## Rodar os testes

```bash
python3 -m unittest test_arpinspect -v
# esperado: Ran 19 tests ... OK
```

Saída real (14/08/2026, Python 3.10.12): **19 testes, todos passando, em 0,069 s.**

---

## Limitações declaradas (honestidade)

- A tabela de um **único host** vê, no máximo, **um MAC por IP num dado instante** — a detecção
  de "IP com dois MACs" pega o caso em que o cache oscilou e ambas as entradas coexistem, ou
  quando você analisa uma captura acumulada (como `exemplo-spoofing.txt`). Para pegar spoofing
  em tempo real, o caminho é o `arpwatch` monitorando mudanças, coberto no
  [18-seguranca](../18-seguranca.md) §5 — este projeto é o *analisador estático*, complementar.
- Não envia pacotes (não precisa de root). Para o lado ativo (montar um ARP request byte a
  byte), veja os exemplos com Scapy no [06-exemplos](../06-exemplos.md) e no
  [12-anatomia-do-pacote](../12-anatomia-do-pacote.md).
- A base OUI cobre fabricantes registrados; MAC aleatório/local não tem fabricante por
  definição, e a ferramenta diz isso em vez de inventar.

---

**Próximo:** volte ao [00-MAPA.md](../00-MAPA.md) ou siga para o núcleo em
[10-fundamentos.md](../10-fundamentos.md).
