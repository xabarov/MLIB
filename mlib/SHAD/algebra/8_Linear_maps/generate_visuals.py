"""Генерация SVG-иллюстраций для SHAD/algebra/8_Linear_maps/lesson.md.

Работает на стандартной библиотеке Python 3 (без matplotlib). SVG — векторный
формат, хорошо рендерится в GitLab и VS Code; при необходимости можно
конвертировать в PNG.

Запуск:
    python3 generate_visuals.py
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

SVG_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'


def save_linear_map_schematic() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="580" height="250" viewBox="0 0 580 250">
<defs>
  <marker id="end" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L8,3 z" fill="#0f766e"/>
  </marker>
</defs>
<rect x="40" y="70" width="150" height="120" rx="16" fill="#dbeafe" stroke="#2563eb" stroke-width="3"/>
<rect x="400" y="70" width="150" height="120" rx="16" fill="#ede9fe" stroke="#7c3aed" stroke-width="3"/>
<text x="115" y="145" text-anchor="middle" font-size="34" font-weight="bold" font-family="Georgia,serif" fill="#1e3a8a">V</text>
<text x="475" y="145" text-anchor="middle" font-size="34" font-weight="bold" font-family="Georgia,serif" fill="#5b21b6">W</text>
<line x1="200" y1="130" x2="390" y2="130" stroke="#0f766e" stroke-width="4" marker-end="url(#end)"/>
<text x="290" y="115" text-anchor="middle" font-size="24" font-weight="bold" fill="#0f766e" font-style="italic">φ</text>
<text x="115" y="215" text-anchor="middle" font-size="14" fill="#374151">область определения</text>
<text x="475" y="215" text-anchor="middle" font-size="14" fill="#374151">область значений</text>
<text x="290" y="32" text-anchor="middle" font-size="16" font-weight="bold" fill="#111827">Схема: линейное отображение между пространствами</text>
</svg>
"""


def save_rotation_r2() -> str:
    c, s = math.cos(0.95), math.sin(0.95)
    vx, vy = 1.55, 0.4
    wx, wy = c * vx - s * vy, s * vx + c * vy
    ax0, ay0 = 0.35, 0.0
    ax1, ay1 = 0.35 * math.cos(0.45), -0.35 * math.sin(0.45)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="-2.5 -2.5 5 5">
<line x1="-2.2" y1="0" x2="2.2" y2="0" stroke="#64748b" stroke-width="0.04"/>
<line x1="0" y1="-2.2" x2="0" y2="2.2" stroke="#64748b" stroke-width="0.04"/>
<defs>
  <marker id="a" orient="auto" markerWidth="8" markerHeight="8" refX="7" refY="2.5" markerUnits="strokeWidth">
    <path d="M0,0 L0,5 L7,2.5 z" fill="currentColor"/>
  </marker>
</defs>
<g stroke-linecap="round" stroke-width="0.08" marker-end="url(#a)">
<line x1="0" y1="0" x2="{vx}" y2="{-vy}" stroke="#2563eb"/>
<line x1="0" y1="0" x2="{wx}" y2="{-wy}" stroke="#ef4444"/>
</g>
<text x="{vx*1.12}" y="{-vy*1.12}" font-size="0.22" fill="#1d4ed8" font-weight="bold" font-style="italic">v</text>
<text x="{wx*1.12}" y="{-wy*1.12}" font-size="0.22" fill="#b91c1c" font-weight="bold" font-style="italic">φ(v)</text>
<path d="M {ax0} {ay0} A 0.35 0.35 0 0 1 {ax1} {ay1}" fill="none" stroke="#0f766e" stroke-width="0.05"/>
<text x="0.42" y="-0.12" font-size="0.16" fill="#0f766e" font-style="italic">α</text>
<text x="0" y="2" text-anchor="middle" font-size="0.18" fill="#111827" font-weight="bold">Поворот плоскости (линейный оператор)</text>
</svg>
"""


def save_projection_r3() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360" viewBox="0 0 480 360">
<defs>
  <marker id="mred" markerWidth="8" markerHeight="8" refX="6" refY="2" orient="auto">
    <path d="M0,0 L0,4 L6,2 z" fill="#b91c1c"/>
  </marker>
  <marker id="mgreen" markerWidth="8" markerHeight="8" refX="6" refY="2" orient="auto">
    <path d="M0,0 L0,4 L6,2 z" fill="#16a34a"/>
  </marker>
</defs>
<polygon points="40,300 200,200 400,200 400,300" fill="#bfdbfe" fill-opacity="0.45" stroke="#3b82f6" stroke-width="2"/>
<text x="50" y="255" font-size="12" fill="#1d4ed8">плоскость z = 0</text>
<line x1="80" y1="90" x2="220" y2="170" stroke="#b91c1c" stroke-width="3" marker-end="url(#mred)"/>
<line x1="80" y1="90" x2="220" y2="256" stroke="#16a34a" stroke-width="3" marker-end="url(#mgreen)"/>
<line x1="220" y1="170" x2="220" y2="256" stroke="#64748b" stroke-width="2" stroke-dasharray="6,5"/>
<text x="230" y="165" font-size="14" fill="#b91c1c" font-style="italic">(x, y, z)</text>
<text x="230" y="268" font-size="14" fill="#166534" font-style="italic">(x, y, 0)</text>
<text x="255" y="220" font-size="12" fill="#64748b">проекция</text>
<text x="240" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#111827">Проекция на плоскость Oxy: φ(x, y, z) = (x, y, 0)</text>
</svg>
"""


def save_kernel_line() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="500" height="400" viewBox="0 0 500 400">
<line x1="100" y1="320" x2="400" y2="80" stroke="#2563eb" stroke-width="4"/>
<circle cx="250" cy="200" r="5" fill="#111827"/>
<text x="262" y="198" font-size="13" fill="#111827">0</text>
<text x="330" y="100" font-size="14" fill="#b45309" font-style="italic">(−1, 1, −1)</text>
<text x="200" y="130" font-size="13" fill="#2563eb" font-style="italic">ker φ</text>
<polygon points="60,100 200,200 200,300 40,200" fill="#a78bfa" fill-opacity="0.2" stroke="#5b21b6" stroke-width="1" stroke-dasharray="4,3"/>
<text x="95" y="155" font-size="11" fill="#5b21b6">x + y = 0 (набросок</text>
<text x="95" y="170" font-size="11" fill="#5b21b6">плоскости в уравнении)</text>
<text x="250" y="28" text-anchor="middle" font-size="15" font-weight="bold" fill="#111827">Прямая — ядро: ker φ = span(−1, 1, −1)</text>
</svg>
"""


def save_two_bases_r2() -> str:
    ox, oy = 200, 200
    s = 55

    def p(x, y):
        return ox + s * x, oy - s * y

    x1, y1 = p(1, 0)
    x2, y2 = p(0, 1)
    fx1, fy1 = p(0.7, 0.7)
    fx2, fy2 = p(0.5, -0.5)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">
<line x1="40" y1="200" x2="400" y2="200" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="200" y1="40" x2="200" y2="460" stroke="#94a3b8" stroke-width="1.5"/>
<defs>
  <marker id="av" orient="auto" refX="8" refY="2.5" markerWidth="8" markerHeight="5">
    <path d="M0,0 L8,2.5 L0,5 z" fill="#2563eb"/>
  </marker>
</defs>
<line x1="200" y1="200" x2="{x1}" y2="{y1}" stroke="#2563eb" stroke-width="3" marker-end="url(#av)"/>
<line x1="200" y1="200" x2="{x2}" y2="{y2}" stroke="#2563eb" stroke-width="3" marker-end="url(#av)"/>
<line x1="200" y1="200" x2="{fx1}" y2="{fy1}" stroke="#7c3aed" stroke-width="2.5"/>
<line x1="200" y1="200" x2="{fx2}" y2="{fy2}" stroke="#db2777" stroke-width="2.5"/>
<text x="{x1+8}" y="{y1}" font-size="16" fill="#1d4ed8" font-weight="bold" font-style="italic">e₁</text>
<text x="{x2+5}" y="{y2+15}" font-size="16" fill="#1d4ed8" font-weight="bold" font-style="italic">e₂</text>
<text x="{fx1+5}" y="{fy1-5}" font-size="15" fill="#5b21b6" font-weight="bold" font-style="italic">f₁</text>
<text x="{fx2+8}" y="{fy2+5}" font-size="15" fill="#be185d" font-weight="bold" font-style="italic">f₂</text>
<rect x="20" y="20" width="330" height="64" fill="#f3f4f6" stroke="#9ca3af" rx="6"/>
<text x="35" y="45" font-size="13" fill="#374151">Смена базиса не двигает векторы, меняет лишь координатную</text>
<text x="35" y="64" font-size="13" fill="#374151">запись одного и того же оператора: B = C⁻¹AC.</text>
<text x="250" y="12" text-anchor="middle" font-size="16" font-weight="bold" fill="#111827">Два базиса на R² (стандартный и f)</text>
</svg>
"""


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    out = {
        "linear_map_V_to_W.svg": save_linear_map_schematic(),
        "rotation_r2.svg": save_rotation_r2(),
        "projection_r3_to_xy.svg": save_projection_r3(),
        "kernel_line_r3.svg": save_kernel_line(),
        "two_bases_r2.svg": save_two_bases_r2(),
    }
    for name, content in out.items():
        p = ASSETS / name
        p.write_text(SVG_HEADER + content, encoding="utf-8")
        print(f"Wrote {p}")


if __name__ == "__main__":
    main()
