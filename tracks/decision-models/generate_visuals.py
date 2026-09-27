"""Rebuild architecture diagrams and measured experiment figures in MLIB colours."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from inspect_model import isolation_demo
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyBboxPatch
from model import attention_mask

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
BG, INK, GREY, PANEL = "#faf9f5", "#141413", "#b0aea5", "#e8e6dc"
BLUE, ORANGE, GREEN = "#6a9bcc", "#d97757", "#788c5d"


def save(fig, name):
    ASSETS.mkdir(exist_ok=True)
    fig.savefig(ASSETS / name, dpi=170, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def box(ax, x, y, width, height, text, colour=PANEL, fontsize=11):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.02",
            facecolor=colour,
            edgecolor=GREY,
            linewidth=0.7,
        )
    )
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=INK,
        linespacing=1.6,
    )


def arrow(ax, start, end):
    ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": INK, "lw": 1.3})


def architecture():
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 7.2))
    titles = ["Token readout", "Pointer readout", "Marker readout"]
    sources = ["механизм SemIf / Nimble", "механизм Kev", "механизм Laya"]
    steps = [
        [
            "state + вопрос + варианты\n[B, L]",
            "Causal Transformer\n[B, L, D]",
            "h в позиции [DECIDE]\n[B, D]",
            "строки W_vocab для A/B/C\n[B, K]",
        ],
        [
            "state + вопрос + варианты\n[B, L]",
            "Causal Transformer\n[B, L, D]",
            "h_decide + h_[/OPT]\n[B, D] + [B, K, D]",
            "dot(Wq h_decide, Wk h_opt) / √D\n[B, K]",
        ],
        [
            "state + вопрос + варианты\n[B, L]",
            "Bidirectional Transformer\n[B, L, D]",
            "h в позициях [OPT]\n[B, K, D]",
            "общая MLP → один скаляр\n[B, K]",
        ],
    ]
    for ax, title, source, cards in zip(axes, titles, sources, steps):
        ax.set(xlim=(0, 4), ylim=(0, 9))
        ax.axis("off")
        ax.text(2, 8.55, title, ha="center", weight="bold", fontsize=15)
        ax.text(2, 8.05, source, ha="center", fontsize=10, color="#66645c")
        for i, text in enumerate(cards):
            y = 6.4 - i * 1.65
            box(ax, 0.18, y, 3.64, 1.08, text, BLUE if i == 1 else PANEL, fontsize=10)
            if i < len(cards) - 1:
                arrow(ax, (2, y - 0.06), (2, y - 0.53))
        arrow(ax, (2, 1.38), (2, 0.93))
        box(
            ax,
            0.18,
            0,
            3.64,
            0.9,
            "softmax по K вариантам → p\nPython собирает typed answer",
            ORANGE,
            10,
        )
    fig.suptitle("Три способа превратить представления в решение", fontsize=18, y=1.01)
    fig.text(
        0.5,
        -0.025,
        "Схемы учебных моделей: backbone и размеры упрощены; веса Jev неизвестны.",
        ha="center",
        fontsize=11,
    )
    fig.tight_layout()
    save(fig, "architectures.png")


def masks():
    report, tokens, segments, _, packed_mask = isolation_demo()
    arrays = [
        attention_mask(tokens, True)[0, 0],
        attention_mask(tokens, False)[0, 0],
        packed_mask[0, 0],
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.5))
    names = ["Обычная causal mask", "Bidirectional mask", "Causal mask с ветвями"]
    borders = np.flatnonzero(np.diff(segments.numpy())) + 0.5
    mids = [float(torch.where(segments == i)[0].float().mean()) for i in range(3)]
    for ax, matrix, name in zip(axes, arrays, names):
        ax.imshow(matrix.numpy(), cmap=ListedColormap([PANEL, BLUE]), vmin=0, vmax=1)
        for border in borders:
            ax.axhline(border, color=BG, lw=1.4)
            ax.axvline(border, color=BG, lw=1.4)
        ax.set_xticks(mids, ["state", "Q1", "Q2"])
        ax.set_yticks(mids, ["state", "Q1", "Q2"])
        ax.set_title(name, fontsize=12, pad=12)
        ax.set_xlabel("key: откуда читаем")
    axes[0].set_ylabel("query: кто читает")
    fig.suptitle("Синий = разрешённый путь информации", fontsize=16, y=1.02)
    fig.tight_layout()
    save(fig, "attention_masks.png")
    return report


def cache_equivalence(report):
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.7), gridspec_kw={"width_ratios": [1, 1.15]})
    ax = axes[0]
    ax.set(xlim=(0, 6), ylim=(0, 5))
    ax.axis("off")
    box(ax, 1.25, 3.7, 3.5, 0.85, "state → K/V каждого слоя", BLUE)
    for x, label in [(0.05, "suffix Q1"), (3.15, "suffix Q2")]:
        box(ax, x, 1.9, 2.8, 0.85, label, PANEL)
        arrow(ax, (3, 3.65), (x + 1.4, 2.85))
        box(ax, x, 0.35, 2.8, 0.85, "своё распределение", ORANGE, 10)
        arrow(ax, (x + 1.4, 1.83), (x + 1.4, 1.25))
    ax.set_title("Общий префикс, независимые продолжения", fontsize=12, pad=12)
    ax = axes[1]
    keys = ["packed_vs_separate_q2", "cached_vs_full_q2", "q2_error_without_position_reset"]
    values = [report[k] for k in keys]
    bars = ax.bar(
        ["packed / separate", "cache / full", "без сброса позиций"],
        np.maximum(values, 1e-8),
        color=[BLUE, BLUE, ORANGE],
        width=0.55,
    )
    ax.set_yscale("log")
    ax.set_ylim(1e-8, max(values) * 20)
    ax.set_ylabel("max |Δ hidden|, log scale")
    ax.set_title("Измерено на учебном Transformer, FP32", fontsize=12, pad=12)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            max(value, 1e-8) * 1.8,
            f"{value:.2g}",
            ha="center",
            fontsize=11,
        )
    ax.tick_params(axis="x", labelsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, "cache_equivalence.png")


def measured_figures(reports):
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.3))
    colours = {"token": GREY, "pointer": BLUE, "marker": ORANGE}
    for report in reports:
        kind, history = report["kind"], report["history"]
        axes[0].plot(
            [p["step"] for p in history],
            [p["loss"] for p in history],
            "o-",
            color=colours[kind],
            label=kind,
        )
    axes[0].set(
        xlabel="optimizer steps",
        ylabel="batch cross-entropy",
        title="Обучение с нуля на синтетической задаче",
    )
    axes[0].legend()
    scores = [r["test_after"]["accuracy"] for r in reports]
    bars = axes[1].bar(
        [r["kind"] for r in reports],
        scores,
        color=[colours[r["kind"]] for r in reports],
        width=0.55,
    )
    axes[1].axhline(reports[0]["random_baseline"], color=INK, ls="--", lw=1, label="uniform choice")
    for bar, value in zip(bars, scores):
        axes[1].text(bar.get_x() + bar.get_width() / 2, value + 0.025, f"{value:.3f}", ha="center")
    axes[1].set(ylim=(0, 1.13), ylabel="accuracy", title="500 вопросов, новые комбинации состояний")
    axes[1].legend(loc="lower right")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, "learning.png")

    report = next(r for r in reports if r["kind"] == "pointer")
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
    for ax, key, title, colour in zip(
        axes,
        ["test_before", "test_after"],
        ["T = 1", "T подобрана на calibration split"],
        [BLUE, ORANGE],
    ):
        result = report[key]
        populated = [b for b in result["bins"] if b["count"]]
        ax.plot([0, 1], [0, 1], "--", color=GREY)
        ax.scatter(
            [b["confidence"] for b in populated],
            [b["accuracy"] for b in populated],
            s=[20 + 1.5 * b["count"] for b in populated],
            color=colour,
            alpha=0.8,
            edgecolors=INK,
            lw=0.5,
        )
        ax.set(
            xlim=(0, 1.03),
            ylim=(-0.03, 1.03),
            xlabel="средний max(p) в bin",
            ylabel="доля правильных ответов",
            title=title,
        )
        ax.text(
            0.05,
            0.91,
            f"NLL = {result['nll']:.3f}\nECE = {result['ece']:.3f}\nT = {result['temperature']:.3f}",
            transform=ax.transAxes,
            va="top",
            fontsize=11,
        )
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Pointer: вероятность проверяется на отдельном test split", fontsize=15, y=1.03)
    fig.text(
        0.5,
        -0.02,
        "Площадь точки отражает размер bin. Маленькая синтетическая выборка не доказывает OOD-калибровку.",
        ha="center",
        fontsize=10,
    )
    fig.tight_layout()
    save(fig, "calibration.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results", type=Path, help="Read *-ce.json reports from this training directory"
    )
    args = parser.parse_args()
    torch.set_num_threads(1)
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "text.color": INK,
            "axes.labelcolor": INK,
            "font.family": "DejaVu Sans",
            "font.size": 10,
        }
    )
    architecture()
    report = masks()
    cache_equivalence(report)
    (ASSETS / "mask_experiment.json").write_text(json.dumps(report, indent=2) + "\n")
    saved = ASSETS / "training_experiment.json"
    if args.results:
        reports = [
            json.loads((args.results / f"{kind}-ce.json").read_text())
            for kind in ["token", "pointer", "marker"]
        ]
        saved.write_text(json.dumps(reports, indent=2) + "\n")
    if saved.exists():
        measured_figures(json.loads(saved.read_text()))
    manifest = {
        "generator": "generate_visuals.py",
        "palette": "MLIB shared visual design system",
        "figures": {
            "architectures.png": "schematic of the local teaching models",
            "attention_masks.png": "actual masks returned by model.py",
            "cache_equivalence.png": "measured FP32 hidden-state differences",
        },
    }
    if saved.exists():
        manifest["figures"].update(
            {
                "learning.png": "measured synthetic training/test results",
                "calibration.png": "measured held-out reliability bins",
            }
        )
    (ASSETS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Generated figures in {ASSETS}")


if __name__ == "__main__":
    main()
