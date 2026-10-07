# PRD: Receita regional de vendas sintéticas

## Contexto e objetivos

O enunciado de ia-3.1 define entradas, saídas e conferências: transformar duas tabelas sintéticas em inner join, pivot e gráfico. Não há decisão pessoal pendente sobre a especificação. O aluno conduz o loop Ralph e registra suas intervenções reais; este agente prepara os requisitos.

## Histórias

### US-001: Ler entradas e produzir inner join

Como leitor do relatório, quero juntar vendas às lojas existentes para atribuir receita à região correta.

- [ ] Ler os CSVs originais sem editar ou excluir nenhuma linha de origem.
- [ ] Gerar vendas_lojas.csv na raiz com exatamente 420 linhas de dados e coluna receita_brl.
- [ ] Somar Decimal(receita_brl) e obter 931274.06; excluir três vendas id_loja=999 e documentar 8120.00 fora do relatório.
- [ ] Registrar que loja 108 Batel não participa do inner join por não ter vendas.
- [ ] Typecheck passes: python -m compileall -q pipeline.py tests
- [ ] Tests pass: executar os testes pertinentes; ao final toda a suíte deve passar.

### US-002: Agregar receita por região e mês

Como analista, quero conferir receitas mensais sem duplicar vendas.

- [ ] Gerar pivot_receita.csv na raiz com cabeçalho exato regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06.
- [ ] Entregar quatro regiões e seis meses, números com ponto decimal e duas casas, sem símbolo monetário.
- [ ] Conservar o total 931274.06 e identificar Sudeste como líder com 265077.49.
- [ ] Typecheck passes: python -m compileall -q pipeline.py tests
- [ ] Tests pass: executar os testes pertinentes; ao final toda a suíte deve passar.

### US-003: Publicar gráfico estático e concluir

Como leitor, quero visualizar a receita mensal e entender o limite da cobertura.

- [ ] Gerar index.html na raiz com gráfico SVG rotulado, seis meses e quatro séries de região.
- [ ] Incluir parágrafo de conclusão de pelo menos 300 caracteres ancorado nos números produzidos.
- [ ] A conclusão deve distinguir loja sem venda das vendas sem loja e não afirmar que a receita descartada era zero.
- [ ] Verificar a página no Chromium do Playwright; dev-browser não está instalado neste ambiente.
- [ ] Typecheck passes: python -m compileall -q pipeline.py tests
- [ ] Tests pass: executar os testes pertinentes; ao final toda a suíte deve passar.

### US-004: Concluir verificações reproduzíveis

Como aluno, quero saber quando o pipeline está pronto por evidências verificáveis.

- [ ] Pelo menos quatro testes reais em tests/test_*.py devem passar em python -m pytest -q.
- [ ] Testar contagem e receita do join, cabeçalho e forma do pivot, conservação da receita e gráfico.
- [ ] Garantir execução repetida produzindo os mesmos três arquivos e registrar comandos e resultados no progress.txt.
- [ ] Só emitir COMPLETE após todas as histórias e verificações concluídas; não inventar falhas nem relatos do aluno.
- [ ] Typecheck passes: python -m compileall -q pipeline.py tests
- [ ] Tests pass: executar os testes pertinentes; ao final toda a suíte deve passar.

## Requisitos funcionais

FR-1: preservar as entradas originais. FR-2: gerar os três arquivos na raiz. FR-3: tratar valores monetários sem perdas de arredondamento intermediário. FR-4: manter aprendizado e estado entre iterações em scripts/ralph/.

## Escopo e tecnologia

Pipeline Python, biblioteca padrão csv e Decimal, pytest para verificar invariantes e SVG estático para o gráfico. Sem banco, API externa, dados reais ou publicação de credenciais. Executar evidências no Docker.

## Sucesso e pendências

As saídas devem cumprir as contas publicadas e os testes. Falta execução real do loop pelo aluno e seu relato de uma falha e ajuste realmente ocorridos, sem simulação de entrevista.
