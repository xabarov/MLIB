"""Точные схемы для темы «Метрики детекции: IoU, PR-кривая, AP и mAP».

Сопоставление предсказаний с истиной, PR-кривая и все варианты AP считаются
здесь настоящим кодом по правилам VOC/COCO. Числа на картинках — результат
прогона, а не подобранные вручную значения.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

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


def _box(ax, xyxy, color, lw=2.0, ls="-", alpha=1.0):
    x1, y1, x2, y2 = xyxy
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                           edgecolor=color, lw=lw, ls=ls, alpha=alpha))


def _clean(ax, lim=10):
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def _despine(ax, keep=("left", "bottom")):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)


# ==========================================================================
# Ядро: сопоставление и AP по правилам VOC / COCO
# ==========================================================================
def iou(a, b):
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def match_detections(preds, scores, gts, thr):
    """Жадное сопоставление по убыванию уверенности (правило VOC/COCO).

    Возвращает массив флагов TP/FP в порядке убывания уверенности и число FN.
    Каждый истинный бокс может быть занят только один раз: повторные попадания
    в уже занятый объект становятся FP — так штрафуются дубликаты.
    """
    order = np.argsort(scores)[::-1]
    taken = [False] * len(gts)
    flags = []
    for i in order:
        best_j, best_iou = -1, 0.0
        for j, g in enumerate(gts):
            v = iou(preds[i], g)
            if v > best_iou:
                best_iou, best_j = v, j
        if best_iou >= thr and best_j >= 0 and not taken[best_j]:
            taken[best_j] = True
            flags.append(1)
        else:
            flags.append(0)
    return np.array(flags), int(sum(1 for t in taken if not t))


def pr_curve(flags, n_gt):
    """Precision и recall как функции числа взятых предсказаний."""
    tp = np.cumsum(flags)
    fp = np.cumsum(1 - flags)
    recall = tp / n_gt
    precision = tp / np.maximum(tp + fp, 1e-12)
    return precision, recall


def ap_all_point(precision, recall):
    """VOC2010+ / «все точки»: площадь под монотонной огибающей."""
    mrec = np.concatenate([[0.0], recall, [1.0]])
    mpre = np.concatenate([[0.0], precision, [0.0]])
    for i in range(len(mpre) - 2, -1, -1):      # огибающая справа налево
        mpre[i] = max(mpre[i], mpre[i + 1])
    idx = np.where(mrec[1:] != mrec[:-1])[0]
    return float(np.sum((mrec[idx + 1] - mrec[idx]) * mpre[idx + 1])), mrec, mpre


def ap_interp(precision, recall, points):
    """Интерполяция по сетке recall: 11 точек (VOC2007) или 101 (COCO)."""
    envelope = []
    for r in points:
        mask = recall >= r
        envelope.append(float(precision[mask].max()) if mask.any() else 0.0)
    return float(np.mean(envelope)), np.array(envelope)


# --------------------------------------------------------------------------
# 1. Геометрия IoU и её слепое пятно
# --------------------------------------------------------------------------
def draw_iou_geometry():
    gt = (2.5, 3.0, 7.5, 7.0)
    cases = [
        ((2.7, 3.2, 7.7, 7.2), "почти точно"),
        ((3.6, 3.8, 8.6, 7.8), "сдвиг"),
        ((4.2, 4.2, 6.2, 5.8), "внутри, но мелкий"),
    ]
    far = [
        ((8.2, 7.6, 9.6, 9.2), "рядом"),
        ((0.3, 0.4, 1.7, 2.0), "далеко"),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(15, 3.5))
    for ax, (b, name) in zip(axes[:3], cases):
        ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
        _box(ax, gt, C_INK, lw=2.6)
        _box(ax, b, C_ORANGE, lw=2.4, ls="--")
        ax.set_title(f"{name}\nIoU = {iou(gt, b):.2f}", pad=8, fontsize=11)
        _clean(ax)
    for ax, (b, name) in zip(axes[3:], far):
        ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
        _box(ax, gt, C_INK, lw=2.6)
        _box(ax, b, C_GRAY, lw=2.4, ls="--")
        ax.set_title(f"{name}\nIoU = {iou(gt, b):.2f}", pad=8, fontsize=11, color=C_GRAY)
        _clean(ax)

    fig.suptitle("IoU не различает «мимо на пиксель» и «мимо на всё изображение» — "
                 "оба случая дают ровно 0",
                 fontsize=13, y=1.06)
    fig.tight_layout()
    _save(fig, "iou_geometry.png")


# --------------------------------------------------------------------------
# 2. Как предсказания превращаются в TP / FP / FN
# --------------------------------------------------------------------------
def draw_matching():
    gts = [(1.2, 5.2, 4.4, 8.8), (5.4, 4.8, 8.8, 8.6), (2.0, 0.8, 5.0, 3.8)]
    preds = [
        (1.4, 5.4, 4.6, 8.9),    # хорошо накрывает объект 1
        (5.6, 5.0, 9.0, 8.7),    # хорошо накрывает объект 2
        (1.0, 5.0, 4.2, 8.5),    # дубликат объекта 1 → FP
        (6.8, 1.2, 8.6, 3.0),    # выдумка на пустом месте → FP
    ]
    scores = [0.95, 0.88, 0.72, 0.60]
    thr = 0.5
    flags, n_fn = match_detections(preds, scores, gts, thr)
    order = np.argsort(scores)[::-1]

    # причина вердикта — иначе строка «IoU 0.77 → FP» читается как ошибка
    reasons, taken = [], set()
    for i in order:
        best_j, best_v = -1, 0.0
        for j, g in enumerate(gts):
            v = iou(preds[i], g)
            if v > best_v:
                best_v, best_j = v, j
        if best_v < thr:
            reasons.append("IoU ниже порога")
        elif best_j in taken:
            reasons.append("объект уже занят")
        else:
            taken.add(best_j)
            reasons.append("первое попадание")

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8),
                             gridspec_kw={"width_ratios": [1, 1.45]})

    ax = axes[0]
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor=C_PANEL, edgecolor="none"))
    for g in gts:
        _box(ax, g, C_INK, lw=2.6)
    for rank, i in enumerate(order):
        color = C_GREEN if flags[rank] else C_ORANGE
        _box(ax, preds[i], color, lw=2.2, ls="--")
        ax.text(preds[i][0] + 0.12, preds[i][3] - 0.55, f"#{rank + 1}",
                color=color, fontsize=11, fontweight="bold")
    missed = gts[2]
    ax.text(missed[0], missed[1] - 0.6, "FN — объект не найден", color=C_BLUE, fontsize=9.5)
    _box(ax, missed, C_BLUE, lw=2.6)
    ax.set_title(f"Сцена: 3 объекта, 4 предсказания (IoU ≥ {thr})", pad=10)
    _clean(ax)

    ax = axes[1]
    rows = []
    for rank, i in enumerate(order):
        best = max(iou(preds[i], g) for g in gts)
        rows.append((f"#{rank + 1}", f"{scores[i]:.2f}", f"{best:.2f}",
                     "TP" if flags[rank] else "FP", reasons[rank]))
    tp = int(flags.sum())
    fp = int((1 - flags).sum())
    precision = tp / (tp + fp)
    recall = tp / len(gts)

    # фиксированные пределы: иначе автомасштаб по тексту раздувает фигуру
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    T = ax.transAxes
    y = 0.94
    ax.text(0.02, y, "", fontsize=10.5, color=C_GRAY, transform=T)
    ax.text(0.10, y, "увер.", fontsize=10.5, color=C_GRAY, transform=T)
    ax.text(0.29, y, "IoU", fontsize=10.5, color=C_GRAY, transform=T)
    ax.text(0.44, y, "итог", fontsize=10.5, color=C_GRAY, transform=T)
    ax.text(0.62, y, "почему", fontsize=10.5, color=C_GRAY, transform=T)
    for tag, sc_, v, verdict, why in rows:
        y -= 0.115
        color = C_GREEN if verdict == "TP" else C_ORANGE
        ax.text(0.02, y, tag, fontsize=11, color=color, fontweight="bold", transform=T)
        ax.text(0.10, y, sc_, fontsize=11.5, transform=T)
        ax.text(0.29, y, v, fontsize=11.5, transform=T)
        ax.text(0.44, y, verdict, fontsize=11.5, color=color,
                fontweight="bold", transform=T)
        ax.text(0.62, y, why, fontsize=10, color=C_GRAY, transform=T)
    y -= 0.10
    ax.plot([0.02, 0.95], [y, y], color=C_GRAY, lw=1.0, transform=T)
    y -= 0.11
    ax.text(0.02, y, f"TP = {tp}      FP = {fp}      FN = {n_fn}",
            fontsize=12, transform=T)
    y -= 0.12
    ax.text(0.02, y, f"precision = {tp}/{tp + fp} = {precision:.2f}",
            fontsize=12, color=C_INK, transform=T)
    y -= 0.10
    ax.text(0.02, y, f"recall = {tp}/{len(gts)} = {recall:.2f}",
            fontsize=12, color=C_INK, transform=T)
    y -= 0.13
    ax.text(0.02, y, "TN не существует: «фон» не перечислим",
            fontsize=10.5, color=C_GRAY, transform=T)
    ax.set_title("Сопоставление идёт по убыванию уверенности", pad=10)

    fig.suptitle("Дубликат — это FP: истинный бокс можно занять только один раз",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "matching_tp_fp.png")


# ==========================================================================
# Синтетический набор детекций для кривых
# ==========================================================================
def _synthetic_detections(seed=11, n_images=60):
    """Правдоподобный детектор: уверенность коррелирует с качеством бокса."""
    rng = np.random.default_rng(seed)
    all_preds, all_scores, all_gts = [], [], []
    for _ in range(n_images):
        n_obj = rng.integers(1, 4)
        gts = []
        for _ in range(n_obj):
            x, y = rng.uniform(0.5, 5.5), rng.uniform(0.5, 5.5)
            w, h = rng.uniform(1.8, 3.2), rng.uniform(1.8, 3.2)
            gts.append((x, y, x + w, y + h))
        preds, scores = [], []
        for g in gts:
            if rng.random() < 0.82:                       # объект найден
                q = rng.beta(5, 2)                        # качество локализации
                shift = (1 - q) * 1.5
                dx, dy = rng.normal(0, shift, 2)
                ds = rng.normal(0, shift * 0.5, 2)
                preds.append((g[0] + dx, g[1] + dy,
                              g[2] + dx + ds[0], g[3] + dy + ds[1]))
                scores.append(float(np.clip(q * 0.85 + rng.normal(0, 0.08), 0.02, 0.99)))
        for _ in range(rng.poisson(0.8)):                 # ложные срабатывания
            x, y = rng.uniform(0.5, 6.0), rng.uniform(0.5, 6.0)
            w, h = rng.uniform(1.5, 3.0), rng.uniform(1.5, 3.0)
            preds.append((x, y, x + w, y + h))
            scores.append(float(np.clip(rng.beta(1.6, 4.0), 0.02, 0.99)))
        all_preds.append(preds)
        all_scores.append(scores)
        all_gts.append(gts)
    return all_preds, all_scores, all_gts


def _dataset_pr(thr, data):
    """PR-кривая по всему набору: сопоставление внутри изображений, ранжирование — глобальное."""
    all_preds, all_scores, all_gts = data
    flags, scores = [], []
    n_gt = 0
    for preds, sc, gts in zip(all_preds, all_scores, all_gts):
        n_gt += len(gts)
        if not preds:
            continue
        f, _ = match_detections(preds, sc, gts, thr)
        order = np.argsort(sc)[::-1]
        flags.extend(f.tolist())
        scores.extend([sc[i] for i in order])
    scores = np.array(scores)
    flags = np.array(flags)
    g = np.argsort(scores)[::-1]           # общий рейтинг по всем изображениям
    return pr_curve(flags[g], n_gt)


# --------------------------------------------------------------------------
# 3. PR-кривая и AP как площадь под огибающей
# --------------------------------------------------------------------------
def draw_pr_curve():
    data = _synthetic_detections()
    precision, recall = _dataset_pr(0.5, data)
    ap, mrec, mpre = ap_all_point(precision, recall)

    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    ax.step(mrec, mpre, where="pre", color=C_ORANGE, lw=2.4,
            label=f"монотонная огибающая · AP = {ap:.3f}")
    ax.fill_between(mrec, mpre, step="pre", color=C_ORANGE, alpha=0.13)
    ax.plot(recall, precision, color=C_GRAY, lw=1.4, alpha=0.95,
            label="сырая PR-кривая (пилообразная)")
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower left", fontsize=10)
    ax.set_title("AP при IoU = 0.5 — площадь под огибающей PR-кривой", pad=12)
    _despine(ax)
    fig.tight_layout()
    _save(fig, "pr_curve_ap.png")


# --------------------------------------------------------------------------
# 4. Три способа посчитать AP по одной и той же кривой
# --------------------------------------------------------------------------
def draw_interpolation_variants():
    data = _synthetic_detections()
    precision, recall = _dataset_pr(0.5, data)

    ap_all, mrec, mpre = ap_all_point(precision, recall)
    pts11 = np.linspace(0, 1, 11)
    ap11, env11 = ap_interp(precision, recall, pts11)
    pts101 = np.linspace(0, 1, 101)
    ap101, env101 = ap_interp(precision, recall, pts101)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    ax.step(mrec, mpre, where="pre", color=C_GRAY, lw=1.8, label="огибающая")
    ax.plot(pts11, env11, "o", color=C_ORANGE, ms=7,
            label=f"11 точек (VOC2007) · AP = {ap11:.3f}")
    ax.vlines(pts11, 0, env11, color=C_ORANGE, lw=1.0, alpha=0.55)
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower left", fontsize=9.5)
    ax.set_title("Грубая сетка завышает или занижает", pad=10)
    _despine(ax)

    ax = axes[1]
    ax.step(mrec, mpre, where="pre", color=C_GREEN, lw=3.4, alpha=0.5,
            label=f"все точки (VOC2010+) · AP = {ap_all:.3f}")
    ax.plot(pts101, env101, "-", color=C_BLUE, lw=1.8,
            label=f"101 точка (COCO) · AP = {ap101:.3f}")
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower left", fontsize=9.5)
    ax.set_title(f"Плотная сетка сходится к точной площади\n"
                 f"расхождение всего {abs(ap_all - ap101):.3f}", pad=10, fontsize=11)
    _despine(ax)

    fig.suptitle("Одна кривая — три числа: «AP» без указания протокола бессмысленно",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "interpolation_variants.png")


# --------------------------------------------------------------------------
# 5. mAP@[.5:.95]: усреднение по порогам IoU
# --------------------------------------------------------------------------
def draw_iou_sweep():
    data = _synthetic_detections()
    thrs = np.arange(0.5, 0.96, 0.05)
    aps = []
    for t in thrs:
        p, r = _dataset_pr(float(t), data)
        aps.append(ap_interp(p, r, np.linspace(0, 1, 101))[0])
    aps = np.array(aps)
    coco = float(aps.mean())

    fig, ax = plt.subplots(figsize=(8.2, 4.5))
    ax.bar([f"{t:.2f}" for t in thrs], aps, color=C_PANEL, edgecolor=C_GRAY, width=0.62)
    ax.axhline(coco, color=C_ORANGE, lw=2.4)
    ax.text(len(thrs) - 0.4, coco + 0.02,
            f"mAP@[.50:.95] = {coco:.3f}", color=C_ORANGE, fontsize=11, ha="right")
    ax.plot(0, aps[0], "o", color=C_BLUE, ms=9)
    ax.text(0.25, aps[0] + 0.02, f"AP@0.50 = {aps[0]:.3f}", color=C_BLUE, fontsize=11)
    for i, v in enumerate(aps):
        ax.text(i, v + 0.008, f"{v:.2f}", ha="center", fontsize=8.5, color=C_GRAY)
    ax.set_xlabel("порог IoU")
    ax.set_ylabel("AP")
    ax.set_ylim(0, max(aps) * 1.25)
    ax.set_title("COCO усредняет AP по десяти порогам IoU", pad=12)
    _despine(ax)
    fig.tight_layout()
    _save(fig, "iou_sweep_map.png")
    return aps[0], coco


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print(f"Generating visuals in {ASSETS}")
    draw_iou_geometry()
    draw_matching()
    draw_pr_curve()
    draw_interpolation_variants()
    ap50, coco = draw_iou_sweep()
    print(f"\nсводка для текста лекции: AP@0.50 = {ap50:.3f}, mAP@[.50:.95] = {coco:.3f}")


if __name__ == "__main__":
    main()
