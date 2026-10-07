"""Conferir relatório no Chromium pelo orquestrador dentro do Docker."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto((ROOT / "index.html").as_uri())
        assert page.locator("svg").count() == 1
        assert page.locator("svg g.serie").count() == 4
        assert page.locator("svg circle").count() == 24
        assert not errors
        page.screenshot(path=str(ROOT / "browser-proof.png"), full_page=True)
        result = {
            "executado_por": "orquestrador no Docker, fora do sandbox interno do Codex",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "html_sha256": hashlib.sha256((ROOT / "index.html").read_bytes()).hexdigest(),
            "series": 4, "pontos": 24, "page_errors": errors,
            "screenshot": "browser-proof.png", "status": "passou",
        }
        (ROOT / "browser-proof.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(result, ensure_ascii=False))
        browser.close()


if __name__ == "__main__":
    main()
