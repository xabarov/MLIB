"""Иллюстрации для лекции про векторные пространства и подпространства."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
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


def _setup_2d(ax: plt.Axes, lim: float = 6.0) -> None:
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.grid(True, alpha=0.28)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)


def _arrow(ax: plt.Axes, vec: np.ndarray, color: str, label: str, lw: float = 2.6, alpha: float = 1.0) -> None:
    ax.annotate("", xy=(vec[0], vec[1]), xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=lw, color=color, alpha=alpha))
    ax.text(vec[0] * 1.05, vec[1] * 1.05, label, color=color, fontsize=11)


def draw_basis_coordinates() -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.4, 7.0))
    _setup_2d(ax, lim=6)

    e1 = np.array([1, 1])
    e2 = np.array([1, -1])
    v = np.array([5, 1])

    _arrow(ax, e1, C_BLUE, r"$e_1$")
    _arrow(ax, e2, C_PURPLE, r"$e_2$")
    _arrow(ax, 3 * e1, C_BLUE, r"$3e_1$", lw=2.0, alpha=0.55)
    ax.annotate("", xy=v, xytext=(3 * e1), arrowprops=dict(arrowstyle="->", lw=2.2, color=C_GREEN, alpha=0.9))
    _arrow(ax, v, C_ORANGE, r"$v$")
    ax.scatter([v[0]], [v[1]], s=70, color=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=5)

    ax.text(-5.5, 5.0, r"$v = 3e_1 + 2e_2$", fontsize=16, color=C_INK, bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8f3dc", edgecolor=C_ORANGE))
    ax.text(-5.5, 4.1, "Один и тот же вектор читается\nпо базису, а не по осям", fontsize=11, color=C_INK)
    ax.set_title("Координаты вектора в нестандартном базисе", fontsize=12, weight="bold")
    _save(fig, "basis_coordinates.png")


def gif_basis_change() -> None:
    _apply_style()
    vector = np.array([4.0, 3.0])
    frames = []
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, t in enumerate(np.linspace(0, 1, 24)):
            fig, ax = plt.subplots(figsize=(7.5, 7.0))
            _setup_2d(ax, lim=6)

            e1 = np.array([1.0, 0.0]) * (1 - t) + np.array([1.0, 1.0]) * t
            e2 = np.array([0.0, 1.0]) * (1 - t) + np.array([1.0, -1.0]) * t
            basis = np.column_stack([e1, e2])
            coords = np.linalg.solve(basis, vector)

            _arrow(ax, e1, C_BLUE, r"$e_1$")
            _arrow(ax, e2, C_PURPLE, r"$e_2$")
            _arrow(ax, vector, C_ORANGE, r"$v$", lw=3.0)
            ax.text(-5.4, 5.0, "Смена базиса меняет координаты,\nно не сам вектор", fontsize=12, color=C_INK)
            ax.text(-5.4, 3.95, rf"$[v]_e \approx ({coords[0]:.2f},\,{coords[1]:.2f})$", fontsize=13, color=C_GREEN, bbox=dict(boxstyle="round,pad=0.3", facecolor="#edf7ea", edgecolor=C_GREEN))
            ax.set_title("Переход к другому базису", fontsize=12, weight="bold")

            fp = tmp_path / f"basis_{i:03d}.png"
            fig.savefig(fp, dpi=140, facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))
        for _ in range(5):
            frames.append(frames[-1])
    imageio.mimsave(ASSETS / "basis_change.gif", frames, duration=0.13, loop=0)


def draw_kernel_plane() -> None:
    _apply_style()
    fig = plt.figure(figsize=(8.6, 6.8))
    ax = fig.add_subplot(111, projection="3d")
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    y = np.linspace(-2.3, 2.3, 24)
    z = np.linspace(-2.3, 2.3, 24)
    Y, Z = np.meshgrid(y, z)
    X = 2 * Y - Z
    ax.plot_surface(X, Y, Z, color=C_BLUE, alpha=0.28, linewidth=0)

    b1 = np.array([2, 1, 0], dtype=float)
    b2 = np.array([-1, 0, 1], dtype=float)
    ax.quiver(0, 0, 0, *b1, color=C_ORANGE, linewidth=2.6, arrow_length_ratio=0.10)
    ax.quiver(0, 0, 0, *b2, color=C_PURPLE, linewidth=2.6, arrow_length_ratio=0.10)
    ax.text(*(b1 + np.array([0.08, 0.1, 0.08])), r"$b_1$", color=C_ORANGE, fontsize=11)
    ax.text(*(b2 + np.array([0.08, 0.1, 0.08])), r"$b_2$", color=C_PURPLE, fontsize=11)

    ax.text2D(0.02, 0.95, r"$U=\{(x,y,z)\mid x-2y+z=0\}$", transform=ax.transAxes, fontsize=14, color=C_INK, bbox=dict(boxstyle="round,pad=0.3", facecolor="#eef3f9", edgecolor=C_BLUE))
    ax.text2D(0.02, 0.87, r"$U=\mathrm{span}\{(2,1,0),\,(-1,0,1)\}$", transform=ax.transAxes, fontsize=12, color=C_INK)
    ax.set_title("Подпространство как множество решений однородной системы", fontsize=12, weight="bold")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=24, azim=34)
    ax.set_box_aspect((1.2, 1.0, 1.0))
    _save(fig, "kernel_plane.png")


def draw_sum_intersection() -> None:
    _apply_style()
    fig = plt.figure(figsize=(8.8, 6.9))
    ax = fig.add_subplot(111, projection="3d")
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    x = np.linspace(-2.4, 2.4, 18)
    y = np.linspace(-2.4, 2.4, 18)
    X, Y = np.meshgrid(x, y)
    Z1 = np.zeros_like(X)
    ax.plot_surface(X, Y, Z1, color=C_BLUE, alpha=0.23, linewidth=0)

    x2 = np.linspace(-2.4, 2.4, 18)
    z2 = np.linspace(-2.4, 2.4, 18)
    X2, Z2 = np.meshgrid(x2, z2)
    Y2 = np.zeros_like(X2)
    ax.plot_surface(X2, Y2, Z2, color=C_ORANGE, alpha=0.23, linewidth=0)

    line = np.linspace(-2.8, 2.8, 120)
    ax.plot(line, np.zeros_like(line), np.zeros_like(line), color=C_GREEN, lw=4.0)
    ax.text(2.25, 0.0, 0.0, r"$U\cap W$", color=C_GREEN, fontsize=11)
    ax.text2D(0.02, 0.95, "Сумма и пересечение подпространств", transform=ax.transAxes, fontsize=14, weight="bold", color=C_INK)
    ax.text2D(0.02, 0.88, r"$U=\{(x,y,0)\},\; W=\{(x,0,z)\}$", transform=ax.transAxes, fontsize=12, color=C_INK)
    ax.text2D(0.02, 0.81, r"$U\cap W$ — общая ось, а $U+W=\mathbb{R}^3$", transform=ax.transAxes, fontsize=12, color=C_INK)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=23, azim=34)
    ax.set_box_aspect((1.2, 1.0, 1.0))
    _save(fig, "sum_intersection.png")


def gif_direct_sum() -> None:
    _apply_style()
    frames = []
    u = np.array([2.0, -1.0, 0.0])
    w_final = np.array([0.0, 0.0, 4.8])

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, t in enumerate(np.linspace(0, 1, 22)):
            w = t * w_final
            v = u + w
            fig = plt.figure(figsize=(8.4, 6.9))
            ax = fig.add_subplot(111, projection="3d")
            fig.patch.set_facecolor(C_BG)
            ax.set_facecolor(C_BG)

            xx = np.linspace(-2.7, 2.7, 10)
            yy = np.linspace(-2.7, 2.7, 10)
            XX, YY = np.meshgrid(xx, yy)
            ZZ = np.zeros_like(XX)
            ax.plot_surface(XX, YY, ZZ, color=C_BLUE, alpha=0.12, linewidth=0)
            ax.plot([0, 0], [0, 0], [-0.4, 5.4], color=C_PURPLE, alpha=0.35, lw=4)

            ax.quiver(0, 0, 0, *u, color=C_BLUE, linewidth=2.7, arrow_length_ratio=0.10)
            ax.quiver(0, 0, 0, *w, color=C_PURPLE, linewidth=2.7, arrow_length_ratio=0.10)
            ax.quiver(0, 0, 0, *v, color=C_ORANGE, linewidth=3.0, arrow_length_ratio=0.10)
            ax.plot([u[0], v[0]], [u[1], v[1]], [u[2], v[2]], color=C_PURPLE, ls="--", lw=2.0)
            ax.plot([w[0], v[0]], [w[1], v[1]], [w[2], v[2]], color=C_BLUE, ls="--", lw=2.0)

            ax.text2D(0.02, 0.95, r"Прямая сумма: каждый вектор раскладывается как $u+w$", transform=ax.transAxes, fontsize=13, color=C_INK, weight="bold")
            ax.text2D(0.02, 0.88, r"$U=\{(x,y,0)\},\; W=\{(0,0,z)\},\; \mathbb{R}^3 = U\oplus W$", transform=ax.transAxes, fontsize=11, color=C_INK)
            ax.set_xlim(-3, 3)
            ax.set_ylim(-3, 3)
            ax.set_zlim(-1, 6)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_zlabel("z")
            ax.view_init(elev=24, azim=36)
            ax.set_box_aspect((1.2, 1.0, 1.2))

            fp = tmp_path / f"direct_sum_{i:03d}.png"
            fig.savefig(fp, dpi=140, facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))
        for _ in range(5):
            frames.append(frames[-1])
    imageio.mimsave(ASSETS / "direct_sum.gif", frames, duration=0.14, loop=0)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_basis_coordinates()
    gif_basis_change()
    draw_kernel_plane()
    draw_sum_intersection()
    gif_direct_sum()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
