from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

sns.set_theme(style="whitegrid", context="talk")


def prepare_axes_2d(ax, lim=5):
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color="#444444", lw=1.2)
    ax.axvline(0, color="#444444", lw=1.2)
    ax.grid(True, alpha=0.25)


def add_arrow_2d(ax, vec, color, label, lw=3, alpha=1.0):
    ax.annotate(
        "",
        xy=(vec[0], vec[1]),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", lw=lw, color=color, alpha=alpha),
    )
    ax.text(
        vec[0] * 1.06,
        vec[1] * 1.06,
        label,
        color=color,
        fontsize=13,
        weight="bold",
    )


def add_arrow_3d(ax, start, vec, color, label=None, lw=3, alpha=1.0):
    ax.quiver(
        start[0],
        start[1],
        start[2],
        vec[0],
        vec[1],
        vec[2],
        color=color,
        linewidth=lw,
        alpha=alpha,
        arrow_length_ratio=0.12,
    )
    if label:
        end = np.array(start) + np.array(vec)
        ax.text(end[0], end[1], end[2], label, color=color, fontsize=12)


def save_basis_coordinates():
    fig, ax = plt.subplots(figsize=(9, 9))
    prepare_axes_2d(ax, lim=6)

    e1 = np.array([1, 1])
    e2 = np.array([1, -1])
    coords = np.array([3, 2])
    v = coords[0] * e1 + coords[1] * e2

    add_arrow_2d(ax, e1, "#2563eb", r"$e_1=(1,1)$")
    add_arrow_2d(ax, e2, "#7c3aed", r"$e_2=(1,-1)$")
    add_arrow_2d(ax, 3 * e1, "#60a5fa", r"$3e_1$", lw=2.5, alpha=0.85)
    add_arrow_2d(ax, v, "#ef4444", r"$v=(5,1)$")

    ax.plot(
        [3 * e1[0], v[0]],
        [3 * e1[1], v[1]],
        color="#f59e0b",
        lw=3,
        linestyle="--",
        alpha=0.9,
    )
    ax.scatter([v[0]], [v[1]], s=120, color="#ef4444", zorder=5)

    ax.text(
        -5.7,
        5.2,
        r"$v=3e_1+2e_2$",
        fontsize=19,
        color="#111827",
        bbox=dict(boxstyle="round,pad=0.4", fc="#fef3c7", ec="#f59e0b"),
    )
    ax.text(
        -5.7,
        4.1,
        "Базис задает новую систему координат",
        fontsize=13,
        color="#374151",
    )
    ax.set_title("Координаты вектора в нестандартном базисе", pad=18, weight="bold")
    fig.tight_layout()
    fig.savefig(ASSETS / "basis_coordinates.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_basis_change_gif():
    vector = np.array([4.0, 3.0])
    frames = []
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, t in enumerate(np.linspace(0, 1, 28)):
            fig, ax = plt.subplots(figsize=(8.4, 8.4))
            prepare_axes_2d(ax, lim=6)

            e1 = np.array([1.0, 0.0]) * (1 - t) + np.array([1.0, 1.0]) * t
            e2 = np.array([0.0, 1.0]) * (1 - t) + np.array([1.0, -1.0]) * t

            basis = np.column_stack([e1, e2])
            coords = np.linalg.solve(basis, vector)

            add_arrow_2d(ax, e1, "#2563eb", r"$e_1$", lw=3.2)
            add_arrow_2d(ax, e2, "#7c3aed", r"$e_2$", lw=3.2)
            add_arrow_2d(ax, vector, "#ef4444", r"$v$", lw=3.6)

            ax.text(
                -5.7,
                5.0,
                "Один и тот же вектор, но разные базисы",
                fontsize=15,
                color="#111827",
                weight="bold",
            )
            ax.text(
                -5.7,
                3.95,
                rf"$[v]_e \approx ({coords[0]:.2f},\, {coords[1]:.2f})$",
                fontsize=16,
                color="#111827",
                bbox=dict(boxstyle="round,pad=0.35", fc="#e0f2fe", ec="#38bdf8"),
            )
            ax.set_title("Смена базиса меняет координаты, но не сам вектор", pad=16)

            frame_path = tmp_path / f"basis_{i:03d}.png"
            fig.tight_layout()
            fig.savefig(frame_path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            frames.append(imageio.imread(frame_path))

    imageio.mimsave(ASSETS / "basis_change.gif", frames, duration=0.12, loop=0)


def save_kernel_plane():
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    y = np.linspace(-2.5, 2.5, 30)
    z = np.linspace(-2.5, 2.5, 30)
    Y, Z = np.meshgrid(y, z)
    X = 2 * Y - Z

    ax.plot_surface(X, Y, Z, color="#60a5fa", alpha=0.35, linewidth=0, shade=True)

    b1 = np.array([2, 1, 0])
    b2 = np.array([-1, 0, 1])
    add_arrow_3d(ax, (0, 0, 0), b1, "#2563eb", r"$b_1$")
    add_arrow_3d(ax, (0, 0, 0), b2, "#7c3aed", r"$b_2$")

    ax.text2D(
        0.02,
        0.96,
        r"$U=\{(x,y,z)\mid x-2y+z=0\}$",
        transform=ax.transAxes,
        fontsize=18,
        color="#111827",
        bbox=dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#3b82f6"),
    )
    ax.text2D(
        0.02,
        0.88,
        r"$U=\mathrm{span}\{(2,1,0),\,(-1,0,1)\}$",
        transform=ax.transAxes,
        fontsize=15,
        color="#374151",
    )

    ax.set_title("Подпространство как множество решений однородной системы", pad=20)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=24, azim=36)
    ax.set_box_aspect((1.2, 1.0, 1.0))
    fig.tight_layout()
    fig.savefig(ASSETS / "kernel_plane.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_sum_intersection():
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    x = np.linspace(-2.6, 2.6, 20)
    y = np.linspace(-2.6, 2.6, 20)
    X, Y = np.meshgrid(x, y)
    Z1 = np.zeros_like(X)

    x2 = np.linspace(-2.6, 2.6, 20)
    z2 = np.linspace(-2.6, 2.6, 20)
    X2, Z2 = np.meshgrid(x2, z2)
    Y2 = np.zeros_like(X2)

    ax.plot_surface(X, Y, Z1, color="#60a5fa", alpha=0.28, linewidth=0)
    ax.plot_surface(X2, Y2, Z2, color="#f59e0b", alpha=0.28, linewidth=0)

    line = np.linspace(-3, 3, 100)
    ax.plot(line, np.zeros_like(line), np.zeros_like(line), color="#dc2626", lw=5)
    ax.text(2.65, 0.0, 0.0, r"$U\cap W$", color="#dc2626", fontsize=14)

    ax.text2D(
        0.02,
        0.95,
        "Сумма и пересечение подпространств",
        transform=ax.transAxes,
        fontsize=19,
        weight="bold",
        color="#111827",
    )
    ax.text2D(
        0.02,
        0.88,
        r"$U=\{(x,y,0)\},\quad W=\{(x,0,z)\}$",
        transform=ax.transAxes,
        fontsize=15,
        color="#374151",
    )
    ax.text2D(
        0.02,
        0.81,
        r"$U\cap W=\{(x,0,0)\},\quad U+W=\mathbb{R}^3$",
        transform=ax.transAxes,
        fontsize=15,
        color="#374151",
    )

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=23, azim=35)
    ax.set_box_aspect((1.2, 1.0, 1.0))
    fig.tight_layout()
    fig.savefig(ASSETS / "sum_intersection.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_direct_sum_gif():
    frames = []
    u = np.array([2.0, -1.0, 0.0])
    w_final = np.array([0.0, 0.0, 5.0])

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, t in enumerate(np.linspace(0, 1, 26)):
            w = t * w_final
            v = u + w

            fig = plt.figure(figsize=(9.2, 7.8))
            ax = fig.add_subplot(111, projection="3d")

            add_arrow_3d(ax, (0, 0, 0), u, "#2563eb", r"$u\in U$", lw=3.2)
            add_arrow_3d(ax, (0, 0, 0), w, "#f59e0b", r"$w\in W$", lw=3.2)
            add_arrow_3d(ax, (0, 0, 0), v, "#ef4444", r"$v=u+w$", lw=3.8)

            ax.plot([u[0], v[0]], [u[1], v[1]], [u[2], v[2]], color="#f59e0b", ls="--", lw=2.3)
            ax.plot([w[0], v[0]], [w[1], v[1]], [w[2], v[2]], color="#2563eb", ls="--", lw=2.3)

            xx = np.linspace(-3, 3, 10)
            yy = np.linspace(-3, 3, 10)
            XX, YY = np.meshgrid(xx, yy)
            ZZ = np.zeros_like(XX)
            ax.plot_surface(XX, YY, ZZ, color="#60a5fa", alpha=0.12, linewidth=0)
            ax.plot([0, 0], [0, 0], [-0.5, 5.8], color="#f59e0b", alpha=0.4, lw=5)

            ax.text2D(
                0.02,
                0.95,
                r"Прямая сумма: $v$ раскладывается на часть из $U$ и часть из $W$",
                transform=ax.transAxes,
                fontsize=15,
                color="#111827",
                weight="bold",
            )
            ax.text2D(
                0.02,
                0.88,
                r"$\mathbb{R}^3 = U \oplus W$, где $U=\{(x,y,0)\},\, W=\{(0,0,z)\}$",
                transform=ax.transAxes,
                fontsize=13,
                color="#374151",
            )

            ax.set_xlim(-3, 3)
            ax.set_ylim(-3, 3)
            ax.set_zlim(-1, 6)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_zlabel("z")
            ax.view_init(elev=24, azim=36)
            ax.set_box_aspect((1.2, 1.0, 1.2))

            frame_path = tmp_path / f"direct_sum_{i:03d}.png"
            fig.tight_layout()
            fig.savefig(frame_path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            frames.append(imageio.imread(frame_path))

    imageio.mimsave(ASSETS / "direct_sum.gif", frames, duration=0.13, loop=0)


def main():
    ASSETS.mkdir(exist_ok=True)
    save_basis_coordinates()
    save_basis_change_gif()
    save_kernel_plane()
    save_sum_intersection()
    save_direct_sum_gif()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
