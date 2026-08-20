"""
Точные схемы для лекции про интегралы с параметром, гамма- и бета-функции.

Запуск:
    python3 generate_visuals.py
"""

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


def draw_parameter_family_area(out_name: str = "parameter_family_area.png") -> None:
    _apply_style()
    x = np.linspace(0.0, 3.5, 500)
    params = [0.6, 1.1, 1.8]
    colors = [C_BLUE, C_GREEN, C_ORANGE]

    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    for a, color in zip(params, colors):
        y = np.exp(-a * x)
        ax.plot(x, y, color=color, lw=2.3, label=rf"$a={a}$")

    a0 = 1.1
    y0 = np.exp(-a0 * x)
    ax.fill_between(x, 0, y0, color=C_BLUE, alpha=0.14)
    ax.text(1.55, 0.56, "при изменении параметра\nменяется вся площадь", fontsize=10, color=C_INK)
    ax.text(2.18, 0.16, r"$F(a)=\int_0^\infty e^{-ax}\,dx$", fontsize=11, color=C_PURPLE)
    ax.set_title("Интеграл с параметром как семейство площадей", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_xlim(0, 3.5)
    ax.set_ylim(0, 1.05)
    ax.grid(True)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    _save(fig, out_name)


def draw_differentiate_under_integral_sign(
    out_name: str = "differentiate_under_integral_sign.png",
) -> None:
    _apply_style()
    x = np.linspace(0.0, 1.0, 500)
    a = 0.6
    da = 0.25
    f = np.exp(a * x)
    f_shift = np.exp((a + da) * x)
    df = x * np.exp(a * x)

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.8))

    axes[0].plot(x, f, color=C_BLUE, lw=2.4, label=r"$f(x,a)$")
    axes[0].plot(x, f_shift, color=C_ORANGE, lw=2.2, label=r"$f(x,a+\Delta a)$")
    axes[0].fill_between(x, f, f_shift, color=C_ORANGE, alpha=0.18)
    axes[0].text(0.47, 1.42, "изменение параметра\nдеформирует весь график", fontsize=10, color=C_INK)
    axes[0].set_title("Семейство подынтегральных функций", fontsize=11, weight="bold")
    axes[0].set_xlabel(r"$x$")
    axes[0].set_ylabel(r"$f(x,a)$")
    axes[0].grid(True)
    axes[0].legend(loc="upper left", fontsize=9, framealpha=0.95)

    axes[1].plot(x, df, color=C_GREEN, lw=2.4, label=r"$\partial f/\partial a$")
    axes[1].fill_between(x, 0, df, color=C_GREEN, alpha=0.16)
    axes[1].text(0.12, 0.63, r"$F'(a)=\int_0^1 \frac{\partial f}{\partial a}(x,a)\,dx$", fontsize=11, color=C_PURPLE)
    axes[1].text(0.12, 0.49, "производная интеграла\nсобирает локальные изменения", fontsize=10, color=C_INK)
    axes[1].set_title("Дифференцирование под знаком интеграла", fontsize=11, weight="bold")
    axes[1].set_xlabel(r"$x$")
    axes[1].set_ylabel(r"$\partial f/\partial a$")
    axes[1].grid(True)
    axes[1].legend(loc="upper left", fontsize=9, framealpha=0.95)

    _save(fig, out_name)


def draw_gamma_family(out_name: str = "gamma_family.png") -> None:
    _apply_style()
    x = np.linspace(0.001, 8.0, 1200)
    params = [0.5, 1.5, 3.0]
    colors = [C_ORANGE, C_BLUE, C_GREEN]

    fig, ax = plt.subplots(figsize=(8.8, 5.0))
    for s, color in zip(params, colors):
        y = x ** (s - 1) * np.exp(-x)
        ax.plot(x, y, color=color, lw=2.3, label=rf"$s={s}$")

    y_mid = x ** (1.5 - 1) * np.exp(-x)
    ax.fill_between(x, 0, y_mid, color=C_BLUE, alpha=0.12)
    ax.text(3.35, 0.56, r"$\Gamma(s)=\int_0^\infty x^{s-1}e^{-x}\,dx$", fontsize=11, color=C_PURPLE)
    ax.text(4.1, 0.36, "около нуля важна степень,\nна бесконечности спасает экспонента", fontsize=10, color=C_INK)
    ax.set_title("Семейство подынтегральных функций для гамма-функции", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$x^{s-1}e^{-x}$")
    ax.set_xlim(0, 8.0)
    ax.set_ylim(0, 1.25)
    ax.grid(True)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    _save(fig, out_name)


def draw_beta_gamma_relation(out_name: str = "beta_gamma_relation.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.9))

    x = np.linspace(0.0, 4.0, 220)
    y = np.linspace(0.0, 4.0, 220)
    xx, yy = np.meshgrid(x, y)
    mask = xx + yy <= 4.0

    axes[0].contourf(xx, yy, mask.astype(float), levels=[0.5, 1.5], colors=[C_BLUE], alpha=0.18)
    for c in [1.0, 2.0, 3.0, 4.0]:
        xs = np.linspace(0.0, c, 100)
        ys = c - xs
        axes[0].plot(xs, ys, color=C_GRAY, lw=1.0)
        axes[0].text(c - 0.1, 0.12, rf"$t={c:.0f}$", fontsize=9, color=C_GRAY, ha="right")
    axes[0].arrow(0, 0, 3.7, 0, width=0.015, head_width=0.12, head_length=0.14, color=C_INK, length_includes_head=True)
    axes[0].arrow(0, 0, 0, 3.7, width=0.015, head_width=0.12, head_length=0.14, color=C_INK, length_includes_head=True)
    axes[0].text(3.86, -0.05, r"$x$", fontsize=11)
    axes[0].text(-0.1, 3.86, r"$y$", fontsize=11)
    axes[0].text(1.3, 2.45, r"$x+y=t$", fontsize=10, color=C_GRAY)
    axes[0].text(0.75, 1.0, "масштаб задаётся\nсуммой $t=x+y$", fontsize=10, color=C_INK)
    axes[0].set_xlim(0, 4.0)
    axes[0].set_ylim(0, 4.0)
    axes[0].set_aspect("equal")
    axes[0].set_title("Первая четверть и линии $x+y=t$", fontsize=11, weight="bold")
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[0].grid(False)

    u = np.linspace(0.0, 1.0, 400)
    beta_shape = (u ** (2.2 - 1)) * ((1 - u) ** (3.1 - 1))
    axes[1].plot(u, beta_shape, color=C_ORANGE, lw=2.5)
    axes[1].fill_between(u, 0, beta_shape, color=C_ORANGE, alpha=0.18)
    axes[1].text(0.08, beta_shape.max() * 0.88, r"$u=\frac{x}{x+y}$", fontsize=11, color=C_PURPLE)
    axes[1].text(0.08, beta_shape.max() * 0.69, r"$B(p,q)=\int_0^1 u^{p-1}(1-u)^{q-1}\,du$", fontsize=11, color=C_INK)
    axes[1].text(0.08, beta_shape.max() * 0.47, r"$\Gamma(p)\Gamma(q)=\Gamma(p+q)B(p,q)$", fontsize=11, color=C_GREEN)
    axes[1].set_title("После замены переменных возникает бета-интеграл", fontsize=11, weight="bold")
    axes[1].set_xlabel(r"$u$")
    axes[1].set_ylabel(r"$u^{p-1}(1-u)^{q-1}$")
    axes[1].grid(True)

    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_parameter_family_area()
    draw_differentiate_under_integral_sign()
    draw_gamma_family()
    draw_beta_gamma_relation()
    print(f"Saved visuals to {ASSETS}")


if __name__ == "__main__":
    main()
