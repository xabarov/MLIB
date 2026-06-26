"""
График функции f(x) = x^4 - 4x^3 для раздела 13.2.

Показывает:
- локальный минимум в x=3, f(3)=-27 (стационарная точка, f' меняет знак - -> +);
- стационарную точку x=0 без экстремума (f' не меняет знака: остается <=0 по обе стороны);
- две точки перегиба x=0 и x=2 (f'' меняет знак);
- почему между точками перегиба 0 и 2 нет максимума: на всем (0, 3) производная неположительна,
  функция монотонно убывает, и точки перегиба влияют только на форму (выпуклость), не на монотонность.
"""

import numpy as np
import matplotlib.pyplot as plt


def f(x):
    return x**4 - 4 * x**3


def f1(x):
    return 4 * x**3 - 12 * x**2


def f2(x):
    return 12 * x**2 - 24 * x


x = np.linspace(-1.2, 4.3, 800)

fig, axes = plt.subplots(3, 1, figsize=(9, 11), sharex=True)
ax_f, ax_d1, ax_d2 = axes

# ---- f(x) ----
ax_f.plot(x, f(x), color="#1f4e79", linewidth=2, label=r"$f(x)=x^4-4x^3$")
ax_f.axhline(0, color="gray", linewidth=0.5)
ax_f.axvline(0, color="gray", linewidth=0.5)

# Зона монотонного убывания
ax_f.axvspan(0, 3, alpha=0.08, color="red", label=r"$f$ убывает: $f' \leq 0$")

# Точки
pts = [
    (0, f(0), "x=0:\nстационарная точка\n(не экстремум)\nточка перегиба", "tab:orange"),
    (2, f(2), "x=2:\nточка перегиба\n(не экстремум)", "tab:green"),
    (3, f(3), "x=3:\nлокальный минимум\nf(3) = -27", "tab:red"),
]
for xp, yp, label, color in pts:
    ax_f.plot(xp, yp, "o", color=color, markersize=9, zorder=5)
    ax_f.annotate(
        label,
        xy=(xp, yp),
        xytext=(xp + 0.4, yp + 12 if yp < -5 else yp + 18),
        fontsize=9,
        color="black",
        arrowprops=dict(arrowstyle="->", color=color, lw=1.2),
    )

ax_f.set_ylim(-35, 30)
ax_f.set_ylabel(r"$f(x)$", fontsize=12)
ax_f.set_title(r"$f(x)=x^4-4x^3$: убывает на $[0,3]$, поэтому между перегибами максимум невозможен",
               fontsize=11)
ax_f.legend(loc="upper left", fontsize=9)
ax_f.grid(alpha=0.3)

# ---- f'(x) ----
ax_d1.plot(x, f1(x), color="#9c27b0", linewidth=2, label=r"$f'(x)=4x^2(x-3)$")
ax_d1.axhline(0, color="gray", linewidth=0.5)
ax_d1.axvline(0, color="gray", linewidth=0.5)
ax_d1.axvspan(0, 3, alpha=0.08, color="red")

for xp, color in [(0, "tab:orange"), (3, "tab:red")]:
    ax_d1.plot(xp, f1(xp), "o", color=color, markersize=9, zorder=5)

ax_d1.annotate(
    "На (0, 3) имеем f'(x) < 0:\nфункция строго убывает,\nни локального максимума,\nни локального минимума внутри нет",
    xy=(1.5, f1(1.5)),
    xytext=(-1.1, -40),
    fontsize=9,
    arrowprops=dict(arrowstyle="->", color="gray"),
)

ax_d1.set_ylim(-30, 30)
ax_d1.set_ylabel(r"$f'(x)$", fontsize=12)
ax_d1.legend(loc="upper left", fontsize=9)
ax_d1.grid(alpha=0.3)

# ---- f''(x) ----
ax_d2.plot(x, f2(x), color="#2e7d32", linewidth=2, label=r"$f''(x)=12x(x-2)$")
ax_d2.axhline(0, color="gray", linewidth=0.5)
ax_d2.axvline(0, color="gray", linewidth=0.5)

for xp, color in [(0, "tab:orange"), (2, "tab:green")]:
    ax_d2.plot(xp, f2(xp), "o", color=color, markersize=9, zorder=5)

ax_d2.annotate("f'' меняет знак: + → −\nточка перегиба",
               xy=(0, 0), xytext=(-1.1, 25),
               fontsize=9,
               arrowprops=dict(arrowstyle="->", color="tab:orange"))

ax_d2.annotate("f'' меняет знак: − → +\nточка перегиба",
               xy=(2, 0), xytext=(2.3, -30),
               fontsize=9,
               arrowprops=dict(arrowstyle="->", color="tab:green"))

ax_d2.set_ylim(-25, 50)
ax_d2.set_xlabel(r"$x$", fontsize=12)
ax_d2.set_ylabel(r"$f''(x)$", fontsize=12)
ax_d2.legend(loc="upper left", fontsize=9)
ax_d2.grid(alpha=0.3)

plt.tight_layout()
out = "/mnt/share/gitlab_projects/wiki/mlib/SHAD/mathematical_analysis/6_derivative_applications/assets/x4_minus_4x3_analysis.png"
plt.savefig(out, dpi=130, bbox_inches="tight")
print(f"Saved: {out}")
