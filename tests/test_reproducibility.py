"""Verifica repetibilidade e correspondência do gráfico com os dados publicados."""

import csv
from decimal import Decimal
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ("vendas_lojas.csv", "pivot_receita.csv", "index.html")
SOURCES = ("vendas.csv", "lojas.csv")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_pipeline_repetido_preserva_fontes_e_reproduz_tres_artefatos(tmp_path):
    for name in ("pipeline.py", *SOURCES):
        shutil.copyfile(ROOT / name, tmp_path / name)
    original = {name: digest(tmp_path / name) for name in SOURCES}
    snapshots = []
    for _ in range(2):
        result = subprocess.run(
            [sys.executable, str(tmp_path / "pipeline.py")],
            cwd=tmp_path, capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        snapshots.append({name: (tmp_path / name).read_bytes() for name in OUTPUTS})
        assert {name: digest(tmp_path / name) for name in SOURCES} == original
    assert snapshots[0] == snapshots[1]
    assert snapshots[1] == {name: (ROOT / name).read_bytes() for name in OUTPUTS}


class ChartParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.region = None
        self.points = {}
        self.in_title = False
        self.title = ""
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "g" and attrs.get("class") == "serie":
            self.region = attrs["aria-label"]
            self.points[self.region] = []
        if tag == "circle" and self.region:
            self.points[self.region].append(None)
        if tag == "title" and self.region:
            self.in_title = True
            self.title = ""

    def handle_data(self, data):
        self.labels.append(data)
        if self.in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "title" and self.in_title:
            self.points[self.region][-1] = self.title
            self.in_title = False
        if tag == "g":
            self.region = None


def test_grafico_tem_series_meses_e_valores_correspondentes_ao_pivot():
    with (ROOT / "pivot_receita.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        months = reader.fieldnames[1:]
        pivot = list(reader)
    chart = ChartParser()
    chart.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    assert set(chart.points) == {row["regiao"] for row in pivot}
    assert len(chart.points) == 4
    assert len(months) == 6
    for month in months:
        assert month in chart.labels
    for row in pivot:
        titles = chart.points[row["regiao"]]
        assert len(titles) == 6
        for month, title in zip(months, titles):
            prefix = f"{row['regiao']} · {month}: R$ "
            assert title.startswith(prefix)
            value = Decimal(title[len(prefix):].replace(".", "").replace(",", "."))
            assert value == Decimal(row[month])
