# Receita mensal por região — Ralph Lab

Pipeline produzido pelo laço Ralph com Codex em Docker. As quatro histórias foram concluídas em seis iterações, com oito testes verdes e relatório conferido no Chromium. Os dados são sintéticos da aula; as fontes originais permanecem intactas.

## Executar e conferir

```bash
python3 pipeline.py
python3 -m pytest -q
```

Geram-se `vendas_lojas.csv`, `pivot_receita.csv` e `index.html` na raiz. Os cálculos usam Decimal; o inner join inclui 420 vendas e R$ 931.274,06. O pivot tem quatro regiões e seis meses, conserva esse total e identifica Sudeste como líder, R$ 265.077,49.

As três vendas com id_loja=999 não têm cadastro correspondente: R$ 8.120,00 ficam fora de todas as regiões. A loja 108 (Batel) existe no cadastro, mas não tem vendas e não recebe linha fictícia. O Sul representa lojas com vendas observadas, não todas as lojas cadastradas. Ausência de registros não comprova cobertura completa da operação.

## Laço e evidências

Da raiz do workspace:

```bash
bash scripts/executar-ralph-docker.sh 10
```

O helper constrói o ambiente específico e inicia container efêmero compatível com bubblewrap. Codex usa `--sandbox workspace-write`; o orquestrador grava commits por iteração. Os artefatos estáveis e os hashes das fontes são verificados antes da conclusão. `COMPLETE` só é aceito no resultado final, com todas as histórias aprovadas e pytest verde; a presença da palavra no prompt não basta.

O script `scripts/ralph/check_browser.py` verifica o HTML no Chromium fora do sandbox interno, ainda no Docker, e produz `browser-proof.json` e `browser-proof.png`. O JSON associa a captura ao hash do HTML, quatro séries,24pontos e ausência de erro de página. Falhas reais de ambiente e suas correções estão preservadas em `ralph-run.log` e `scripts/ralph/progress.txt`; a condução foi automática, sem atribuir intervenções manuais ao aluno.
