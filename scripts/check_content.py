"""Check complete TR/EN coverage, navigation and documented example flags."""
import ast
from pathlib import Path
import re
import shlex

import yaml

ROOT = Path(__file__).resolve().parents[1]


class ConfigLoader(yaml.SafeLoader):
    """Read the known SuperFences tag as data, without importing/executing it."""


ConfigLoader.add_constructor(
    "tag:yaml.org,2002:python/name:pymdownx.superfences.fence_code_format",
    lambda loader, node: "pymdownx.superfences.fence_code_format",
)


def main():
    docs = ROOT / "docs"
    turkish = {p.relative_to(docs).as_posix() for p in docs.rglob("*.md") if not p.name.endswith(".en.md")}
    english = {p.relative_to(docs).as_posix().replace(".en.md", ".md") for p in docs.rglob("*.en.md")}
    assert turkish == english, {"missing_en": sorted(turkish-english), "missing_tr": sorted(english-turkish)}
    diagram_count = 0
    for name in sorted(turkish):
        tr = (docs / name).read_text()
        en = (docs / name.replace(".md", ".en.md")).read_text()
        pattern = r"```mermaid\n(.*?)```"
        tr_diagrams, en_diagrams = re.findall(pattern, tr, re.S), re.findall(pattern, en, re.S)
        assert len(tr_diagrams) == len(en_diagrams), f"Diagram translation missing: {name}"
        for diagram in tr_diagrams + en_diagrams:
            assert "accTitle:" in diagram and "accDescr:" in diagram, f"Missing accessible description: {name}"
            diagram_count += 1
    config = yaml.load((ROOT / "mkdocs.yml").read_text(), Loader=ConfigLoader)
    nav_files, labels = set(), set()

    def walk(items):
        for item in items:
            for label, target in item.items():
                labels.add(label)
                if isinstance(target, list):
                    walk(target)
                else:
                    nav_files.add(target)
    walk(config["nav"])
    assert nav_files == turkish, {"not_in_nav": sorted(turkish-nav_files), "missing_file": sorted(nav_files-turkish)}
    i18n = next(p["i18n"] for p in config["plugins"] if isinstance(p, dict) and "i18n" in p)
    translations = next(l["nav_translations"] for l in i18n["languages"] if l["locale"] == "en")
    assert labels <= translations.keys(), sorted(labels-translations.keys())

    flags = {}
    for script in (ROOT / "examples").glob("*.py"):
        supported = {"--help", "-h"}
        for node in ast.walk(ast.parse(script.read_text())):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument":
                supported.update(arg.value for arg in node.args if isinstance(arg, ast.Constant)
                                 and isinstance(arg.value, str) and arg.value.startswith("-"))
        flags[script.name] = supported

    commands, failures = 0, []
    for page in docs.rglob("*.md"):
        for block in re.findall(r"```(?:bash|sh)\n(.*?)```", page.read_text(), re.S):
            for line in block.replace("\\\n", " ").splitlines():
                tokens = shlex.split(line, comments=True)
                examples = [(i, t.split("/")[-1]) for i, t in enumerate(tokens)
                            if re.fullmatch(r"examples/\d+_[\w]+\.py", t)]
                for index, name in examples:
                    commands += 1
                    if name not in flags:
                        failures.append(f"{page.relative_to(ROOT)}: missing {name}")
                        continue
                    for token in tokens[index+1:]:
                        if token.startswith("--") and token.split("=", 1)[0] not in flags[name]:
                            failures.append(f"{page.relative_to(ROOT)}: {name}: unsupported {token}")
    assert not failures, "\n".join(failures)
    print({"pages_per_language": len(turkish), "languages": ["tr", "en"],
           "translated_navigation_labels": len(labels), "documented_example_commands": commands,
           "mermaid_diagrams": diagram_count})


if __name__ == "__main__":
    main()
