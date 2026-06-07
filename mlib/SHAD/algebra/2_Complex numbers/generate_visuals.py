"""
Графики и анимации для лекции SHAD/algebra/2_Complex numbers.

Палитра: SHAD/lecture_visual_generation/lecture_visual_design_system.md
"""

from __future__ import annotations

import math
from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"


def _apply_style():
    plt.rcParams.update(
        {
            "figure.facecolor": C_BG,
            "axes.facecolor": C_BG,
            "axes.edgecolor": C_GRAY,
            "axes.labelcolor": C_INK,
            "text.color": C_INK,
            "xtick.color": C_INK,
            "ytick.color": C_INK,
            "grid.color": C_GRAY,
            "grid.alpha": 0.35,
            "font.size": 11,
        }
    )


def draw_complex_plane_points(out_name: str = "complex_plane_points.png"):
    """Примеры из §6: 1+i, -2+3i, 3+4i, -4i."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.2, 7.2))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    pairs = [
        (1, 1, r"$1+i$", C_ORANGE),
        (-2, 3, r"$-2+3i$", C_BLUE),
        (3, 4, r"$3+4i$", C_GREEN),
        (0, -4, r"$-4i$", C_PANEL),
    ]
    lim = 5.2
    ax.axhline(0, color=C_GRAY, lw=1.2, zorder=0)
    ax.axvline(0, color=C_GRAY, lw=1.2, zorder=0)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$\operatorname{Re}$", fontsize=13, color=C_INK)
    ax.set_ylabel(r"$\operatorname{Im}$", fontsize=13, color=C_INK)
    ax.set_title("Комплексная плоскость: несколько чисел $z=a+bi$", fontsize=14, weight="bold", color=C_INK)
    ax.grid(True, linestyle="--", alpha=0.45)
    for a, b, label, color in pairs:
        ax.scatter([a], [b], s=220, c=color, edgecolors=C_INK, linewidths=1.4, zorder=4)
        ax.annotate(
            label,
            xy=(a, b),
            xytext=(8, 10),
            textcoords="offset points",
            fontsize=11,
            color=C_INK,
            arrowprops=dict(arrowstyle="-", color=C_GRAY, lw=0.9),
        )
        ax.plot([0, a], [0, b], color=C_GRAY, ls=":", lw=1.0, zorder=1)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_modulus_argument(out_name: str = "complex_modulus_argument.png"):
    """$z=-1+i\\sqrt{3}$, $r=2$, $\\varphi=2\\pi/3$ (как в лекции, §10)."""
    _apply_style()
    a, b = -1.0, math.sqrt(3)
    phi = 2 * math.pi / 3
    fig, ax = plt.subplots(figsize=(7.4, 6.6))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    lim = 2.6
    ax.axhline(0, color=C_GRAY, lw=1.2)
    ax.axvline(0, color=C_GRAY, lw=1.2)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-0.3, lim)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$\operatorname{Re}$", fontsize=12, color=C_INK)
    ax.set_ylabel(r"$\operatorname{Im}$", fontsize=12, color=C_INK)
    ax.set_title(r"Модуль и аргумент: $z=-1+i\sqrt{3}$", fontsize=14, weight="bold", color=C_INK)
    ax.grid(True, linestyle="--", alpha=0.4)
    # radius vector
    arr = FancyArrowPatch(
        (0, 0),
        (a, b),
        arrowstyle="-|>",
        mutation_scale=14,
        lw=2.4,
        color=C_ORANGE,
        zorder=3,
    )
    ax.add_patch(arr)
    ax.scatter([a], [b], s=200, c=C_BLUE, edgecolors=C_INK, linewidths=1.3, zorder=4)
    ax.text(a - 0.35, b + 0.12, r"$z$", fontsize=13, color=C_INK)
    ax.text(a * 0.42, b * 0.42, r"$r=|z|$", fontsize=11, color=C_INK)
    arc = Arc(
        (0, 0),
        width=1.55,
        height=1.55,
        angle=0.0,
        theta1=0.0,
        theta2=math.degrees(phi),
        color=C_GREEN,
        lw=2.2,
        zorder=2,
    )
    ax.add_patch(arc)
    ax.text(0.12, 0.42, r"$\varphi$", fontsize=12, color=C_GREEN, weight="bold")
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_roots_of_unity_cube(out_name: str = "roots_of_unity_cube.png"):
    """Вершины для $z^3=1$ на $|z|=1$."""
    _apply_style()
    n = 3
    angles = [2 * math.pi * k / n for k in range(n)]
    fig, ax = plt.subplots(figsize=(6.8, 6.8))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.set_aspect("equal")
    t = np.linspace(0, 2 * math.pi, 400)
    ax.plot(np.cos(t), np.sin(t), color=C_GRAY, lw=1.8, zorder=1)
    ax.axhline(0, color=C_GRAY, lw=0.9, alpha=0.6)
    ax.axvline(0, color=C_GRAY, lw=0.9, alpha=0.6)
    colors = [C_ORANGE, C_BLUE, C_GREEN]
    for k, ang in enumerate(angles):
        x, y = math.cos(ang), math.sin(ang)
        ax.scatter([x], [y], s=240, c=colors[k], edgecolors=C_INK, linewidths=1.3, zorder=4)
        off = 0.28
        ax.text(x + off * math.cos(ang), y + off * math.sin(ang), rf"$w_{k}$", fontsize=12, color=C_INK)
    for k in range(n):
        x1, y1 = math.cos(angles[k]), math.sin(angles[k])
        x2, y2 = math.cos(angles[(k + 1) % n]), math.sin(angles[(k + 1) % n])
        ax.plot([x1, x2], [y1, y2], color=C_INK, lw=1.2, alpha=0.55, zorder=2)
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)
    ax.axis("off")
    ax.set_title(r"Корни уравнения $z^3=1$ на единичной окружности", fontsize=13, weight="bold", color=C_INK)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_primitive_roots_six(out_name: str = "primitive_roots_six.png"):
    """Корни шестой степени с выделением первообразных: k=1 и k=5."""
    _apply_style()
    n = 6
    primitive = {1, 5}
    fig, ax = plt.subplots(figsize=(7.4, 7.0))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.set_aspect("equal")

    t = np.linspace(0, 2 * math.pi, 480)
    ax.plot(np.cos(t), np.sin(t), color=C_GRAY, lw=1.7, zorder=1)
    ax.axhline(0, color=C_GRAY, lw=0.9, alpha=0.6)
    ax.axvline(0, color=C_GRAY, lw=0.9, alpha=0.6)

    for k in range(n):
        ang = 2 * math.pi * k / n
        x, y = math.cos(ang), math.sin(ang)
        color = C_ORANGE if k in primitive else C_BLUE
        size = 280 if k in primitive else 190
        ax.scatter([x], [y], s=size, c=color, edgecolors=C_INK, linewidths=1.4, zorder=4)
        ax.text(
            1.22 * x,
            1.22 * y,
            rf"$k={k}$",
            ha="center",
            va="center",
            fontsize=11,
            color=C_INK,
        )

    ax.text(-1.55, 1.35, r"$\gcd(k,6)=1$", fontsize=13, weight="bold", color=C_ORANGE)
    ax.text(-1.55, 1.17, r"первообразные: $k=1,5$", fontsize=11, color=C_INK)
    ax.text(-1.55, -1.42, r"остальные возвращаются к $1$ раньше", fontsize=11, color=C_INK)
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.65, 1.65)
    ax.axis("off")
    ax.set_title(r"Первообразные корни уравнения $z^6=1$", fontsize=14, weight="bold", color=C_INK)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def gif_cube_roots_highlight(out_name: str = "roots_cube_roots_pulse.gif", duration: float = 0.35):
    """Поочерёдная подсветка трёх корней из единости."""
    _apply_style()
    n = 3
    angles = [2 * math.pi * k / n for k in range(n)]
    frames = []
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for step in range(n * 4):
            hi = step % n
            fig, ax = plt.subplots(figsize=(6.2, 6.2))
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            ax.set_aspect("equal")
            t = np.linspace(0, 2 * math.pi, 360)
            ax.plot(np.cos(t), np.sin(t), color=C_GRAY, lw=1.6, zorder=1)
            colors = [C_ORANGE, C_BLUE, C_GREEN]
            for k, ang in enumerate(angles):
                x, y = math.cos(ang), math.sin(ang)
                scale = 1.22 if k == hi else 1.0
                col = colors[k]
                ax.scatter(
                    [x],
                    [y],
                    s=int(220 * scale),
                    c=col,
                    edgecolors=C_INK,
                    linewidths=1.8 if k == hi else 1.2,
                    zorder=4,
                )
            ax.set_xlim(-1.35, 1.35)
            ax.set_ylim(-1.35, 1.35)
            ax.axis("off")
            ax.set_title(r"$z^3=1$: три корня на окружности $|z|=1$", fontsize=12, weight="bold", color=C_INK)
            fig.tight_layout()
            fp = tmp_path / f"rf_{step:03d}.png"
            fig.savefig(fp, dpi=130, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))
    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_complex_plane_points()
    draw_modulus_argument()
    draw_roots_of_unity_cube()
    draw_primitive_roots_six()
    gif_cube_roots_highlight()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
