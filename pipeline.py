"""Produz inner join e receita mensal por região, preservando as fontes."""

import csv
from decimal import Decimal
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MONTHS = [f"2026-{month:02d}" for month in range(1, 7)]


def brl(value):
    """Formata apenas a apresentação, mantendo os cálculos em Decimal."""
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def write_report(revenues, total, excluded, excluded_total, stores, joined):
    """Gera relatório independente de serviços externos a partir da agregação."""
    totals = {region: sum(values.values(), Decimal(0)) for region, values in revenues.items()}
    leader = max(totals, key=totals.get)
    ceiling = (max(value for values in revenues.values() for value in values.values())
               / Decimal(10000)).to_integral_value(rounding="ROUND_CEILING") * Decimal(10000)
    colors = ["#2563eb", "#b45309", "#047857", "#a21caf"]
    parts = ['<svg viewBox="0 0 900 420" role="img" aria-labelledby="chart-title chart-desc">',
             '<title id="chart-title">Receita mensal por região</title>',
             '<desc id="chart-desc">Quatro séries de janeiro a junho de 2026. Eixo vertical: receita em reais.</desc>']
    for step in range(6):
        value = ceiling * Decimal(step) / Decimal(5)
        y = 330 - step * 54
        parts.append(f'<path d="M100 {y} H840" stroke="#d1d5db"/><text x="90" y="{y + 5}" text-anchor="end">{brl(value)}</text>')
    for index, month in enumerate(MONTHS):
        parts.append(f'<text x="{100 + index * 148}" y="357" text-anchor="middle">{month}</text>')
    parts.append('<text x="100" y="30">Receita (R$)</text>')
    for index, (region, values) in enumerate(revenues.items()):
        color = colors[index % len(colors)]
        points = [(100 + month_index * 148, Decimal(330) - value / ceiling * Decimal(270), month, value)
                  for month_index, (month, value) in enumerate(values.items())]
        coordinates = " ".join(f"{x},{y:.2f}" for x, y, _, _ in points)
        parts.append(f'<g class="serie" aria-label="{escape(region)}"><polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="3"/>')
        for x, y, month, value in points:
            parts.append(f'<circle cx="{x}" cy="{y:.2f}" r="5" fill="{color}"><title>{escape(region)} · {month}: R$ {brl(value)}</title></circle>')
        parts.append(f'</g><text x="{100 + index * 195}" y="399" fill="{color}">{escape(region)}</text>')
    parts.append('</svg>')
    participating = {row["id_loja"] for row in joined}
    idle = "; ".join(f"{store['id_loja']} ({store['nome_loja']})" for store in stores
                     if store["id_loja"] not in participating)
    conclusion = (
        f"Entre janeiro e junho de 2026, o inner join reúne {len(joined)} vendas e conserva "
        f"R$ {brl(total)} no pivot de {len(revenues)} regiões e seis meses. "
        f"{leader} lidera a receita acumulada com R$ {brl(totals[leader])}. "
        f"As {len(excluded)} vendas sem loja cadastrada somam R$ {brl(excluded_total)} e foram "
        "excluídas: essa receita não é zero e não pode ser atribuída a uma região com estas fontes. "
        f"Já a loja {idle} está cadastrada, mas não tem vendas nas fontes; "
        "ela não recebe linha fictícia no inner join. Os dados são sintéticos e o relatório "
        "descreve apenas a cobertura das fontes disponíveis, sem demonstrar completude dos dados da empresa."
    )
    table = '<table><caption>Receita mensal em R$</caption><thead><tr><th>Região</th>'
    table += ''.join(f'<th scope="col">{month}</th>' for month in MONTHS) + '</tr></thead><tbody>'
    for region, values in revenues.items():
        table += f'<tr><th scope="row">{escape(region)}</th>'
        table += ''.join(f'<td>{brl(value)}</td>' for value in values.values()) + '</tr>'
    table += '</tbody></table>'
    page = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Receita mensal por região</title><style>
body {{font-family:system-ui,sans-serif;color:#172033;background:#f3f4f6;margin:0;padding:24px}}
main {{max-width:1000px;margin:auto;background:white;padding:28px;border-radius:12px}}
h1 {{margin-top:0}} svg {{width:100%;height:auto}} svg text {{font-size:15px}}
p {{line-height:1.7}} .tabela {{overflow-x:auto}} table {{border-collapse:collapse;width:100%;font-size:14px}}
th,td {{padding:10px;text-align:right;border-bottom:1px solid #ddd}} th:first-child {{text-align:left}}
caption {{text-align:left;padding:12px 0;font-weight:bold}}
@media(max-width:600px) {{body {{padding:8px}} main {{padding:16px}}}}
</style></head><body><main><h1>Receita mensal por região</h1>
<p>Dados sintéticos · Janeiro a junho de 2026 · Valores em reais</p>
{''.join(parts)}<div class="tabela">{table}</div>
<h2>Conclusão e cobertura</h2><p>{escape(conclusion)}</p>
</main></body></html>
'''
    (ROOT / "index.html").write_text(page, encoding="utf-8")


def read_csv(path):
    """Lê cabeçalho e registros sem modificar o arquivo de origem."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def main():
    sale_fields, sales = read_csv(ROOT / "vendas.csv")
    store_fields, stores = read_csv(ROOT / "lojas.csv")
    stores_by_id = {store["id_loja"]: store for store in stores}
    if len(stores_by_id) != len(stores):
        raise ValueError("id_loja duplicado no cadastro de lojas")

    joined = []
    excluded = []
    for sale in sales:
        store = stores_by_id.get(sale["id_loja"])
        if store is None:
            excluded.append(sale)
            continue
        joined.append({**sale, **store})

    fields = sale_fields + [field for field in store_fields if field not in sale_fields]
    with (ROOT / "vendas_lojas.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(joined)

    total = sum((Decimal(row["receita_brl"]) for row in joined), Decimal(0))
    excluded_total = sum((Decimal(row["receita_brl"]) for row in excluded), Decimal(0))
    revenues = {region: {month: Decimal(0) for month in MONTHS}
                for region in sorted({row["regiao"] for row in joined})}
    for row in joined:
        revenues[row["regiao"]][row["data"][:7]] += Decimal(row["receita_brl"])
    with (ROOT / "pivot_receita.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["regiao", *MONTHS])
        writer.writeheader()
        for region, monthly in revenues.items():
            writer.writerow({"regiao": region,
                             **{month: f"{monthly_value:.2f}" for month, monthly_value in monthly.items()}})
    regional_totals = {region: sum(monthly.values(), Decimal(0))
                       for region, monthly in revenues.items()}
    if sum(regional_totals.values(), Decimal(0)) != total:
        raise ValueError("Pivot não conserva a receita do inner join")
    leader = max(regional_totals, key=regional_totals.get)
    write_report(revenues, total, excluded, excluded_total, stores, joined)
    print("Relatório: index.html; gráfico SVG com quatro séries e seis meses")
    print(f"Pivot: {len(revenues)} regiões; {len(MONTHS)} meses; receita_brl={total:.2f}")
    print(f"Região líder: {leader}; receita_brl={regional_totals[leader]:.2f}")
    print(f"Inner join: {len(joined)} vendas; receita_brl={total:.2f}")
    print(f"Vendas sem loja: {len(excluded)}; receita excluída={excluded_total:.2f}")
    participating = {row["id_loja"] for row in joined}
    for store in stores:
        if store["id_loja"] not in participating:
            print(f"Loja sem vendas no inner join: {store['id_loja']} {store['nome_loja']}")


if __name__ == "__main__":
    main()
