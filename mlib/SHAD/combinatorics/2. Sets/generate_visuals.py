"""Иллюстрации для лекции про множества и круги Эйлера."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"
C_PURPLE = "#7c6ccf"

CENTER_A = (-0.62, 0.0)
CENTER_B = (0.62, 0.0)
RADIUS = 1.18


def _apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": C_BG,
            "axes.facecolor": C_BG,
            "axes.edgecolor": C_GRAY,
            "axes.labelcolor": C_INK,
            "text.color": C_INK,
            "xtick.color": C_INK,
            "ytick.color": C_INK,
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, out_name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _setup_axis(ax: plt.Axes) -> None:
    ax.set_xlim(-2.55, 2.55)
    ax.set_ylim(-1.65, 1.65)
    ax.set_aspect("equal")
    ax.axis("off")


def _lens_points(n: int = 96) -> np.ndarray:
    """Boundary points for the intersection of two equal circles."""
    c1 = np.array(CENTER_A, dtype=float)
    c2 = np.array(CENTER_B, dtype=float)
    half_distance = (c2[0] - c1[0]) / 2
    angle = np.arccos(half_distance / RADIUS)

    left_arc = np.column_stack(
        [
            c1[0] + RADIUS * np.cos(np.linspace(angle, -angle, n)),
            c1[1] + RADIUS * np.sin(np.linspace(angle, -angle, n)),
        ]
    )
    right_angle = np.pi - angle
    right_arc = np.column_stack(
        [
            c2[0] + RADIUS * np.cos(np.linspace(-right_angle, right_angle, n)),
            c2[1] + RADIUS * np.sin(np.linspace(-right_angle, right_angle, n)),
        ]
    )
    return np.vstack([left_arc, right_arc])


def _draw_universe(ax: plt.Axes) -> None:
    ax.add_patch(Rectangle((-2.25, -1.25), 4.5, 2.5, facecolor=C_PANEL, edgecolor=C_GRAY, lw=1.4, alpha=0.45))
    ax.text(2.08, 1.06, r"$U$", ha="center", va="center", fontsize=15, weight="bold")


def _draw_circles(ax: plt.Axes, *, alpha_a: float = 0.24, alpha_b: float = 0.24) -> None:
    ax.add_patch(Circle(CENTER_A, RADIUS, facecolor=C_BLUE, edgecolor=C_BLUE, lw=2.4, alpha=alpha_a))
    ax.add_patch(Circle(CENTER_B, RADIUS, facecolor=C_ORANGE, edgecolor=C_ORANGE, lw=2.4, alpha=alpha_b))
    ax.text(-1.08, 0.58, r"$A$", fontsize=18, weight="bold", color=C_BLUE)
    ax.text(0.95, 0.58, r"$B$", fontsize=18, weight="bold", color=C_ORANGE)


def draw_two_sets_regions(out_name: str = "two_sets_regions.png") -> None:
    """Статическая схема областей на диаграмме Эйлера."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.0, 5.8))
    _setup_axis(ax)
    _draw_universe(ax)
    _draw_circles(ax)
    ax.add_patch(Polygon(_lens_points(), closed=True, facecolor=C_GREEN, edgecolor=C_GREEN, lw=1.6, alpha=0.50))

    ax.text(-1.18, -0.06, r"$A\setminus B$", ha="center", va="center", fontsize=14)
    ax.text(0.0, -0.06, r"$A\cap B$", ha="center", va="center", fontsize=14, weight="bold")
    ax.text(1.18, -0.06, r"$B\setminus A$", ha="center", va="center", fontsize=14)
    ax.text(-1.68, -1.0, r"$U\setminus(A\cup B)$", ha="center", va="center", fontsize=13)

    ax.text(
        -2.25,
        1.48,
        r"Два множества делят $U$ на четыре области",
        fontsize=14,
        weight="bold",
    )
    ax.text(
        -2.25,
        -1.50,
        "Операции над множествами выбирают одну или несколько таких областей.",
        fontsize=11,
    )
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def _draw_inclusion_frame(ax: plt.Axes, step: int, pulse: float) -> None:
    _setup_axis(ax)
    _draw_universe(ax)

    if step == 0:
        _draw_circles(ax, alpha_a=0.56, alpha_b=0.10)
        title = r"Шаг 1: считаем элементы множества $A$"
        formula = r"$|A|=10$"
        note = r"В пересечении уже есть $3$ элемента."
    elif step == 1:
        _draw_circles(ax, alpha_a=0.35, alpha_b=0.48)
        ax.add_patch(
            Polygon(
                _lens_points(),
                closed=True,
                facecolor=C_PURPLE,
                edgecolor=C_PURPLE,
                lw=1.7,
                alpha=0.28 + 0.24 * pulse,
            )
        )
        title = r"Шаг 2: добавляем $|B|$, пересечение посчитано дважды"
        formula = r"$|A|+|B|=10+7$"
        note = r"$A\cap B$ попало и в $A$, и в $B$."
    else:
        _draw_circles(ax, alpha_a=0.36, alpha_b=0.36)
        ax.add_patch(Polygon(_lens_points(), closed=True, facecolor=C_GREEN, edgecolor=C_GREEN, lw=1.9, alpha=0.60))
        title = r"Шаг 3: вычитаем лишний повтор пересечения"
        formula = r"$|A\cup B|=10+7-3=14$"
        note = "После вычитания каждая область объединения учтена ровно один раз."

    ax.text(-1.18, -0.04, "7", ha="center", va="center", fontsize=18, weight="bold")
    ax.text(0.0, -0.04, "3", ha="center", va="center", fontsize=18, weight="bold")
    ax.text(1.18, -0.04, "4", ha="center", va="center", fontsize=18, weight="bold")
    ax.text(-2.25, 1.48, title, fontsize=13, weight="bold")
    ax.text(-2.25, -1.50, note, fontsize=11)
    ax.text(
        0,
        1.25,
        formula,
        ha="center",
        va="center",
        fontsize=16,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8f3dc", edgecolor=C_ORANGE),
    )


def gif_inclusion_exclusion_two_sets(out_name: str = "inclusion_exclusion_two_sets.gif") -> None:
    """GIF: как возникает поправка на пересечение в формуле включений и исключений."""
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    frames = []
    steps = [0] * 8 + [1] * 10 + [2] * 12

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, step in enumerate(steps):
            fig, ax = plt.subplots(figsize=(9.0, 5.8))
            pulse = np.sin(np.pi * i / max(1, len(steps) - 1))
            _draw_inclusion_frame(ax, step, pulse)
            fig.tight_layout(pad=0.6)
            fp = tmp_path / f"inclusion_{i:03d}.png"
            fig.savefig(fp, dpi=140, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))

        for _ in range(5):
            frames.append(frames[-1])

    imageio.mimsave(ASSETS / out_name, frames, duration=0.18, loop=0)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_two_sets_regions()
    gif_inclusion_exclusion_two_sets()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
