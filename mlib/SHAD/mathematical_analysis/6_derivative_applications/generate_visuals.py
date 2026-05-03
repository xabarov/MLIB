"""Генерация визуалов для темы 6_derivative_applications.

Использование (из активированной venv):

    python generate_visuals.py

Все картинки и анимация сохраняются в ./assets/.
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
import seaborn as sns


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

sns.set_theme(style="whitegrid", context="talk")


COLOR_F = "#2563eb"
COLOR_ACCENT = "#ef4444"
COLOR_SECANT = "#7c3aed"
COLOR_TANGENT = "#ef4444"
COLOR_GRID = "#94a3b8"
COLOR_NEUTRAL = "#334155"


def savefig(fig, name):
    ASSETS.mkdir(exist_ok=True, parents=True)
    path = ASSETS / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


def setup_axes(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axhline(0, color=COLOR_NEUTRAL, lw=0.8, alpha=0.6)
    ax.axvline(0, color=COLOR_NEUTRAL, lw=0.8, alpha=0.6)
    ax.grid(True, alpha=0.25)


def save_rolle():
    """Теорема Ролля: f(a) = f(b), касательная горизонтальна в точке c."""
    a, b = -1.5, 1.5

    def f(x):
        return (x + 1.5) * (x - 1.5) * 0.4

    def fp(x):
        return 0.4 * (2 * x)

    xs = np.linspace(a - 0.4, b + 0.4, 400)
    ys = f(xs)

    fig, ax = plt.subplots(figsize=(9, 6))
    setup_axes(ax, (-2.3, 2.3), (-1.6, 0.6))

    ax.plot(xs, ys, color=COLOR_F, lw=3, label=r"$y=f(x)$")

    ax.plot([a, b], [f(a), f(b)], "o", color=COLOR_ACCENT, markersize=10, zorder=5)
    ax.axhline(f(a), color=COLOR_SECANT, lw=1.8, ls="--", alpha=0.8,
               label=r"$f(a)=f(b)$")

    c = 0.0
    t = np.linspace(c - 0.9, c + 0.9, 50)
    ax.plot(t, np.full_like(t, f(c)), color=COLOR_TANGENT, lw=2.5,
            label=r"касательная в $c$: $f'(c)=0$")
    ax.plot([c], [f(c)], "o", color=COLOR_TANGENT, markersize=11, zorder=6)

    ax.annotate(r"$a$", (a, f(a)), textcoords="offset points", xytext=(-14, 10),
                fontsize=15, color=COLOR_ACCENT)
    ax.annotate(r"$b$", (b, f(b)), textcoords="offset points", xytext=(8, 10),
                fontsize=15, color=COLOR_ACCENT)
    ax.annotate(r"$c$", (c, f(c)), textcoords="offset points", xytext=(8, -18),
                fontsize=15, color=COLOR_TANGENT)

    ax.set_title("Теорема Ролля: существует $c\\in(a,b)$ с $f'(c)=0$")
    ax.legend(loc="lower center", fontsize=12)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    savefig(fig, "rolle.png")


def save_lagrange():
    """Теорема Лагранжа: секущая и параллельная касательная."""
    a, b = 0.2, 2.6

    def f(x):
        return np.log(1 + x) * 1.6

    def fp(x):
        return 1.6 / (1 + x)

    xs = np.linspace(a - 0.2, b + 0.3, 400)
    ys = f(xs)

    slope = (f(b) - f(a)) / (b - a)
    c = 1.6 / slope - 1

    fig, ax = plt.subplots(figsize=(9, 6))
    setup_axes(ax, (-0.2, 3.2), (-0.2, 2.5))

    ax.plot(xs, ys, color=COLOR_F, lw=3, label=r"$y=f(x)$")

    ax.plot([a, b], [f(a), f(b)], "o", color=COLOR_ACCENT, markersize=10, zorder=5)
    sec_x = np.linspace(a - 0.1, b + 0.2, 30)
    sec_y = f(a) + slope * (sec_x - a)
    ax.plot(sec_x, sec_y, color=COLOR_SECANT, lw=2.2, ls="--",
            label=r"секущая: $\dfrac{f(b)-f(a)}{b-a}$")

    t = np.linspace(c - 0.75, c + 0.75, 30)
    ax.plot(t, f(c) + slope * (t - c), color=COLOR_TANGENT, lw=2.8,
            label=r"касательная в $c$ параллельна секущей")
    ax.plot([c], [f(c)], "o", color=COLOR_TANGENT, markersize=11, zorder=6)

    ax.annotate(r"$a$", (a, f(a)), textcoords="offset points", xytext=(-16, -4),
                fontsize=15, color=COLOR_ACCENT)
    ax.annotate(r"$b$", (b, f(b)), textcoords="offset points", xytext=(10, -4),
                fontsize=15, color=COLOR_ACCENT)
    ax.annotate(r"$c$", (c, f(c)), textcoords="offset points", xytext=(8, -20),
                fontsize=15, color=COLOR_TANGENT)

    ax.set_title("Теорема Лагранжа: $f'(c)=\\dfrac{f(b)-f(a)}{b-a}$")
    ax.legend(loc="lower right", fontsize=12)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    savefig(fig, "lagrange.png")


def save_extrema():
    """Локальные экстремумы на примере x^3 - 3x."""
    def f(x):
        return x**3 - 3 * x

    def fp(x):
        return 3 * x**2 - 3

    xs = np.linspace(-2.4, 2.4, 500)
    ys = f(xs)

    fig, ax = plt.subplots(figsize=(9, 6))
    setup_axes(ax, (-2.6, 2.6), (-4.5, 4.5))

    ax.plot(xs, ys, color=COLOR_F, lw=3, label=r"$f(x)=x^3-3x$")

    xmax, ymax = -1, f(-1)
    xmin, ymin = 1, f(1)
    ax.plot([xmax], [ymax], "o", color=COLOR_ACCENT, markersize=12, zorder=5)
    ax.plot([xmin], [ymin], "o", color="#16a34a", markersize=12, zorder=5)

    for x0, y0 in [(xmax, ymax), (xmin, ymin)]:
        t = np.linspace(x0 - 0.6, x0 + 0.6, 20)
        ax.plot(t, np.full_like(t, y0), color=COLOR_NEUTRAL, lw=1.5, alpha=0.7)

    ax.annotate("локальный максимум\n$f'(-1)=0,\\ f''(-1)<0$",
                (xmax, ymax), textcoords="offset points",
                xytext=(-150, 25), fontsize=11, color=COLOR_ACCENT,
                arrowprops=dict(arrowstyle="->", color=COLOR_ACCENT, lw=1.2))
    ax.annotate("локальный минимум\n$f'(1)=0,\\ f''(1)>0$",
                (xmin, ymin), textcoords="offset points",
                xytext=(30, -55), fontsize=11, color="#16a34a",
                arrowprops=dict(arrowstyle="->", color="#16a34a", lw=1.2))

    ax.text(-1.9, 3.5, r"$f'>0$", color=COLOR_NEUTRAL, fontsize=13)
    ax.text(-0.3, 3.5, r"$f'<0$", color=COLOR_NEUTRAL, fontsize=13)
    ax.text(1.5, 3.5, r"$f'>0$", color=COLOR_NEUTRAL, fontsize=13)

    ax.set_title("Смена знака $f'$ определяет локальные экстремумы")
    ax.legend(loc="lower right", fontsize=12)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    savefig(fig, "extrema.png")


def save_convexity():
    """Выпуклость: хорда над графиком, касательная под графиком."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    xs = np.linspace(-2, 2, 400)

    ax = axes[0]
    ys = xs**2
    ax.plot(xs, ys, color=COLOR_F, lw=3, label=r"$f(x)=x^2$")
    a, b = -1.4, 1.6
    ax.plot([a, b], [a**2, b**2], color=COLOR_SECANT, lw=2.2, ls="--",
            label=r"хорда лежит выше графика")
    ax.plot([a, b], [a**2, b**2], "o", color=COLOR_SECANT, markersize=9)
    x0 = 0.4
    t = np.linspace(x0 - 1.2, x0 + 1.2, 30)
    tangent = 2 * x0 * (t - x0) + x0**2
    ax.plot(t, tangent, color=COLOR_TANGENT, lw=2.2,
            label=r"касательная лежит ниже графика")
    ax.plot([x0], [x0**2], "o", color=COLOR_TANGENT, markersize=10)
    ax.set_title("Выпуклая функция: $f''\\geq 0$")
    setup_axes(ax, (-2.1, 2.3), (-0.8, 4.5))
    ax.legend(loc="upper center", fontsize=11)
    ax.set_xlabel("x")

    ax = axes[1]
    ys = -(xs**2) + 3
    ax.plot(xs, ys, color=COLOR_F, lw=3, label=r"$f(x)=-x^2+3$")
    a, b = -1.4, 1.6
    ax.plot([a, b], [-a**2 + 3, -b**2 + 3], color=COLOR_SECANT, lw=2.2,
            ls="--", label=r"хорда лежит ниже графика")
    ax.plot([a, b], [-a**2 + 3, -b**2 + 3], "o", color=COLOR_SECANT, markersize=9)
    x0 = 0.4
    t = np.linspace(x0 - 1.2, x0 + 1.2, 30)
    tangent = -2 * x0 * (t - x0) + (-x0**2 + 3)
    ax.plot(t, tangent, color=COLOR_TANGENT, lw=2.2,
            label=r"касательная лежит выше графика")
    ax.plot([x0], [-x0**2 + 3], "o", color=COLOR_TANGENT, markersize=10)
    ax.set_title("Вогнутая функция: $f''\\leq 0$")
    setup_axes(ax, (-2.1, 2.3), (-1.5, 4.5))
    ax.legend(loc="lower center", fontsize=11)
    ax.set_xlabel("x")

    fig.suptitle("Геометрия выпуклости и вогнутости", fontsize=16)
    fig.tight_layout()
    savefig(fig, "convexity.png")


def save_inflection():
    """Точка перегиба: смена знака f''."""
    def f(x):
        return x**3 - 3 * x

    def fpp(x):
        return 6 * x

    xs = np.linspace(-2.2, 2.2, 500)
    ys = f(xs)

    fig, ax = plt.subplots(figsize=(9, 6))
    setup_axes(ax, (-2.4, 2.4), (-4.5, 4.5))

    left_mask = xs <= 0
    right_mask = xs >= 0
    ax.plot(xs[left_mask], ys[left_mask], color="#dc2626", lw=3,
            label=r"$f''<0$: выпуклость вверх")
    ax.plot(xs[right_mask], ys[right_mask], color="#2563eb", lw=3,
            label=r"$f''>0$: выпуклость вниз")

    ax.plot([0], [0], "o", color="#7c3aed", markersize=14, zorder=6)
    ax.annotate("точка перегиба\n$f''(0)=0$", (0, 0),
                textcoords="offset points", xytext=(20, 25), fontsize=12,
                color="#7c3aed",
                arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=1.2))

    t = np.linspace(-1.2, 1.2, 30)
    ax.plot(t, -3 * t, color="#7c3aed", lw=1.6, ls="--", alpha=0.7,
            label=r"касательная в точке перегиба")

    ax.set_title("Точка перегиба функции $f(x)=x^3-3x$")
    ax.legend(loc="lower right", fontsize=11)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    savefig(fig, "inflection.png")


def save_lhopital_vs_taylor():
    """Иллюстрация: (x - sin x) / x^3 стремится к 1/6."""
    xs = np.linspace(-1.2, 1.2, 500)
    mask = np.abs(xs) > 1e-3
    xs_plot = xs[mask]
    ratio = (xs_plot - np.sin(xs_plot)) / xs_plot**3

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.axhline(1 / 6, color=COLOR_ACCENT, lw=1.8, ls="--",
               label=r"предел $=\dfrac{1}{6}$")
    ax.plot(xs_plot, ratio, color=COLOR_F, lw=3,
            label=r"$\dfrac{x-\sin x}{x^3}$")
    ax.axvline(0, color=COLOR_NEUTRAL, lw=0.8, alpha=0.6)
    ax.grid(True, alpha=0.25)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(0.10, 0.22)

    ax.set_title("Правило Лопиталя и Тейлор дают один ответ")
    ax.legend(loc="upper right", fontsize=12)
    ax.set_xlabel("x")
    ax.set_ylabel("значение отношения")
    savefig(fig, "lhopital_limit.png")


def taylor_sin_coefficients(n):
    """Возвращает коэффициенты многочлена Тейлора для sin(x) порядка n в нуле."""
    coeffs = np.zeros(n + 1)
    for k in range(n + 1):
        if k % 2 == 1:
            sign = 1 if ((k - 1) // 2) % 2 == 0 else -1
            coeffs[k] = sign / math.factorial(k)
    return coeffs


def eval_poly(coeffs, x):
    y = np.zeros_like(x)
    for k, c in enumerate(coeffs):
        if c == 0:
            continue
        y = y + c * x**k
    return y


def save_taylor_animation():
    """GIF: приближение sin(x) многочленами Тейлора разных порядков."""
    xs = np.linspace(-2 * np.pi, 2 * np.pi, 600)
    ys_true = np.sin(xs)

    orders = [1, 3, 5, 7, 9, 11, 13, 15]

    with TemporaryDirectory() as tmpdir:
        frame_paths = []
        for i, n in enumerate(orders):
            coeffs = taylor_sin_coefficients(n)
            ys_poly = eval_poly(coeffs, xs)

            fig, ax = plt.subplots(figsize=(9, 6))
            ax.plot(xs, ys_true, color=COLOR_F, lw=3,
                    label=r"$\sin x$")
            ax.plot(xs, ys_poly, color=COLOR_ACCENT, lw=2.5,
                    label=f"многочлен Тейлора порядка {n}")
            ax.plot([0], [0], "o", color="#7c3aed", markersize=10, zorder=5)
            ax.axhline(0, color=COLOR_NEUTRAL, lw=0.8, alpha=0.6)
            ax.axvline(0, color=COLOR_NEUTRAL, lw=0.8, alpha=0.6)
            ax.grid(True, alpha=0.25)
            ax.set_xlim(-2 * np.pi, 2 * np.pi)
            ax.set_ylim(-2.5, 2.5)
            ax.set_title(f"Приближение $\\sin x$ в окрестности нуля, $n={n}$")
            ax.legend(loc="upper left", fontsize=12)
            ax.set_xlabel("x")
            ax.set_ylabel("y")

            frame_path = Path(tmpdir) / f"frame_{i:02d}.png"
            fig.savefig(frame_path, dpi=110, bbox_inches="tight")
            plt.close(fig)
            frame_paths.append(frame_path)

        ASSETS.mkdir(exist_ok=True, parents=True)
        gif_path = ASSETS / "taylor_sin.gif"
        frames = [imageio.imread(p) for p in frame_paths]
        imageio.mimsave(gif_path, frames, duration=900, loop=0)
        print(f"  wrote {gif_path.relative_to(ROOT)}")


def main():
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
