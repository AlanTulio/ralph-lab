"""Produz o inner join dos CSVs sintéticos, preservando as fontes."""

import csv
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parent


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
    print(f"Inner join: {len(joined)} vendas; receita_brl={total:.2f}")
    print(f"Vendas sem loja: {len(excluded)}; receita excluída={excluded_total:.2f}")
    participating = {row["id_loja"] for row in joined}
    for store in stores:
        if store["id_loja"] not in participating:
            print(f"Loja sem vendas no inner join: {store['id_loja']} {store['nome_loja']}")


if __name__ == "__main__":
    main()
