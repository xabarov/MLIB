"""Точные схемы для темы «Self-attention и трансформеры».

Все числа на картинках — результат прогона, а не подобранные вручную значения:
дисперсия логитов и энтропия softmax меряются на выборках, перестановочная
эквивариантность проверяется численно, свойство позиционных кодировок
«скалярное произведение зависит только от сдвига» — тоже, поиск по ключу
делается вручную собранной головой без всякого обучения, а коллапс рангов
и стоимость слоя считаются по формулам и прогоном.
"""

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


def _despine(ax, keep=("left", "bottom")):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)


# ==========================================================================
# Внимание в двадцать строк
# ==========================================================================


def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


def attention(X, Wq, Wk, Wv, mask=None, temp=1.0):
    """Одна голова: возвращает выход и матрицу внимания."""
    Q, K, V = X @ Wq, X @ Wk, X @ Wv
    scores = Q @ K.T / (temp * np.sqrt(Q.shape[-1]))
    if mask is not None:
        scores = np.where(mask, scores, -np.inf)
    A = softmax(scores)
    return A @ V, A


def diversity(X):
    """Насколько токены отличаются друг от друга: 0 — все одинаковы."""
    return np.linalg.norm(X - X.mean(0, keepdims=True)) / np.linalg.norm(X)


# ==========================================================================
# 1. Зачем делить на sqrt(d_k)
# ==========================================================================


def run_scaling(dims=(4, 16, 64, 256, 1024), n_keys=16, trials=600, seed=0):
    rng = np.random.default_rng(seed)
    out = {}
    for d in dims:
        q = rng.normal(size=(20_000, d))
        k = rng.normal(size=(20_000, d))
        std = float((q * k).sum(1).std())

        ent, ent_s, jac, jac_s, mx, mx_s = [], [], [], [], [], []
        for _ in range(trials):
            qq = rng.normal(size=d)
            K = rng.normal(size=(n_keys, d))
            for scale, E, J, M in ((1.0, ent, jac, mx),
                                   (1 / np.sqrt(d), ent_s, jac_s, mx_s)):
                p = softmax(K @ qq * scale)
                E.append(-(p * np.log(p + 1e-12)).sum())
                J.append(np.linalg.norm(np.diag(p) - np.outer(p, p)))
                M.append(p.max())
        out[d] = dict(std=std, ent=np.mean(ent), ent_s=np.mean(ent_s),
                      jac=np.mean(jac), jac_s=np.mean(jac_s),
                      mx=np.mean(mx), mx_s=np.mean(mx_s))
    return out, n_keys


def draw_scaling(res, n_keys):
    _apply_style()
    data, _ = res, None
    dims = np.array(list(data))
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13.2, 4.2))

    ax1.plot(dims, [data[d]["std"] for d in dims], color=C_ORANGE, lw=2.4,
             marker="o", ms=6, label="измеренный std логитов $q\\cdot k$")
    ax1.plot(dims, np.sqrt(dims), color=C_INK, lw=1.2, ls="--",
             label="$\\sqrt{d_k}$")
    ax1.set_xscale("log", base=2)
    ax1.set_yscale("log", base=2)
    ax1.set_xlabel("$d_k$")
    ax1.set_ylabel("std логитов")
    ax1.set_title("логиты растут как $\\sqrt{d_k}$", fontsize=11.5)
    ax1.legend(fontsize=9.5)

    ax2.plot(dims, [data[d]["ent"] for d in dims], color=C_ORANGE, lw=2.4,
             marker="o", ms=6, label="без деления на $\\sqrt{d_k}$")
    ax2.plot(dims, [data[d]["ent_s"] for d in dims], color=C_BLUE, lw=2.4,
             marker="s", ms=6, label="с делением")
    ax2.axhline(np.log(n_keys), color=C_GRAY, ls=":", lw=1.3)
    ax2.text(dims[0], np.log(n_keys) - 0.16, f"равномерное внимание: $\\ln$ {n_keys}",
             fontsize=9.5, color=C_GRAY)
    ax2.set_xscale("log", base=2)
    ax2.set_xlabel("$d_k$")
    ax2.set_ylabel("энтропия внимания, нат")
    ax2.set_ylim(0, np.log(n_keys) * 1.08)
    ax2.set_title(f"внимание по {n_keys} ключам", fontsize=11.5)
    ax2.legend(fontsize=9.5, loc="center left")

    ax3.plot(dims, [data[d]["jac"] for d in dims], color=C_ORANGE, lw=2.4,
             marker="o", ms=6, label="без деления")
    ax3.plot(dims, [data[d]["jac_s"] for d in dims], color=C_BLUE, lw=2.4,
             marker="s", ms=6, label="с делением")
    ax3.set_xscale("log", base=2)
    ax3.set_xlabel("$d_k$")
    ax3.set_ylabel("$\\|\\,\\mathrm{diag}(p) - pp^{\\top}\\|_F$")
    ax3.set_title("градиент через softmax", fontsize=11.5)
    ax3.set_ylim(0, None)
    ax3.legend(fontsize=9.5)

    for ax in (ax1, ax2, ax3):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
        _despine(ax)

    fig.suptitle("Без деления на $\\sqrt{d_k}$ внимание вырождается в argmax, "
                 "а градиент через него исчезает", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "softmax_scaling.png")
    return data


# ==========================================================================
# 2. Внимание работает с множеством: эквивариантность и позиции
# ==========================================================================


def sinusoidal(n, d, base=10000.0):
    pos = np.arange(n)[:, None]
    i = np.arange(d // 2)[None, :]
    ang = pos / base ** (2 * i / d)
    pe = np.zeros((n, d))
    pe[:, 0::2] = np.sin(ang)
    pe[:, 1::2] = np.cos(ang)
    return pe


def draw_set_and_positions(seed=0):
    _apply_style()
    rng = np.random.default_rng(seed)
    n, d = 10, 32
    X = rng.normal(size=(n, d))
    Wq, Wk, Wv = (rng.normal(size=(d, d)) / np.sqrt(d) for _ in range(3))
    perm = rng.permutation(n)

    out, A = attention(X, Wq, Wk, Wv)
    out_p, A_p = attention(X[perm], Wq, Wk, Wv)
    resid = float(np.abs(out_p - out[perm]).max())

    n_pe, d_pe = 128, 64
    PE = sinusoidal(n_pe, d_pe)
    ks = np.arange(0, 48)
    ts = (0, 20, 50, 80)
    curves = np.array([[PE[t] @ PE[t + k] for k in ks] for t in ts])
    spread = float(np.abs(curves - curves.mean(0)).max())

    fig = plt.figure(figsize=(13.2, 4.3))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.35], wspace=0.3)

    for col, (M, title) in enumerate([
        (A, "внимание на исходном порядке"),
        (A_p, "тот же вход, токены переставлены"),
    ]):
        ax = fig.add_subplot(gs[0, col])
        ax.imshow(M, cmap="Greys", vmin=0, vmax=M.max())
        ax.set_title(title, fontsize=10.5)
        ax.set_xlabel("ключ")
        if col == 0:
            ax.set_ylabel("запрос")
        ax.set_xticks(range(n), [str(i) for i in range(n)], fontsize=7)
        ax.set_yticks(range(n), [str(i) for i in range(n)], fontsize=7)
        _despine(ax, keep=())

    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(ks, curves[0], color=C_ORANGE, lw=2.6, label=f"$t = {ts[0]}$")
    for t, color, mk, off in zip(ts[1:], (C_BLUE, C_GREEN, C_INK),
                                 ("o", "s", "^"), (0, 1, 2)):
        sel = np.arange(off, len(ks), 4)
        ax3.plot(ks[sel], curves[ts.index(t)][sel], color=color, lw=0,
                 marker=mk, ms=5.5, alpha=0.9, label=f"$t = {t}$")
    ax3.set_xlabel("сдвиг $k$")
    ax3.set_ylabel("$PE(t)\\cdot PE(t+k)$")
    ax3.set_title(f"четыре кривые совпадают до {spread:.0e}", fontsize=11)
    ax3.legend(fontsize=9.5, ncol=2)
    ax3.grid(alpha=0.25, color=C_GRAY, lw=0.6)
    _despine(ax3)

    fig.suptitle(
        f"Внимание — операция над множеством: $\\max|\\mathrm{{Attn}}(PX) - "
        f"P\\,\\mathrm{{Attn}}(X)| = {resid:.0e}$; "
        f"порядок приходит только из позиционных кодировок",
        fontsize=12.5, y=1.03)
    _save(fig, "set_and_positions.png")
    return dict(resid=resid, spread=spread, pe_k0=curves[0][0],
                pe_k1=curves[0][1], pe_k47=curves[0][-1])


# ==========================================================================
# 3. Голова как поиск по ключу и зачем их много
# ==========================================================================


def run_lookup(n_items=8, d_key=16, d_val=16, sharp=8.0, trials=400, seed=1):
    rng = np.random.default_rng(seed)

    def scene():
        keys = rng.normal(size=(n_items, d_key))
        keys /= np.linalg.norm(keys, axis=1, keepdims=True)
        vals = rng.normal(size=(n_items, d_val))
        vals /= np.linalg.norm(vals, axis=1, keepdims=True)
        return keys, vals

    keys, vals = scene()
    t = 3
    A_single = softmax(keys @ keys[t] * sharp)
    out_single = A_single @ vals
    cos_single = float(out_single @ vals[t] / np.linalg.norm(out_single))

    a, b = 2, 6
    q2 = (keys[a] + keys[b]) / np.linalg.norm(keys[a] + keys[b])
    A_double = softmax(keys @ q2 * sharp)
    out_double = A_double @ vals
    cos_a = float(out_double @ vals[a] / np.linalg.norm(out_double))
    cos_b = float(out_double @ vals[b] / np.linalg.norm(out_double))

    # можно ли вытащить оба значения линейной проекцией выхода слоя
    errs = {}
    for name in ("1 голова", "2 головы"):
        H, Y = [], []
        for _ in range(trials):
            k2, v2 = scene()
            i, j = rng.choice(n_items, 2, replace=False)
            if name == "1 голова":
                qq = (k2[i] + k2[j]) / np.linalg.norm(k2[i] + k2[j])
                h = softmax(k2 @ qq * sharp) @ v2
            else:
                h = np.concatenate([softmax(k2 @ k2[i] * sharp) @ v2,
                                    softmax(k2 @ k2[j] * sharp) @ v2])
            H.append(h)
            Y.append(np.concatenate([v2[i], v2[j]]))
        H, Y = np.array(H), np.array(Y)
        W, *_ = np.linalg.lstsq(H, Y, rcond=None)
        errs[name] = float(np.linalg.norm(H @ W - Y) / np.linalg.norm(Y))

    return dict(A_single=A_single, t=t, cos_single=cos_single, A_double=A_double,
                a=a, b=b, cos_a=cos_a, cos_b=cos_b,
                norm_double=float(np.linalg.norm(out_double)), errs=errs,
                n_items=n_items, d_val=d_val)


def draw_lookup(r):
    _apply_style()
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13.2, 4.0),
                                        gridspec_kw={"width_ratios": [1, 1, 0.8]})
    idx = np.arange(r["n_items"])

    colors = [C_ORANGE if i == r["t"] else C_GRAY for i in idx]
    ax1.bar(idx, r["A_single"], color=colors, width=0.62)
    ax1.text(r["t"], r["A_single"][r["t"]] + 0.03, f"{r['A_single'][r['t']]:.3f}",
             ha="center", fontsize=10, color=C_ORANGE)
    ax1.set_ylim(0, 1.12)
    ax1.set_xlabel("позиция в последовательности")
    ax1.set_ylabel("вес внимания")
    ax1.set_title(f"запрос = ключ #{r['t']}: cos с нужным\nзначением "
                  f"{r['cos_single']:.4f}", fontsize=11)

    colors2 = [C_ORANGE if i in (r["a"], r["b"]) else C_GRAY for i in idx]
    ax2.bar(idx, r["A_double"], color=colors2, width=0.62)
    for i in (r["a"], r["b"]):
        ax2.text(i, r["A_double"][i] + 0.03, f"{r['A_double'][i]:.3f}",
                 ha="center", fontsize=10, color=C_ORANGE)
    ax2.set_ylim(0, 1.12)
    ax2.set_xlabel("позиция в последовательности")
    ax2.set_title(f"одна голова, два нужных значения:\ncos с каждым "
                  f"{r['cos_a']:.2f} и {r['cos_b']:.2f} — это смесь", fontsize=11)

    names = list(r["errs"])
    vals = [r["errs"][k] for k in names]
    ax3.bar(np.arange(2), vals, color=[C_ORANGE, C_BLUE], width=0.6)
    for x, v in enumerate(vals):
        ax3.text(x, v + 0.02, f"{v:.3f}", ha="center", fontsize=10.5)
    ax3.set_xticks(np.arange(2), [f"{names[0]}\n({r['d_val']} чисел)",
                                  f"{names[1]}\n({2 * r['d_val']} чисел)"],
                   fontsize=9.5)
    ax3.set_ylim(0, max(vals) * 1.25)
    ax3.set_ylabel("ошибка восстановления\nобоих значений")
    ax3.set_title("линейно достать оба\nзначения из выхода", fontsize=11)

    for ax in (ax1, ax2, ax3):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
        _despine(ax)

    fig.suptitle("Голова — это мягкий поиск по ключу; двух разных ответов "
                 "одна голова вернуть не может", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "multihead_lookup.png")
    return r


# ==========================================================================
# 4. Внимание усредняет, а усреднение стирает различия
# ==========================================================================


def run_collapse(n=64, d=32, depth=30, seed=0):
    rng = np.random.default_rng(seed)
    X0 = rng.normal(size=(n, d))
    runs = {}
    configs = [
        ("чистое внимание, $\\tau = 1$", 1.0, False, C_ORANGE),
        ("острое внимание, $\\tau = 0.05$", 0.05, False, C_GREEN),
        ("$\\tau = 1$ + остаточная связь", 1.0, True, C_BLUE),
        ("$\\tau = 0.05$ + остаточная связь", 0.05, True, C_INK),
    ]
    for label, temp, resid, color in configs:
        X = X0.copy()
        hist, lam = [], []
        for _ in range(depth):
            Wq, Wk, Wv = (rng.normal(size=(d, d)) / np.sqrt(d) for _ in range(3))
            out, A = attention(X, Wq, Wk, Wv, temp=temp)
            ev = np.sort(np.abs(np.linalg.eigvals(A)))[::-1]
            lam.append(ev[1])
            X = X + out if resid else out
            X = X / np.linalg.norm(X) * np.linalg.norm(X0)   # держим масштаб
            hist.append(diversity(X))
        runs[label] = dict(hist=np.array(hist), lam=float(np.mean(lam)), color=color)
    return runs


def draw_collapse(runs):
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    for label, r in runs.items():
        depth = np.arange(1, len(r["hist"]) + 1)
        ax.plot(depth, np.maximum(r["hist"], 1e-6), color=r["color"], lw=2.3,
                marker="o", ms=3.5,
                label=f"{label}: средний $|\\lambda_2(A)|$ = {r['lam']:.2f}")
    ax.set_yscale("log")
    ax.set_ylim(1e-5, 2)
    ax.set_xlabel("номер слоя")
    ax.set_ylabel("различие между токенами (лог)")
    ax.set_title("$X \\leftarrow \\mathrm{softmax}(QK^{\\top}/\\sqrt{d})\\,V$ "
                 "со случайными весами, масштаб нормируется на каждом слое",
                 fontsize=11.5)
    ax.legend(fontsize=9.5, loc="lower left")
    ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
    _despine(ax)
    fig.suptitle("Внимание — это взвешенное среднее, а повторное усреднение "
                 "стирает различия", fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "rank_collapse.png")
    return {k: (v["hist"], v["lam"]) for k, v in runs.items()}


# ==========================================================================
# 5. Цена: квадратичность и KV-кэш
# ==========================================================================


def layer_flops(n, d, ffn_mult=4):
    """FLOPs одного слоя на батч из одной последовательности длины n."""
    proj = 8 * n * d**2                    # Q, K, V и выходная проекция
    quad = 4 * n**2 * d                    # QK^T и AV
    ffn = 4 * ffn_mult * n * d**2          # две матрицы FFN
    return proj, quad, ffn


def draw_cost(seed=0):
    _apply_style()
    ns = np.logspace(np.log10(128), np.log10(1 << 20), 60)
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.8, 4.6))

    cross = {}
    for d, color, ls in ((1024, C_BLUE, "--"), (4096, C_ORANGE, "-")):
        proj, quad, ffn = layer_flops(ns, d)
        share = quad / (proj + quad + ffn)
        axL.plot(ns, share, color=color, lw=2.4, ls=ls, label=f"$d$ = {d}")
        n_star = 6 * d                     # 4n²d = 24nd²  ->  n = 6d
        cross[d] = n_star
        axL.axvline(n_star, color=color, ls=":", lw=1.2)
        axL.annotate(f"$n = 6d$ = {n_star}", xy=(n_star, 0.5),
                     xytext=(n_star * 1.15, 0.30 if d == 1024 else 0.14),
                     fontsize=9.5, color=color,
                     arrowprops=dict(arrowstyle="->", color=color, lw=1.0))
    axL.axhline(0.5, color=C_GRAY, ls="--", lw=1.2)
    axL.set_xscale("log")
    axL.set_xlabel("длина контекста $n$, токенов (лог)")
    axL.set_ylabel("доля квадратичной части в FLOPs слоя")
    axL.set_ylim(0, 1.02)
    axL.set_title("квадратичность догоняет линейную часть только при $n \\approx 6d$",
                  fontsize=11.5)
    axL.legend(fontsize=9.5, loc="upper left")

    # KV-кэш: 2 (K и V) × n × d × слоёв × 2 байта
    configs = [
        ("7B: 32 слоя, $d$ = 4096", 32, 4096, 1, C_ORANGE),
        ("7B с GQA 4:1", 32, 4096, 4, C_BLUE),
        ("70B: 80 слоёв, $d$ = 8192, GQA 8:1", 80, 8192, 8, C_GREEN),
    ]
    ctx = np.array([2048, 8192, 32768, 131072])
    rows = []
    for label, layers, d, gqa, color in configs:
        gb = 2 * ctx * d / gqa * layers * 2 / 1024**3
        axR.plot(ctx, gb, color=color, lw=2.4, marker="o", ms=5, label=label)
        rows.append((label, float(2 * d / gqa * layers * 2 / 1024**2), gb))
    axR.axhline(13.5, color=C_GRAY, ls="--", lw=1.3)
    axR.text(2100, 15, "вес модели 7B в fp16 ≈ 13.5 ГБ", fontsize=9.5, color=C_GRAY)
    axR.set_xscale("log", base=2)
    axR.set_yscale("log")
    axR.set_xticks(ctx, [f"{c // 1024}k" for c in ctx])
    axR.set_xlabel("длина контекста, токенов")
    axR.set_ylabel("KV-кэш на одну последовательность, ГБ (лог)")
    axR.set_title("память под кэш растёт линейно и упирается в железо", fontsize=11.5)
    axR.legend(fontsize=9, loc="upper left")

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
        _despine(ax)

    fig.suptitle("Две разные цены: FLOPs при обучении и память при генерации",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "attention_cost.png")
    return cross, rows, ctx


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем «Self-attention и трансформеры»:")
    scaling, n_keys = run_scaling()
    draw_scaling(scaling, n_keys)
    sets = draw_set_and_positions()
    lookup = draw_lookup(run_lookup())
    collapse = draw_collapse(run_collapse())
    cross, kv_rows, ctx = draw_cost()

    print("\nЧисла для текста лекции:")
    for d, r in scaling.items():
        print(f"  d_k = {d:5d}: std логитов {r['std']:6.2f} (sqrt = {np.sqrt(d):6.2f}); "
              f"энтропия {r['ent']:.3f} → {r['ent_s']:.3f} с делением; "
              f"max вес {r['mx']:.3f} → {r['mx_s']:.3f}; "
              f"|J| {r['jac']:.4f} → {r['jac_s']:.4f}")
    print(f"  перестановка: max|Attn(PX) - P·Attn(X)| = {sets['resid']:.2e}")
    print(f"  PE: разброс по t = {sets['spread']:.2e}; "
          f"PE·PE при k=0: {sets['pe_k0']:.2f}, k=1: {sets['pe_k1']:.2f}, "
          f"k=47: {sets['pe_k47']:.2f}")
    print(f"  поиск одной головой: вес {lookup['A_single'][lookup['t']]:.4f}, "
          f"cos {lookup['cos_single']:.4f}")
    print(f"  две цели одной головой: веса {lookup['A_double'][lookup['a']]:.3f}/"
          f"{lookup['A_double'][lookup['b']]:.3f}, cos {lookup['cos_a']:.3f}/"
          f"{lookup['cos_b']:.3f}, норма выхода {lookup['norm_double']:.3f}")
    for k, v in lookup["errs"].items():
        print(f"  восстановление обоих значений, {k}: ошибка {v:.3f}")
    for label, (hist, lam) in collapse.items():
        first_dead = next((i + 1 for i, v in enumerate(hist) if v < 1e-3), None)
        print(f"  {label}: |λ2| = {lam:.3f}, различие L1 {hist[0]:.3f} → "
              f"L{len(hist)} {hist[-1]:.2e}" +
              (f", ниже 0.001 на слое {first_dead}" if first_dead else ""))
    for d, n_star in cross.items():
        print(f"  d = {d}: квадратичная часть догоняет линейную при n = {n_star}")
    for label, per_token_mb, gb in kv_rows:
        print(f"  {label}: {per_token_mb:.3f} МБ на токен; " +
              ", ".join(f"{c // 1024}k → {g:.1f} ГБ" for c, g in zip(ctx, gb)))


if __name__ == "__main__":
    main()
