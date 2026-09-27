"""Temperature scaling, proper losses and reliability bins, without a trainer framework."""

import math

import torch
from torch.nn import functional as F


def probabilities(logits, temperature=1.0):
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be finite and positive")
    return (logits / temperature).softmax(-1)


@torch.no_grad()
def fit_temperature(logits, labels):
    """Minimize NLL on CALIBRATION data only; finite grid makes the example explicit."""
    # Build the tiny fixed grid on CPU; MPS does not implement logspace in PyTorch 2.14.
    candidates = torch.logspace(-1, 1, 121, device="cpu").to(logits.device)
    candidates = torch.cat([candidates, candidates.new_tensor([1.0])])
    losses = torch.stack([F.cross_entropy(logits / t, labels) for t in candidates])
    return float(candidates[losses.argmin()])


@torch.no_grad()
def metrics(logits, labels, temperature=1.0, bins=10):
    if bins < 1 or len(labels) == 0:
        raise ValueError("Need a nonempty sample and at least one bin")
    p = probabilities(logits, temperature)
    confidence, prediction = p.max(-1)
    correct = prediction.eq(labels)
    target = F.one_hot(labels, p.size(-1))
    # floor(p * bins), with p=1 included in the last bin.
    bucket = (confidence * bins).long().clamp(max=bins - 1)
    records, ece = [], 0.0
    for i in range(bins):
        selected = bucket == i
        count = int(selected.sum())
        avg_p = float(confidence[selected].mean()) if count else None
        accuracy = float(correct[selected].float().mean()) if count else None
        if count:
            ece += count / len(labels) * abs(avg_p - accuracy)
        records.append({"count": count, "confidence": avg_p, "accuracy": accuracy})
    return {
        "n": len(labels),
        "accuracy": float(correct.float().mean()),
        "nll": float(F.cross_entropy(logits / temperature, labels)),
        "brier": float(((p - target) ** 2).sum(-1).mean()),
        "ece": ece,
        "temperature": temperature,
        "bins": records,
    }


def proper_reward(p, target, ordinal=False):
    """Log + 0.5*spherical score; optionally subtract ranked probability score.

    An educational unclipped scoring rule. The upstream Laya version has additional
    masking, weights and log clipping. p can have leading exploration dimensions.
    """
    log_score = (target * p.clamp_min(1e-12).log()).sum(-1)
    spherical = (target * p).sum(-1) / p.norm(dim=-1).clamp_min(1e-12)
    reward = log_score + 0.5 * spherical
    if ordinal:
        reward = reward - ((p.cumsum(-1) - target.cumsum(-1)) ** 2).sum(-1) / (p.size(-1) - 1)
    return reward


def rlcd_loss(logits, labels, option_mask, group_size=8, sigma=0.3, ce_weight=1.0):
    """Laya-inspired Gaussian policy gradient + CE; not TypeSafe's private RLCD.

    The action is a noisy logit vector. It MUST be detached in log pi(action | z).
    Leave-one-out baseline is used here; Laya's notebook uses a group-mean baseline
    and advantage normalization. Exploration happens in training, not inference.
    """
    if group_size < 2 or sigma <= 0:
        raise ValueError("Need group_size >= 2 and sigma > 0")
    z = logits.masked_fill(~option_mask, 0.0)
    noise = torch.randn((group_size, *z.shape), device=z.device) * sigma * option_mask
    count = option_mask.sum(-1, keepdim=True)
    noise = (noise - noise.sum(-1, keepdim=True) / count) * option_mask
    actions = z.detach()[None] + noise
    reported = actions.masked_fill(~option_mask, float("-inf")).softmax(-1)
    target = F.one_hot(labels, z.size(-1)).float()
    with torch.no_grad():
        rewards = proper_reward(reported, target)
        baseline = (rewards.sum(0, keepdim=True) - rewards) / (group_size - 1)
        advantage = rewards - baseline
    log_policy = -(((actions - z[None]) ** 2) * option_mask).sum(-1) / (2 * sigma**2)
    return -(advantage * log_policy).mean() + ce_weight * F.cross_entropy(logits, labels)
