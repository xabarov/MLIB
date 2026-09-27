"""Turn a predicted distribution into values with ordinary Python.

This small teaching interface is intentionally not a Jev wire-protocol adapter.
Concentration describes distribution shape; it is not a probability of correctness.
"""

import math

import torch
from calibration import probabilities


def answer(logits, options, kind="choice", temperature=1.0):
    if logits.ndim != 1 or len(options) != logits.numel() or not options:
        raise ValueError("Need one logit per nonempty option list")
    if len(set(options)) != len(options) or not torch.isfinite(logits).all():
        raise ValueError("Options must be distinct and all supplied logits finite")
    p = probabilities(logits.detach().cpu(), temperature)
    distribution = dict(zip(options, p.tolist()))
    if kind == "noul":
        if options != ["false", "true"]:
            raise ValueError("noul uses options ['false', 'true'] in that order")
        return {"type": kind, "noul": float(p[1]), "probabilities": distribution}
    if kind not in {"choice", "score"}:
        raise ValueError("Unknown question type")
    entropy = float(-(p * p.clamp_min(1e-12).log()).sum())
    concentration = 1.0 if len(options) == 1 else 1.0 - entropy / math.log(len(options))
    value = (
        options[int(p.argmax())] if kind == "choice" else float(p @ torch.arange(len(p)).float())
    )
    return {
        "type": kind,
        kind: value,
        "probabilities": distribution,
        "concentration": max(0.0, min(1.0, concentration)),
    }
