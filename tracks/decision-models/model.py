"""Three decision readouts over a small Transformer, with visible tensor shapes.

Original teaching code, inspired by the mechanisms of SemIf/Nimble, Kev and Laya.
This is NOT their released architecture or weights. All attention is written out
so masks, branch isolation and immutable KV caches can be inspected in a debugger.
"""

import math
from dataclasses import dataclass

import torch
from data import CODES, PAD, WORDS
from torch import nn
from torch.nn import functional as F


@dataclass
class Config:
    vocab_size: int = len(WORDS)
    width: int = 64
    heads: int = 4
    layers: int = 2
    max_length: int = 128


def attention_mask(tokens, causal):
    """True means allowed: [B, 1, query_position, key_position].

    Padded queries may read valid keys; their outputs are never used. Masking every
    key for a padded query would produce softmax(-inf, ..., -inf) = NaN.
    """
    b, t = tokens.shape
    valid_keys = (tokens != PAD)[:, None, None, :]
    allow = valid_keys.expand(b, 1, t, t)
    if causal:
        allow = allow & torch.ones(t, t, device=tokens.device, dtype=torch.bool).tril()
    return allow


def branch_mask(segments):
    """State = 0; questions = 1, 2, ... . Causal order inside each branch.

    State cannot read questions; a question can read state and its own earlier tokens.
    For exact packed/separate equivalence, restart position IDs after the state too.
    """
    t = segments.numel()
    causal = torch.ones(t, t, dtype=torch.bool, device=segments.device).tril()
    same_branch = segments[:, None] == segments[None, :]
    return (causal & (same_branch | (segments[None, :] == 0)))[None, None]


class Attention(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        if cfg.width % cfg.heads:
            raise ValueError("width must be divisible by heads")
        self.heads = cfg.heads
        self.qkv = nn.Linear(cfg.width, 3 * cfg.width)
        self.out = nn.Linear(cfg.width, cfg.width)

    def forward(self, x, allow, past=None):
        b, t, d = x.shape
        # [B,T,3D] -> three [B,H,T,D/H] tensors.
        q, k, v = self.qkv(x).reshape(b, t, 3, self.heads, d // self.heads).permute(2, 0, 3, 1, 4)
        if past is not None:
            # Concatenation does not modify the shared prefix cache.
            k = torch.cat([past[0], k], dim=2)
            v = torch.cat([past[1], v], dim=2)
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(d // self.heads)
        weights = scores.masked_fill(~allow, float("-inf")).softmax(dim=-1)
        result = (weights @ v).transpose(1, 2).contiguous().reshape(b, t, d)
        return self.out(result), (k, v), weights


class Block(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(cfg.width), nn.LayerNorm(cfg.width)
        self.attn = Attention(cfg)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.width, 4 * cfg.width), nn.GELU(), nn.Linear(4 * cfg.width, cfg.width)
        )

    def forward(self, x, allow, past=None):
        update, cache, weights = self.attn(self.ln1(x), allow, past)
        x = x + update
        return x + self.mlp(self.ln2(x)), cache, weights


class Transformer(nn.Module):
    def __init__(self, cfg, causal):
        super().__init__()
        self.cfg, self.causal = cfg, causal
        self.token_embedding = nn.Embedding(cfg.vocab_size, cfg.width)
        self.position_embedding = nn.Embedding(cfg.max_length, cfg.width)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.layers)])
        self.norm = nn.LayerNorm(cfg.width)

    def forward(self, tokens, allow=None, positions=None, past=None):
        """Return hidden [B,T,D], per-layer caches, per-layer attention maps.

        Cached calls are restricted to unpadded causal sequences in this teaching code.
        Full-sequence calls support padding; production branch batching is upstream work.
        """
        if tokens.ndim != 2 or tokens.size(1) == 0 or (tokens[:, 0] == PAD).any():
            raise ValueError("Expected nonempty [B,T] tokens with a non-padding first token")
        if past is not None and (not self.causal or len(past) != len(self.blocks)):
            raise ValueError("A cache must match every layer of a causal backbone")
        offset = 0 if past is None else past[0][0].size(2)
        t = tokens.size(1)
        if positions is None:
            positions = torch.arange(offset, offset + t, device=tokens.device)
        if positions.min() < 0 or positions.max() >= self.cfg.max_length:
            raise ValueError("Position IDs exceed max_length")
        if allow is None:
            if past is None:
                allow = attention_mask(tokens, self.causal)
            else:
                if (tokens == PAD).any():
                    raise ValueError("Cached suffixes must be unpadded in this minimal runtime")
                q = torch.arange(offset, offset + t, device=tokens.device)
                k = torch.arange(offset + t, device=tokens.device)
                allow = (k[None, :] <= q[:, None])[None, None]
        x = self.token_embedding(tokens) + self.position_embedding(positions)
        caches, maps = [], []
        for i, block in enumerate(self.blocks):
            x, cache, weights = block(x, allow, None if past is None else past[i])
            caches.append(cache)
            maps.append(weights)
        return self.norm(x), caches, maps


def gather_positions(hidden, positions):
    # [B,T,D], [B,K] -> [B,K,D]. Also supports K=1 for the decision position.
    return hidden.gather(1, positions[..., None].expand(-1, -1, hidden.size(-1)))


class TokenReadout(nn.Module):
    """SemIf/Nimble-like: project into the existing candidate-token rows of W_vocab."""

    def __init__(self, cfg):
        super().__init__()
        self.lm_head = nn.Linear(cfg.width, cfg.vocab_size, bias=False)
        self.register_buffer("code_ids", torch.tensor(CODES))

    def forward(self, hidden, batch):
        """Project the decision token into the candidate-token rows of W_vocab."""
        decision = gather_positions(hidden, batch["decision"][:, None]).squeeze(1)
        k = batch["option_mask"].size(1)
        # Equivalent to full-vocabulary logits followed by candidate indexing.
        return F.linear(decision, self.lm_head.weight[self.code_ids[:k]])


class PointerReadout(nn.Module):
    """Kev-like: compare the decision token with each option's closing marker."""

    def __init__(self, cfg):
        super().__init__()
        self.query = nn.Linear(cfg.width, cfg.width)
        self.key = nn.Linear(cfg.width, cfg.width)

    def forward(self, hidden, batch):
        """Score each option by dot-product with the decision token."""
        decision = gather_positions(hidden, batch["decision"][:, None])  # [B,1,D]
        options = gather_positions(hidden, batch["ends"])  # [B,K,D]
        return (self.query(decision) * self.key(options)).sum(-1) / math.sqrt(hidden.size(-1))


class MarkerReadout(nn.Module):
    """Laya-like: a shared MLP scores contextual option-start markers."""

    def __init__(self, cfg):
        super().__init__()
        self.scorer = nn.Sequential(
            nn.LayerNorm(cfg.width),
            nn.Linear(cfg.width, cfg.width),
            nn.GELU(),
            nn.Linear(cfg.width, 1),
        )

    def forward(self, hidden, batch):
        """Score each option by a shared MLP applied to its starting marker."""
        return self.scorer(gather_positions(hidden, batch["starts"])).squeeze(-1)


class DecisionModel(nn.Module):
    def __init__(self, kind="pointer", cfg=None):
        super().__init__()
        self.cfg = cfg or Config()
        self.kind = kind
        heads = {"token": TokenReadout, "pointer": PointerReadout, "marker": MarkerReadout}
        if kind not in heads:
            raise ValueError(f"Choose a readout from {tuple(heads)}")
        self.backbone = Transformer(self.cfg, causal=(kind != "marker"))
        # The readout is initialized from scratch, not pretrained. The backbone is also initialized from scratch.
        self.readout = heads[kind](self.cfg)
        # Use PyTorch's default initialization; no pretrained parameters are loaded.

    def forward(self, batch):
        hidden, _, _ = self.backbone(batch["tokens"])
        logits = self.readout(hidden, batch)
        return logits.masked_fill(~batch["option_mask"], float("-inf"))
