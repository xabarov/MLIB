"""Inspect tensor shapes, three readouts, packed isolation and a shared KV prefix."""

import argparse
import json
import random

import torch
from data import WORDS, collate, decode, make_example
from model import Config, DecisionModel, branch_mask
from train import load_model
from typed import answer


@torch.no_grad()
def isolation_demo(device="cpu"):
    with torch.random.fork_rng():
        torch.manual_seed(123)
        backbone = DecisionModel("pointer", Config(width=32, heads=4, layers=2)).backbone.eval()
    backbone = backbone.to(device)
    first = make_example(73, random.Random(3), n_options=3)
    second = make_example(73, random.Random(8), n_options=2)
    s = first.state_length
    assert first.tokens[:s] == second.tokens[:s]
    suffix1, suffix2 = first.tokens[s:], second.tokens[s:]
    tokens = torch.tensor([first.tokens + suffix2], device=device)
    segments = torch.tensor([0] * s + [1] * len(suffix1) + [2] * len(suffix2), device=device)
    positions = torch.tensor(
        list(range(len(first.tokens))) + list(range(s, s + len(suffix2))), device=device
    )
    allow = branch_mask(segments)
    packed, _, _ = backbone(tokens, allow=allow, positions=positions)
    independent1, _, _ = backbone(torch.tensor([first.tokens], device=device))
    independent2, _, _ = backbone(torch.tensor([second.tokens], device=device))
    # Prefill state once; both suffixes use exactly the same unmodified cache object.
    _, prefix, _ = backbone(torch.tensor([first.tokens[:s]], device=device))
    saved_prefix = [(k.clone(), v.clone()) for k, v in prefix]
    cached1, _, _ = backbone(torch.tensor([suffix1], device=device), past=prefix)
    cached2, _, _ = backbone(torch.tensor([suffix2], device=device), past=prefix)
    changed = tokens.clone()
    changed[:, len(first.tokens) :] = WORDS.index("violet")
    perturbed, _, _ = backbone(changed, allow=allow, positions=positions)
    changed_first = tokens.clone()
    changed_first[:, s : len(first.tokens)] = WORDS.index("green")
    perturbed_first, _, _ = backbone(changed_first, allow=allow, positions=positions)
    # A deliberately wrong position assignment shows why the reset matters.
    wrong_positions, _, _ = backbone(tokens, allow=allow)
    report = {
        "packed_vs_separate_q1": float((packed[:, : len(first.tokens)] - independent1).abs().max()),
        "packed_vs_separate_q2": float(
            (packed[:, len(first.tokens) :] - independent2[:, s:]).abs().max()
        ),
        "cached_vs_full_q1": float((cached1 - independent1[:, s:]).abs().max()),
        "cached_vs_full_q2": float((cached2 - independent2[:, s:]).abs().max()),
        "q1_change_after_editing_q2": float(
            (perturbed[:, : len(first.tokens)] - packed[:, : len(first.tokens)]).abs().max()
        ),
        "q2_change_after_editing_q1": float(
            (perturbed_first[:, len(first.tokens) :] - packed[:, len(first.tokens) :]).abs().max()
        ),
        "q2_error_without_position_reset": float(
            (wrong_positions[:, len(first.tokens) :] - independent2[:, s:]).abs().max()
        ),
        "prefix_unchanged": all(
            torch.equal(k, a) and torch.equal(v, b) for (k, v), (a, b) in zip(prefix, saved_prefix)
        ),
    }
    return report, tokens, segments, positions, allow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["token", "pointer", "marker"], default="pointer")
    parser.add_argument("--checkpoint", help="Optional checkpoint written by train.py")
    args = parser.parse_args()
    torch.set_num_threads(1)
    torch.manual_seed(7)
    model, temperature = (
        load_model(args.checkpoint) if args.checkpoint else (DecisionModel(args.model).eval(), 1.0)
    )
    example = make_example(73, random.Random(3), n_options=3)
    batch = collate([example])
    with torch.no_grad():
        hidden, caches, maps = model.backbone(batch["tokens"])
        logits = model(batch)
    print("Trained checkpoint" if args.checkpoint else "RANDOM weights — tensor mechanics only")
    print(decode(example.tokens))
    print("tokens", tuple(batch["tokens"].shape), "hidden", tuple(hidden.shape))
    print("attention", tuple(maps[0].shape), "K cache", tuple(caches[0][0].shape))
    print("option starts", example.starts, "option ends", example.ends)
    print("logits", tuple(logits.shape), "gold option", example.options[example.label])
    print(json.dumps(answer(logits[0], example.options, temperature=temperature), indent=2))
    print("\nCausal mask/cache experiment (a separate random backbone):")
    print(json.dumps(isolation_demo()[0], indent=2))


if __name__ == "__main__":
    main()
