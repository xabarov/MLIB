"""
Иллюстрация для §3: четыре комбинации "открыто/замкнуто" на R.

(a) (0, 1)   - открыто, не замкнуто
(b) [0, 1]   - замкнуто, не открыто
(c) [0, 1)   - ни открыто, ни замкнуто
(d) R       - и открыто, и замкнуто (плюс пустое)
"""

import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(4, 1, figsize=(10, 7))

config = [
    dict(
        ax=axes[0],
        title=r"(а) $(0,\,1)$ — открыто, не замкнуто",
        left=0, right=1, left_closed=False, right_closed=False,
        note=r"край $\{0,\,1\}$ НЕ принадлежит, граница не лежит в множестве"
             "\n"
             r"⇒ нельзя «убежать» в граничную точку: предел может выйти из множества",
    ),
    dict(
        ax=axes[1],
        title=r"(б) $[0,\,1]$ — замкнуто, не открыто",
        left=0, right=1, left_closed=True, right_closed=True,
        note=r"край $\{0,\,1\}$ ПРИНАДЛЕЖИТ, граница в множестве"
             "\n"
             r"⇒ в точке 0 нет «места для шага влево»: множество не открыто",
    ),
    dict(
        ax=axes[2],
        title=r"(в) $[0,\,1)$ — НИ открыто, НИ замкнуто",
        left=0, right=1, left_closed=True, right_closed=False,
        note=r"0 принадлежит (нет места слева ⇒ не открыто),"
             "\n"
             r"1 не принадлежит, но является пределом (1 − 1/n ∈ A) ⇒ не замкнуто",
    ),
    dict(
        ax=axes[3],
        title=r"(г) $\mathbb{R}$ — И открыто, И замкнуто (пустое $\varnothing$ — тоже)",
        left=-1.5, right=2.5, left_closed=None, right_closed=None,
        note=r"граничных точек нет (граница пуста), оба условия выполнены тривиально",
    ),
]


def draw(ax, left, right, left_closed, right_closed, title, note):
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-1, 1)
    ax.axhline(0, color="black", linewidth=0.8)

    # отрезок числовой прямой с метками
    for tick in [-0.5, 0, 0.5, 1, 1.5]:
        ax.plot([tick, tick], [-0.07, 0.07], color="black", linewidth=0.8)
        ax.text(tick, -0.32, f"{tick:g}", ha="center", fontsize=9)

    # подсветка множества
    if title.startswith("(г)"):
        ax.axvspan(-0.5, 1.5, alpha=0.25, color="#1f77b4")
        ax.text(0.5, 0.5, "вся прямая", ha="center", fontsize=10, style="italic",
                color="#0b3d72")
    else:
        ax.axvspan(left, right, alpha=0.25, color="#1f77b4")
        # концы
        for x, closed in [(left, left_closed), (right, right_closed)]:
            if closed:
                ax.plot(x, 0, "o", color="#0b3d72", markersize=11,
                        markeredgecolor="#0b3d72", zorder=5)
            else:
                ax.plot(x, 0, "o", color="white", markersize=11,
                        markeredgecolor="#0b3d72", markeredgewidth=2, zorder=5)

    ax.set_title(title, fontsize=11, loc="left")
    ax.text(1.55, 0.0, note, fontsize=8.5, va="center", color="#444")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


for cfg in config:
    draw(**cfg)

# легенда внизу
fig.text(
    0.02, 0.01,
    r"• — точка ВКЛЮЧЕНА (граница принадлежит множеству)     "
    r"○ — точка НЕ включена (открытый конец)",
    fontsize=9, color="#333",
)

plt.suptitle("Четыре варианта: «открыто» и «замкнуто» — не противоположности",
             fontsize=12, y=0.995)
plt.tight_layout(rect=[0, 0.03, 1, 0.98])

out = "/mnt/share/gitlab_projects/wiki/mlib/SHAD/mathematical_analysis/10_metric_normed_spaces/assets/open_closed_four_cases.png"
plt.savefig(out, dpi=140, bbox_inches="tight")
print(f"Saved: {out}")
