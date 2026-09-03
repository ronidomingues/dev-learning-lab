# Especificação — `portao`

## Objetivo

Uma ferramenta de linha de comando que recebe um *diff* e decide, de forma
determinística, se aquela mudança pode entrar no repositório. Feita para
verificar código produzido por agentes de IA, mas indiferente à origem: ela
verifica o *diff*, não quem o escreveu.

## Restrições

- Python 3.10+, **somente biblioteca padrão**. Zero dependências.
- Nenhum acesso à rede sem `--online` explícito.
- Nunca modifica arquivo nenhum. Só lê e relata.
- Código de saída: `0` aprovado, `1` reprovado, `2` erro de uso.

## Critérios de aceitação

- **CA-01** O leitor de *diff* identifica os arquivos alterados e as linhas
  adicionadas, com o número de linha correto no arquivo de destino.
- **CA-02** O leitor distingue arquivo novo de arquivo removido.
- **CA-03** A regra de escopo reprova arquivo fora de `escopo_permitido`.
- **CA-04** A regra de escopo reprova alteração em arquivo de teste, exceto
  quando `testes_editaveis` estiver ligado.
- **CA-05** A regra de tamanho reprova *diff* acima do limite total de linhas
  alteradas.
- **CA-06** A regra de tamanho apenas **avisa** quando um único arquivo passa
  do limite por arquivo, sem bloquear.
- **CA-07** A regra de segredos detecta chave privada e tokens de formato
  conhecido em linhas adicionadas.
- **CA-08** A regra de segredos ignora valores de exemplo e respeita o escape
  `portao: ignora-segredo`.
- **CA-09** A regra de pacotes reprova, sem rede, qualquer dependência
  adicionada que não esteja na lista aprovada.
- **CA-10** A regra de critérios reprova todo critério da especificação que não
  seja citado por nenhum arquivo de teste.
- **CA-11** A CLI devolve `0` quando aprovado e `1` quando reprovado.
- **CA-12** Configuração inválida é rejeitada com mensagem clara e código `2`.

## Fora de escopo

Corrigir o que encontrar; integração com GitHub; interface gráfica; análise
semântica do código (isso é trabalho de linter e de humano).
