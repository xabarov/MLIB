"""Точные схемы для лекции про условные вероятности."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"


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
            "grid.color": C_GRAY,
            "grid.alpha": 0.3,
            "font.size": 11,
        }
    )


def _save(fig: "plt.Figure", name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_conditional_probability_restriction(
    out_name: str = "conditional_probability_restriction.png",
) -> None:
    """Сужение пространства исходов до B и выделение A∩B внутри."""
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    for ax in axes:
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_xlim(-3.2, 3.2)
        ax.set_ylim(-2.2, 2.2)

    # --- Левая панель: полное пространство ---
    ax = axes[0]
    omega = mpatches.Ellipse((0, 0), 5.8, 3.8, facecolor="#f2efe6",
                              edgecolor=C_INK, lw=2.0)
    ellipse_b = mpatches.Ellipse((0.5, 0), 3.2, 2.4,
                                  facecolor=C_BLUE, edgecolor=C_BLUE,
                                  alpha=0.30, lw=1.8)
    ellipse_a = mpatches.Ellipse((-0.3, 0.1), 2.8, 1.9,
                                  facecolor=C_ORANGE, edgecolor=C_ORANGE,
                                  alpha=0.30, lw=1.8)
    ax.add_patch(omega)
    ax.add_patch(ellipse_b)
    ax.add_patch(ellipse_a)

    # Точки — элементарные исходы
    rng = np.random.default_rng(42)
    pts = rng.uniform(-2.5, 2.5, (60, 2))
    mask_b = (pts[:, 0] - 0.5) ** 2 / 2.56 + pts[:, 1] ** 2 / 1.44 < 1
    mask_a = (pts[:, 0] + 0.3) ** 2 / 1.96 + (pts[:, 1] - 0.1) ** 2 / 0.9025 < 1
    mask_omega = pts[:, 0] ** 2 / 8.41 + pts[:, 1] ** 2 / 3.61 < 1
    in_ab = mask_a & mask_b & mask_omega
    in_a_only = mask_a & ~mask_b & mask_omega
    in_b_only = mask_b & ~mask_a & mask_omega
    in_neither = ~mask_a & ~mask_b & mask_omega

    ax.scatter(pts[in_ab, 0], pts[in_ab, 1], s=22, color=C_INK, zorder=5)
    ax.scatter(pts[in_a_only, 0], pts[in_a_only, 1], s=22, color=C_INK, zorder=5)
    ax.scatter(pts[in_b_only, 0], pts[in_b_only, 1], s=22, color=C_INK, zorder=5)
    ax.scatter(pts[in_neither, 0], pts[in_neither, 1], s=22, color=C_GRAY, zorder=5, alpha=0.5)

    ax.text(0, 2.05, r"$\Omega$", fontsize=18, weight="bold", ha="center", color=C_INK)
    ax.text(-1.8, 0.8, r"$A$", fontsize=16, color=C_ORANGE, weight="bold")
    ax.text(2.0, 0.8, r"$B$", fontsize=16, color=C_BLUE, weight="bold")
    ax.text(0.4, 0.1, r"$A \cap B$", fontsize=11, color=C_INK, ha="center",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.6, edgecolor="none"))
    ax.set_title("Полное пространство $\\Omega$", fontsize=13, weight="bold", pad=8)

    # --- Правая панель: сужение до B ---
    ax = axes[1]
    ellipse_b2 = mpatches.Ellipse((0, 0), 5.6, 4.0, facecolor=C_BLUE,
                                   edgecolor=C_INK, alpha=0.18, lw=2.5)
    ellipse_ab = mpatches.Ellipse((-0.9, 0.1), 2.4, 1.7,
                                   facecolor=C_ORANGE, edgecolor=C_ORANGE,
                                   alpha=0.40, lw=1.8)
    ax.add_patch(ellipse_b2)
    ax.add_patch(ellipse_ab)

    # Точки только внутри B
    ax.scatter(pts[in_ab, 0] * 1.6 - 0.3, pts[in_ab, 1] * 1.5,
               s=30, color=C_ORANGE, zorder=5)
    ax.scatter(pts[in_b_only, 0] * 1.6 - 0.3, pts[in_b_only, 1] * 1.5,
               s=22, color=C_INK, zorder=5)

    ax.text(0, 2.2, r"$B$ (новое пространство)", fontsize=13,
            weight="bold", ha="center", color=C_INK)
    ax.text(-1.8, 0.6, r"$A \cap B$", fontsize=14, color=C_ORANGE, weight="bold")

    frac_text = r"$\mathbb{P}(A|B) = \dfrac{\mathbb{P}(A \cap B)}{\mathbb{P}(B)}$"
    ax.text(0, -1.9, frac_text, fontsize=14, ha="center",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=C_PANEL, edgecolor=C_GRAY, lw=1.2))
    ax.set_title("После условия: пространство сузилось до $B$", fontsize=13, weight="bold", pad=8)

    fig.suptitle("Условная вероятность как доля в суженном пространстве",
                 fontsize=13, y=1.01)
    _save(fig, out_name)


def draw_total_probability_partition(
    out_name: str = "total_probability_partition.png",
) -> None:
    """Разбиение события A через полную группу H1, H2, H3."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 5.5)

    # Три вертикальные полосы — гипотезы H1, H2, H3
    widths = [3.0, 3.5, 3.5]
    colors = [C_BLUE, C_GREEN, C_GRAY]
    labels = [r"$H_1$", r"$H_2$", r"$H_3$"]
    x = 0.0
    boundaries = [0.0]
    for w, c, lbl in zip(widths, colors, labels):
        rect = mpatches.FancyBboxPatch((x + 0.06, 0.06), w - 0.12, 5.0 - 0.12,
                                       boxstyle="round,pad=0.05",
                                       facecolor=c, edgecolor=C_INK,
                                       alpha=0.20, lw=2.0)
        ax.add_patch(rect)
        ax.text(x + w / 2, 4.75, lbl, ha="center", fontsize=16, weight="bold", color=C_INK)
        x += w
        boundaries.append(x)

    # Горизонтальная "лента" события A
    a_y_lo, a_y_hi = 1.6, 3.0
    x = 0.0
    probs = [r"$\mathbb{P}(A|H_1)\cdot\mathbb{P}(H_1)$",
             r"$\mathbb{P}(A|H_2)\cdot\mathbb{P}(H_2)$",
             r"$\mathbb{P}(A|H_3)\cdot\mathbb{P}(H_3)$"]
    for w, lbl in zip(widths, probs):
        rect = mpatches.FancyBboxPatch((x + 0.15, a_y_lo), w - 0.30, a_y_hi - a_y_lo,
                                       boxstyle="round,pad=0.05",
                                       facecolor=C_ORANGE, edgecolor=C_ORANGE,
                                       alpha=0.45, lw=1.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, (a_y_lo + a_y_hi) / 2, lbl,
                ha="center", va="center", fontsize=9.5, color=C_INK,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", alpha=0.65,
                          edgecolor="none"))
        x += w

    # Подписи
    ax.text(-0.35, (a_y_lo + a_y_hi) / 2, r"$A$", fontsize=20,
            weight="bold", color=C_ORANGE, va="center")

    formula = (r"$\mathbb{P}(A) = \mathbb{P}(A|H_1)\mathbb{P}(H_1)"
               r" + \mathbb{P}(A|H_2)\mathbb{P}(H_2)"
               r" + \mathbb{P}(A|H_3)\mathbb{P}(H_3)$")
    ax.text(5.0, -0.3, formula, ha="center", fontsize=12,
            bbox=dict(boxstyle="round,pad=0.4", facecolor=C_PANEL,
                      edgecolor=C_GRAY, lw=1.2))

    ax.set_title("Формула полной вероятности: событие $A$ разбивается по гипотезам",
                 fontsize=13, weight="bold", pad=12)
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_conditional_probability_restriction()
    print("  conditional_probability_restriction.png — OK")
    draw_total_probability_partition()
    print("  total_probability_partition.png — OK")
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
