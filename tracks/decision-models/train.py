"""Train a small decision model locally; calibrate and evaluate on separate states."""

import argparse
import json
import random
import time
from dataclasses import asdict
from pathlib import Path

import torch
from calibration import fit_temperature, metrics, rlcd_loss
from data import collate, make_dataset, make_example, split_states
from model import Config, DecisionModel
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parent


@torch.no_grad()
def evaluate(model, examples, device="cpu"):
    model.eval()
    batch = collate(examples, device)
    return model(batch).cpu(), batch["labels"].cpu()


def load_model(path, device="cpu"):
    checkpoint = torch.load(path, map_location=device, weights_only=True)
    model = DecisionModel(checkpoint["kind"], Config(**checkpoint["config"])).to(device)
    model.load_state_dict(checkpoint["model"])
    return model.eval(), checkpoint["temperature"]


def run(kind="pointer", steps=2000, seed=7, device="cpu", objective="ce", batch_size=48):
    if steps < 1 or batch_size < 1 or objective not in {"ce", "rlcd"}:
        raise ValueError("Positive steps/batch_size and a supported objective are required")
    torch.manual_seed(seed)
    rng = random.Random(seed)
    split = split_states()
    model = DecisionModel(kind).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=0.01)
    history, started = [], time.perf_counter()
    for step in range(steps):
        model.train()
        examples = [make_example(rng.choice(split["train"]), rng) for _ in range(batch_size)]
        batch = collate(examples, device)
        logits = model(batch)
        loss = (
            F.cross_entropy(logits, batch["labels"])
            if objective == "ce"
            else rlcd_loss(logits, batch["labels"], batch["option_mask"])
        )
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step == 0 or (step + 1) % 100 == 0 or step + 1 == steps:
            point = {
                "step": step + 1,
                "loss": float(loss.detach()),
                "batch_accuracy": float(logits.argmax(-1).eq(batch["labels"]).float().mean()),
            }
            history.append(point)
            print(
                f"{kind:7} {objective:4} step={step + 1:4} loss={point['loss']:.4f} "
                f"batch_acc={point['batch_accuracy']:.3f}",
                flush=True,
            )

    # Fixed examples, disjoint state IDs. No test labels enter training or temperature fit.
    calibration = make_dataset(split["calibration"], 400, seed=100)
    test = make_dataset(split["test"], 500, seed=200)
    cal_z, cal_y = evaluate(model, calibration, device)
    temperature = fit_temperature(cal_z, cal_y)
    test_z, test_y = evaluate(model, test, device)
    report = {
        "task": "synthetic person-colour retrieval; NOT an NLP/Jev benchmark",
        "kind": kind,
        "objective": objective,
        "seed": seed,
        "steps": steps,
        "batch_size": batch_size,
        "optimizer": {"name": "AdamW", "lr": 0.002, "weight_decay": 0.01, "grad_clip": 1.0},
        "initialization": "PyTorch module defaults; random, not pretrained",
        "config": asdict(model.cfg),
        "parameters": sum(p.numel() for p in model.parameters()),
        "device": device,
        "torch": str(torch.__version__),
        "elapsed_seconds": time.perf_counter() - started,
        "split_seed": 42,
        "state_counts": {k: len(v) for k, v in split.items()},
        "random_baseline": sum(1 / len(e.options) for e in test) / len(test),
        "calibration_before": metrics(cal_z, cal_y),
        "calibration_after": metrics(cal_z, cal_y, temperature),
        "test_before": metrics(test_z, test_y),
        "test_after": metrics(test_z, test_y, temperature),
        "history": history,
    }
    checkpoint = {
        "kind": kind,
        "config": asdict(model.cfg),
        "model": model.state_dict(),
        "temperature": temperature,
    }
    return model, checkpoint, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["token", "pointer", "marker", "all"], default="pointer")
    parser.add_argument("--objective", choices=["ce", "rlcd"], default="ce")
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--batch-size", type=int, default=48)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", choices=["cpu", "mps", "cuda"], default="cpu")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--out", type=Path, default=ROOT / "out")
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    args.out.mkdir(parents=True, exist_ok=True)
    kinds = ["token", "pointer", "marker"] if args.model == "all" else [args.model]
    for kind in kinds:
        _, checkpoint, report = run(
            kind, args.steps, args.seed, args.device, args.objective, args.batch_size
        )
        stem = f"{kind}-{args.objective}"
        torch.save(checkpoint, args.out / f"{stem}.pt")
        (args.out / f"{stem}.json").write_text(json.dumps(report, indent=2) + "\n")
        before, after = report["test_before"], report["test_after"]
        print(
            f"test accuracy={after['accuracy']:.3f}; NLL {before['nll']:.3f} -> "
            f"{after['nll']:.3f}; fitted T={after['temperature']:.3f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
