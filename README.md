# Ralph Lab — contrato preparado

Dados sintéticos da aula, PRD dividido em quatro histórias e seis testes de aceitação. O pipeline será produzido pelo laço, não foi executado nem concluído neste preparo. Não há log fictício de execução.

O script upstream foi estendido com `--tool codex`, usando `codex exec --sandbox workspace-write`. As opções upstream de outros agentes não são necessárias. Referência: https://developers.openai.com/codex/noninteractive.

O aluno executa da raiz do workspace, conforme `../AGENTS.md`:

```bash
docker compose exec -w /home/alan/mestrado_agents/exercicios/ralph-lab autograde bash -o pipefail -c 'export PATH="$HOME/.local/bin:$PATH"; bash scripts/ralph/ralph.sh --tool codex 10 2>&1 | tee ralph-run.log'
```

Após cada rodada, confira uma falha real e registre a intervenção feita, se houver. Não altere os CSVs originais nem enfraqueça testes para ajustar números. Critérios: 420 vendas após inner join, receita R$ 931.274,06, pivot de quatro regiões e seis meses, gráfico com conclusão e pelo menos quatro testes verdes.

As três vendas sem loja não entram em região alguma; a loja 108, sem vendas, não ganha receita ou linha fictícia. O relatório não demonstra completude dos dados da empresa.

Este comando foi preparado e a sintaxe do script foi conferida; o funcionamento da CLI e de seu sandbox no Docker será demonstrado na execução, não presumido a partir deste README.

Execute `python pipeline.py` na raiz para gerar `vendas_lojas.csv`. O pipeline
usa a biblioteca padrão e soma receitas com `Decimal`, preservando os CSVs
originais. O inner join inclui 420 vendas, com receita de R$ 931.274,06.
As três vendas com `id_loja=999`, que somam R$ 8.120,00, ficam fora do
relatório por não terem loja cadastrada. A loja 108 (Batel) está cadastrada,
mas não participa do inner join porque não tem vendas; não se cria registro
fictício para ela. Pivot e gráfico serão implementados nas próximas histórias.
