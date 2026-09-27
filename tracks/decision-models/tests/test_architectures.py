"""Architectural invariants: masks, readouts, learning and calibration separation."""

import random
import sys
import unittest
from pathlib import Path

import torch
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from calibration import fit_temperature, metrics, rlcd_loss  # noqa: E402
from data import CODES, collate, make_dataset, make_example, split_states  # noqa: E402
from inspect_model import isolation_demo  # noqa: E402
from model import Config, DecisionModel, gather_positions  # noqa: E402
from typed import answer  # noqa: E402


class ArchitectureTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(17)
        self.cfg = Config(width=32, heads=4, layers=2)
        self.examples = [
            make_example(73, random.Random(2), 2),
            make_example(301, random.Random(9), 5),
        ]

    def test_padding_does_not_change_a_decision(self):
        for kind in ["token", "pointer", "marker"]:
            with self.subTest(kind=kind), torch.no_grad():
                model = DecisionModel(kind, self.cfg).eval()
                batched = model(collate(self.examples))
                separate = model(collate(self.examples[:1]))
                torch.testing.assert_close(batched[0, :2], separate[0], atol=1e-5, rtol=1e-5)
                self.assertTrue(torch.isneginf(batched[0, 2:]).all())
                torch.testing.assert_close(batched.softmax(-1).sum(-1), torch.ones(2))

    def test_candidate_only_projection_matches_full_lm_head(self):
        model = DecisionModel("token", self.cfg)
        batch = collate(self.examples)
        hidden, _, _ = model.backbone(batch["tokens"])
        h = gather_positions(hidden, batch["decision"][:, None]).squeeze(1)
        expected = model.readout.lm_head(h)[:, CODES]
        torch.testing.assert_close(model.readout(hidden, batch), expected)

    def test_causal_and_bidirectional_have_different_information_paths(self):
        tokens = collate(self.examples[:1])["tokens"]
        edited = tokens.clone()
        edited[0, -2] = 16  # Change a token strictly AFTER the option-start marker.
        pos = self.examples[0].starts[0]
        for kind in ["pointer", "marker"]:
            backbone = DecisionModel(kind, self.cfg).backbone.eval()
            a = backbone(tokens)[0][0, pos]
            b = backbone(edited)[0][0, pos]
            if kind == "pointer":
                torch.testing.assert_close(a, b)
            else:
                self.assertGreater(float((a - b).abs().max().detach()), 1e-4)

    def test_branch_isolation_cache_and_position_reset(self):
        report = isolation_demo()[0]
        for key in [
            "packed_vs_separate_q1",
            "packed_vs_separate_q2",
            "cached_vs_full_q1",
            "cached_vs_full_q2",
            "q1_change_after_editing_q2",
            "q2_change_after_editing_q1",
        ]:
            self.assertLess(report[key], 2e-5, key)
        self.assertTrue(report["prefix_unchanged"])
        self.assertGreater(report["q2_error_without_position_reset"], 0.01)

    def test_all_heads_can_learn_and_have_finite_gradients(self):
        batch = collate(make_dataset(split_states()["train"], 8, seed=17))
        for kind in ["token", "pointer", "marker"]:
            with self.subTest(kind=kind):
                torch.manual_seed(17)
                model = DecisionModel(kind, self.cfg)
                optimizer = torch.optim.AdamW(model.parameters(), lr=0.003)
                initial = float(F.cross_entropy(model(batch), batch["labels"]).detach())
                for _ in range(50):
                    loss = F.cross_entropy(model(batch), batch["labels"])
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                final = float(F.cross_entropy(model(batch), batch["labels"]).detach())
                self.assertLess(final, initial * 0.3)
                self.assertTrue(
                    all(
                        torch.isfinite(p.grad).all()
                        for p in model.parameters()
                        if p.grad is not None
                    )
                )

    def test_rlcd_handles_padding_and_updates_logits_without_ce(self):
        z = torch.tensor([[0.1, 0.2, 0.0], [0.3, 0.1, -0.1]], requires_grad=True)
        mask = torch.tensor([[True, True, False], [True, True, True]])
        logits = z.masked_fill(~mask, float("-inf"))
        loss = rlcd_loss(logits, torch.tensor([0, 2]), mask, group_size=128, ce_weight=0.0)
        loss.backward()
        self.assertTrue(torch.isfinite(z.grad).all())
        self.assertEqual(float(z.grad[0, 2]), 0.0)
        self.assertLess(float(z.grad[0, 0]), 0.0)  # Gradient descent raises the target logit.
        self.assertLess(float(z.grad[1, 2]), 0.0)

    def test_splits_are_disjoint_states(self):
        split = split_states()
        self.assertEqual(len(set.union(*(set(s) for s in split.values()))), 625)
        self.assertEqual(sum(map(len, split.values())), 625)
        rng = random.Random(2)
        labels = {make_example(73, rng, 3).label for _ in range(30)}
        self.assertEqual(labels, {0, 1, 2})

    def test_temperature_changes_probabilities_but_not_argmax(self):
        logits = torch.tensor([[8.0, 0.0], [8.0, 0.0], [8.0, 0.0], [0.0, 8.0]])
        labels = torch.tensor([0, 0, 1, 1])
        t = fit_temperature(logits, labels)
        before, after = metrics(logits, labels), metrics(logits, labels, t)
        self.assertEqual(before["accuracy"], after["accuracy"])
        self.assertLess(after["nll"], before["nll"])
        self.assertEqual(sum(b["count"] for b in after["bins"]), 4)
        self.assertNotAlmostEqual(
            float(logits.softmax(-1)[0, 0]), float((logits / t).softmax(-1)[0, 0])
        )

    @unittest.skipUnless(torch.backends.mps.is_available(), "Requires Apple MPS")
    def test_temperature_and_metrics_accept_mps_logits(self):
        logits = torch.tensor([[8.0, 0.0], [8.0, 0.0], [8.0, 0.0], [0.0, 8.0]], device="mps")
        labels = torch.tensor([0, 0, 1, 1], device="mps")
        temperature = fit_temperature(logits, labels)
        before = metrics(logits, labels)
        after = metrics(logits, labels, temperature)
        self.assertEqual(before["accuracy"], after["accuracy"])
        self.assertLess(after["nll"], before["nll"])
        self.assertEqual(sum(b["count"] for b in after["bins"]), 4)

    def test_typed_answers_are_python_readouts(self):
        result = answer(torch.tensor([0.2, 0.3, 0.5]).log(), ["low", "mid", "high"], "score")
        self.assertAlmostEqual(result["score"], 1.3, places=6)
        boolean = answer(torch.tensor([0.0, 0.0]), ["false", "true"], "noul")
        self.assertEqual(boolean["noul"], 0.5)
        uniform = answer(torch.zeros(3), ["a", "b", "c"])
        self.assertAlmostEqual(uniform["concentration"], 0.0, places=6)
        with self.assertRaises(ValueError):
            answer(torch.zeros(2), ["yes", "no"], "noul")


if __name__ == "__main__":
    unittest.main()
