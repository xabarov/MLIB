"""
Точные схемы и GIF для лекции про комплексные пространства,
эрмитовы формы, самосопряжённые операторы и SVD.

Запуск:
    python3 generate_visuals.py
"""

from __future__ import annotations

from pathlib import Path

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_BLUE = "#6a9bcc"
C_ORANGE = "#d97757"
C_GREEN = "#788c5d"
C_PURPLE = "#7c6ccf"
C_PANEL = "#f0eee6"


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
            "grid.alpha": 0.25,
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, out_name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _setup_2d(ax: plt.Axes, lim: float = 2.8) -> None:
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.grid(True, alpha=0.25)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)


def _arrow(ax: plt.Axes, xy: np.ndarray, color: str, label: str | None = None, lw: float = 2.4) -> None:
    ax.annotate("", xy=xy, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=lw, color=color))
    if label:
        ax.text(xy[0] + 0.07, xy[1] + 0.07, label, color=color, fontsize=13)


def draw_hermitian_pairing(out_name: str = "hermitian_pairing_conjugation.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    _setup_2d(ax, lim=2.7)

    z = np.array([1.75, 1.15])
    w = np.array([1.25, -1.55])
    _arrow(ax, z, C_BLUE, r"$z$")
    _arrow(ax, w, C_ORANGE, r"$w$")

    ax.add_patch(Arc((0, 0), 1.25, 1.25, theta1=-51, theta2=33, color=C_GREEN, lw=2.0))
    ax.text(0.82, -0.1, r"$\langle z,w\rangle$", color=C_GREEN, fontsize=13)

    ax.text(
        -2.45,
        2.25,
        r"$\langle z,w\rangle=\overline{\langle w,z\rangle}$",
        fontsize=14,
        bbox=dict(boxstyle="round,pad=0.35", facecolor=C_PANEL, edgecolor=C_GRAY),
    )
    ax.text(-2.45, 1.85, r"один аргумент линейный, другой сопряжённо-линейный", fontsize=11)
    ax.scatter([z[0], w[0]], [z[1], w[1]], s=52, color=[C_BLUE, C_ORANGE], edgecolors=C_INK, zorder=5)
    ax.set_title("Эрмитово спаривание учитывает комплексное сопряжение", weight="bold")
    _save(fig, out_name)


def draw_jacobi_sylvester(out_name: str = "jacobi_sylvester_minors.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.4, 5.8))
    ax.axis("off")

    matrix = np.array([[4, 1, 2], [1, 3, -1], [2, -1, 5]])
    x0, y0 = 0.18, 0.2
    cell = 0.16
    for i in range(3):
        for j in range(3):
            color = "#ffffff"
            if i <= 0 and j <= 0:
                color = "#dfeaf6"
            if i <= 1 and j <= 1:
                color = "#efe7dc"
            if i <= 2 and j <= 2:
                color = "#e8ebdd"
            rect = plt.Rectangle((x0 + j * cell, y0 + (2 - i) * cell), cell, cell, facecolor=color, edgecolor=C_INK, lw=1.2)
            ax.add_patch(rect)
            ax.text(x0 + j * cell + cell / 2, y0 + (2 - i) * cell + cell / 2, str(matrix[i, j]), ha="center", va="center", fontsize=13)

    ax.text(0.16, 0.76, "ведущие главные миноры", fontsize=14, weight="bold", color=C_INK)
    ax.text(0.62, 0.62, r"$\Delta_1=4$", fontsize=13, color=C_BLUE)
    ax.text(0.62, 0.48, r"$\Delta_2=4\cdot 3-1\cdot 1=11$", fontsize=13, color=C_ORANGE)
    ax.text(0.62, 0.32, r"$\Delta_3=\det A=43$", fontsize=13, color=C_GREEN)
    ax.text(0.18, 0.08, r"если $\Delta_1,\Delta_2,\Delta_3>0$, форма положительно определена", fontsize=13)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _save(fig, out_name)


def draw_self_adjoint_spectral(out_name: str = "self_adjoint_orthogonal_eigenbasis.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.6, 5.8))
    _setup_2d(ax, lim=2.9)

    theta = np.deg2rad(28)
    u1 = np.array([np.cos(theta), np.sin(theta)])
    u2 = np.array([-np.sin(theta), np.cos(theta)])
    l1, l2 = 2.15, 0.95

    ellipse = Ellipse((0, 0), width=2 * l1, height=2 * l2, angle=np.rad2deg(theta), facecolor=C_PURPLE, edgecolor=C_PURPLE, alpha=0.17, lw=2)
    ax.add_patch(ellipse)
    _arrow(ax, l1 * u1, C_BLUE, r"$e_1$")
    _arrow(ax, l2 * u2, C_ORANGE, r"$e_2$")
    ax.plot([-l1 * u1[0], l1 * u1[0]], [-l1 * u1[1], l1 * u1[1]], color=C_BLUE, lw=1.6, alpha=0.7)
    ax.plot([-l2 * u2[0], l2 * u2[0]], [-l2 * u2[1], l2 * u2[1]], color=C_ORANGE, lw=1.6, alpha=0.7)
    ax.text(-2.55, 2.35, r"$A=A^*$", fontsize=15, bbox=dict(boxstyle="round,pad=0.35", facecolor=C_PANEL, edgecolor=C_GRAY))
    ax.text(-2.55, 2.0, r"собственные векторы можно выбрать ортонормированными", fontsize=11)
    ax.set_title("Самосопряжённый оператор имеет ортонормированный собственный базис", weight="bold")
    _save(fig, out_name)


def draw_svd_static(out_name: str = "svd_unit_circle_to_ellipse.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.2))
    angles = np.linspace(0, 2 * np.pi, 300)
    circle = np.vstack([np.cos(angles), np.sin(angles)])
    theta_v = np.deg2rad(32)
    theta_u = np.deg2rad(-24)
    v = np.array([[np.cos(theta_v), -np.sin(theta_v)], [np.sin(theta_v), np.cos(theta_v)]])
    s = np.diag([2.2, 0.85])
    u = np.array([[np.cos(theta_u), -np.sin(theta_u)], [np.sin(theta_u), np.cos(theta_u)]])

    stages = [circle, s @ circle, u @ s @ circle]
    titles = [r"$V^*$: поворот базиса", r"$\Sigma$: растяжение осей", r"$U$: финальный поворот"]
    colors = [C_BLUE, C_ORANGE, C_PURPLE]

    for ax, data, title, color in zip(axes, stages, titles, colors):
        _setup_2d(ax, lim=2.6)
        ax.plot(data[0], data[1], color=color, lw=2.4)
        ax.add_patch(Circle((0, 0), 1, fill=False, edgecolor=C_GRAY, lw=1.2, ls="--"))
        ax.set_title(title, weight="bold")
        ax.set_xticks([])
        ax.set_yticks([])

    fig.suptitle(r"SVD: $A=U\Sigma V^*$ переводит единичный круг в эллипс", fontsize=14, weight="bold")
    _save(fig, out_name)


def draw_svd_gif(out_name: str = "gif_svd_circle_to_ellipse.gif") -> None:
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    tmp_frames: list[np.ndarray] = []
    angles = np.linspace(0, 2 * np.pi, 260)
    circle = np.vstack([np.cos(angles), np.sin(angles)])
    theta = np.deg2rad(34)
    rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    sigma = np.diag([2.15, 0.72])
    target = rot @ sigma @ circle

    for k in range(36):
        t = k / 35
        data = (1 - t) * circle + t * target
        fig, ax = plt.subplots(figsize=(5.2, 5.2))
        _setup_2d(ax, lim=2.55)
        ax.add_patch(Circle((0, 0), 1, fill=False, edgecolor=C_GRAY, lw=1.1, ls="--"))
        ax.plot(data[0], data[1], color=C_PURPLE, lw=2.7)
        ax.plot(target[0], target[1], color=C_ORANGE, lw=1.2, alpha=0.28)
        ax.set_title("Единичный круг постепенно становится эллипсом", weight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
        fig.canvas.draw()
        tmp_frames.append(np.asarray(fig.canvas.buffer_rgba()).copy())
        plt.close(fig)

    frames = tmp_frames + tmp_frames[::-1]
    imageio.mimsave(ASSETS / out_name, frames, duration=0.055)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_hermitian_pairing()
    draw_jacobi_sylvester()
    draw_self_adjoint_spectral()
    draw_svd_static()
    draw_svd_gif()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
