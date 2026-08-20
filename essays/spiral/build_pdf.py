"""Сборка иллюстрированного PDF из new_spiral.md.

markdown -> стилизованный HTML (палитра SHAD) -> chromium --headless print-to-pdf.
Картинки врезаются по якорным заголовкам как <figure> с подписью.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
SRC_MD = HERE / "new_spiral.md"
ASSETS = HERE / "assets"
HTML_OUT = HERE / "new_spiral.html"
PDF_OUT = HERE / "new_spiral.pdf"

# (маркер-подстрока заголовка, файл, подпись). Вставка ПЕРЕД строкой-маркером.
FIGURES = [
    ("## 0. Один закон",
     "01_cover_spiral.jpg",
     "Спираль абстракций: каждый виток возвращает прежнее на более высоком уровне."),
    ("## 1. Управление потоком",
     "02_three_beats.jpg",
     "Три такта: естественный язык (тезис) → формальная решётка (антитезис) → "
     "естественная форма, опирающаяся на скрытую структуру (синтез)."),
    ("## 4. Структуры данных",
     "03_tower_underneath.png",
     "Снятие (Aufhebung): естественно-языковое намерение сверху, формальная башня — "
     "схемы, типы, машинный код — работает снизу, не удалена."),
    ("## 7. Где место новым фишкам",
     "05_frontier_gaps.png",
     "Фронтир — достроить недостающие формальные слои под намерением; "
     "пунктиром — балки, которых ещё нет."),
    ("## 9. Организация памяти",
     "04_memory_layers.jpg",
     "Область видимости памяти = область применимости знания: от эфемерного ядра "
     "к внешнему конфигу."),
    ("## 11. Открытые вопросы",
     "06_horizon.jpg",
     "Спираль продолжает виток вперёд — на один уровень выше."),
]

CSS = """
@page { size: A4; margin: 18mm 16mm; }
:root{
  --bg:#faf9f5; --ink:#141413; --gray:#b0aea5; --panel:#e8e6dc;
  --orange:#d97757; --blue:#6a9bcc; --green:#788c5d; --purple:#7c6ccf;
}
*{ box-sizing:border-box; }
html,body{ background:var(--bg); color:var(--ink); }
body{
  font-family:"PT Serif","Noto Serif","DejaVu Serif",serif;
  font-size: 11.2pt; line-height: 1.62; margin:0;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
.wrap{ max-width: 760px; margin:0 auto; padding: 0 4px; }
h1,h2,h3,h4{ font-family:"PT Sans","Noto Sans","DejaVu Sans",sans-serif; line-height:1.22; color:var(--ink); }
h1{ font-size:25pt; margin:0 0 4px; letter-spacing:-.4px; }
h2{ font-size:16pt; margin:26px 0 8px; padding-top:6px; border-top:2px solid var(--panel);
    break-after:avoid; }
h3{ font-size:12.6pt; margin:18px 0 6px; color:#2a2a28; break-after:avoid; }
p{ margin:8px 0; }
strong{ color:#000; }
em{ color:#3a3a37; }
a{ color:var(--blue); text-decoration:none; }
blockquote{
  margin:10px 0 18px; padding:8px 16px; color:#54524c;
  border-left:3px solid var(--orange); background:#f3f1ea; font-style:italic;
}
ul,ol{ margin:8px 0 8px 4px; padding-left:22px; }
li{ margin:3px 0; }
code{ font-family:"DejaVu Sans Mono","Liberation Mono",monospace; font-size:9.6pt;
      background:var(--panel); padding:1px 5px; border-radius:4px; }
pre{ background:#f1efe7; border:1px solid var(--panel); border-radius:8px;
     padding:12px 14px; overflow-x:auto; line-height:1.4; break-inside:avoid; }
pre code{ background:none; padding:0; font-size:9pt; color:#26251f; }
table{ border-collapse:collapse; width:100%; margin:12px 0; font-size:10pt;
       break-inside:avoid; }
th,td{ border:1px solid var(--gray); padding:6px 9px; text-align:left; vertical-align:top; }
th{ background:var(--panel); font-family:"PT Sans","Noto Sans","DejaVu Sans",sans-serif; font-size:9.4pt; }
tr:nth-child(even) td{ background:#f5f3ec; }
hr{ border:none; border-top:1px solid var(--gray); margin:22px 0; }
figure{ margin:20px 0 22px; break-inside:avoid; text-align:center; }
figure img{ width:100%; border:1px solid var(--panel); border-radius:10px; }
figcaption{ font-family:"PT Sans","Noto Sans","DejaVu Sans",sans-serif; font-size:8.8pt;
  color:#6a6760; margin-top:7px; line-height:1.4; padding:0 6px; }
.cover figcaption{ font-size:9.4pt; }
h1+.subtitle{ color:#6a6760; font-family:"PT Sans","Noto Sans","DejaVu Sans",sans-serif; font-size:10pt; }
"""


def build_markdown_with_figures(md_text: str) -> str:
    lines = md_text.splitlines()
    out: list[str] = []
    pending = {marker: (img, cap) for marker, img, cap in FIGURES}
    for line in lines:
        for marker, (img, cap) in list(pending.items()):
            if line.strip().startswith(marker):
                cover = "cover" if img.startswith("01_") else ""
                out.append("")
                out.append(
                    f'<figure class="{cover}">'
                    f'<img src="assets/{img}" alt="">'
                    f"<figcaption>{cap}</figcaption></figure>"
                )
                out.append("")
                del pending[marker]
                break
        out.append(line)
    if pending:
        print("WARN: маркеры не найдены:", list(pending), file=sys.stderr)
    return "\n".join(out)


def main() -> int:
    md_text = SRC_MD.read_text(encoding="utf-8")
    md_text = build_markdown_with_figures(md_text)

    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists", "md_in_html"],
    )
    html = (
        "<!doctype html><html lang='ru'><head><meta charset='utf-8'>"
        f"<style>{CSS}</style></head><body><div class='wrap'>"
        f"{html_body}</div></body></html>"
    )
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"HTML -> {HTML_OUT}")

    chromium = shutil.which("chromium-browser") or shutil.which("chromium") or "/snap/bin/chromium"
    cmd = [
        chromium, "--headless", "--no-sandbox", "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_OUT}",
        HTML_OUT.as_uri(),
    ]
    print("run:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not PDF_OUT.exists():
        # старый флаг заголовков
        cmd[cmd.index("--no-pdf-header-footer")] = "--print-to-pdf-no-header"
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not PDF_OUT.exists():
        print(res.stdout, res.stderr, file=sys.stderr)
        return 1
    print(f"PDF  -> {PDF_OUT}  ({PDF_OUT.stat().st_size//1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
