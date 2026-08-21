"""Точные схемы для темы «Архитектуры сегментации».

Потеря разрешения при понижении масштаба, рост рецептивного поля от дилатации
и ошибка квантования RoI pooling считаются здесь на реальных сетках и массивах.
Схематична только одна картинка — устройство U-Net, и числовых утверждений
в ней нет.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

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


def mask_iou(a, b):
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return float(inter / union) if union else 1.0


# --------------------------------------------------------------------------
# Синтетическая сцена: круг, вытянутый прямоугольник и тонкий «столб»
# --------------------------------------------------------------------------
def _scene(n=256):
    yy, xx = np.mgrid[0:n, 0:n]
    sky = np.zeros((n, n), dtype=int)                       # 0 — фон
    ground = yy > n * 0.72
    circle1 = (xx - n * 0.30) ** 2 + (yy - n * 0.52) ** 2 < (n * 0.15) ** 2
    circle2 = (xx - n * 0.56) ** 2 + (yy - n * 0.55) ** 2 < (n * 0.13) ** 2
    pole = (np.abs(xx - n * 0.82) < n * 0.012) & (yy > n * 0.22) & (yy < n * 0.80)
    sem = sky.copy()
    sem[ground] = 1                                          # 1 — «дорога»
    sem[circle1 | circle2] = 2                               # 2 — «объект»
    sem[pole] = 3                                            # 3 — «столб»
    inst = np.zeros((n, n), dtype=int)
    inst[circle1] = 1
    inst[circle2] = 2
    return sem, inst, {"circle1": circle1, "circle2": circle2,
                       "pole": pole, "ground": ground}


# --------------------------------------------------------------------------
# 1. Три вида сегментации на одной сцене
# --------------------------------------------------------------------------
def draw_task_flavours():
    sem, _, parts = _scene()

    cmap_sem = ListedColormap([C_PANEL, "#cfd6c4", C_BLUE, C_ORANGE])
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.3))

    ax = axes[0]
    ax.imshow(sem, cmap=cmap_sem, interpolation="nearest")
    ax.set_title("Семантическая\nкласс у каждого пикселя", pad=10, fontsize=11)
    ax.text(0.5, -0.09, "два круга — один класс «объект»", transform=ax.transAxes,
            ha="center", color=C_GRAY, fontsize=9.5)
    _bare(ax)

    ax = axes[1]
    inst_show = np.zeros_like(sem)
    inst_show[parts["circle1"]] = 1
    inst_show[parts["circle2"]] = 2
    ax.imshow(inst_show, cmap=ListedColormap([C_PANEL, C_BLUE, C_ORANGE]),
              interpolation="nearest")
    ax.set_title("Инстансная\nобъекты различимы", pad=10, fontsize=11)
    ax.text(0.5, -0.09, "фон и «дорога» не размечаются вовсе",
            transform=ax.transAxes, ha="center", color=C_GRAY, fontsize=9.5)
    _bare(ax)

    ax = axes[2]
    pan = np.zeros_like(sem)
    pan[parts["ground"]] = 1
    pan[parts["pole"]] = 2
    pan[parts["circle1"]] = 3
    pan[parts["circle2"]] = 4
    ax.imshow(pan, cmap=ListedColormap([C_PANEL, "#cfd6c4", C_GREEN, C_BLUE, C_ORANGE]),
              interpolation="nearest")
    ax.set_title("Паноптическая\nвсё сразу, без пересечений", pad=10, fontsize=11)
    ax.text(0.5, -0.09, "«вещи» — по экземплярам, «материал» — сплошняком",
            transform=ax.transAxes, ha="center", color=C_GRAY, fontsize=9.5)
    _bare(ax)

    fig.suptitle("Одна сцена — три разные постановки задачи", fontsize=13, y=1.0)
    fig.tight_layout()
    _save(fig, "task_flavours.png")


# --------------------------------------------------------------------------
# 2. Главный конфликт: разрешение против семантики
# --------------------------------------------------------------------------
def _downup(mask, stride):
    """Понизить разрешение в stride раз усреднением и вернуть обратно."""
    n = mask.shape[0]
    small = mask.reshape(n // stride, stride, n // stride, stride).mean(axis=(1, 3))
    up = np.repeat(np.repeat(small, stride, axis=0), stride, axis=1)
    return small, up >= 0.5


def draw_resolution_loss():
    _, _, parts = _scene()
    target = parts["circle1"] | parts["circle2"] | parts["pole"]

    strides = [4, 8, 16, 32]
    results = [(s, *_downup(target, s)) for s in strides]

    fig, axes = plt.subplots(1, 5, figsize=(15, 3.6))
    ax = axes[0]
    ax.imshow(target, cmap=ListedColormap([C_PANEL, C_INK]), interpolation="nearest")
    ax.set_title("исходная разметка\n256×256", pad=8, fontsize=10.5)
    _bare(ax)

    for ax, (s, small, up) in zip(axes[1:], results):
        v = mask_iou(target, up)
        ax.imshow(up, cmap=ListedColormap([C_PANEL, C_ORANGE if s >= 16 else C_INK]),
                  interpolation="nearest")
        ax.set_title(f"stride {s} → {small.shape[0]}×{small.shape[0]}\nIoU = {v:.2f}",
                     pad=8, fontsize=10.5)
        _bare(ax)

    lost = [f"stride {s}: IoU {mask_iou(target, up):.2f}" for s, _, up in results]
    fig.text(0.5, -0.04,
             "тонкий столб исчезает первым:  " + "   ·   ".join(lost),
             ha="center", fontsize=9.5, color=C_GRAY)
    fig.suptitle("Понижение разрешения стирает тонкие структуры — "
                 "и это происходит внутри любого CNN-бэкбона",
                 fontsize=13, y=1.03)
    fig.tight_layout()
    _save(fig, "resolution_loss.png")
    return {s: mask_iou(target, up) for s, _, up in results}


# --------------------------------------------------------------------------
# 3. Дилатация: рецептивное поле без потери разрешения
# --------------------------------------------------------------------------
def _receptive_field(dilations, ksize=3):
    """Размер рецептивного поля стопки свёрток с заданными дилатациями (stride 1)."""
    rf = 1
    for d in dilations:
        rf += (ksize - 1) * d
    return rf


def _rf_footprint(dilations, ksize=3, size=41):
    """Какие пиксели входа реально влияют на центральный выход."""
    grid = np.zeros((size, size))
    grid[size // 2, size // 2] = 1
    for d in reversed(dilations):
        new = np.zeros_like(grid)
        offs = [(i - ksize // 2) * d for i in range(ksize)]
        for dy in offs:
            for dx in offs:
                new += np.roll(np.roll(grid, dy, axis=0), dx, axis=1)
        grid = new
    return grid > 0


def draw_dilation():
    plain = [1, 1, 1]
    dilated = [1, 2, 4]
    fp_plain = _rf_footprint(plain)
    fp_dil = _rf_footprint(dilated)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2),
                             gridspec_kw={"width_ratios": [1, 1, 1.25]})

    for ax, fp, dil, color in ((axes[0], fp_plain, plain, C_BLUE),
                               (axes[1], fp_dil, dilated, C_ORANGE)):
        ax.imshow(fp, cmap=ListedColormap([C_PANEL, color]), interpolation="nearest")
        rf = _receptive_field(dil)
        ax.set_title(f"дилатации {dil}\nрецептивное поле {rf}×{rf}", pad=10, fontsize=11)
        ax.plot(fp.shape[0] // 2, fp.shape[0] // 2, "s", color=C_INK, ms=4)
        _bare(ax)

    ax = axes[2]
    depths = np.arange(1, 9)
    rf_plain = [_receptive_field([1] * k) for k in depths]
    rf_dil = [_receptive_field([2 ** i for i in range(k)]) for k in depths]
    ax.plot(depths, rf_plain, "o-", color=C_BLUE, lw=2.4, label="обычные свёртки 3×3")
    ax.plot(depths, rf_dil, "o-", color=C_ORANGE, lw=2.4, label="дилатации 1, 2, 4, 8, …")
    ax.set_yscale("log", base=2)
    ax.set_xlabel("число слоёв")
    ax.set_ylabel("сторона рецептивного поля")
    ax.set_title("Экспоненциальный рост вместо линейного", pad=10)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    fig.suptitle("Дилатация расширяет обзор, не понижая разрешения карты",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "dilation.png")
    return rf_plain[-1], rf_dil[-1]


# --------------------------------------------------------------------------
# 4. Устройство U-Net (схема, без числовых утверждений)
# --------------------------------------------------------------------------
def draw_unet():
    fig, ax = plt.subplots(figsize=(11, 5.2))
    levels = 4
    w, h = 1.15, 0.62
    gap_x, gap_y = 2.05, 1.05

    enc, dec = [], []
    for i in range(levels):
        x_e = i * gap_x
        x_d = (2 * levels - 1 - i) * gap_x
        y = -i * gap_y
        enc.append((x_e, y))
        dec.append((x_d, y))

    def block(x, y, color, label, sub):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                    facecolor=C_PANEL, edgecolor=color, lw=2.2))
        ax.text(x + w / 2, y + h / 2 + 0.09, label, ha="center", va="center",
                fontsize=9.5, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 0.13, sub, ha="center", va="center",
                fontsize=8.2, color=C_GRAY)

    for i, (x, y) in enumerate(enc):
        block(x, y, C_BLUE, f"энкодер {i + 1}", f"{256 // 2 ** i}²")
    for i, (x, y) in enumerate(dec):
        block(x, y, C_ORANGE, f"декодер {i + 1}", f"{256 // 2 ** i}²")

    # спуск и подъём
    for i in range(levels - 1):
        ax.add_patch(FancyArrowPatch((enc[i][0] + w / 2, enc[i][1]),
                                     (enc[i + 1][0] + w / 2, enc[i + 1][1] + h),
                                     arrowstyle="-|>", mutation_scale=12,
                                     color=C_BLUE, lw=1.6))
        ax.add_patch(FancyArrowPatch((dec[i + 1][0] + w / 2, dec[i + 1][1] + h),
                                     (dec[i][0] + w / 2, dec[i][1]),
                                     arrowstyle="-|>", mutation_scale=12,
                                     color=C_ORANGE, lw=1.6))

    # skip-соединения — суть архитектуры
    for i in range(levels):
        ax.add_patch(FancyArrowPatch((enc[i][0] + w, enc[i][1] + h / 2),
                                     (dec[i][0], dec[i][1] + h / 2),
                                     arrowstyle="-|>", mutation_scale=12,
                                     color=C_GREEN, lw=2.0, ls="--",
                                     connectionstyle="arc3,rad=-0.12"))
    ax.text(levels * gap_x - 0.35, 0.52, "skip-соединения: возвращают точную\n"
            "геометрию, потерянную при спуске",
            ha="center", fontsize=10, color=C_GREEN)

    ax.text(enc[-1][0] + w / 2, enc[-1][1] - 0.45, "здесь максимум семантики\nи минимум разрешения",
            ha="center", fontsize=9.5, color=C_GRAY)

    ax.set_xlim(-0.5, (2 * levels - 1) * gap_x + w + 0.5)
    ax.set_ylim(-(levels - 1) * gap_y - 0.95, 1.15)
    ax.axis("off")
    fig.suptitle("U-Net: спуск за семантикой, подъём за разрешением, "
                 "skip — чтобы не потерять границы", fontsize=13, y=0.98)
    fig.tight_layout()
    _save(fig, "unet.png")


# --------------------------------------------------------------------------
# 5. RoI pooling против RoIAlign: цена округления
# --------------------------------------------------------------------------
def draw_roi_align():
    # RoI в координатах изображения и шаг карты признаков
    roi = (26.7, 18.3, 91.4, 74.9)
    stride = 16.0
    roi_feat = tuple(v / stride for v in roi)
    # Mask R-CNN описывает квантование RoI pooling как округление [x/stride]
    quant = tuple(float(np.round(v)) for v in roi_feat)

    shift_px = max(abs(quant[i] - roi_feat[i]) for i in range(4)) * stride

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))

    for ax, box, color, title in (
        (axes[0], quant, C_ORANGE, "RoI pooling: координаты округлены"),
        (axes[1], roi_feat, C_GREEN, "RoIAlign: координаты дробные"),
    ):
        ax.add_patch(Rectangle((0, 0), 8, 6, facecolor=C_PANEL, edgecolor="none"))
        for gx in range(9):
            ax.plot([gx, gx], [0, 6], color=C_GRAY, lw=0.8, alpha=0.7)
        for gy in range(7):
            ax.plot([0, 8], [gy, gy], color=C_GRAY, lw=0.8, alpha=0.7)
        ax.add_patch(Rectangle((roi_feat[0], roi_feat[1]),
                               roi_feat[2] - roi_feat[0], roi_feat[3] - roi_feat[1],
                               fill=False, edgecolor=C_INK, lw=2.4, ls="--"))
        ax.add_patch(Rectangle((box[0], box[1]), box[2] - box[0], box[3] - box[1],
                               fill=False, edgecolor=color, lw=3.0))
        # точки билинейной выборки внутри ячеек 2×2
        if color == C_GREEN:
            for i in range(2):
                for j in range(2):
                    cx = box[0] + (box[2] - box[0]) * (i + 0.5) / 2
                    cy = box[1] + (box[3] - box[1]) * (j + 0.5) / 2
                    ax.plot(cx, cy, "o", color=C_GREEN, ms=6)
        ax.set_xlim(0, 8)
        ax.set_ylim(6, 0)
        ax.set_aspect("equal")
        ax.set_title(title, pad=10, fontsize=11)
        _bare(ax)

    axes[0].text(0.5, -0.10,
                 f"сдвиг границы до {shift_px:.1f} пикселя изображения",
                 transform=axes[0].transAxes, ha="center", color=C_ORANGE, fontsize=10)
    axes[1].text(0.5, -0.10, "значения берутся билинейной интерполяцией",
                 transform=axes[1].transAxes, ha="center", color=C_GREEN, fontsize=10)

    fig.suptitle("Округление RoI незаметно для бокса и фатально для маски",
                 fontsize=13, y=1.0)
    fig.tight_layout()
    _save(fig, "roi_align.png")
    return shift_px


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print(f"Generating visuals in {ASSETS}")
    draw_task_flavours()
    ious = draw_resolution_loss()
    rf_plain, rf_dil = draw_dilation()
    draw_unet()
    shift = draw_roi_align()
    print("\nсводка для текста лекции:")
    print("  IoU после down/up:", {k: round(v, 3) for k, v in ious.items()})
    print(f"  рецептивное поле на 8 слоях: обычное {rf_plain}, с дилатацией {rf_dil}")
    print(f"  сдвиг границы RoI при округлении: {shift:.1f} px")


if __name__ == "__main__":
    main()
