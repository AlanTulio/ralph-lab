"""Produz inner join e receita mensal por região, preservando as fontes."""

import csv
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MONTHS = [f"2026-{month:02d}" for month in range(1, 7)]


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
