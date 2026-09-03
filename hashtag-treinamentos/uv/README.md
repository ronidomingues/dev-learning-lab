# UV

Este documento apresenta um resumo detalhado sobre a ferramenta **UV** (desenvolvida pela Astral), considerada uma das soluções mais modernas, eficientes e rápidas para o gerenciamento de ambientes e pacotes em Python.

---

## Sumario

- [UV](#uv)
  - [Sumario](#sumario)
  - [1. Introdução ao UV e sua Proposta](#1-introdução-ao-uv-e-sua-proposta)
  - [2. Instalação do UV](#2-instalação-do-uv)
  - [3. Criação e Inicialização de Projetos (`uv init`)](#3-criação-e-inicialização-de-projetos-uv-init)
  - [4. Gerenciamento de Ambientes Virtuais e Dependências](#4-gerenciamento-de-ambientes-virtuais-e-dependências)
  - [5. Execução de Scripts (`uv run`)](#5-execução-de-scripts-uv-run)
  - [6. Controle de Versões do Python (`uv python`)](#6-controle-de-versões-do-python-uv-python)
  - [7. Conclusão e Benefícios](#7-conclusão-e-benefícios)

---

## 1. Introdução ao UV e sua Proposta

O **UV** é uma ferramenta escrita em **Rust** projetada para unificar e substituir de forma extremamente rápida diversas ferramentas tradicionais do ecossistema Python, tais como:

* `pip` e `pip-tools`
* `pipx`
* `poetry`
* `pyenv`
* `virtualenv`
* `twine`

A principal vantagem do UV é a sua **velocidade impressionante**, otimizando fluxos de trabalho para desenvolvimento web, APIs, automações e análise de dados.

---

## 2. Instalação do UV

* Utilizando o `pip` tradicional.

    ```bash
    pip install uv
    ```

* Através do **instalador oficial** recomendado para maior facilidade e performance em diferentes sistemas operacionais (Windows, macOS e Linux).

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh >> install_uv.sh

    chmod +x install_uv.sh

    ./install_uv.sh
    ```

---

## 3. Criação e Inicialização de Projetos (`uv init`)

Para iniciar um novo projeto do zero utilizando o UV:

1. Executa-se o comando `uv init` no terminal.
2. O UV gera automaticamente uma estrutura padrão e limpa de arquivos essenciais:

* `.gitignore`
* `main.py` (arquivo de entrada padrão)
* `pyproject.toml` (centralizador de configurações e dependências do projeto)

---

## 4. Gerenciamento de Ambientes Virtuais e Dependências

O UV simplifica drasticamente a rotina de gerenciamento de pacotes:

* **Adicionar bibliotecas:** O comando `uv add <nome_da_biblioteca>` instala o pacote e já o registra de forma automática no arquivo de configuração (`pyproject.toml`).
* **Remover bibliotecas:** O comando `uv remove <nome_da_biblioteca>` desinstala a dependência e atualiza os arquivos do projeto.
* **Sincronização:** O comando `uv sync` garante que o ambiente virtual esteja perfeitamente alinhado com as especificações do `pyproject.toml` ou arquivos legados como `requirements.txt`.

---

## 5. Execução de Scripts (`uv run`)

Com o comando `uv run`, é possível executar scripts e ferramentas de desenvolvimento (como linters e formatadores, por exemplo, Ruff ou Pyright) sem a necessidade de ativar manualmente o ambiente virtual (`activate`), tornando a execução direta e ágil.

---

## 6. Controle de Versões do Python (`uv python`)

O UV também assume o papel de gerenciador de versões do interpretador Python (`uv python`), permitindo baixar, alternar e controlar facilmente diferentes versões do Python de maneira isolada para cada projeto.

---

## 7. Conclusão e Benefícios

O uso do UV traz diversas vantagens para desenvolvedores Python:

* Organização centralizada.
* Previsibilidade e padronização.
* Agilidade extrema devido à sua implementação em Rust.
* Simplificação de fluxos complexos que antes exigiam múltiplos utilitários separados.
