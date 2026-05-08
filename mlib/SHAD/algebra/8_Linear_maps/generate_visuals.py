"""Иллюстрации для лекции про линейные отображения и операторы."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
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


def _save(fig: plt.Figure, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _setup_2d(ax: plt.Axes, lim: float = 2.6) -> None:
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.grid(True, alpha=0.28)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)


def _arrow(ax: plt.Axes, start: np.ndarray, end: np.ndarray, color: str, label: str, lw: float = 2.5) -> None:
    ax.annotate("", xy=(end[0], end[1]), xytext=(start[0], start[1]), arrowprops=dict(arrowstyle="->", lw=lw, color=color))
    ax.text(end[0] * 1.04 + 0.03, end[1] * 1.04 + 0.03, label, color=color, fontsize=11)


def draw_linear_map_scheme() -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)

    left = plt.Rectangle((0.7, 1.0), 2.2, 1.8, facecolor="#eef3f9", edgecolor=C_BLUE, linewidth=2.2)
    right = plt.Rectangle((7.1, 1.0), 2.2, 1.8, facecolor="#f2edf9", edgecolor=C_PURPLE, linewidth=2.2)
    ax.add_patch(left)
    ax.add_patch(right)
    ax.text(1.8, 1.9, "V", fontsize=24, weight="bold", color=C_BLUE, ha="center", va="center")
    ax.text(8.2, 1.9, "W", fontsize=24, weight="bold", color=C_PURPLE, ha="center", va="center")
    ax.annotate("", xy=(6.7, 1.9), xytext=(3.2, 1.9), arrowprops=dict(arrowstyle="->", lw=2.8, color=C_GREEN))
    ax.text(4.95, 2.18, r"$\varphi$", fontsize=18, color=C_GREEN, ha="center")
    ax.text(1.8, 0.65, "область определения", fontsize=10, ha="center", color=C_INK)
    ax.text(8.2, 0.65, "область значений", fontsize=10, ha="center", color=C_INK)
    ax.text(5.0, 3.45, "Линейное отображение между двумя пространствами", fontsize=13, weight="bold", ha="center", color=C_INK)
    _save(fig, "linear_map_V_to_W.png")


def draw_rotation() -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    _setup_2d(ax, lim=2.4)
    v = np.array([1.6, 0.45])
    alpha = 0.95
    rot = np.array([[np.cos(alpha), -np.sin(alpha)], [np.sin(alpha), np.cos(alpha)]])
    w = rot @ v
    _arrow(ax, np.zeros(2), v, C_BLUE, r"$v$")
    _arrow(ax, np.zeros(2), w, C_ORANGE, r"$\varphi(v)$")
    theta = np.linspace(0, alpha, 80)
    ax.plot(0.45 * np.cos(theta), 0.45 * np.sin(theta), color=C_GREEN, lw=2)
    ax.text(0.52, 0.15, r"$\alpha$", color=C_GREEN, fontsize=11)
    ax.set_title("Поворот плоскости: линейный оператор", fontsize=12, weight="bold")
    _save(fig, "rotation_r2.png")


def draw_projection() -> None:
    _apply_style()
    fig = plt.figure(figsize=(7.0, 5.6))
    fig.subplots_adjust(top=0.83)
    ax = fig.add_subplot(111, projection="3d")
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    x = np.linspace(-1.7, 1.7, 12)
    y = np.linspace(-1.7, 1.7, 12)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    ax.plot_surface(X, Y, Z, color=C_BLUE, alpha=0.20, linewidth=0)

    v = np.array([0.9, 1.0, 1.4])
    p = np.array([0.9, 1.0, 0.0])
    ax.quiver(0, 0, 0, *v, color=C_ORANGE, linewidth=2.8, arrow_length_ratio=0.11)
    ax.quiver(0, 0, 0, *p, color=C_GREEN, linewidth=2.8, arrow_length_ratio=0.11)
    ax.plot([v[0], p[0]], [v[1], p[1]], [v[2], p[2]], color=C_GRAY, lw=1.8, ls="--")
    ax.text(*(v + np.array([0.08, 0.08, 0.08])), r"$(x,y,z)$", color=C_ORANGE, fontsize=10)
    ax.text(*(p + np.array([0.08, 0.08, 0.08])), r"$(x,y,0)$", color=C_GREEN, fontsize=10)
    ax.text2D(0.05, 0.89, r"$\varphi(x,y,z)=(x,y,0)$", transform=ax.transAxes, fontsize=14, color=C_INK, bbox=dict(boxstyle="round,pad=0.3", facecolor="#edf7ea", edgecolor=C_GREEN))
    ax.text2D(0.05, 0.72, "Вертикальная компонента исчезает,\nточка падает на плоскость Oxy", transform=ax.transAxes, fontsize=11, color=C_INK)
    ax.set_title("Проекция на координатную плоскость", fontsize=12, weight="bold", pad=16)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=22, azim=34)
    ax.set_box_aspect((1.2, 1.2, 0.8))
    _save(fig, "projection_r3_to_xy.png")


def draw_kernel_line() -> None:
    _apply_style()
    fig = plt.figure(figsize=(7.2, 5.7))
    fig.subplots_adjust(top=0.82)
    ax = fig.add_subplot(111, projection="3d")
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    t = np.linspace(-2.0, 2.0, 100)
    x = -t
    y = t
    z = -t
    ax.plot(x, y, z, color=C_ORANGE, lw=3.4)
    ax.scatter([0], [0], [0], color=C_INK, s=28)

    plane_x = np.linspace(-2.2, 2.2, 10)
    plane_y = np.linspace(-2.2, 2.2, 10)
    PX, PY = np.meshgrid(plane_x, plane_y)
    PZ = -PX - PY
    ax.plot_surface(PX, PY, PZ, color=C_PURPLE, alpha=0.10, linewidth=0)

    ax.text(-1.9, 1.8, -1.9, r"$\ker\varphi$", color=C_ORANGE, fontsize=11)
    ax.text2D(0.04, 0.89, r"$\ker\varphi=\mathrm{span}\{(-1,1,-1)\}$", transform=ax.transAxes, fontsize=14, color=C_INK, bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8f3dc", edgecolor=C_ORANGE))
    ax.text2D(0.04, 0.72, "Ядро всегда является подпространством:\nздесь это прямая через начало", transform=ax.transAxes, fontsize=11, color=C_INK)
    ax.set_title("Геометрия ядра линейного отображения", fontsize=12, weight="bold", pad=16)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=22, azim=38)
    ax.set_box_aspect((1.2, 1.1, 1.1))
    _save(fig, "kernel_line_r3.png")


def draw_two_bases() -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(6.5, 5.8))
    _setup_2d(ax, lim=2.2)

    e1 = np.array([1.0, 0.0])
    e2 = np.array([0.0, 1.0])
    f1 = np.array([1.0, 1.0])
    f2 = np.array([1.0, -1.0])
    v = np.array([1.4, 0.9])

    _arrow(ax, np.zeros(2), e1, C_BLUE, r"$e_1$")
    _arrow(ax, np.zeros(2), e2, C_BLUE, r"$e_2$")
    _arrow(ax, np.zeros(2), f1 / 1.3, C_PURPLE, r"$f_1$", lw=2.2)
    _arrow(ax, np.zeros(2), f2 / 1.3, C_GREEN, r"$f_2$", lw=2.2)
    _arrow(ax, np.zeros(2), v, C_ORANGE, r"$v$", lw=2.8)

    ax.text(-2.0, 1.85, r"$A=[\varphi]_e,\quad B=[\varphi]_f=C^{-1}AC$", fontsize=12, color=C_INK, bbox=dict(boxstyle="round,pad=0.25", facecolor="#eef3f9", edgecolor=C_BLUE))
    ax.text(-2.0, 1.3, "Оператор тот же,\nменяется только координатная запись", fontsize=11, color=C_INK)
    ax.set_title("Одна плоскость, два базиса", fontsize=12, weight="bold")
    _save(fig, "two_bases_r2.png")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_linear_map_scheme()
    draw_rotation()
    draw_projection()
    draw_kernel_line()
    draw_two_bases()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
