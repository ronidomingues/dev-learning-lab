# Tabela ARP — mapa do assunto

> **O que é a tabela ARP, como lê-la, como ela funciona por dentro e por que ela decide o
> tamanho de uma rede.** Do "caderninho do porteiro" à carga de broadcast Θ(N²) e ao trilema
> seguro/sem-estado/sem-infraestrutura.
>
> Produzido em 14/08/2026 · 27 documentos + projeto-modelo executável (19 testes verdes)

---

## Em uma frase

A tabela ARP é a lista de "quem é quem" (IP → MAC) que cada máquina mantém para saber a quem
entregar **fisicamente** um pacote dentro do próprio segmento — e o ARP é o protocolo de 1982,
nunca alterado, que a preenche.

---

## O que você saberá ao final

**Prático**
- ler e interpretar a tabela nos três sistemas (`ip neigh`, `arp -a`, `Get-NetNeighbor`);
- diagnosticar em segundos se um problema é de camada 2 (local) ou acima (remoto);
- provocar e observar a máquina de estados NUD ao vivo;
- detectar IP duplicado, ARP spoofing e *unicast flooding*;
- dimensionar o cache (`gc_thresh`) e endurecer um host contra spoofing;
- rodar uma ferramenta própria que inspeciona a rede e reprova pipelines com anomalia.

**Conceitual**
- por que existem dois endereços (IP e MAC) e por que isso é teoricamente necessário;
- o pacote ARP byte a byte, e por que ele resolve o **próximo salto**, nunca o destino remoto;
- a máquina de estados NUD e de onde vem cada temporizador;
- gratuitous ARP, proxy ARP, RARP, InARP, e o NDP do IPv6.

**De pesquisa**
- por que a carga de broadcast cresce com N² e por que isso é o teto de camada 2;
- o trilema "seguro / sem estado / sem infraestrutura — escolha dois";
- como EVPN, eBPF e a nuvem suprimem o ARP, fechando o círculo com o "servidor central" de 1982.

---

## Roteiro de leitura

### Só quero ler a tabela hoje (30 min)
```
01 → 04
```

### Quero usar no dia a dia e diagnosticar (meio dia)
```
01 → 02 → 04 → 05 → 06 → 19 → 07-projeto-modelo
```

### Quero entender o protocolo de verdade (2–3 dias)
```
01 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 75
```

### Quero nível profissional de redes (1–2 semanas)
```
o roteiro acima → 17 → 18 → 19 → 20 → 70 → 80 → 85
```

### Quero dominar o assunto
```
tudo, na ordem numérica (60 e 65 ao final)
```

---

## Os arquivos

### Bloco A · Porta de entrada
| Arquivo | O que é | Nível |
|---|---|---|
| [01-introducao-leigo](01-introducao-leigo.md) | o "caderninho do porteiro"; ler a tabela real | iniciante |
| [02-pre-requisitos](02-pre-requisitos.md) | IP/máscara/hex mínimos, tempo realista, rota de resgate | iniciante |
| [03-instalacao](03-instalacao.md) | manual por SO: ferramentas, captura, lab isolado, erros literais | iniciante |
| [04-como-comecar](04-como-comecar.md) | do terminal ao primeiro ciclo ARP, estados ao vivo | iniciante |
| [05-manual-de-uso](05-manual-de-uso.md) | referência de comandos por tarefa (Linux/mac/Win) | iniciante→interm. |
| [06-exemplos](06-exemplos.md) | 14 exemplos, do trivial a produção | iniciante→avançado |
| [07-projeto-modelo/](07-projeto-modelo/) | `arpinspect`: lê, enriquece por OUI e detecta anomalias; 19 testes | intermediário |

### Bloco B · Núcleo
| Arquivo | O que é | Nível |
|---|---|---|
| [10-fundamentos](10-fundamentos.md) | camadas, IP×MAC, next hop, broadcast, os cinco porquês | iniciante→interm. |
| [11-historia](11-historia.md) | Plummer 1982, por que quase não mudou, "cercado, não consertado" | intermediário |
| [12-anatomia-do-pacote](12-anatomia-do-pacote.md) | os 28 bytes, decodificados à mão | interm.→avançado |
| [13-o-ciclo-de-resolucao](13-o-ciclo-de-resolucao.md) | do pacote que quer sair ao quadro no fio | intermediário |
| [14-a-tabela-por-dentro](14-a-tabela-por-dentro.md) | máquina de estados NUD, timers, coletor de lixo | avançado |
| [15-variacoes-do-protocolo](15-variacoes-do-protocolo.md) | gratuitous, proxy, RARP, InARP, multicast | interm.→avançado |
| [16-arp-em-cada-sistema](16-arp-em-cada-sistema.md) | Linux, macOS, Windows, roteadores — as políticas | interm.→avançado |
| [17-arp-em-redes-reais](17-arp-em-redes-reais.md) | VLAN, Wi-Fi, VRRP, Docker, Kubernetes, nuvem | avançado |
| [18-seguranca](18-seguranca.md) | ARP spoofing, detecção, DAI, endurecimento | avançado |
| [19-diagnostico](19-diagnostico.md) | a tabela como primeira ferramenta; caso resolvido | interm.→avançado |
| [20-ipv6-e-ndp](20-ipv6-e-ndp.md) | o sucessor: NDP, NS/NA, SLAAC, o que mudou | avançado |
| [60-teoria-avancada](60-teoria-avancada.md) | N² do broadcast, o trilema, teorema de Rice | pesquisa |
| [65-estado-da-arte](65-estado-da-arte.md) | EVPN suppression, eBPF, versões — ago/2026 | pesquisa |

### Bloco C · Prática e erros
| Arquivo | O que é |
|---|---|
| [70-pratica](70-pratica.md) | 12 laboratórios progressivos + 4 desafios |
| [75-armadilhas](75-armadilhas.md) | armadilhas, 8 mitos e por que persistem |

### Bloco D · Economia e ecossistema
| Arquivo | O que é |
|---|---|
| [80-custos-e-licencas](80-custos-e-licencas.md) | tudo grátis; licenças, custos ocultos de lab/nuvem |
| [85-cursos-e-certificacoes](85-cursos-e-certificacoes.md) | cursos PT/EN/FR, certificações (com franqueza) |

### Bloco E · Fontes
| Arquivo | O que é |
|---|---|
| [90-bibliografia](90-bibliografia.md) | Kurose, Tanenbaum, Stevens, Sanders — comentados |
| [95-referencias](95-referencias.md) | RFCs, IEEE, código do kernel, docs, rastreabilidade |
| [GLOSSARIO](GLOSSARIO.md) | ~70 termos definidos |

---

## As 12 camadas de profundidade (onde cada uma vive)

1. Intuição p/ leigo → `01` · 2. Definição informal → `01`, `10` · 3. Por que existe → `11` ·
4. Ambiente e 1º uso → `03`, `04` · 5. Fundamentos formais → `10`, `12` · 6. Mecânica interna →
`13`, `14` · 7. Implementação prática → `06`, `07` · 8. Casos reais → `17` · 9. Trade-offs/
alternativas → `15`, `16`, `20` · 10. Economia → `80` · 11. Pesquisa → `60` · 12. Fronteira →
`65`. Nenhuma pulada.

---

## Status por bloco

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 27 documentos + projeto-modelo executável. Núcleo do 10 ao 65 completo.
- **Verificação:** saídas reais desta máquina (Ubuntu 22.04.5, iproute2 5.15.0); transições de
  estado NUD medidas segundo a segundo; `arpinspect` + **19 testes passando** contra a tabela
  real e o arquivo de spoofing. Versões, EVPN, cursos e RFC pesquisados na web em 14/08/2026.
- **Não executado (declarado):** comandos macOS/Windows/Cisco; captura (`tcpdump`/Wireshark) e
  varredura (`arp-scan`/`arping`) — exigem root, ausente no ambiente de escrita; labs de ataque
  (exigem lab isolado). MACs tiveram os 3 últimos octetos mascarados por privacidade da rede.
- **Pendente:** nada de estrutura. Reavaliar `65` e `03` a cada 6 meses; `80`/`85` a cada ano.
- *Última atualização: 14/08/2026*
