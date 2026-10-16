"""Точные схемы для темы «K-means, K-NN и GMM».

Все кривые и границы строятся на данных, сгенерированных в этом файле:
центроиды проходят настоящие итерации Lloyd, метрики выбора K считаются
через sklearn, границы K-NN получаются из обученных классификаторов, а
эллипсы GMM — из оценённых ковариаций.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Ellipse
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs, make_moons
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"
C_PURPLE = "#8f7aa8"
COLORS = [C_BLUE, C_ORANGE, C_GREEN, C_PURPLE]


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


def _clean(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(alpha=0.22, color=C_GRAY, lw=0.6)


def _scatter_clusters(ax, X, labels, centers=None):
    for k in np.unique(labels):
        ax.scatter(
            X[labels == k, 0],
            X[labels == k, 1],
            s=20,
            color=COLORS[int(k) % len(COLORS)],
            alpha=0.72,
            linewidths=0,
        )
    if centers is not None:
        ax.scatter(
            centers[:, 0],
            centers[:, 1],
            s=120,
            marker="X",
            color=C_INK,
            edgecolors=C_BG,
            linewidths=0.8,
            zorder=3,
        )


def draw_kmeans_lloyd(seed=3):
    """Показывает реальные шаги assignment/update в алгоритме Lloyd."""
    _apply_style()
    X, _ = make_blobs(
        n_samples=180,
        centers=[(-2.1, -1.2), (0.1, 2.0), (2.0, -0.8)],
        cluster_std=[0.55, 0.62, 0.58],
        random_state=seed,
    )
    rng = np.random.default_rng(seed)
    centers = X[rng.choice(len(X), size=3, replace=False)].copy()
    snapshots = []
    for _iteration in range(7):
        labels = np.argmin(((X[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2), axis=1)
        snapshots.append((labels.copy(), centers.copy()))
        new_centers = np.array(
            [X[labels == k].mean(axis=0) for k in range(3)]
        )
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    chosen = [0, min(1, len(snapshots) - 1), len(snapshots) - 1]
    fig, axes = plt.subplots(1, 3, figsize=(12.3, 4.1), sharex=True, sharey=True)
    for ax, index in zip(axes, chosen):
        labels, cs = snapshots[index]
        _scatter_clusters(ax, X, labels, cs)
        ax.set_title(f"итерация {index}: assignment → update", fontsize=10.5)
        ax.set_xlim(-3.6, 3.5)
        ax.set_ylim(-3.2, 3.2)
        ax.set_aspect("equal")
        _clean(ax)
    fig.suptitle("Lloyd попеременно назначает точки и пересчитывает центроиды", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "kmeans_lloyd.png")


def draw_cluster_selection(seed=7):
    _apply_style()
    X, _ = make_blobs(
        n_samples=480,
        centers=[(-2.2, -1.2), (0.1, 2.0), (2.2, -0.7), (0.0, -0.2)],
        cluster_std=[0.55, 0.58, 0.62, 0.46],
        random_state=seed,
    )
    ks = np.arange(2, 9)
    inertia = []
    silhouettes = []
    for k in ks:
        model = KMeans(n_clusters=k, n_init=20, random_state=seed).fit(X)
        inertia.append(model.inertia_)
        silhouettes.append(silhouette_score(X, model.labels_))
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(11.2, 4.3))
    ax_l.plot(ks, inertia, color=C_INK, marker="o", lw=2.2)
    ax_l.set_xlabel("число кластеров K")
    ax_l.set_ylabel("inertia")
    ax_l.set_title("локоть: выигрыш от новых кластеров убывает")
    ax_l.axvline(4, color=C_ORANGE, ls="--", lw=1.3)
    ax_l.text(4.1, inertia[-1], "структура данных", color=C_ORANGE, fontsize=9.5)
    ax_r.plot(ks, silhouettes, color=C_BLUE, marker="o", lw=2.2)
    ax_r.set_xlabel("число кластеров K")
    ax_r.set_ylabel("средний silhouette")
    ax_r.set_title("silhouette: компактность и разделённость")
    best = int(ks[np.argmax(silhouettes)])
    ax_r.axvline(best, color=C_GREEN, ls="--", lw=1.3)
    ax_r.text(best + 0.1, min(silhouettes) + 0.01, f"максимум при K={best}", color=C_GREEN, fontsize=9.5)
    for ax in (ax_l, ax_r):
        ax.set_xticks(ks)
        _clean(ax)
    fig.suptitle("Выбор K требует критерия: inertia сама по себе всегда падает", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "cluster_selection.png")
    return best, float(max(silhouettes))


def _plot_boundary(ax, model, X, y, title):
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 180), np.linspace(y_min, y_max, 180))
    zz = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    cmap = ListedColormap(["#dbe8f2", "#f3d5c7"])
    ax.contourf(xx, yy, zz, levels=[-0.5, 0.5, 1.5], cmap=cmap, alpha=0.8)
    ax.scatter(X[y == 0, 0], X[y == 0, 1], s=15, color=C_BLUE, alpha=0.75)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], s=15, color=C_ORANGE, alpha=0.75)
    ax.set_title(title, fontsize=10.5)
    ax.set_aspect("equal")
    _clean(ax)


def draw_knn_bias_variance(seed=10):
    _apply_style()
    X, y = make_moons(n_samples=500, noise=0.25, random_state=seed)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.35, random_state=seed, stratify=y
    )
    ks_to_show = [1, 15, 80]
    fig = plt.figure(figsize=(12.2, 7.0))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.85], hspace=0.34, wspace=0.18)
    for col, k in enumerate(ks_to_show):
        model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
        model.fit(X_train, y_train)
        _plot_boundary(fig.add_subplot(grid[0, col]), model, X_train, y_train, f"k={k}: test accuracy {model.score(X_test, y_test):.2f}")
    cv_ks = np.arange(1, 61)
    errors = []
    for k in cv_ks:
        model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
        model.fit(X_train, y_train)
        errors.append(1 - model.score(X_test, y_test))
    ax = fig.add_subplot(grid[1, :])
    ax.plot(cv_ks, errors, color=C_INK, lw=2.2)
    ax.scatter([cv_ks[int(np.argmin(errors))]], [min(errors)], color=C_ORANGE, s=55, zorder=3)
    ax.set_xlabel("число соседей k")
    ax.set_ylabel("ошибка на test")
    ax.set_title("малое k переобучается, большое k сглаживает границу")
    _clean(ax)
    fig.suptitle("K-NN: один параметр управляет bias–variance trade-off", fontsize=13, y=0.99)
    _save(fig, "knn_bias_variance.png")


def _draw_ellipse(ax, mean, covariance, color):
    values, vectors = np.linalg.eigh(covariance)
    order = values.argsort()[::-1]
    values, vectors = values[order], vectors[:, order]
    angle = np.degrees(np.arctan2(vectors[1, 0], vectors[0, 0]))
    width, height = 2 * 2.0 * np.sqrt(values)
    ellipse = Ellipse(
        mean,
        width,
        height,
        angle=angle,
        facecolor=color,
        edgecolor=color,
        alpha=0.18,
        lw=2.0,
    )
    ax.add_patch(ellipse)


def draw_gmm_soft_assignments(seed=5):
    _apply_style()
    rng = np.random.default_rng(seed)
    means = np.array([[-2.1, 0.0], [0.7, 1.8], [2.0, -1.0]])
    covariances = np.array(
        [
            [[0.65, 0.32], [0.32, 0.48]],
            [[0.55, -0.22], [-0.22, 0.75]],
            [[0.65, 0.18], [0.18, 0.38]],
        ]
    )
    X = np.vstack(
        [rng.multivariate_normal(mean, cov, size=180) for mean, cov in zip(means, covariances)]
    )
    model = GaussianMixture(n_components=3, covariance_type="full", n_init=10, random_state=seed)
    model.fit(X)
    responsibilities = model.predict_proba(X)
    labels = responsibilities.argmax(axis=1)
    confidence = responsibilities.max(axis=1)
    fig, ax = plt.subplots(figsize=(6.7, 5.3))
    for k in range(3):
        _draw_ellipse(ax, model.means_[k], model.covariances_[k], COLORS[k])
    for k in range(3):
        mask = labels == k
        ax.scatter(
            X[mask, 0],
            X[mask, 1],
            s=19,
            color=COLORS[k],
            alpha=0.35 + 0.6 * confidence[mask],
            linewidths=0,
        )
        ax.scatter(*model.means_[k], marker="X", s=140, color=C_INK, zorder=3)
    ambiguous = np.argsort(confidence)[:4]
    ax.scatter(X[ambiguous, 0], X[ambiguous, 1], s=90, facecolors="none", edgecolors=C_INK, lw=1.3)
    ax.text(
        -3.7,
        3.0,
        "прозрачность = уверенность\nв принадлежности компоненте",
        fontsize=10,
        bbox={"facecolor": C_BG, "edgecolor": "none", "pad": 2},
    )
    ax.set_xlim(-4.2, 4.0)
    ax.set_ylim(-3.0, 3.6)
    ax.set_aspect("equal")
    ax.set_title("GMM: эллиптические компоненты и мягкие responsibilities")
    _clean(ax)
    fig.tight_layout()
    _save(fig, "gmm_soft_assignments.png")
    return float(model.bic(X)), float(model.score(X))


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем «K-means, K-NN и GMM»:")
    draw_kmeans_lloyd()
    best_k, best_silhouette = draw_cluster_selection()
    draw_knn_bias_variance()
    bic, log_likelihood = draw_gmm_soft_assignments()
    print(f"  silhouette максимум: K={best_k}, score={best_silhouette:.3f}")
    print(f"  пример GMM: BIC={bic:.1f}, средний log-likelihood={log_likelihood:.3f}")


if __name__ == "__main__":
    main()
