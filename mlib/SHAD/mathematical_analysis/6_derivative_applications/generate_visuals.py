"""Точные визуалы в общей стилистике для темы 6_derivative_applications."""

from __future__ import annotations

import math
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
            "grid.alpha": 0.3,
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / name
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


def _setup_axes(ax: plt.Axes, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.grid(True, alpha=0.3)


def save_rolle() -> None:
    _apply_style()
    a, b = -1.6, 1.6
    x = np.linspace(a, b, 500)
    y = 0.34 * (x**2 - 2.56)

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    _setup_axes(ax, (-2.1, 2.1), (-1.45, 0.45))
    ax.plot(x, y, color=C_BLUE, lw=2.6, label=r"$f(x)$")
    ax.scatter([a, b], [0.0, 0.0], s=80, color=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    ax.axhline(0, color=C_PURPLE, lw=1.7, ls="--", alpha=0.85, label=r"$f(a)=f(b)$")
    c = 0.0
    ax.plot([-0.9, 0.9], [y[np.argmin(np.abs(x - c))]] * 2, color=C_GREEN, lw=2.2, label="горизонтальная касательная")
    ax.scatter([c], [y[np.argmin(np.abs(x - c))]], s=85, color=C_GREEN, edgecolors=C_INK, linewidths=1.0, zorder=6)
    ax.text(a - 0.06, 0.08, r"$a$", color=C_ORANGE, fontsize=11)
    ax.text(b + 0.04, 0.08, r"$b$", color=C_ORANGE, fontsize=11)
    ax.text(c + 0.08, -0.96, r"$c$", color=C_GREEN, fontsize=11)
    ax.set_title("Теорема Ролля: внутри отрезка находится точка с $f'(c)=0$", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="lower center", fontsize=9, ncol=3, framealpha=0.95)
    fig.tight_layout()
    _save(fig, "rolle.png")


def save_lagrange() -> None:
    _apply_style()
    a, b = 0.2, 2.7
    x = np.linspace(0.0, 3.1, 500)
    f = 1.7 * np.log1p(x)
    slope = (1.7 * np.log1p(b) - 1.7 * np.log1p(a)) / (b - a)
    c = 1.7 / slope - 1
    sec_x = np.linspace(a, b, 60)
    sec_y = 1.7 * np.log1p(a) + slope * (sec_x - a)
    tang_x = np.linspace(c - 0.8, c + 0.8, 60)
    tang_y = 1.7 * np.log1p(c) + slope * (tang_x - c)

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    _setup_axes(ax, (-0.1, 3.2), (-0.15, 2.45))
    ax.plot(x, f, color=C_BLUE, lw=2.6, label=r"$f(x)$")
    ax.plot(sec_x, sec_y, color=C_ORANGE, lw=2.0, ls="--", label="секущая")
    ax.plot(tang_x, tang_y, color=C_GREEN, lw=2.2, label="параллельная касательная")
    ax.scatter([a, b], [1.7 * np.log1p(a), 1.7 * np.log1p(b)], s=80, color=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    ax.scatter([c], [1.7 * np.log1p(c)], s=85, color=C_GREEN, edgecolors=C_INK, linewidths=1.0, zorder=6)
    ax.text(a - 0.03, 1.7 * np.log1p(a) - 0.16, r"$a$", fontsize=11, color=C_ORANGE)
    ax.text(b + 0.03, 1.7 * np.log1p(b) - 0.02, r"$b$", fontsize=11, color=C_ORANGE)
    ax.text(c + 0.06, 1.7 * np.log1p(c) - 0.16, r"$c$", fontsize=11, color=C_GREEN)
    ax.set_title("Теорема Лагранжа: найдется касательная, параллельная секущей", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
    fig.tight_layout()
    _save(fig, "lagrange.png")


def save_extrema() -> None:
    _apply_style()
    x = np.linspace(-2.4, 2.4, 500)
    y = x**3 - 3 * x
    ymax = (-1) ** 3 - 3 * (-1)
    ymin = 1**3 - 3 * 1

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    _setup_axes(ax, (-2.5, 2.5), (-4.4, 4.4))
    ax.plot(x, y, color=C_BLUE, lw=2.6, label=r"$f(x)=x^3-3x$")
    ax.scatter([-1], [ymax], s=90, color=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    ax.scatter([1], [ymin], s=90, color=C_GREEN, edgecolors=C_INK, linewidths=1.0, zorder=5)
    ax.text(-1.85, 3.35, r"$f'>0$", color=C_GREEN, fontsize=11)
    ax.text(-0.25, 3.35, r"$f'<0$", color=C_ORANGE, fontsize=11)
    ax.text(1.4, 3.35, r"$f'>0$", color=C_GREEN, fontsize=11)
    ax.annotate("локальный максимум", (-1, ymax), textcoords="offset points", xytext=(-105, 20), color=C_ORANGE, fontsize=10, arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.0))
    ax.annotate("локальный минимум", (1, ymin), textcoords="offset points", xytext=(18, -38), color=C_GREEN, fontsize=10, arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.0))
    ax.set_title("Смена знака $f'$ определяет локальные экстремумы", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
    fig.tight_layout()
    _save(fig, "extrema.png")


def save_convexity() -> None:
    _apply_style()
    x = np.linspace(-2.0, 2.0, 400)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0))

    ax = axes[0]
    y = x**2
    a, b, x0 = -1.3, 1.5, 0.35
    chord_y = np.interp([a, b], x, y)
    t = np.linspace(x0 - 1.2, x0 + 1.2, 60)
    tangent = 2 * x0 * (t - x0) + x0**2
    ax.plot(x, y, color=C_BLUE, lw=2.5, label=r"$x^2$")
    ax.plot([a, b], chord_y, color=C_ORANGE, lw=2.0, ls="--", label="хорда выше графика")
    ax.plot(t, tangent, color=C_GREEN, lw=2.0, label="касательная ниже графика")
    ax.scatter([a, b, x0], [a**2, b**2, x0**2], s=70, color=C_PURPLE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    _setup_axes(ax, (-2.1, 2.1), (-0.7, 4.4))
    ax.set_title("Выпуклая функция", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.legend(loc="upper center", fontsize=8, framealpha=0.95)

    ax = axes[1]
    y = -x**2 + 3
    a, b, x0 = -1.3, 1.5, 0.35
    chord_y = [-a**2 + 3, -b**2 + 3]
    t = np.linspace(x0 - 1.2, x0 + 1.2, 60)
    tangent = -2 * x0 * (t - x0) + (-x0**2 + 3)
    ax.plot(x, y, color=C_BLUE, lw=2.5, label=r"$-x^2+3$")
    ax.plot([a, b], chord_y, color=C_ORANGE, lw=2.0, ls="--", label="хорда ниже графика")
    ax.plot(t, tangent, color=C_GREEN, lw=2.0, label="касательная выше графика")
    ax.scatter([a, b, x0], [-a**2 + 3, -b**2 + 3, -x0**2 + 3], s=70, color=C_PURPLE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    _setup_axes(ax, (-2.1, 2.1), (-1.3, 4.4))
    ax.set_title("Вогнутая функция", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.legend(loc="lower center", fontsize=8, framealpha=0.95)

    fig.suptitle("Геометрия выпуклости и вогнутости", fontsize=13, weight="bold", color=C_INK)
    fig.tight_layout()
    _save(fig, "convexity.png")


def save_inflection() -> None:
    _apply_style()
    x = np.linspace(-2.2, 2.2, 500)
    y = x**3 - 3 * x
    mask_left = x <= 0
    mask_right = x >= 0
    tangent = -3 * x

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    _setup_axes(ax, (-2.3, 2.3), (-4.4, 4.4))
    ax.plot(x[mask_left], y[mask_left], color=C_ORANGE, lw=2.6, label=r"$f''<0$")
    ax.plot(x[mask_right], y[mask_right], color=C_BLUE, lw=2.6, label=r"$f''>0$")
    ax.plot(x, tangent, color=C_PURPLE, lw=1.8, ls="--", label="касательная в точке перегиба")
    ax.scatter([0], [0], s=90, color=C_GREEN, edgecolors=C_INK, linewidths=1.0, zorder=6)
    ax.annotate("перегиб", (0, 0), textcoords="offset points", xytext=(18, 22), color=C_GREEN, fontsize=10, arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.0))
    ax.set_title("Точка перегиба: меняется знак второй производной", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
    fig.tight_layout()
    _save(fig, "inflection.png")


def save_lhopital_vs_taylor() -> None:
    _apply_style()
    x = np.linspace(-1.2, 1.2, 600)
    x = x[np.abs(x) > 1e-3]
    y = (x - np.sin(x)) / x**3

    fig, ax = plt.subplots(figsize=(8.2, 4.9))
    ax.plot(x, y, color=C_BLUE, lw=2.5, label=r"$\frac{x-\sin x}{x^3}$")
    ax.axhline(1 / 6, color=C_ORANGE, lw=2.0, ls="--", label=r"$\frac{1}{6}$")
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(0.10, 0.22)
    ax.set_title(r"Отношение $(x-\sin x)/x^3$ стремится к $1/6$", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel("значение отношения")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "lhopital_limit.png")


def _taylor_sin_coefficients(n: int) -> np.ndarray:
    coeffs = np.zeros(n + 1)
    for k in range(n + 1):
        if k % 2 == 1:
            sign = 1 if ((k - 1) // 2) % 2 == 0 else -1
            coeffs[k] = sign / math.factorial(k)
    return coeffs


def _eval_poly(coeffs: np.ndarray, x: np.ndarray) -> np.ndarray:
    y = np.zeros_like(x)
    for k, c in enumerate(coeffs):
        if c != 0:
            y = y + c * x**k
    return y


def save_taylor_animation() -> None:
    _apply_style()
    x = np.linspace(-2 * np.pi, 2 * np.pi, 700)
    y_true = np.sin(x)
    orders = [1, 3, 5, 7, 9, 11, 13, 15]

    with TemporaryDirectory() as tmpdir:
        frames = []
        tmp = Path(tmpdir)
        for i, n in enumerate(orders):
            coeffs = _taylor_sin_coefficients(n)
            y_poly = _eval_poly(coeffs, x)
            fig, ax = plt.subplots(figsize=(8.4, 5.2))
            ax.plot(x, y_true, color=C_BLUE, lw=2.5, label=r"$\sin x$")
            ax.plot(x, y_poly, color=C_ORANGE, lw=2.2, label=f"Тейлор, порядок {n}")
            ax.axhline(0, color=C_GRAY, lw=0.9)
            ax.axvline(0, color=C_GRAY, lw=0.9)
            ax.set_xlim(-2 * np.pi, 2 * np.pi)
            ax.set_ylim(-2.5, 2.5)
            ax.set_title(r"Локальное приближение $\sin x$ многочленами Тейлора", weight="bold", color=C_INK)
            ax.set_xlabel(r"$x$")
            ax.set_ylabel(r"$y$")
            ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            frame_path = tmp / f"frame_{i:02d}.png"
            fig.savefig(frame_path, dpi=130, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(frame_path))

        for _ in range(6):
            frames.append(frames[-1])

    gif_path = ASSETS / "taylor_sin.gif"
    imageio.mimsave(gif_path, frames, duration=0.9, loop=0)
    print(f"  wrote {gif_path.relative_to(ROOT)}")


def main() -> None:
    print("Генерация визуалов для темы 6_derivative_applications...")
    save_rolle()
    save_lagrange()
    save_extrema()
    save_convexity()
    save_inflection()
    save_lhopital_vs_taylor()
    save_taylor_animation()
    print("Готово.")


if __name__ == "__main__":
    main()
