"""Genera guion-calidad.pdf a partir de guion-calidad.md.

Uso: python3 presentacion/guion_pdf.py <ruta-a-chrome>   (necesita Playwright)
"""
import html
import pathlib
import re
import sys
import tempfile

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
STYLE = """
body{font-family:"Hanken Grotesk","Calibri",system-ui,sans-serif;color:#1c1712;font-size:12.5px;line-height:1.45}
h1{font-family:Cambria,Georgia,serif;font-size:26px;margin:0 0 6px;border-bottom:4px solid #c8432a;padding-bottom:8px}
h2{font-family:Cambria,Georgia,serif;font-size:17px;margin:18px 0 6px;display:flex;align-items:center;gap:10px;break-after:avoid}
h2 .n{background:#c8432a;color:#fff;border-radius:50%;width:26px;height:26px;display:inline-grid;place-items:center;font-size:14px;flex:none}
h2 .who{margin-left:auto;font-family:"Hanken Grotesk",Calibri,sans-serif;font-size:12px;background:#2f7a4a;color:#fff;padding:3px 10px;border-radius:999px;font-weight:700}
.say{background:#fbf6ec;border-left:5px solid #a8481f;padding:6px 14px;margin:6px 0;break-inside:avoid}
.say p{margin:5px 0;font-size:13.5px}
.spk{margin:10px 0 2px;color:#a8481f}
table{border-collapse:collapse;width:100%;margin:8px 0} th{background:#1c1712;color:#fff;text-align:left} th,td{padding:6px 8px;border-bottom:1px solid #e2d6c1}
code{background:#efe7d6;padding:0 4px;border-radius:4px} li{margin:3px 0 3px 18px}
"""


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", text)


def to_html(lines):
    out, para, i = [], [], 0

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if not set("".join(cells)) <= set("-: "):
                    rows.append(cells)
                i += 1
            out.append("<table>" + "".join(
                "<tr>" + "".join(f"<th>{inline(c)}</th>" if r == 0 else f"<td>{inline(c)}</td>" for c in row) + "</tr>"
                for r, row in enumerate(rows)) + "</table>")
            continue
        if line.startswith("# "):
            flush()
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            flush()
            m = re.match(r"(\d+) · (.+?) · (.+?) \((.+)\)$", line[3:])
            out.append(f'<h2><span class="n">{m.group(1)}</span>{inline(m.group(2))}<span class="who">{inline(m.group(3))} · {m.group(4)}</span></h2>'
                       if m else f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("> "):
            flush()
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                if lines[i].strip() != ">":
                    quote.append(lines[i][2:])
                i += 1
            out.append('<div class="say">' + "".join(f"<p>{inline(q)}</p>" for q in quote) + "</div>")
            continue
        elif line.startswith("- "):
            flush()
            out.append(f"<li>{inline(line[2:])}</li>")
        elif line.startswith("**") and line.endswith(":**"):
            flush()
            out.append(f'<p class="spk">{inline(line)}</p>')
        elif not line.strip():
            flush()
        else:
            para.append(line)
        i += 1
    flush()
    return "\n".join(out)


def main():
    chrome = sys.argv[1] if len(sys.argv) > 1 else None
    body = to_html((HERE / "guion-calidad.md").read_text(encoding="utf-8").split("\n"))
    doc = f"<!doctype html><html lang=es><head><meta charset=utf-8><style>{STYLE}</style></head><body>{body}</body></html>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(doc)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome) if chrome else p.chromium.launch()
        page = browser.new_page()
        page.goto("file://" + tmp.name)
        page.pdf(path=str(HERE / "guion-calidad.pdf"), format="A4", print_background=True,
                 margin={"top": "16mm", "bottom": "14mm", "left": "16mm", "right": "16mm"})
        browser.close()
    pathlib.Path(tmp.name).unlink()


if __name__ == "__main__":
    main()
