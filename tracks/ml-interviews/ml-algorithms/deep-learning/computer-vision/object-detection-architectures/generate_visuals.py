"""Точные схемы для темы «Архитектуры детекции объектов».

IoU, шаги NMS и венгерское сопоставление считаются на реальных координатах,
а не расставляются на глаз. Единственная схематичная картинка — родословная
семейств (structural diagram), в ней нет числовых утверждений.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"


def _apply_style():
    plt.rcParams.update(
        {
            "figure.facecolor": C_BG,
            "axes.facecolor": C_BG,
            "axes.edgecolor": C_GRAY,
            "axes.labelcolor": C_INK,
            "text.color": C_INK,
            "xtick.color": C_INK,
            "ytick.color": C_INK,
            "font.size": 11,
            "axes.titlesize": 12,
            "legend.frameon": False,
        }
    )


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"  {name}")


def _box(ax, xyxy, color, lw=2.0, ls="-", alpha=1.0, label=None):
    x1, y1, x2, y2 = xyxy
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                           edgecolor=color, lw=lw, ls=ls, alpha=alpha, label=label))


def iou(a, b):
    """IoU двух боксов в формате (x1, y1, x2, y2)."""
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def _clean(ax, xlim=(0, 10), ylim=(0, 10)):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


# --------------------------------------------------------------------------
# 1. Что вообще предсказывает детектор
# --------------------------------------------------------------------------
def draw_detection_task():
    gt = [(1.2, 1.5, 4.0, 6.2), (5.0, 3.0, 8.6, 7.4), (6.4, 0.8, 9.2, 3.2)]
    names = ["кошка", "собака", "мяч"]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.1))

    ax = axes[0]
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
    ax.text(5, 5, "одна метка\nна всё изображение", ha="center", va="center",
            fontsize=11, color=C_INK)
    ax.set_title("Классификация", pad=10)
    _clean(ax)

    ax = axes[1]
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
    _box(ax, gt[0], C_ORANGE, lw=2.6)
    ax.text(gt[0][0], gt[0][3] + 0.2, names[0], color=C_ORANGE, fontsize=10)
    ax.set_title("Локализация: один объект", pad=10)
    _clean(ax)

    ax = axes[2]
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
    for b, nm, c in zip(gt, names, (C_ORANGE, C_BLUE, C_GREEN)):
        _box(ax, b, c, lw=2.6)
        ax.text(b[0], b[3] + 0.2, nm, color=c, fontsize=10)
    ax.set_title("Детекция: сколько объектов — неизвестно заранее", pad=10)
    _clean(ax)

    fig.suptitle("Выход детектора — множество переменной длины", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "detection_task.png")


# --------------------------------------------------------------------------
# 2. Якоря и назначение по IoU
# --------------------------------------------------------------------------
def draw_iou_assignment():
    gt = (3.0, 3.0, 7.0, 6.6)
    anchors = [
        (2.6, 2.8, 6.6, 6.2),
        (3.6, 3.4, 8.0, 7.4),
        (1.0, 1.2, 4.2, 4.4),
        (6.2, 5.4, 9.4, 8.6),
    ]
    ious = [iou(gt, a) for a in anchors]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4),
                             gridspec_kw={"width_ratios": [1, 1.05]})

    ax = axes[0]
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
    _box(ax, gt, C_INK, lw=3.0)
    ax.text(gt[0], gt[3] + 0.25, "истинный бокс", color=C_INK, fontsize=10)
    for a, v in zip(anchors, ious):
        color = C_GREEN if v >= 0.5 else (C_ORANGE if v >= 0.3 else C_GRAY)
        _box(ax, a, color, lw=2.0, ls="--")
        ax.text(a[0] + 0.1, a[1] + 0.15, f"IoU {v:.2f}", color=color, fontsize=9.5)
    ax.set_title("Якоря вокруг объекта", pad=10)
    _clean(ax)

    ax = axes[1]
    order = np.argsort(ious)[::-1]
    labels = [f"якорь {i + 1}" for i in order]
    vals = [ious[i] for i in order]
    colors = [C_GREEN if v >= 0.5 else (C_ORANGE if v >= 0.3 else C_GRAY) for v in vals]
    ax.barh(labels, vals, color=colors, height=0.55)
    ax.axvline(0.5, color=C_INK, lw=1.4, ls="--")
    ax.text(0.5, -0.75, " порог 0.5: положительный якорь", color=C_INK, fontsize=10)
    ax.axvline(0.3, color=C_GRAY, lw=1.2, ls=":")
    ax.text(0.3, 3.55, "0.3 ", color=C_GRAY, fontsize=9.5, ha="right")
    for i, v in enumerate(vals):
        ax.text(v + 0.015, i, f"{v:.2f}", va="center", fontsize=10, color=C_INK)
    ax.set_xlim(0, 0.95)
    ax.invert_yaxis()
    ax.set_xlabel("IoU с истинным боксом")
    ax.set_title("Правило назначения: кто отвечает за объект", pad=10)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)

    fig.suptitle("Anchor-based: истина назначается якорям по порогу IoU",
                 fontsize=13, y=1.03)
    fig.tight_layout()
    _save(fig, "iou_assignment.png")


# --------------------------------------------------------------------------
# 3. NMS: как из плотной сетки предсказаний получается ответ
# --------------------------------------------------------------------------
def nms(boxes, scores, thr=0.5):
    """Классический greedy NMS. Возвращает (оставленные, подавленные_кем)."""
    order = list(np.argsort(scores)[::-1])
    keep, killed_by = [], {}
    while order:
        best = order.pop(0)
        keep.append(best)
        rest = []
        for i in order:
            if iou(boxes[best], boxes[i]) > thr:
                killed_by[i] = best
            else:
                rest.append(i)
        order = rest
    return keep, killed_by


def draw_nms_steps():
    boxes = [
        (2.8, 2.9, 6.9, 6.5), (3.1, 3.2, 7.2, 6.9), (2.5, 2.6, 6.6, 6.2),
        (3.4, 2.8, 7.4, 6.4),
        (5.6, 6.4, 9.2, 9.3), (5.9, 6.7, 9.5, 9.6),
    ]
    scores = [0.92, 0.85, 0.71, 0.66, 0.88, 0.74]
    keep, killed_by = nms(boxes, scores, thr=0.5)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5))

    ax = axes[0]
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
    for b, s in zip(boxes, scores):
        _box(ax, b, C_GRAY, lw=1.8)
        ax.text(b[0] + 0.08, b[3] - 0.45, f"{s:.2f}", color=C_INK, fontsize=9)
    ax.set_title(f"До NMS: {len(boxes)} предсказаний", pad=10)
    _clean(ax)

    ax = axes[1]
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
    for i, b in enumerate(boxes):
        if i in keep:
            continue
        _box(ax, b, C_GRAY, lw=1.2, ls=":", alpha=0.75)
    for i in keep:
        _box(ax, boxes[i], C_ORANGE, lw=2.8)
        ax.text(boxes[i][0] + 0.08, boxes[i][3] - 0.45, f"{scores[i]:.2f}",
                color=C_ORANGE, fontsize=10)
    ax.set_title(f"После NMS (IoU > 0.5): осталось {len(keep)}", pad=10)
    _clean(ax)

    lines = [
        f"бокс {i + 1} подавлен боксом {j + 1} (IoU {iou(boxes[i], boxes[j]):.2f})"
        for i, j in sorted(killed_by.items())
    ]
    fig.text(0.5, -0.04, "   ·   ".join(lines), ha="center", fontsize=9.5, color=C_GRAY)
    fig.suptitle("NMS — не обучаемый шаг, а ручное правило поверх модели",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "nms_steps.png")


# --------------------------------------------------------------------------
# 4. DETR: венгерское сопоставление вместо якорей и NMS
# --------------------------------------------------------------------------
def _greedy_assignment(cost):
    """Назначение «по строкам»: каждый объект берёт лучший из ещё свободных запросов."""
    used, pairs, total = set(), [], 0.0
    for i in range(cost.shape[0]):
        j = min((j for j in range(cost.shape[1]) if j not in used),
                key=lambda j: cost[i, j])
        used.add(j)
        pairs.append((i, j))
        total += cost[i, j]
    return pairs, total


def draw_hungarian_matching():
    # Два сильно перекрывающихся объекта — типичная сцена в толпе.
    gt = [(1.8, 2.2, 5.8, 7.0), (2.6, 3.0, 6.6, 7.8)]
    queries = [
        (2.3, 3.0, 6.3, 7.8),   # q1 — годится обоим, но объекту 2 подходит заметно лучше
        (0.8, 2.0, 4.8, 6.8),   # q2 — приемлем только для объекта 1
        (7.4, 1.0, 9.4, 3.0),   # q3 — пусто
        (0.6, 8.2, 2.4, 9.6),   # q4 — пусто
    ]
    cost = np.array([[1.0 - iou(g, q) for q in queries] for g in gt])

    rows, cols = linear_sum_assignment(cost)
    hungarian = list(zip(rows.tolist(), cols.tolist()))
    h_total = float(cost[rows, cols].sum())
    greedy, g_total = _greedy_assignment(cost)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6),
                             gridspec_kw={"width_ratios": [1, 1.25]})

    ax = axes[0]
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
    for k, g in enumerate(gt):
        _box(ax, g, C_INK, lw=2.8)
        ax.text(g[2] + 0.15, g[3] - 0.25, f"объект {k + 1}",
                color=C_INK, fontsize=9.5, ha="left")
    matched = set(cols.tolist())
    for i, q in enumerate(queries):
        if i in matched:
            _box(ax, q, C_ORANGE, lw=2.4, ls="--")
            ax.text(q[0] + 0.1, q[1] - 0.5, f"q{i + 1}", color=C_ORANGE, fontsize=10)
        else:
            _box(ax, q, C_GRAY, lw=1.6, ls=":")
            ax.text(q[0], q[1] - 0.5, f"q{i + 1} → ∅", color=C_GRAY, fontsize=9.5)
    ax.set_title("Два перекрывающихся объекта, четыре запроса", pad=10)
    _clean(ax)

    ax = axes[1]
    im = ax.imshow(cost, cmap=LinearSegmentedColormap.from_list(
        "warm", [C_BG, C_PANEL, C_ORANGE]), vmin=0, vmax=1)
    ax.set_xticks(range(len(queries)), [f"q{i + 1}" for i in range(len(queries))])
    ax.set_yticks(range(len(gt)), [f"объект {i + 1}" for i in range(len(gt))])
    for r in range(cost.shape[0]):
        for c in range(cost.shape[1]):
            picked = (r, c) in hungarian
            ax.text(c, r, f"{cost[r, c]:.2f}", ha="center", va="center", fontsize=10.5,
                    color=C_BG if cost[r, c] > 0.75 else C_INK,
                    fontweight="bold" if picked else "normal")
            if picked:
                ax.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False,
                                       edgecolor=C_GREEN, lw=3.2))
            if (r, c) in greedy and not picked:
                ax.add_patch(Rectangle((c - 0.45, r - 0.45), 0.9, 0.9, fill=False,
                                       edgecolor=C_BLUE, lw=2.0, ls="--"))
    ax.set_title("Стоимость пары $= 1 - \\mathrm{IoU}$", pad=10)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03).outline.set_visible(False)

    ax.text(0.0, 1.72,
            f"— — жадно, по строкам:  {g_total:.2f}", color=C_BLUE, fontsize=10.5)
    ax.text(0.0, 1.99,
            f"—— венгерский алгоритм:  {h_total:.2f}", color=C_GREEN, fontsize=10.5)

    fig.suptitle(
        "Объект 1 уступает свой лучший запрос объекту 2 — глобально это дешевле",
        fontsize=13, y=1.03)
    fig.tight_layout()
    _save(fig, "hungarian_matching.png")


# --------------------------------------------------------------------------
# 5. Родословная: что каждое поколение убрало из пайплайна
# --------------------------------------------------------------------------
def draw_family_tree():
    stages = [
        ("R-CNN\n2014", ["внешние proposals", "CNN на каждый кроп", "SVM + регрессор"], C_GRAY),
        ("Fast R-CNN\n2015", ["внешние proposals", "один прогон CNN", "RoI pooling"], C_GRAY),
        ("Faster R-CNN\n2015", ["RPN вместо\nselective search", "якоря", "NMS"], C_BLUE),
        ("YOLO / SSD\n2016", ["без proposals", "плотная сетка", "якоря, NMS"], C_BLUE),
        ("FCOS / CenterNet\n2019", ["без якорей", "предсказание\nиз точки", "NMS"], C_ORANGE),
        ("DETR\n2020", ["без якорей", "без NMS", "венгерское\nсопоставление"], C_GREEN),
    ]

    fig, ax = plt.subplots(figsize=(13, 4.6))
    w, gap = 1.72, 0.42
    for i, (title, bullets, color) in enumerate(stages):
        x = i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 1.1), w, 2.3, boxstyle="round,pad=0.06",
                                    facecolor=C_PANEL, edgecolor=color, lw=2.2))
        ax.text(x + w / 2, 3.05, title, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=C_INK)
        for j, b in enumerate(bullets):
            ax.text(x + w / 2, 2.45 - j * 0.44, b, ha="center", va="center",
                    fontsize=8.6, color=C_INK)
        if i:
            ax.add_patch(FancyArrowPatch((x - gap + 0.04, 2.25), (x - 0.04, 2.25),
                                         arrowstyle="-|>", mutation_scale=13,
                                         color=C_GRAY, lw=1.6))

    total = len(stages) * (w + gap) - gap
    ax.annotate("", xy=(total, 0.62), xytext=(0, 0.62),
                arrowprops=dict(arrowstyle="-|>", color=C_INK, lw=1.8))
    ax.text(total / 2, 0.24,
            "каждое поколение убирает ещё один написанный руками кусок пайплайна",
            ha="center", fontsize=10.5, color=C_INK)

    ax.set_xlim(-0.25, total + 0.25)
    ax.set_ylim(0, 3.7)
    ax.axis("off")
    fig.suptitle("Эволюция детекторов: что именно исчезает на каждом шаге",
                 fontsize=13, y=1.0)
    fig.tight_layout()
    _save(fig, "family_tree.png")


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print(f"Generating visuals in {ASSETS}")
    draw_detection_task()
    draw_iou_assignment()
    draw_nms_steps()
    draw_hungarian_matching()
    draw_family_tree()


if __name__ == "__main__":
    main()
