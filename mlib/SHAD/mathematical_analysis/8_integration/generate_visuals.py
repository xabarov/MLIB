"""
Точные графики и схемы для темы про интегрирование.

Запуск:
    python3 generate_visuals.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

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
            "grid.alpha": 0.3,
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, out_name: str) -> None:
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_riemann_sum_area(out_name: str = "riemann_sum_area.png") -> None:
    _apply_style()
    x = np.linspace(0.0, 2.8, 500)
    y = 0.55 + 0.55 * x + 0.25 * np.sin(2.2 * x)

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.plot(x, y, color=C_BLUE, lw=2.4, label=r"$y=f(x)$")
    ax.fill_between(x, 0, y, color=C_BLUE, alpha=0.12)

    n = 7
    xs = np.linspace(0.2, 2.6, n + 1)
    for left, right in zip(xs[:-1], xs[1:]):
        mid = 0.5 * (left + right)
        height = 0.55 + 0.55 * mid + 0.25 * np.sin(2.2 * mid)
        ax.add_patch(
            plt.Rectangle(
                (left, 0),
                right - left,
                height,
                facecolor=C_ORANGE,
                edgecolor=C_ORANGE,
                alpha=0.24,
                linewidth=1.2,
            )
        )

    ax.text(1.62, 0.62, "интегральная сумма", color=C_ORANGE, fontsize=10)
    ax.text(1.15, 1.9, "при измельчении разбиения\nпрямоугольники заполняют площадь", color=C_INK, fontsize=10)
    ax.set_title("Определённый интеграл как предел интегральных сумм", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_xlim(0, 2.8)
    ax.set_ylim(0, 2.6)
    ax.grid(True)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
    _save(fig, out_name)


def draw_fundamental_theorem_accumulation(out_name: str = "fundamental_theorem_accumulation.png") -> None:
    _apply_style()
    t = np.linspace(0.0, 3.0, 500)
    f = 0.8 + 0.4 * t + 0.15 * np.sin(2.8 * t)

    x = np.linspace(0.0, 3.0, 500)
    f_x = 0.8 + 0.4 * x + 0.15 * np.sin(2.8 * x)
    F = np.cumsum(f_x) * (x[1] - x[0])

    x0 = 1.8
    idx = np.searchsorted(x, x0)
    slope = f_x[idx]
    tangent = F[idx] + slope * (x - x0)

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.6))

    axes[0].plot(t, f, color=C_BLUE, lw=2.3)
    mask = t <= x0
    axes[0].fill_between(t[mask], 0, f[mask], color=C_ORANGE, alpha=0.22)
    axes[0].axvline(x0, color=C_GREEN, lw=1.6, ls="--")
    axes[0].text(x0 + 0.05, 0.2, r"$x$", color=C_GREEN)
    axes[0].set_title(r"Слева: $F(x)=\int_a^x f(t)\,dt$ накапливает площадь", fontsize=11, weight="bold")
    axes[0].set_xlabel(r"$t$")
    axes[0].set_ylabel(r"$f(t)$")
    axes[0].grid(True)

    axes[1].plot(x, F, color=C_PURPLE, lw=2.3, label=r"$F(x)$")
    axes[1].plot(x, tangent, color=C_GREEN, lw=2.0, ls="--", label="касательная")
    axes[1].scatter([x0], [F[idx]], s=75, color=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    axes[1].text(x0 + 0.08, F[idx] + 0.12, r"наклон $=f(x)$", color=C_GREEN, fontsize=10)
    axes[1].set_title(r"Справа: производная функции накопления равна $f(x)$", fontsize=11, weight="bold")
    axes[1].set_xlabel(r"$x$")
    axes[1].set_ylabel(r"$F(x)$")
    axes[1].grid(True)
    axes[1].legend(loc="upper left", fontsize=9, framealpha=0.95)

    _save(fig, out_name)


def draw_substitution_interval_map(out_name: str = "substitution_interval_map.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 4.8), height_ratios=[1, 1.1])

    x_points = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    u_points = x_points**2

    for ax in axes:
        ax.set_xlim(-0.05, 1.08)
        ax.set_ylim(-0.5, 0.55)
        ax.axis("off")

    axes[0].plot([0, 1], [0, 0], color=C_BLUE, lw=2.5)
    axes[0].scatter(x_points, np.zeros_like(x_points), color=C_BLUE, s=45)
    axes[0].text(-0.02, 0.18, r"$x$", color=C_BLUE, fontsize=12)
    axes[0].text(0.0, -0.28, r"$a=0$", color=C_INK, fontsize=10)
    axes[0].text(1.0, -0.28, r"$b=1$", color=C_INK, fontsize=10, ha="right")
    axes[0].set_title("Замена переменной меняет не только обозначение, но и масштаб оси", weight="bold")

    axes[1].plot([0, 1], [0, 0], color=C_ORANGE, lw=2.5)
    axes[1].scatter(u_points, np.zeros_like(u_points), color=C_ORANGE, s=45)
    axes[1].text(-0.02, 0.18, r"$u=x^2$", color=C_ORANGE, fontsize=12)
    axes[1].text(0.0, -0.28, r"$u(a)=0$", color=C_INK, fontsize=10)
    axes[1].text(1.0, -0.28, r"$u(b)=1$", color=C_INK, fontsize=10, ha="right")

    for xp, up in zip(x_points, u_points):
        axes[0].annotate("", xy=(up, 0.32), xytext=(xp, 0.08), arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.2))

    axes[0].text(0.56, 0.38, "равные шаги по $x$\nпереходят в неравные по $u$", color=C_GREEN, fontsize=10)
    _save(fig, out_name)


def draw_double_integral_region_iterated(out_name: str = "double_integral_region_iterated.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    x = np.linspace(0, 2, 400)
    ax.plot(x, x, color=C_BLUE, lw=2.4, label=r"$y=x$")
    ax.fill_between(x, 0, x, color=C_BLUE, alpha=0.16)

    x0 = 1.35
    ax.plot([x0, x0], [0, x0], color=C_ORANGE, lw=4.0, alpha=0.8)
    ax.scatter([x0, x0], [0, x0], color=C_ORANGE, s=40, zorder=5)
    ax.text(x0 + 0.06, 0.58, "внутренний интеграл\nпо $y$", color=C_ORANGE, fontsize=10)
    ax.text(0.52, 1.55, r"$D=\{0\leq x\leq 2,\ 0\leq y\leq x\}$", color=C_INK, fontsize=11)
    ax.set_title("Двойной интеграл по области и вертикальный срез", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_xlim(0, 2.1)
    ax.set_ylim(0, 2.1)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
    _save(fig, out_name)


def draw_polar_change_of_variables(out_name: str = "polar_change_of_variables.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.3, 6.2))
    ax.set_aspect("equal")

    theta = np.linspace(0, 2 * np.pi, 500)
    for r in [0.5, 1.0, 1.5, 2.0]:
        ax.plot(r * np.cos(theta), r * np.sin(theta), color=C_GRAY, lw=1.0, alpha=0.7)
    for phi in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        ax.plot([0, 2.1 * np.cos(phi)], [0, 2.1 * np.sin(phi)], color=C_GRAY, lw=0.9, alpha=0.7)

    r0 = 1.4
    phi0 = 0.55
    dr = 0.35
    dphi = 0.38
    sector = np.array(
        [
            [r0 * np.cos(phi0), r0 * np.sin(phi0)],
            [(r0 + dr) * np.cos(phi0), (r0 + dr) * np.sin(phi0)],
            [(r0 + dr) * np.cos(phi0 + dphi), (r0 + dr) * np.sin(phi0 + dphi)],
            [r0 * np.cos(phi0 + dphi), r0 * np.sin(phi0 + dphi)],
        ]
    )
    ax.add_patch(Polygon(sector, closed=True, facecolor=C_ORANGE, edgecolor=C_ORANGE, alpha=0.32, linewidth=1.8))

    mid_arc = (r0 + dr / 2) * np.array([np.cos(phi0 + dphi), np.sin(phi0 + dphi)])
    ax.text(1.1, 1.32, r"малый элемент площади", color=C_ORANGE, fontsize=10)
    ax.text(1.0, 0.86, r"$\Delta S \approx r\,\Delta r\,\Delta \varphi$", color=C_GREEN, fontsize=11)
    ax.text(0.92, 0.48, r"поэтому $dx\,dy=r\,dr\,d\varphi$", color=C_GREEN, fontsize=11)

    ax.annotate("", xy=(r0 * np.cos(phi0), r0 * np.sin(phi0)), xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.0, color=C_BLUE))
    ax.text(0.67, 0.32, r"$r$", color=C_BLUE, fontsize=12)
    arc_t = np.linspace(phi0, phi0 + dphi, 80)
    ax.plot(0.55 * np.cos(arc_t), 0.55 * np.sin(arc_t), color=C_PURPLE, lw=2.0)
    ax.text(0.52, 0.43, r"$\varphi$", color=C_PURPLE, fontsize=12)

    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.set_xlim(-2.2, 2.3)
    ax.set_ylim(-2.0, 2.2)
    ax.set_title("Полярные координаты и роль якобиана", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.grid(False)
    _save(fig, out_name)


def draw_line_integral_work_curve(out_name: str = "line_integral_work_curve.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.8, 5.8))

    x = np.linspace(0, 1.1, 300)
    y = x**2
    ax.plot(x, y, color=C_BLUE, lw=2.5, label=r"$\gamma:\ y=x^2$")

    grid_x = np.linspace(0.0, 1.0, 8)
    grid_y = np.linspace(0.0, 1.0, 8)
    gx, gy = np.meshgrid(grid_x, grid_y)
    u = gy
    v = gx
    ax.quiver(gx, gy, u, v, color=C_GREEN, alpha=0.75, angles="xy", scale_units="xy", scale=7)

    t0 = 0.72
    p = np.array([t0, t0**2])
    tangent = np.array([1.0, 2 * t0])
    tangent = tangent / np.linalg.norm(tangent)
    ax.arrow(p[0], p[1], 0.26 * tangent[0], 0.26 * tangent[1], width=0.008, head_width=0.05, head_length=0.05, color=C_ORANGE, length_includes_head=True, zorder=5)
    ax.scatter([p[0]], [p[1]], color=C_ORANGE, s=65, edgecolors=C_INK, linewidths=1.0, zorder=6)

    ax.text(0.76, 0.76, "вектор поля", color=C_GREEN, fontsize=10)
    ax.text(0.52, 0.66, "касательное\nнаправление", color=C_ORANGE, fontsize=10)
    ax.text(0.08, 0.9, r"$\int_\gamma P\,dx+Q\,dy$ измеряет работу вдоль пути", color=C_INK, fontsize=11)
    ax.set_title("Криволинейный интеграл второго рода", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_xlim(0, 1.1)
    ax.set_ylim(0, 1.15)
    ax.grid(True)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
    _save(fig, out_name)


def draw_surface_integral_flux_patch(out_name: str = "surface_integral_flux_patch.png") -> None:
    _apply_style()
    fig = plt.figure(figsize=(8.4, 6.2))
    ax = fig.add_subplot(111, projection="3d")
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    x = np.linspace(-1.1, 1.1, 20)
    y = np.linspace(-1.1, 1.1, 20)
    xx, yy = np.meshgrid(x, y)
    zz = 0.45 * xx + 0.2 * yy + 0.25
    ax.plot_surface(xx, yy, zz, color=C_BLUE, alpha=0.35, linewidth=0)

    px, py = 0.15, 0.1
    pz = 0.45 * px + 0.2 * py + 0.25
    normal = np.array([-0.45, -0.2, 1.0])
    normal = normal / np.linalg.norm(normal)
    field = np.array([0.2, 0.15, 0.95])

    ax.quiver(px, py, pz, *(0.55 * normal), color=C_ORANGE, linewidth=2.6, arrow_length_ratio=0.15)
    ax.quiver(px, py, pz, *(0.7 * field), color=C_GREEN, linewidth=2.6, arrow_length_ratio=0.15)
    ax.scatter([px], [py], [pz], color=C_PURPLE, s=55, depthshade=False)

    ax.text(px + 0.08, py - 0.02, pz + 0.52, r"$n$", color=C_ORANGE, fontsize=11)
    ax.text(px + 0.18, py + 0.08, pz + 0.72, r"$F$", color=C_GREEN, fontsize=11)
    ax.text2D(0.04, 0.92, r"Поток зависит от скалярного произведения $F\cdot n$", transform=ax.transAxes, fontsize=12, color=C_INK, bbox=dict(boxstyle="round,pad=0.25", facecolor=C_PANEL, edgecolor=C_GRAY))
    ax.set_title("Поверхностный интеграл потока", weight="bold", pad=14)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    ax.view_init(elev=24, azim=-48)
    ax.grid(False)
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_riemann_sum_area()
    draw_fundamental_theorem_accumulation()
    draw_substitution_interval_map()
    draw_double_integral_region_iterated()
    draw_polar_change_of_variables()
    draw_line_integral_work_curve()
    draw_surface_integral_flux_patch()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
