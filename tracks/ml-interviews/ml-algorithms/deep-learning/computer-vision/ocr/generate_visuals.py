"""Точные схемы для темы «OCR: детекция и распознавание текста».

Все числа на картинках — результат прогона, а не подобранные вручную значения:
вероятность строки по CTC считается forward-алгоритмом и сверяется с полным
перебором путей, редакционное расстояние — настоящей динамикой Левенштейна,
прямоугольники вокруг изогнутого текста — честной минимизацией площади.
"""

import itertools
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

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


def _clean(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def _despine(ax, keep=("left", "bottom")):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)


# ==========================================================================
# Ядро 1: CTC — свёртка пути, forward-алгоритм, полный перебор для сверки
# ==========================================================================
BLANK = 0


def collapse(path):
    """Правило свёртки CTC: схлопнуть повторы, затем убрать blank."""
    out = []
    prev = None
    for s in path:
        if s != prev and s != BLANK:
            out.append(s)
        prev = s
    return tuple(out)


def ctc_forward(probs, target):
    """P(target | probs) суммой по всем путям — стандартная alpha-рекурсия.

    probs: (T, V), строки — распределения по алфавиту (индекс 0 — blank).
    """
    ext = [BLANK]
    for s in target:
        ext += [s, BLANK]
    L = len(ext)
    alpha = np.zeros(L)
    alpha[0] = probs[0][BLANK]
    if L > 1:
        alpha[1] = probs[0][ext[1]]
    for t in range(1, len(probs)):
        prev = alpha.copy()
        for i in range(L):
            a = prev[i]
            if i >= 1:
                a += prev[i - 1]
            if i >= 2 and ext[i] != BLANK and ext[i] != ext[i - 2]:
                a += prev[i - 2]
            alpha[i] = a * probs[t][ext[i]]
    return alpha[-1] + (alpha[-2] if L > 1 else 0.0)


def ctc_brute_force(probs, target):
    """Сумма по всем путям полным перебором + список путей с вероятностями."""
    T, V = probs.shape
    total, paths = 0.0, []
    for path in itertools.product(range(V), repeat=T):
        if collapse(path) == tuple(target):
            p = float(np.prod([probs[t][s] for t, s in enumerate(path)]))
            total += p
            paths.append((path, p))
    paths.sort(key=lambda x: -x[1])
    return total, paths


# ==========================================================================
# Ядро 2: расстояние Левенштейна с матрицей и обратным ходом
# ==========================================================================
def levenshtein_matrix(ref, hyp):
    n, m = len(ref), len(hyp)
    D = np.zeros((n + 1, m + 1), dtype=int)
    D[:, 0] = np.arange(n + 1)
    D[0, :] = np.arange(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            D[i, j] = min(D[i - 1, j] + 1, D[i, j - 1] + 1, D[i - 1, j - 1] + cost)
    # обратный ход — путь оптимального выравнивания
    path = [(n, m)]
    i, j = n, m
    while i > 0 or j > 0:
        cands = []
        if i > 0 and j > 0:
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            cands.append((D[i - 1, j - 1] + cost, i - 1, j - 1))
        if i > 0:
            cands.append((D[i - 1, j] + 1, i - 1, j))
        if j > 0:
            cands.append((D[i, j - 1] + 1, i, j - 1))
        best = min(cands, key=lambda c: c[0])
        _, i, j = best
        path.append((i, j))
    return D, path[::-1]


def cer(ref, hyp):
    D, _ = levenshtein_matrix(ref, hyp)
    return D[-1, -1] / len(ref)


def wer(ref, hyp):
    D, _ = levenshtein_matrix(ref.split(), hyp.split())
    return D[-1, -1] / len(ref.split())


# ==========================================================================
# Ядро 3: минимальный по площади повёрнутый прямоугольник (перебор углов)
# ==========================================================================
def min_area_rect(points, step_deg=0.25):
    best = None
    for ang in np.arange(0.0, 90.0, step_deg):
        th = np.deg2rad(ang)
        R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
        rot = points @ R.T
        lo, hi = rot.min(axis=0), rot.max(axis=0)
        area = float(np.prod(hi - lo))
        if best is None or area < best[0]:
            corners = np.array(
                [[lo[0], lo[1]], [hi[0], lo[1]], [hi[0], hi[1]], [lo[0], hi[1]]]
            ) @ R
            best = (area, corners)
    return best


def shoelace(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(np.roll(x, -1), y))


def curved_band(n=80, thickness=0.72):
    """Полигон изогнутой текстовой строки: полоса вдоль дуги."""
    t = np.linspace(0.6, 9.4, n)
    cx, cy = t, 3.2 + 1.35 * np.sin((t - 0.6) * 0.42)
    dx = np.gradient(cx)
    dy = np.gradient(cy)
    nx, ny = -dy, dx
    norm = np.hypot(nx, ny)
    nx, ny = nx / norm, ny / norm
    top = np.column_stack([cx + nx * thickness / 2, cy + ny * thickness / 2])
    bot = np.column_stack([cx - nx * thickness / 2, cy - ny * thickness / 2])
    return np.vstack([top, bot[::-1]])


# ==========================================================================
# Диаграммы
# ==========================================================================
def _text_lines(ax, x, y, w, n, color=C_GRAY, lw=2.4, seed=3):
    """Абстрактные «строки текста» — штрихи разной длины."""
    rng = np.random.default_rng(seed)
    for k in range(n):
        frac = rng.uniform(0.55, 1.0)
        ax.plot([x, x + w * frac], [y - 0.34 * k] * 2, color=color, lw=lw,
                solid_capstyle="round")


def draw_pipeline():
    """Двухэтапный пайплайн OCR: детекция -> выпрямление -> распознавание."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(11.5, 4.2))
    _clean(ax, (0, 23), (0, 8))

    def panel(x, w, title):
        ax.add_patch(Rectangle((x, 1.6), w, 4.6, facecolor="white",
                               edgecolor=C_GRAY, lw=1.2))
        ax.text(x + w / 2, 6.7, title, ha="center", fontsize=11, color=C_INK)

    def arrow(x0, x1, label):
        ax.add_patch(FancyArrowPatch((x0, 3.9), (x1, 3.9), arrowstyle="-|>",
                                     mutation_scale=16, color=C_INK, lw=1.4))
        ax.text((x0 + x1) / 2, 4.35, label, ha="center", fontsize=8.5,
                color=C_INK)

    # 1. вход: сцена со строками под наклоном
    panel(0.5, 4.6, "вход")
    for (px, py, pw, ang) in [(1.3, 5.3, 2.6, -8), (1.6, 3.4, 2.4, 5)]:
        tr = matplotlib.transforms.Affine2D().rotate_deg_around(px, py, ang) + ax.transData
        for k in range(2):
            ax.plot([px, px + pw], [py - 0.4 * k] * 2, color=C_GRAY, lw=2.6,
                    solid_capstyle="round", transform=tr)

    arrow(5.3, 6.7, "детекция")

    # 2. детекция: те же строки + рамки
    panel(7.0, 4.6, "полигоны строк")
    for (px, py, pw, ang) in [(7.8, 5.3, 2.6, -8), (8.1, 3.4, 2.4, 5)]:
        tr = matplotlib.transforms.Affine2D().rotate_deg_around(px, py, ang) + ax.transData
        for k in range(2):
            ax.plot([px, px + pw], [py - 0.4 * k] * 2, color=C_GRAY, lw=2.6,
                    solid_capstyle="round", transform=tr)
        ax.add_patch(Rectangle((px - 0.25, py - 0.75), pw + 0.5, 1.15, fill=False,
                               edgecolor=C_ORANGE, lw=1.8, transform=tr))

    arrow(11.8, 13.2, "выпрямление")

    # 3. rectification: горизонтальные вырезанные полосы
    panel(13.5, 4.6, "выпрямленные вырезки")
    for py in (5.0, 3.0):
        ax.add_patch(Rectangle((14.2, py - 0.65), 3.2, 1.0, facecolor=C_PANEL,
                               edgecolor=C_ORANGE, lw=1.4))
        ax.plot([14.5, 17.1], [py - 0.15] * 2, color=C_INK, lw=2.6,
                solid_capstyle="round")

    arrow(18.3, 19.7, "распознавание")

    # 4. выход: последовательности символов (абстрактные квадратики)
    panel(20.0, 2.6, "строки")
    for py in (5.0, 3.0):
        for k in range(5):
            ax.add_patch(Rectangle((20.4 + 0.42 * k, py - 0.4), 0.32, 0.5,
                                   facecolor=C_BLUE if k % 2 else C_GREEN,
                                   edgecolor="none"))

    ax.set_title("Двухэтапный пайплайн OCR: найти текст → выпрямить → прочитать",
                 fontsize=13, pad=12)
    _save(fig, "ocr_pipeline.png")


def draw_text_geometry():
    """Изогнутая строка и три способа её описать; заполненность — по площадям."""
    _apply_style()
    band = curved_band()
    area_band = shoelace(band)

    # axis-aligned bbox
    lo, hi = band.min(axis=0), band.max(axis=0)
    area_aabb = float(np.prod(hi - lo))
    # min-area rotated rect
    area_rot, corners_rot = min_area_rect(band)

    fill_aabb = area_band / area_aabb
    fill_rot = area_band / area_rot

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.6))
    titles = [
        f"осевой бокс\nзаполненность {fill_aabb:.0%}",
        f"повёрнутый бокс\nзаполненность {fill_rot:.0%}",
        "полигон\nзаполненность 100%",
    ]
    for ax, title in zip(axes, titles):
        _clean(ax, (-0.3, 10.3), (0.6, 6.6))
        ax.add_patch(Polygon(band, closed=True, facecolor=C_PANEL,
                             edgecolor=C_GRAY, lw=1.0))
        ax.set_title(title, fontsize=11)
    axes[0].add_patch(Rectangle(lo, *(hi - lo), fill=False, edgecolor=C_ORANGE, lw=2.0))
    axes[1].add_patch(Polygon(corners_rot, closed=True, fill=False,
                              edgecolor=C_ORANGE, lw=2.0))
    axes[2].add_patch(Polygon(band, closed=True, fill=False, edgecolor=C_ORANGE, lw=2.0))
    fig.suptitle("Изогнутая строка: чем точнее представление, тем меньше фона в рамке",
                 fontsize=13, y=1.06)
    _save(fig, "text_geometry.png")
    return fill_aabb, fill_rot


def make_ctc_table():
    """Токовый пример: T=6, алфавит {–, c, a, t}, целевая строка «cat»."""
    P = np.array(
        [
            #  –     c     a     t
            [0.10, 0.70, 0.10, 0.10],
            [0.15, 0.40, 0.35, 0.10],
            [0.20, 0.10, 0.60, 0.10],
            [0.35, 0.10, 0.35, 0.20],
            [0.25, 0.05, 0.05, 0.65],
            [0.60, 0.05, 0.05, 0.30],
        ]
    )
    assert np.allclose(P.sum(axis=1), 1.0)
    return P


def draw_ctc_alignment():
    """Решётка CTC: пути, свёртка, вероятность строки суммой по путям."""
    _apply_style()
    P = make_ctc_table()
    symbols = ["–", "c", "a", "t"]
    target = (1, 2, 3)  # "cat"

    p_forward = ctc_forward(P, target)
    p_brute, paths = ctc_brute_force(P, target)
    assert abs(p_forward - p_brute) < 1e-12, (p_forward, p_brute)
    n_paths = len(paths)

    greedy = tuple(int(i) for i in P.argmax(axis=1))
    greedy_str = "".join(symbols[s] for s in greedy)
    p_best_path = paths[0][1]
    best_path_str = "".join(symbols[s] for s in paths[0][0])

    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(12.5, 4.4), gridspec_kw={"width_ratios": [1.15, 1]}
    )

    # --- слева: тепловая карта P с жадным путём
    im = axL.imshow(P.T, cmap="Greys", vmin=0, vmax=1, aspect="auto")
    axL.set_xticks(range(6), [f"t={t+1}" for t in range(6)])
    axL.set_yticks(range(4), symbols)
    for t in range(6):
        for s in range(4):
            axL.text(t, s, f"{P[t, s]:.2f}", ha="center", va="center",
                     fontsize=9, color="white" if P[t, s] > 0.5 else C_INK)
    for t, s in enumerate(greedy):
        axL.add_patch(Rectangle((t - 0.5, s - 0.5), 1, 1, fill=False,
                                edgecolor=C_ORANGE, lw=2.4))
    axL.set_title(f"выход сети $P(s\\,|\\,t)$; жадный путь «{greedy_str}» → «cat»")
    _despine(axL, keep=())
    im.set_clim(0, 1.15)

    # --- справа: топ путей, сворачивающихся в «cat»
    top = paths[:8]
    labels = ["".join(symbols[s] for s in p) for p, _ in top]
    vals = [p for _, p in top]
    y = np.arange(len(top))[::-1]
    axR.barh(y, vals, color=[C_ORANGE if i == 0 else C_BLUE for i in range(len(top))],
             height=0.62)
    axR.set_yticks(y, [f"«{s}»" for s in labels], fontsize=9.5)
    for yi, v in zip(y, vals):
        axR.text(v + 0.0006, yi, f"{v:.4f}", va="center", fontsize=8.5)
    axR.set_xlabel("вероятность пути")
    axR.set_title(
        f"пути → «cat»: всего {n_paths}, сумма P(«cat») = {p_brute:.3f}",
        fontsize=11,
    )
    _despine(axR)
    fig.suptitle(
        "CTC: вероятность строки — сумма по всем путям, которые в неё сворачиваются",
        fontsize=13, y=1.03,
    )
    fig.tight_layout()
    _save(fig, "ctc_alignment.png")
    return p_brute, n_paths, p_best_path, best_path_str, greedy_str


def draw_ctc_decoding():
    """Пример, где жадное декодирование выбирает не самую вероятную строку."""
    _apply_style()
    P = np.array([[0.6, 0.4], [0.6, 0.4]])  # алфавит {–, a}, T=2
    symbols = ["–", "a"]

    rows = []
    for path in itertools.product(range(2), repeat=2):
        p = float(P[0, path[0]] * P[1, path[1]])
        lab = "".join(symbols[s] for s in collapse(path)) or "∅"
        rows.append(("".join(symbols[s] for s in path), lab, p))

    p_empty = sum(p for _, lab, p in rows if lab == "∅")
    p_a = sum(p for _, lab, p in rows if lab == "a")
    greedy_path = "".join(symbols[int(i)] for i in P.argmax(axis=1))

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.5, 3.8))

    x = np.arange(len(rows))
    colors = [C_GRAY if lab == "∅" else C_BLUE for _, lab, _ in rows]
    axL.bar(x, [p for *_, p in rows], color=colors, width=0.6)
    axL.set_xticks(x, [f"«{pth}»\n→ {lab}" for pth, lab, _ in rows], fontsize=9.5)
    for xi, (_, _, p) in zip(x, rows):
        axL.text(xi, p + 0.008, f"{p:.2f}", ha="center", fontsize=9)
    axL.set_title(f"четыре пути; жадный выбирает «{greedy_path}» → ∅")
    axL.set_ylabel("вероятность пути")
    _despine(axL)

    axR.bar([0, 1], [p_empty, p_a], color=[C_GRAY, C_ORANGE], width=0.45)
    axR.set_xticks([0, 1], ["∅ (пустая строка)", "«a»"])
    for xi, v in [(0, p_empty), (1, p_a)]:
        axR.text(xi, v + 0.01, f"{v:.2f}", ha="center", fontsize=10)
    axR.set_title("после суммирования по путям выигрывает «a»")
    axR.set_ylabel("вероятность строки")
    _despine(axR)

    fig.suptitle(
        "Жадное декодирование берёт лучший путь, а не лучшую строку",
        fontsize=13, y=1.04,
    )
    fig.tight_layout()
    _save(fig, "ctc_decoding.png")
    return p_empty, p_a


def draw_cer_wer():
    """Матрица Левенштейна и контраст CER против WER на одной паре строк."""
    _apply_style()
    ref = "модель читает текст"
    hyp = "модел чнтает тексt"

    D, path = levenshtein_matrix(ref, hyp)
    dist = int(D[-1, -1])
    cer_v = cer(ref, hyp)
    wer_v = wer(ref, hyp)

    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(12.5, 4.8), gridspec_kw={"width_ratios": [1.55, 1]}
    )

    axL.imshow(D, cmap="Greys", vmin=0, vmax=D.max() * 1.35)
    axL.set_xticks(range(len(hyp) + 1), ["·"] + list(hyp), fontsize=9)
    axL.set_yticks(range(len(ref) + 1), ["·"] + list(ref), fontsize=9)
    on_path = set(path)
    dark = D.max() * 1.35 * 0.5
    for i in range(D.shape[0]):
        for j in range(D.shape[1]):
            hit = (i, j) in on_path
            axL.text(j, i, D[i, j], ha="center", va="center", fontsize=7,
                     color=C_ORANGE if hit else ("white" if D[i, j] > dark else C_INK),
                     fontweight="bold" if hit else "normal")
    axL.set_title(f"матрица Левенштейна: расстояние = {dist}", fontsize=11)
    _despine(axL, keep=())

    axR.bar([0, 1], [cer_v, wer_v], color=[C_BLUE, C_ORANGE], width=0.45)
    axR.set_xticks([0, 1], ["CER", "WER"])
    for xi, v in [(0, cer_v), (1, wer_v)]:
        axR.text(xi, v + 0.02, f"{v:.2f}", ha="center", fontsize=11)
    axR.set_ylim(0, 1.15)
    axR.set_title("те же три ошибки, две разные метрики", fontsize=11)
    _despine(axR)

    fig.suptitle(
        f"«{ref}» → «{hyp}»: три посимвольные ошибки портят все три слова",
        fontsize=13, y=1.03,
    )
    fig.tight_layout()
    _save(fig, "cer_wer.png")
    return dist, cer_v, wer_v


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем OCR:")
    draw_pipeline()
    fill_aabb, fill_rot = draw_text_geometry()
    p_cat, n_paths, p_best, best_path, greedy_str = draw_ctc_alignment()
    p_empty, p_a = draw_ctc_decoding()
    dist, cer_v, wer_v = draw_cer_wer()

    print("\nЧисла для текста лекции:")
    print(f"  заполненность осевого бокса      : {fill_aabb:.3f}")
    print(f"  заполненность повёрнутого бокса  : {fill_rot:.3f}")
    print(f"  P('cat') по CTC                  : {p_cat:.4f}")
    print(f"  число путей, дающих 'cat'        : {n_paths}")
    print(f"  лучший путь                      : «{best_path}» с p={p_best:.4f}")
    print(f"  жадный путь                      : «{greedy_str}»")
    print(f"  жадный пример: P(∅)={p_empty:.2f}, P('a')={p_a:.2f}")
    print(f"  Левенштейн={dist}, CER={cer_v:.3f}, WER={wer_v:.3f}")


if __name__ == "__main__":
    main()
