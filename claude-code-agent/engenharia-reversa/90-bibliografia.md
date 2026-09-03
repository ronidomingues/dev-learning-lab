# 90 · Bibliografia comentada

**Nível:** todos · **Data:** 03/09/2026

Livros com autor, título, editora e edição/ano. Para cada um: **nível**, o que faz melhor, e se
envelheceu. Marco o que é **legalmente gratuito** (autor liberou). **Não invento ISBN nem
edição**; na dúvida, cito só autor e título e digo que é aproximado.

---

## Fundamentos (leia antes ou junto)

- **Randal E. Bryant & David R. O'Hallaron — *Computer Systems: A Programmer's Perspective*
  (CS:APP), 3ª ed., Pearson, 2015.** *Nível: iniciante→interm.*
  A melhor fundação para entender o que você reverte: como C vira máquina, pilha, ligação,
  memória virtual. **Não é** um livro de RE, mas talvez o mais útil *para* RE. Envelhece pouco
  (x86-64). Há material do curso (CMU 15-213) aberto online.

- **Jeff Duntemann — *Assembly Language Step-by-Step: Programming with Linux*, 3ª ed., Wiley,
  2009.** *Nível: iniciante.* Assembly x86 do zero, didático. Um pouco datado (32-bit forte),
  mas ótimo para a intuição inicial.

- **Randall Hyde — *The Art of Assembly Language*, 2ª ed., No Starch, 2010.** *Nível:
  interm.* Referência densa de assembly. Versões antigas circulam **gratuitamente** (o autor
  liberou edições históricas). Bom como consulta, não como primeira leitura.

- **Henry S. Warren Jr. — *Hacker's Delight*, 2ª ed., Addison-Wesley, 2012.** *Nível: avançado.*
  Truques de bits e aritmética — inclusive a "divisão por constante mágica" que você vê no
  assembly otimizado ([`14`](14-analise-estatica.md)). Clássico atemporal.

---

## Engenharia reversa (o núcleo)

- **Dennis Yurichev — *Reverse Engineering for Beginners* (também publicado como *Understanding
  Assembly Language*).** *Nível: iniciante→interm.* **LEGALMENTE GRATUITO** — o autor
  disponibiliza o PDF completo (~1000+ páginas) em beginners.re/, atualizado ao longo dos anos.
  Cobre x86/x64/ARM, muitos exemplos comparando C↔assembly em vários compiladores. **Melhor
  custo-benefício absoluto** (custo zero). Comece por ele junto com o CERO ([`85`](85-cursos-e-certificacoes.md)).

- **Dennis Andriesse — *Practical Binary Analysis*, No Starch, 2018.** *Nível: interm.→avançado.*
  Foco em Linux/ELF, ferramentas e construção das suas próprias (desmontagem, instrumentação
  binária, execução simbólica com Capstone/PIN/angr). Prático e moderno. **Recomendado** para
  quem quer automatizar. Envelhece bem.

- **Chris Eagle & Kara Nance — *The Ghidra Book: The Definitive Guide*, No Starch, 2020.**
  *Nível: interm.* A referência de Ghidra. O Ghidra evoluiu (versão 12.x em 2026), então
  algumas telas/detalhes mudaram, mas os conceitos seguem válidos. Complemente com a doc oficial.

- **Chris Eagle — *The IDA Pro Book*, 2ª ed., No Starch, 2011.** *Nível: interm.* Clássico da
  IDA. Datado quanto à interface (a IDA mudou muito, virou assinatura em 2024), mas ainda
  ensina *como pensar* em desmontagem interativa. Leia se for usar IDA; senão, prefira o Ghidra Book.

---

## Análise de malware

- **Michael Sikorski & Andrew Honig — *Practical Malware Analysis*, No Starch, 2012.**
  *Nível: interm.* **O livro-texto do campo.** Método completo (estático/dinâmico, laboratório,
  anti-análise) com labs. Foco em Windows x86 de 2012 — a plataforma envelheceu, o **método
  não**. Ainda é a recomendação nº 1 para malware. Leia mesmo em 2026.

- **Monnappa K A — *Learning Malware Analysis*, Packt, 2018.** *Nível: iniciante→interm.*
  Mais recente que o Sikorski, com memória forense (Volatility) e exemplos modernos. Boa
  ponte prática.

- **Michael Ligh et al. — *The Art of Memory Forensics*, Wiley, 2014.** *Nível: avançado.*
  Forense de memória (Volatility). Especializado, mas essencial se você vai para DFIR/malware.

---

## Exploração e vulnerabilidades (ponte com [`21`](21-vulnerabilidades.md))

- **Jon Erickson — *Hacking: The Art of Exploitation*, 2ª ed., No Starch, 2008.** *Nível:
  iniciante→interm.* Ensina os fundamentos de overflow/shellcode de forma hands-on, com um
  LiveCD. Datado (pré-mitigations modernas), mas **excelente para a intuição** de como um bug
  vira controle. Um clássico.

- **Chris Anley et al. — *The Shellcoder's Handbook*, 2ª ed., Wiley, 2007.** *Nível: avançado.*
  Referência histórica de exploração. Datado, mas fundacional. Use com material moderno sobre
  ROP/ASLR.

- **Allen Harper et al. — *Gray Hat Hacking: The Ethical Hacker's Handbook*, 6ª ed.,
  McGraw-Hill, 2022.** *Nível: interm.→avançado.* Amplo e atualizado; cobre RE, exploração e
  ferramentas modernas. Bom panorama recente.

---

## Sistemas e internals (para reverter fundo)

- **Mark Russinovich, David Solomon, Alex Ionescu — *Windows Internals*, 7ª ed. (2 vols.),
  Microsoft Press, 2017/2021.** *Nível: avançado.* Indispensável para reverter software e
  malware **Windows** a sério. Denso, de consulta.

- **Bruce Dang, Alexandre Gazet, Elias Bachaalany — *Practical Reverse Engineering*, Wiley,
  2014.** *Nível: avançado.* x86/x64/ARM, kernel, virtualização, desofuscação. Mais avançado e
  ainda muito relevante. **Recomendado** após o básico.

---

## Como escolher (trilha de leitura)

1. **Base:** CS:APP (ou o curso 15-213) + Yurichev (grátis).
2. **RE prático:** Practical Binary Analysis + The Ghidra Book.
3. **Malware:** Practical Malware Analysis (+ Learning Malware Analysis).
4. **Exploração:** Hacking: The Art of Exploitation → material moderno de ROP.
5. **Avançado:** Practical Reverse Engineering + Windows Internals (se for Windows).

**Clássicos que continuam valendo:** CS:APP, Yurichev, Practical Malware Analysis (pelo método),
Hacker's Delight. **Datados (leia com ressalva de plataforma/interface):** IDA Pro Book,
Shellcoder's Handbook, Art of Exploitation (mitigations), telas do Ghidra Book.

**Traduções em português:** *Hacking: A Arte da Exploração* teve edição em PT (Alta Books);
*Análise Prática de Malware* / títulos da No Starch aparecem por editoras nacionais em
qualidade variável — quando possível, prefira o original em inglês, que é a língua-franca do
campo e recebe correções. (Não afirmo ISBNs específicos das traduções por não os ter conferido.)

---

## Autoteste

1. Qual livro é **legalmente gratuito**, e por que é o melhor custo-benefício para começar?
2. Practical Malware Analysis é de 2012. Por que ainda é a recomendação nº 1?
3. Qual livro você usaria para **automatizar** análise em Linux/ELF?
4. Um livro "datado" ainda pode valer a pena? Dê um exemplo e diga o que aproveitar dele.
5. Que livro **não** é sobre RE mas é talvez o mais útil *para* RE, e por quê?
6. Monte uma trilha de 3 livros do zero à análise de malware.
