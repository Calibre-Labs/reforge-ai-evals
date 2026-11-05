"""Fill one of the eval page templates with your data and write a self-contained HTML page.

    python3 build_page.py results examples/mapper-results.json --out results.html
    python3 build_page.py scorer my-check.json --out my-check.html --title "TC-8 half-empty columns"
    python3 build_page.py scorer my-judge.json --out my-judge.html

The template is results or scorer (one layout for code checks and LLM judges). The JSON follows the schema in README.md.
No dependencies beyond the standard library.
"""
import argparse
import html
import json
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATES = ("results", "scorer")


def build(template: str, data: dict, title: str | None = None) -> str:
    page = (HERE / f"{template}.html").read_text()
    # "</" or "<!--" inside the JSON would end or confuse the script tag.
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
    title = title or data.get("title") or template
    return page.replace("__PAGE_TITLE__", html.escape(title), 1).replace("__PAGE_DATA__", blob, 1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("template", choices=TEMPLATES)
    ap.add_argument("data", type=Path, help="page data as JSON")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--title")
    a = ap.parse_args()
    a.out.write_text(build(a.template, json.loads(a.data.read_text()), a.title))
    print(f"Wrote {a.out}")


if __name__ == "__main__":
    main()
