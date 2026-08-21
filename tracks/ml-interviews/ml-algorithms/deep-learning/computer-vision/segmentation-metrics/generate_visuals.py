"""Точные схемы для темы «Метрики сегментации: mIoU, Dice и PQ».

Все числа считаются на настоящих бинарных масках: пиксельная точность, IoU,
Dice, чувствительность к размеру объекта и разложение PQ = SQ × RQ.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from scipy.ndimage import binary_dilation

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


def _bare(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def _despine(ax, keep=("left", "bottom")):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)


# ==========================================================================
# Метрики
# ==========================================================================
def iou(a, b):
    u = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / u) if u else 1.0


def dice(a, b):
    s = a.sum() + b.sum()
    return float(2 * np.logical_and(a, b).sum() / s) if s else 1.0


def pixel_accuracy(pred, gt):
    return float((pred == gt).mean())


# --------------------------------------------------------------------------
# 1. Пиксельная точность врёт
# --------------------------------------------------------------------------
def draw_pixel_accuracy_lies():
    n = 256
    yy, xx = np.mgrid[0:n, 0:n]
    gt = (xx - n * 0.5) ** 2 + (yy - n * 0.5) ** 2 < (n * 0.09) ** 2   # мелкий объект
    empty = np.zeros_like(gt)
    good = binary_dilation(gt, iterations=3)   # чуть раздутая, но осмысленная маска

    variants = [
        (empty, "предсказать «всё фон»", C_GRAY),
        (good, "разумное предсказание", C_GREEN),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.4))

    ax = axes[0]
    ax.imshow(gt, cmap=ListedColormap([C_PANEL, C_INK]), interpolation="nearest")
    share = gt.mean()
    ax.set_title(f"истинная маска\nобъект занимает {share:.1%} пикселей", pad=10,
                 fontsize=11)
    _bare(ax)

    for ax, (pred, name, color) in zip(axes[1:], variants):
        ax.imshow(pred, cmap=ListedColormap([C_PANEL, color]), interpolation="nearest")
        pa = pixel_accuracy(pred, gt)
        v = iou(pred, gt)
        ax.set_title(f"{name}\npixel acc = {pa:.1%}   IoU = {v:.2f}", pad=10, fontsize=11)
        _bare(ax)

    fig.suptitle("Вырожденное решение получает почти идеальную пиксельную точность",
                 fontsize=13, y=1.0)
    fig.tight_layout()
    _save(fig, "pixel_accuracy_lies.png")
    return pixel_accuracy(empty, gt), iou(empty, gt)


# --------------------------------------------------------------------------
# 2. Точная связь Dice и IoU
# --------------------------------------------------------------------------
def draw_iou_vs_dice():
    # проверяем формулу на настоящих масках, а не постулируем её
    n = 200
    yy, xx = np.mgrid[0:n, 0:n]
    gt = (xx - n * 0.45) ** 2 + (yy - n * 0.5) ** 2 < (n * 0.22) ** 2
    pairs = []
    for shift in range(0, 90, 6):
        pred = (xx - n * 0.45 - shift) ** 2 + (yy - n * 0.5) ** 2 < (n * 0.22) ** 2
        pairs.append((iou(gt, pred), dice(gt, pred)))
    pairs = np.array(pairs)
    formula = 2 * pairs[:, 0] / (1 + pairs[:, 0])
    max_err = float(np.max(np.abs(pairs[:, 1] - formula)))

    grid = np.linspace(0, 1, 200)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))

    ax = axes[0]
    ax.plot(grid, grid, color=C_GRAY, lw=1.6, ls="--", label="y = x")
    ax.plot(grid, 2 * grid / (1 + grid), color=C_ORANGE, lw=2.6,
            label=r"Dice $= 2\,\mathrm{IoU}/(1+\mathrm{IoU})$")
    ax.plot(pairs[:, 0], pairs[:, 1], "o", color=C_BLUE, ms=5,
            label="замеры на масках")
    ax.set_xlabel("IoU")
    ax.set_ylabel("Dice")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right", fontsize=9.5)
    ax.set_title(f"Одно однозначно определяет другое\n"
                 f"максимальное расхождение с формулой: {max_err:.2e}",
                 pad=10, fontsize=11)
    _despine(ax)

    ax = axes[1]
    ax.plot(grid, 2 * grid / (1 + grid) - grid, color=C_GREEN, lw=2.6)
    peak = grid[np.argmax(2 * grid / (1 + grid) - grid)]
    peak_v = float(np.max(2 * grid / (1 + grid) - grid))
    ax.axvline(peak, color=C_INK, lw=1.0, ls=":")
    ax.text(peak + 0.02, peak_v, f"  максимум разрыва\n  при IoU ≈ {peak:.2f}: {peak_v:.2f}",
            fontsize=10, va="center")
    ax.set_xlabel("IoU")
    ax.set_ylabel("Dice − IoU")
    ax.set_xlim(0, 1)
    ax.set_title("Dice всегда мягче, и мягче всего — в середине", pad=10)
    _despine(ax)

    fig.suptitle("Dice и IoU монотонно связаны: ранжирование моделей они не меняют",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "iou_vs_dice.png")
    return max_err, peak, peak_v


# --------------------------------------------------------------------------
# 3. Одна и та же ошибка границы стоит по-разному
# --------------------------------------------------------------------------
def draw_small_object_sensitivity():
    n = 400
    yy, xx = np.mgrid[0:n, 0:n]
    radii = [6, 10, 16, 26, 42, 68]
    err_px = 2

    ious, dices, areas = [], [], []
    for r in radii:
        gt = (xx - n // 2) ** 2 + (yy - n // 2) ** 2 < r ** 2
        pred = binary_dilation(gt, iterations=err_px)
        ious.append(iou(gt, pred))
        dices.append(dice(gt, pred))
        areas.append(int(gt.sum()))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4),
                             gridspec_kw={"width_ratios": [1.1, 1]})

    ax = axes[0]
    for r, color in zip((radii[0], radii[-1]), (C_ORANGE, C_BLUE)):
        gt = (xx - n // 2) ** 2 + (yy - n // 2) ** 2 < r ** 2
        pred = binary_dilation(gt, iterations=err_px)
        ax.contour(pred, levels=[0.5], colors=[color], linewidths=1.8,
                   linestyles="dashed")
        ax.contour(gt, levels=[0.5], colors=[C_INK], linewidths=2.0)
        ax.text(n // 2 + r + 6, n // 2 - r,
                f"r = {r}: IoU {iou(gt, pred):.2f}", color=color, fontsize=10)
    ax.set_xlim(n // 2 - 90, n // 2 + 130)
    ax.set_ylim(n // 2 + 90, n // 2 - 90)
    ax.set_aspect("equal")
    ax.set_title(f"Обе маски раздуты ровно на {err_px} пикселя", pad=10)
    _bare(ax)

    ax = axes[1]
    ax.plot(areas, ious, "o-", color=C_ORANGE, lw=2.4, label="IoU")
    ax.plot(areas, dices, "o-", color=C_GREEN, lw=2.4, label="Dice")
    ax.set_xscale("log")
    ax.set_xlabel("площадь объекта, пикселей")
    ax.set_ylabel("метрика при ошибке 2 px")
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", fontsize=10)
    ax.set_title("Мелкий объект наказывается несравнимо сильнее", pad=10)
    _despine(ax)

    fig.suptitle("Абсолютная ошибка одна, цена — разная: вот почему mIoU "
                 "проседает на редких мелких классах", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "small_object_sensitivity.png")
    return list(zip(areas, [round(v, 3) for v in ious]))


# --------------------------------------------------------------------------
# 4. Panoptic Quality = SQ × RQ
# --------------------------------------------------------------------------
def panoptic_quality(gt_masks, pred_masks):
    """PQ по определению: сопоставление по IoU > 0.5 (оно единственно возможное)."""
    matches = []
    used_pred = set()
    for gi, g in enumerate(gt_masks):
        for pi, p in enumerate(pred_masks):
            if pi in used_pred:
                continue
            v = iou(g, p)
            if v > 0.5:
                matches.append((gi, pi, v))
                used_pred.add(pi)
                break
    tp = len(matches)
    fp = len(pred_masks) - tp
    fn = len(gt_masks) - tp
    sq = float(np.mean([m[2] for m in matches])) if tp else 0.0
    rq = tp / (tp + 0.5 * fp + 0.5 * fn) if (tp + fp + fn) else 0.0
    return sq * rq, sq, rq, tp, fp, fn, matches


def draw_panoptic_quality():
    n = 260
    yy, xx = np.mgrid[0:n, 0:n]

    def disc(cx, cy, r):
        return (xx - cx) ** 2 + (yy - cy) ** 2 < r ** 2

    gt_masks = [disc(70, 80, 38), disc(160, 90, 32), disc(110, 190, 30)]
    pred_masks = [
        disc(73, 83, 36),      # хорошо совпал
        disc(163, 92, 26),     # совпал хуже
        disc(220, 210, 24),    # выдумка → FP
    ]                          # третий истинный сегмент не найден → FN

    pq, sq, rq, tp, fp, fn, matches = panoptic_quality(gt_masks, pred_masks)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4),
                             gridspec_kw={"width_ratios": [1, 1, 1.15]})

    ax = axes[0]
    canvas = np.zeros((n, n))
    for i, g in enumerate(gt_masks, start=1):
        canvas[g] = i
    ax.imshow(canvas, cmap=ListedColormap([C_PANEL, C_INK, C_INK, C_INK]),
              interpolation="nearest")
    ax.set_title(f"истина: {len(gt_masks)} сегмента", pad=10)
    _bare(ax)

    ax = axes[1]
    canvas = np.zeros((n, n))
    matched_pred = {m[1] for m in matches}
    for i, p in enumerate(pred_masks):
        canvas[p] = 1 if i in matched_pred else 2
    ax.imshow(canvas, cmap=ListedColormap([C_PANEL, C_GREEN, C_ORANGE]),
              interpolation="nearest")
    ax.set_title(f"предсказание: {tp} совпало, {fp} лишний", pad=10)
    _bare(ax)

    ax = axes[2]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    T = ax.transAxes
    lines = [
        (f"TP = {tp}     FP = {fp}     FN = {fn}", C_INK, 12),
        ("", C_INK, 6),
        (f"SQ = средний IoU по TP = {sq:.3f}", C_BLUE, 11.5),
        ("     насколько точно обведено", C_GRAY, 9.5),
        ("", C_INK, 6),
        (f"RQ = TP / (TP + ½FP + ½FN) = {rq:.3f}", C_GREEN, 11.5),
        ("     это F1 по сегментам", C_GRAY, 9.5),
        ("", C_INK, 6),
        (f"PQ = SQ × RQ = {pq:.3f}", C_ORANGE, 13),
    ]
    y = 0.88
    for text, color, size in lines:
        ax.text(0.02, y, text, transform=T, color=color, fontsize=size,
                fontweight="bold" if size >= 12 else "normal")
        y -= 0.095
    ax.set_title("PQ раскладывается на два независимых вопроса", pad=10)

    fig.suptitle("Panoptic Quality: качество обводки отдельно, "
                 "полнота обнаружения отдельно", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "panoptic_quality.png")
    return pq, sq, rq


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print(f"Generating visuals in {ASSETS}")
    pa, iou_empty = draw_pixel_accuracy_lies()
    max_err, peak, peak_v = draw_iou_vs_dice()
    sens = draw_small_object_sensitivity()
    pq, sq, rq = draw_panoptic_quality()
    print("\nсводка для текста лекции:")
    print(f"  «всё фон»: pixel acc {pa:.4f}, IoU {iou_empty:.3f}")
    print(f"  Dice = 2IoU/(1+IoU), макс. расхождение с замерами {max_err:.2e}")
    print(f"  максимум разрыва Dice−IoU при IoU {peak:.2f}: {peak_v:.3f}")
    print(f"  IoU при ошибке 2 px по площадям: {sens}")
    print(f"  PQ {pq:.3f} = SQ {sq:.3f} × RQ {rq:.3f}")


if __name__ == "__main__":
    main()
