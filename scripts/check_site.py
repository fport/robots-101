"""Çalışan yerel MkDocs sitesini Chrome ile sınar. pip install playwright gerekir."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from html.parser import HTMLParser
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])


def check_built_links():
    pages = {}
    for path in (ROOT / "site").rglob("*.html"):
        parser = Links()
        parser.feed(path.read_text())
        pages[path.resolve()] = parser
    failures = set()
    for path, parser in pages.items():
        for href in parser.links:
            parts = urlsplit(href)
            if parts.scheme or parts.netloc or href.startswith("/"):
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            if target.is_dir():
                target /= "index.html"
            if not target.exists():
                failures.add(f"{path.relative_to(ROOT)} -> {href}")
            elif parts.fragment and target in pages and unquote(parts.fragment) not in pages[target].ids:
                failures.add(f"Eksik anchor: {path.relative_to(ROOT)} -> {href}")
    if failures:
        raise AssertionError("\n".join(sorted(failures)))
    return len(pages)


def main():
    pages = check_built_links()
    errors = []
    output = ROOT / "outputs/site-check"
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(BASE, wait_until="load")
        page.screenshot(path=str(output / "desktop.png"), full_page=True)
        page.locator('label[for="__palette_1"]').click()
        page.wait_for_function("document.body.dataset.mdColorScheme === 'default'")
        page.locator('label[for="__palette_0"]').click()
        page.wait_for_function("document.body.dataset.mdColorScheme === 'slate'")
        page.locator('[data-md-component="search-query"]').fill("SmolVLA")
        page.wait_for_selector(".md-search-result__item", timeout=15000)
        search_results = page.locator(".md-search-result__item").count()
        page.goto(BASE + "/temel/laboratuvar/", wait_until="load")
        page.locator("#joint-a").evaluate("e => { e.value=0; e.dispatchEvent(new Event('input')); }")
        page.locator("#joint-b").evaluate("e => { e.value=0; e.dispatchEvent(new Event('input')); }")
        assert "32.0 cm" in page.locator("#arm-result").inner_text()
        page.locator("#episodes").fill("0")
        assert "Pozitif" in page.locator("#dataset-result").inner_text()
        page.locator("#episodes").fill("50")
        assert "30.000" in page.locator("#dataset-result").inner_text()
        page.locator("#chunk-steps").evaluate("e => { e.value=50; e.dispatchEvent(new Event('input')); }")
        assert "1.67 s" in page.locator("#chunk-result").inner_text()
        page.locator("#chunk-steps").evaluate("e => { e.value=1; e.dispatchEvent(new Event('input')); }")
        assert "kuyruk boşalabilir" in page.locator("#chunk-result").inner_text()
        page.screenshot(path=str(output / "lab.png"), full_page=True)
        page.goto(BASE + "/basla/rota/", wait_until="load")
        page.locator("#p01").check()
        page.reload(wait_until="load")
        assert page.locator("#p01").is_checked()
        assert "1 / 12" in page.locator("#progress-summary").inner_text()
        page.locator("#learning-progress button").click()
        assert not page.locator("#p01").is_checked()
        page.goto(BASE + "/pratik/cozumlu-sorular/", wait_until="load")
        assert page.locator("details").count() == 16
        page.locator("details summary").first.click()
        assert page.locator("details").first.evaluate("e => e.open")
        page.goto(BASE + "/ogrenme/smolvla-ic-yapi/", wait_until="load")
        page.screenshot(path=str(output / "smolvla-deep.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        for route in ["/", "/temel/laboratuvar/", "/ogrenme/smolvla/",
                      "/basla/derinlik/", "/temel/kinematik-ik/", "/simulasyon/denetleyici/",
                      "/donanim/kamera-kalibrasyonu/", "/ogrenme/veri-muhendisligi/",
                      "/ogrenme/smolvla-ic-yapi/", "/ogrenme/egitim-deneyleri/",
                      "/pratik/cozumlu-sorular/"]:
            page.goto(BASE + route, wait_until="load")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Yatay taşma: {route}"
        page.goto(BASE, wait_until="load")
        page.screenshot(path=str(output / "mobile.png"), full_page=True)
        browser.close()
    assert not errors, errors
    report = {"html_pages_checked": pages, "search_results": search_results,
              "local_links_and_anchors": "pass", "kinematics": "pass", "dataset_calculator": "pass",
              "chunk_calculator": "pass", "theme_toggle": "pass",
              "worked_solutions_toggle": "pass",
              "progress_persistence": "pass", "mobile_overflow": "pass", "browser_errors": errors}
    (output / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
