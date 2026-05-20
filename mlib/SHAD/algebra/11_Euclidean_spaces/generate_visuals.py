"""
Точные схемы для лекции про евклидовы пространства.

Запуск:
    python3 generate_visuals.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch, Polygon, Rectangle

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
            "grid.alpha": 0.28,
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, out_name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _setup_2d(ax: plt.Axes, lim: float = 3.0) -> None:
    ax.set_xlim(-0.5, lim)
    ax.set_ylim(-0.7, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.grid(True, alpha=0.28)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)


def draw_cauchy_angle(out_name: str = "cauchy_angle_geometry.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    _setup_2d(ax, lim=3.2)

    u = np.array([2.5, 0.6])
    v = np.array([1.1, 2.2])

    ax.annotate("", xy=u, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_BLUE))
    ax.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_ORANGE))
    ax.text(u[0] + 0.08, u[1], r"$x$", color=C_BLUE, fontsize=14)
    ax.text(v[0] + 0.08, v[1] + 0.05, r"$y$", color=C_ORANGE, fontsize=14)

    angle_u = np.degrees(np.arctan2(u[1], u[0]))
    angle_v = np.degrees(np.arctan2(v[1], v[0]))
    ax.add_patch(Arc((0, 0), 1.0, 1.0, theta1=angle_u, theta2=angle_v, color=C_GREEN, lw=2.2))
    ax.text(0.62, 0.48, r"$\varphi$", color=C_GREEN, fontsize=13)

    ax.text(
        0.55,
        2.85,
        r"$|\langle x,y\rangle|\leq \|x\|\,\|y\|$",
        fontsize=14,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#f3f1e8", edgecolor=C_GRAY),
    )
    ax.text(1.28, 2.55, r"$\cos\varphi=\frac{\langle x,y\rangle}{\|x\|\|y\|}$", fontsize=12)
    ax.set_title("Скалярное произведение задаёт угол", weight="bold")
    ax.set_xlabel(r"$e_1$")
    ax.set_ylabel(r"$e_2$")
    _save(fig, out_name)


def draw_projection_decomposition(out_name: str = "projection_orthogonal_decomposition.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.4, 5.8))
    _setup_2d(ax, lim=3.4)

    t = np.linspace(-0.3, 3.4, 200)
    line_y = 0.45 * t
    ax.plot(t, line_y, color=C_BLUE, lw=3.0, label=r"$U$")

    x = np.array([2.55, 2.35])
    direction = np.array([1.0, 0.45])
    direction = direction / np.linalg.norm(direction)
    proj_len = np.dot(x, direction)
    p = proj_len * direction

    ax.annotate("", xy=x, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_ORANGE))
    ax.annotate("", xy=p, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_BLUE))
    ax.plot([p[0], x[0]], [p[1], x[1]], color=C_GREEN, lw=2.4, ls="--")
    ax.scatter([p[0], x[0]], [p[1], x[1]], color=[C_BLUE, C_ORANGE], edgecolors=C_INK, s=60, zorder=5)

    ax.text(x[0] + 0.08, x[1] + 0.02, r"$x$", color=C_ORANGE, fontsize=14)
    ax.text(p[0] + 0.04, p[1] - 0.28, r"$\operatorname{proj}_U x$", color=C_BLUE, fontsize=12)
    ax.text((p[0] + x[0]) / 2 + 0.08, (p[1] + x[1]) / 2, r"$x-\operatorname{proj}_U x\perp U$", color=C_GREEN, fontsize=11)
    ax.set_title("Ортогональное разложение $x=u+w$", weight="bold")
    ax.legend(loc="upper left", fontsize=10, framealpha=0.95)
    _save(fig, out_name)


def draw_gram_schmidt_steps(out_name: str = "gram_schmidt_steps.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))

    a1 = np.array([1.2, 1.5])
    a2 = np.array([2.5, 1.0])
    b1 = a1
    b2 = a2 - np.dot(a2, b1) / np.dot(b1, b1) * b1

    for ax in axes:
        _setup_2d(ax, lim=3.0)

    axes[0].annotate("", xy=a1, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_BLUE))
    axes[0].annotate("", xy=a2, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_ORANGE))
    axes[0].text(a1[0] + 0.07, a1[1], r"$a_1$", color=C_BLUE, fontsize=13)
    axes[0].text(a2[0] + 0.07, a2[1], r"$a_2$", color=C_ORANGE, fontsize=13)
    axes[0].set_title("Исходная система", weight="bold")

    axes[1].annotate("", xy=b1, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_BLUE))
    axes[1].annotate("", xy=b2, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_GREEN))
    axes[1].plot([a2[0], b2[0]], [a2[1], b2[1]], color=C_GRAY, ls="--", lw=1.6)
    axes[1].scatter([a2[0]], [a2[1]], color=C_ORANGE, edgecolors=C_INK, s=50, zorder=5)
    axes[1].text(b1[0] + 0.07, b1[1], r"$b_1=a_1$", color=C_BLUE, fontsize=12)
    axes[1].text(b2[0] + 0.07, b2[1] - 0.18, r"$b_2\perp b_1$", color=C_GREEN, fontsize=12)
    axes[1].text(0.45, 2.72, r"$b_2=a_2-\operatorname{proj}_{b_1}a_2$", fontsize=11)
    axes[1].set_title("После вычитания проекции", weight="bold")

    fig.suptitle("Ортогонализация Грама-Шмидта", fontsize=14, weight="bold")
    _save(fig, out_name)


def draw_gram_area(out_name: str = "gram_determinant_area.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.6, 5.8))
    _setup_2d(ax, lim=3.2)

    u = np.array([2.2, 0.55])
    v = np.array([0.8, 2.1])
    parallelogram = np.array([[0, 0], u, u + v, v])
    ax.add_patch(Polygon(parallelogram, closed=True, facecolor=C_ORANGE, edgecolor=C_ORANGE, alpha=0.22, linewidth=2.0))
    ax.annotate("", xy=u, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.5, color=C_BLUE))
    ax.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.5, color=C_GREEN))
    ax.plot([u[0], u[0] + v[0]], [u[1], u[1] + v[1]], color=C_ORANGE, lw=1.8)
    ax.plot([v[0], u[0] + v[0]], [v[1], u[1] + v[1]], color=C_ORANGE, lw=1.8)

    ax.text(u[0] + 0.05, u[1] - 0.2, r"$u$", color=C_BLUE, fontsize=13)
    ax.text(v[0] + 0.05, v[1] + 0.05, r"$v$", color=C_GREEN, fontsize=13)
    ax.text(1.05, 1.35, r"$S=\sqrt{\det G(u,v)}$", color=C_INK, fontsize=13)
    ax.text(1.02, 1.1, r"$G_{ij}=\langle v_i,v_j\rangle$", color=C_INK, fontsize=11)
    ax.set_title("Определитель Грама измеряет площадь", weight="bold")
    _save(fig, out_name)


def draw_orthogonal_operator(out_name: str = "orthogonal_operator_preserves_grid.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))
    theta = np.deg2rad(32)
    rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

    grid = []
    for x in np.linspace(-1.5, 1.5, 5):
        grid.append((np.array([x, -1.5]), np.array([x, 1.5])))
    for y in np.linspace(-1.5, 1.5, 5):
        grid.append((np.array([-1.5, y]), np.array([1.5, y])))

    for ax, title, transform in [(axes[0], "До оператора", np.eye(2)), (axes[1], "После ортогонального оператора", rot)]:
        ax.set_xlim(-2.3, 2.3)
        ax.set_ylim(-2.3, 2.3)
        ax.set_aspect("equal")
        ax.axis("off")
        for a, b in grid:
            ta = transform @ a
            tb = transform @ b
            ax.plot([ta[0], tb[0]], [ta[1], tb[1]], color=C_GRAY, lw=1.0, alpha=0.72)
        e1 = transform @ np.array([1.4, 0.0])
        e2 = transform @ np.array([0.0, 1.4])
        ax.annotate("", xy=e1, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_BLUE))
        ax.annotate("", xy=e2, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_ORANGE))
        ax.add_patch(Rectangle((-1.5, -1.5), 3, 3, fill=False, edgecolor=C_PANEL, linewidth=2.0))
        ax.set_title(title, weight="bold")

    axes[1].text(-2.0, -2.05, r"$A^TA=I$: длины и углы сохраняются", fontsize=12, color=C_GREEN)
    fig.suptitle("Ортогональный оператор поворачивает геометрию без деформации", fontsize=14, weight="bold")
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_cauchy_angle()
    draw_projection_decomposition()
    draw_gram_schmidt_steps()
    draw_gram_area()
    draw_orthogonal_operator()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
