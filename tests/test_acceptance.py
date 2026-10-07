"""Contrato dos entregáveis; executar após o laço gerar os arquivos."""
import csv
from decimal import Decimal
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MONTHS = [f"2026-{month:02d}" for month in range(1, 7)]
TOTAL = Decimal("931274.06")


def rows(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_join_conta_somente_vendas_com_loja_existente():
    joined = rows("vendas_lojas.csv")
    assert len(joined) == 420
    source = rows("vendas.csv")
    stores = {row["id_loja"] for row in rows("lojas.csv")}
    expected = {row["id_venda"] for row in source if row["id_loja"] in stores}
    actual = [row["id_venda"] for row in joined]
    assert len(actual) == len(set(actual))
    assert set(actual) == expected


def test_join_preserva_receita_sem_vendas_orfas():
    joined = rows("vendas_lojas.csv")
    assert sum(Decimal(row["receita_brl"]) for row in joined) == TOTAL
    assert "999" not in {row["id_loja"] for row in joined}
    orphan = [row for row in rows("vendas.csv") if row["id_loja"] == "999"]
    assert len(orphan) == 3
    assert sum(Decimal(row["receita_brl"]) for row in orphan) == Decimal("8120.00")


def test_loja_sem_venda_nao_ganha_registro_ficticio():
    stores = {row["id_loja"]: row for row in rows("lojas.csv")}
    assert stores["108"]["nome_loja"] == "Batel"
    assert "108" not in {row["id_loja"] for row in rows("vendas_lojas.csv")}


def test_pivot_tem_quatro_regioes_e_seis_meses():
    pivot = rows("pivot_receita.csv")
    assert len(pivot) == 4
    assert list(pivot[0]) == ["regiao", *MONTHS]
    assert {row["regiao"] for row in pivot} == {"Centro-Oeste", "Nordeste", "Sudeste", "Sul"}


def test_cada_celula_do_pivot_corresponde_as_vendas_da_regiao_e_mes():
    joined = rows("vendas_lojas.csv")
    stores = {row["id_loja"]: row["regiao"] for row in rows("lojas.csv")}
    pivot = rows("pivot_receita.csv")
    for region in pivot:
        for month in MONTHS:
            expected = sum((Decimal(row["receita_brl"]) for row in joined
                            if stores[row["id_loja"]] == region["regiao"]
                            and row["data"].startswith(month)), Decimal(0))
            assert Decimal(region[month]) == expected
    assert sum(Decimal(row[month]) for row in pivot for month in MONTHS) == TOTAL


def test_regiao_lider_e_conclusao_correspondem_aos_numeros():
    pivot = rows("pivot_receita.csv")
    totals = {row["regiao"]: sum(Decimal(row[month]) for month in MONTHS) for row in pivot}
    assert max(totals, key=totals.get) == "Sudeste"
    assert totals["Sudeste"] == Decimal("265077.49")
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    assert re.search(r"<svg\b|<canvas\b", page, re.I)
    paragraphs = re.findall(r"<p(?:\s[^>]*)?>(.*?)</p>", page, re.I | re.S)
    assert any(len(re.sub(r"<[^>]+>", "", paragraph).strip()) >= 300 for paragraph in paragraphs)
    assert "Sudeste" in page
