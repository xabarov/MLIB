"""
Точные графики и анимации для темы про функции многих переменных.

Запуск:
    python3 generate_visuals.py
"""

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
            "grid.alpha": 0.35,
            "font.size": 11,
        }
    )


def _quadratic(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return x**2 + 0.6 * x * y + 1.4 * y**2


def draw_tangent_plane_local_linearization(out_name: str = "tangent_plane_local_linearization.png") -> None:
    _apply_style()
    x = np.linspace(-0.95, 1.15, 100)
    y = np.linspace(-1.0, 1.0, 100)
    xx, yy = np.meshgrid(x, y)

    def surface(xv: np.ndarray, yv: np.ndarray) -> np.ndarray:
        return 0.55 * xv**2 + 0.28 * xv * yv + 0.7 * yv**2 + 0.25 * xv - 0.18 * yv + 0.2

    a, b = 0.32, -0.18
    z0 = surface(np.array([[a]]), np.array([[b]])).item()
    fx = 1.1 * a + 0.28 * b + 0.25
    fy = 0.28 * a + 1.4 * b - 0.18
    tangent = z0 + fx * (xx - a) + fy * (yy - b)
    zz = surface(xx, yy)

    fig = plt.figure(figsize=(9.0, 6.8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)

    ax.plot_surface(xx, yy, zz, color=C_BLUE, alpha=0.58, linewidth=0, antialiased=True, shade=True)
    ax.plot_surface(xx, yy, tangent, color=C_ORANGE, alpha=0.32, linewidth=0, antialiased=True, shade=False)
    ax.scatter([a], [b], [z0], color=C_GREEN, s=70, depthshade=False)
    ax.plot([a, a], [b, b], [z0 - 0.55, z0], color=C_GRAY, lw=1.3, ls="--")

    ax.text(a + 0.05, b - 0.07, z0 + 0.05, "точка касания", color=C_INK, fontsize=10)
    ax.text(a - 0.72, b - 0.72, tangent.min() + 0.16, "касательная плоскость", color=C_ORANGE, fontsize=10)
    ax.text(a + 0.42, b + 0.38, surface(np.array([[a + 0.42]]), np.array([[b + 0.38]])).item() + 0.08, "график функции", color=C_BLUE, fontsize=10)

    ax.set_xlabel(r"$x$", labelpad=8)
    ax.set_ylabel(r"$y$", labelpad=8)
    ax.set_zlabel(r"$z$", labelpad=6)
    ax.set_title(
        "Дифференцируемость как локальное линейное приближение",
        fontsize=12,
        weight="bold",
        color=C_INK,
        pad=14,
    )
    ax.view_init(elev=28, azim=-58)
    ax.xaxis.pane.set_facecolor((0.98, 0.97, 0.94, 0.8))
    ax.yaxis.pane.set_facecolor((0.98, 0.97, 0.94, 0.8))
    ax.zaxis.pane.set_facecolor((0.98, 0.97, 0.94, 0.25))
    ax.grid(False)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_gradient_level_sets(out_name: str = "gradient_level_sets.png") -> None:
    _apply_style()
    x = np.linspace(-2.4, 2.4, 400)
    y = np.linspace(-2.1, 2.1, 360)
    xx, yy = np.meshgrid(x, y)
    zz = _quadratic(xx, yy)

    p = np.array([0.9, -0.45])
    grad = np.array([2 * p[0] + 0.6 * p[1], 0.6 * p[0] + 2.8 * p[1]])
    tangent = np.array([-grad[1], grad[0]])
    tangent = tangent / np.linalg.norm(tangent)

    fig, ax = plt.subplots(figsize=(8.6, 6.0))
    levels = np.linspace(0.3, 8.8, 12)
    contour = ax.contour(xx, yy, zz, levels=levels, colors=C_BLUE, linewidths=1.4, alpha=0.95)
    ax.clabel(contour, inline=True, fontsize=8, fmt="%.1f")

    ax.scatter([p[0]], [p[1]], s=90, color=C_ORANGE, edgecolors=C_INK, linewidths=1.2, zorder=5)
    ax.arrow(
        p[0],
        p[1],
        0.55 * grad[0],
        0.55 * grad[1],
        width=0.018,
        head_width=0.12,
        head_length=0.16,
        color=C_GREEN,
        length_includes_head=True,
        zorder=6,
    )
    ax.arrow(
        p[0],
        p[1],
        0.95 * tangent[0],
        0.95 * tangent[1],
        width=0.012,
        head_width=0.1,
        head_length=0.14,
        color=C_ORANGE,
        length_includes_head=True,
        zorder=6,
    )
    ax.text(p[0] + 0.06, p[1] - 0.18, "точка a", fontsize=10, color=C_INK)
    ax.text(p[0] + 0.72, p[1] - 0.08, "градиент", fontsize=10, color=C_GREEN)
    ax.text(p[0] - 0.85, p[1] + 0.68, "касательное\nнаправление", fontsize=10, color=C_ORANGE)

    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_title(
        "Линии уровня, градиент и касательное направление",
        fontsize=12,
        weight="bold",
        color=C_INK,
    )
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_lagrange_tangency(out_name: str = "lagrange_tangency_unit_circle.png") -> None:
    _apply_style()
    t = np.linspace(0, 2 * np.pi, 600)
    x_circle = np.cos(t)
    y_circle = np.sin(t)

    x_pos = np.linspace(0.22, 1.7, 400)
    x_neg = np.linspace(-1.7, -0.22, 400)
    y_pos = 0.5 / x_pos
    y_neg = 0.5 / x_neg

    p = np.array([1 / np.sqrt(2), 1 / np.sqrt(2)])
    grad_f = np.array([p[1], p[0]])
    grad_g = np.array([2 * p[0], 2 * p[1]])

    fig, ax = plt.subplots(figsize=(7.6, 7.0))
    ax.plot(x_circle, y_circle, color=C_BLUE, lw=2.6, label=r"$x^2+y^2=1$")
    ax.plot(x_pos, y_pos, color=C_PURPLE, lw=2.1, label=r"$xy=\frac{1}{2}$")
    ax.plot(x_neg, y_neg, color=C_PURPLE, lw=2.1)

    ax.scatter([p[0]], [p[1]], s=100, color=C_ORANGE, edgecolors=C_INK, linewidths=1.2, zorder=5)
    ax.arrow(
        p[0],
        p[1],
        0.35 * grad_f[0],
        0.35 * grad_f[1],
        width=0.012,
        head_width=0.08,
        head_length=0.1,
        color=C_GREEN,
        length_includes_head=True,
        zorder=6,
    )
    ax.arrow(
        p[0],
        p[1],
        0.2 * grad_g[0],
        0.2 * grad_g[1],
        width=0.01,
        head_width=0.08,
        head_length=0.1,
        color=C_ORANGE,
        length_includes_head=True,
        zorder=6,
    )
    ax.text(0.88, 1.06, r"$\nabla f$", color=C_GREEN, fontsize=10)
    ax.text(1.02, 0.9, r"$\nabla g$", color=C_ORANGE, fontsize=10)
    ax.text(0.55, 0.56, "точка касания", color=C_INK, fontsize=10)

    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.25, 1.35)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_title(
        "Метод Лагранжа: в точке условного экстремума градиенты коллинеарны",
        fontsize=12,
        weight="bold",
        color=C_INK,
    )
    ax.legend(loc="lower left", fontsize=10, framealpha=0.95)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_conditional_extremum_constraint_curve(
    out_name: str = "conditional_extremum_constraint_curve.png",
) -> None:
    _apply_style()
    x = np.linspace(-1.55, 1.55, 500)
    y = np.linspace(-1.55, 1.55, 500)
    xx, yy = np.meshgrid(x, y)
    levels_value = xx + yy

    t = np.linspace(0, 2 * np.pi, 700)
    x_curve = np.cos(t)
    y_curve = np.sin(t)

    p_max = np.array([1 / np.sqrt(2), 1 / np.sqrt(2)])
    p_min = -p_max

    fig, ax = plt.subplots(figsize=(7.7, 6.9))
    levels = np.linspace(-1.8, 1.8, 10)
    contour = ax.contour(xx, yy, levels_value, levels=levels, colors=C_BLUE, linewidths=1.25, alpha=0.85)
    ax.clabel(contour, inline=True, fontsize=8, fmt="%.1f")

    ax.plot(x_curve, y_curve, color=C_PURPLE, lw=2.7, label=r"ограничение $x^2+y^2=1$")
    ax.scatter(
        [p_max[0], p_min[0]],
        [p_max[1], p_min[1]],
        s=95,
        color=[C_ORANGE, C_GREEN],
        edgecolors=C_INK,
        linewidths=1.1,
        zorder=6,
    )

    tang_x = np.linspace(-1.45, 1.45, 100)
    ax.plot(tang_x, np.sqrt(2) - tang_x, color=C_ORANGE, lw=2.2, ls="--", alpha=0.95, label=r"уровень $f(x,y)=x+y=\sqrt{2}$")
    ax.plot(tang_x, -np.sqrt(2) - tang_x, color=C_GREEN, lw=2.2, ls="--", alpha=0.95, label=r"уровень $f(x,y)=x+y=-\sqrt{2}$")

    ax.text(0.84, 0.94, "условный\nмаксимум", color=C_ORANGE, fontsize=10)
    ax.text(-1.23, -1.12, "условный\nминимум", color=C_GREEN, fontsize=10)
    ax.text(-1.42, 1.18, "линии уровня\n$f(x,y)=x+y$", color=C_BLUE, fontsize=10)
    ax.text(-0.45, 1.32, "сравниваем значения\nтолько на окружности", color=C_INK, fontsize=10)

    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_title(
        "Условный экстремум: максимум и минимум ищутся вдоль ограничения",
        fontsize=12,
        weight="bold",
        color=C_INK,
    )
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def gif_gradient_descent(out_name: str = "gif_gradient_descent_quadratic.gif", duration: float = 0.22) -> None:
    _apply_style()
    x = np.linspace(-2.2, 2.2, 320)
    y = np.linspace(-2.2, 2.2, 320)
    xx, yy = np.meshgrid(x, y)
    zz = _quadratic(xx, yy)

    alpha = 0.28
    point = np.array([1.7, 1.35], dtype=float)
    trajectory = [point.copy()]
    for _ in range(18):
        grad = np.array([2 * point[0] + 0.6 * point[1], 0.6 * point[0] + 2.8 * point[1]])
        point = point - alpha * grad
        trajectory.append(point.copy())

    frames = []
    levels = np.linspace(0.15, 8.5, 13)
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for idx in range(1, len(trajectory) + 1):
            fig, ax = plt.subplots(figsize=(7.8, 6.0))
            ax.contour(xx, yy, zz, levels=levels, colors=C_BLUE, linewidths=1.3, alpha=0.9)
            hist = np.array(trajectory[:idx])
            ax.plot(hist[:, 0], hist[:, 1], "-o", color=C_ORANGE, lw=2.0, ms=4.5)
            ax.scatter([0], [0], s=110, color=C_GREEN, edgecolors=C_INK, linewidths=1.1, zorder=5)
            ax.text(0.08, -0.18, "минимум", color=C_GREEN, fontsize=10)

            if idx < len(trajectory):
                current = trajectory[idx - 1]
                grad = np.array([2 * current[0] + 0.6 * current[1], 0.6 * current[0] + 2.8 * current[1]])
                step = -alpha * grad
                ax.arrow(
                    current[0],
                    current[1],
                    step[0],
                    step[1],
                    width=0.01,
                    head_width=0.08,
                    head_length=0.1,
                    color=C_PURPLE,
                    length_includes_head=True,
                    zorder=6,
                )

            ax.set_xlim(-2.1, 2.1)
            ax.set_ylim(-2.1, 2.1)
            ax.set_aspect("equal")
            ax.set_xlabel(r"$x$")
            ax.set_ylabel(r"$y$")
            ax.set_title(
                "Градиентный спуск на выпуклой квадратичной функции",
                fontsize=12,
                weight="bold",
                color=C_INK,
            )
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            frame_path = tmp_path / f"frame_{idx:03d}.png"
            fig.savefig(frame_path, dpi=140, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(frame_path))

        for _ in range(8):
            frames.append(frames[-1])

    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_tangent_plane_local_linearization()
    draw_gradient_level_sets()
    draw_conditional_extremum_constraint_curve()
    draw_lagrange_tangency()
    gif_gradient_descent()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
