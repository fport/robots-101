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
            if parts.scheme or parts.netloc:
                continue
            if parts.path.startswith("/"):
                target = (ROOT / "site" / unquote(parts.path).lstrip("/")).resolve()
            else:
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


def wait_for_diagrams(page):
    try:
        page.wait_for_function("""() =>
        !document.querySelector('pre.workshop-diagram') &&
        [...document.querySelectorAll('figure.diagram')].every(figure =>
            figure.dataset.diagramReady === 'true' && figure.querySelector('svg[role="img"]'))
        """, timeout=20000)
    except Exception as exc:
        notes = page.locator(".diagram-error").all_text_contents()
        states = page.locator("figure.diagram").evaluate_all("figures => figures.map(f => f.dataset.diagramReady)")
        raise AssertionError(f"Diagram failed at {page.url}: {notes}; states={states}") from exc
    return page.locator("figure.diagram").count()


def main():
    pages = check_built_links()
    errors = []
    console_errors = []
    external_requests = []
    output = ROOT / "outputs/site-check"
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        def local_only(route):
            if urlsplit(route.request.url).hostname not in {"127.0.0.1", "localhost"}:
                external_requests.append(route.request.url)
                route.abort()
            else:
                route.continue_()
        page.route("http://**/*", local_only)
        page.route("https://**/*", local_only)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: console_errors.append({"text": message.text, "url": message.location.get("url", "")}) if message.type == "error" else None)
        failed_resources = {}
        def record_response(response):
            if response.status >= 400:
                failed_resources[response.url] = response.status
        page.on("response", record_response)
        page.goto(BASE, wait_until="load")
        assert page.locator("html").get_attribute("lang") == "tr"
        assert page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--neon').trim()") == "#b6ff00"
        page.screenshot(path=str(output / "desktop.png"), full_page=True)
        page.locator('label[for="__palette_1"]').click()
        page.wait_for_function("document.body.dataset.mdColorScheme === 'default'")
        page.locator('label[for="__palette_0"]').click()
        page.wait_for_function("document.body.dataset.mdColorScheme === 'slate'")
        page.locator('[data-md-component="search-query"]').fill("SmolVLA")
        page.wait_for_selector(".md-search-result__item", timeout=15000)
        search_results = page.locator(".md-search-result__item").count()
        page.goto(BASE + "/basla/sifirdan/", wait_until="load")
        assert wait_for_diagrams(page) == 1
        assert "GÖR / ÖLÇ" in page.locator("figure.diagram svg").text_content()
        dark_fill = page.locator("figure.diagram .node rect").first.evaluate("e => getComputedStyle(e).fill")
        page.locator("figure.diagram").screenshot(path=str(output / "diagram-tr-dark.png"))
        page.locator('label[for="__palette_1"]').click()
        page.wait_for_function("document.querySelector('figure.diagram').dataset.diagramTheme === 'default'")
        light_fill = page.locator("figure.diagram .node rect").first.evaluate("e => getComputedStyle(e).fill")
        assert dark_fill != light_fill
        page.locator("figure.diagram").screenshot(path=str(output / "diagram-tr-light.png"))
        page.locator('label[for="__palette_0"]').click()
        page.wait_for_function("document.querySelector('figure.diagram').dataset.diagramTheme === 'slate'")
        page.locator(".md-select button").hover()
        page.locator('.md-select__link[hreflang="en"]').click()
        page.wait_for_url(BASE + "/en/basla/sifirdan/")
        assert page.locator("html").get_attribute("lang") == "en"
        assert "new" in page.locator("h1").inner_text().lower()
        assert wait_for_diagrams(page) == 1
        assert "OBSERVE AGAIN" in page.locator("figure.diagram svg").text_content()
        page.goto(BASE + "/en/", wait_until="load")
        page.screenshot(path=str(output / "desktop-en.png"), full_page=True)
        assert "Start here" in page.locator(".md-tabs").inner_text()
        page.locator('[data-md-component="search-query"]').fill("friction")
        page.wait_for_selector(".md-search-result__item", timeout=15000)
        english_search_results = page.locator(".md-search-result__item").count()
        assert page.locator('.md-search-result__link[href*="simulasyon"]').count() > 0
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
        page.goto(BASE + "/en/temel/laboratuvar/", wait_until="load")
        assert "time steps" in page.locator("#dataset-result").inner_text()
        assert "30,000" in page.locator("#dataset-result").inner_text()
        page.locator("#episodes").fill("0")
        assert "positive" in page.locator("#dataset-result").inner_text()
        page.locator("#episodes").fill("50")
        page.locator("#chunk-steps").evaluate("e => { e.value=1; e.dispatchEvent(new Event('input')); }")
        assert "queue may run empty" in page.locator("#chunk-result").inner_text()
        assert "Tip:" in page.locator("#arm-result").inner_text()
        page.screenshot(path=str(output / "lab-en.png"), full_page=True)
        page.goto(BASE + "/basla/rota/", wait_until="load")
        page.locator("#p01").check()
        page.reload(wait_until="load")
        assert page.locator("#p01").is_checked()
        assert "1 / 12" in page.locator("#progress-summary").inner_text()
        page.goto(BASE + "/en/basla/rota/", wait_until="load")
        assert page.locator("#p01").is_checked()
        assert "1 / 12 milestones completed" in page.locator("#progress-summary").inner_text()
        page.locator("#learning-progress button").click()
        assert not page.locator("#p01").is_checked()
        page.goto(BASE + "/pratik/cozumlu-sorular/", wait_until="load")
        assert page.locator("details").count() == 16
        page.locator("details summary").first.click()
        assert page.locator("details").first.evaluate("e => e.open")
        page.goto(BASE + "/en/pratik/cozumlu-sorular/", wait_until="load")
        assert page.locator("details").count() == 16
        assert page.locator("details summary").first.inner_text() == "Solution"
        page.locator("details summary").first.click()
        assert page.locator("details").first.evaluate("e => e.open")
        page.goto(BASE + "/ogrenme/smolvla-ic-yapi/", wait_until="load")
        wait_for_diagrams(page)
        page.screenshot(path=str(output / "smolvla-deep.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        routes = sorted({"/" + path.parent.relative_to(ROOT / "site").as_posix().strip(".") + "/"
                         for path in (ROOT / "site").rglob("index.html")})
        routes = [route.replace("//", "/") for route in routes]
        diagrams_checked = 0
        for route in routes:
            page.goto(BASE + route, wait_until="load")
            diagrams_checked += wait_for_diagrams(page)
            expected_lang = "en" if route.startswith("/en/") else "tr"
            assert page.locator("html").get_attribute("lang") == expected_lang, route
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Yatay taşma: {route}"
            if route == "/basla/sifirdan/":
                page.locator("figure.diagram").screenshot(path=str(output / "diagram-tr-mobile.png"))
            if route == "/ogrenme/smolvla-ic-yapi/":
                canvas = page.locator(".diagram-canvas")
                assert canvas.evaluate("e => e.scrollWidth > e.clientWidth")
                canvas.focus()
                page.keyboard.press("ArrowRight")
                page.wait_for_function("document.querySelector('.diagram-canvas').scrollLeft > 0")
                canvas.screenshot(path=str(output / "diagram-wide-mobile.png"))
        page.goto(BASE, wait_until="load")
        page.screenshot(path=str(output / "mobile.png"), full_page=True)
        page.goto(BASE + "/en/", wait_until="load")
        page.screenshot(path=str(output / "mobile-en.png"), full_page=True)
        browser.close()
    # Material 9.7.7 assumes hreflang alternates are language roots, while
    # static-i18n 1.3.1 emits article URLs. Its optional sitemap probe therefore
    # receives 404s. Keep this existing integration issue visible in the report;
    # every other resource/console error and every runtime error must fail.
    alternate_sitemaps = {BASE + route + "sitemap.xml" for route in routes if route != "/"}
    known_sitemap_404s = {url for url, status in failed_resources.items()
                        if status == 404 and url in alternate_sitemaps}
    unexpected_resources = {url: status for url, status in failed_resources.items()
                            if url not in known_sitemap_404s}
    for message in console_errors:
        if (message["url"] in known_sitemap_404s and
                message["text"] == "Failed to load resource: the server responded with a status of 404 (Not Found)"):
            continue
        errors.append(f"{message['text']} ({message['url']})")
    assert not errors, sorted(set(errors))
    assert not unexpected_resources, unexpected_resources
    assert not external_requests, external_requests
    report = {"html_pages_checked": pages, "search_results": search_results,
              "english_search_results": english_search_results, "mobile_content_pages_checked": len(routes),
              "mermaid_diagrams_checked": diagrams_checked, "mermaid_theme_toggle": "pass",
              "mermaid_offline_rendering": "pass", "mermaid_keyboard_scroll": "pass",
              "language_switch_same_article": "pass", "english_lab": "pass", "neon_palette": "pass",
              "local_links_and_anchors": "pass", "kinematics": "pass", "dataset_calculator": "pass",
              "chunk_calculator": "pass", "theme_toggle": "pass",
              "worked_solutions_toggle": "pass",
              "progress_persistence_across_languages": "pass", "mobile_overflow": "pass", "browser_errors": errors,
              "known_resource_warnings": {"material_alternate_sitemap_404": sorted(known_sitemap_404s)}}
    (output / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
