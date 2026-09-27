"""A tiny, fully inspectable task: select the queried person's colour.

No downloads or language knowledge: 625 possible states (5 colours ** 4 people).
Train/calibration/test have disjoint states, but share vocabulary and task rules.
"""

import random
from dataclasses import dataclass

import torch

WORDS = [
    "[PAD]",
    "[STATE]",
    "[SEP]",
    "[Q]",
    "[OPT]",
    "[/OPT]",
    "[DECIDE]",
    "A",
    "B",
    "C",
    "D",
    "E",
    "alice",
    "bob",
    "carol",
    "dave",
    "red",
    "green",
    "blue",
    "amber",
    "violet",
]
VOCAB = {word: index for index, word in enumerate(WORDS)}
PEOPLE, COLOURS = WORDS[12:16], WORDS[16:21]
CODES = [VOCAB[c] for c in "ABCDE"]
PAD = VOCAB["[PAD]"]


@dataclass
class Example:
    """An example of the decision task, with a state and a question about one person."""
    tokens: list[int]
    starts: list[int]
    ends: list[int]
    label: int
    state_length: int
    options: list[str]
    person: str


def split_states(seed=42):
    """
    Split the 625 possible states into train, calibration, and test sets.
    The split is deterministic given the seed."""
    states = list(range(len(COLOURS) ** len(PEOPLE)))
    random.Random(seed).shuffle(states)
    return {"train": states[:400], "calibration": states[400:500], "test": states[500:]}


def make_example(state_id, rng, n_options=None):
    """
    Create a single example of the decision task, given a state_id and a random number generator.
    The state_id must be in [0, 625), and the random number generator is used to select the person and the options.
    The number of options can be specified, or randomly chosen between 2 and 5 if not specified.
    """
    if not 0 <= state_id < 625:
        raise ValueError("state_id must be in [0, 625)")
    colours = [COLOURS[(state_id // (5**i)) % 5] for i in range(4)]
    person = rng.choice(PEOPLE)
    answer = colours[PEOPLE.index(person)]
    k = rng.randint(2, 5) if n_options is None else n_options
    if not 2 <= k <= 5:
        raise ValueError("The teaching vocabulary supports 2–5 options")
    options = [answer, *rng.sample([c for c in COLOURS if c != answer], k - 1)]
    rng.shuffle(options)  # Label index changes even when the semantic answer is unchanged.
    # A state's serialization is stable across questions, and varies across states.
    order = random.Random(state_id + 991).sample(range(4), 4)
    words = ["[STATE]"]
    for i in order:
        words.extend([PEOPLE[i], colours[i]])
    words.append("[SEP]")
    state_length = len(words)
    words.extend(["[Q]", person])
    starts, ends = [], []
    for i, option in enumerate(options):
        starts.append(len(words))
        words.extend(["[OPT]", "ABCDE"[i], option, "[/OPT]"])
        ends.append(len(words) - 1)
    words.append("[DECIDE]")
    return Example(
        [VOCAB[w] for w in words],
        starts,
        ends,
        options.index(answer),
        state_length,
        options,
        person,
    )


def make_dataset(states, count, seed):
    """
    Create a dataset of examples, given a list of states, a count of examples to generate, and a random seed.
    The dataset is a list of Example objects, each with a state and a question about one person.
    """
    rng = random.Random(seed)
    return [make_example(rng.choice(states), rng) for _ in range(count)]


def collate(examples, device="cpu"):
    """
    Collate a batch of examples into a dictionary of tensors, suitable for input to a model.
    The batch is a dictionary with the following keys:
        - "tokens": a tensor of shape (batch_size, max_seq_length) containing the token ids of the examples.
        - "starts": a tensor of shape (batch_size, max_num_options) containing the start indices of the options in the token sequence.
        - "ends": a tensor of shape (batch_size, max_num_options) containing the end indices of the options in the token sequence.
        - "decision": a tensor of shape (batch_size,) containing the index of the decision token in the token sequence.
        - "option_mask": a tensor of shape (batch_size, max_num_options) containing a boolean mask indicating which options are valid for each example.
        - "labels": a tensor of shape (batch_size,) containing the index of the correct option for each example.
    """
    if not examples:
        raise ValueError("Cannot collate an empty batch")
    b, t = len(examples), max(len(e.tokens) for e in examples)
    k = max(len(e.options) for e in examples)
    batch = {
        "tokens": torch.full((b, t), PAD, dtype=torch.long),
        "starts": torch.zeros(b, k, dtype=torch.long),
        "ends": torch.zeros(b, k, dtype=torch.long),
        "decision": torch.tensor([len(e.tokens) - 1 for e in examples]),
        "option_mask": torch.zeros(b, k, dtype=torch.bool),
        "labels": torch.tensor([e.label for e in examples]),
    }
    for i, example in enumerate(examples):
        n = len(example.options)
        batch["tokens"][i, : len(example.tokens)] = torch.tensor(example.tokens)
        batch["starts"][i, :n] = torch.tensor(example.starts)
        batch["ends"][i, :n] = torch.tensor(example.ends)
        batch["option_mask"][i, :n] = True
    return {name: value.to(device) for name, value in batch.items()}


def decode(ids):
    return " ".join(WORDS[i] for i in ids)


if __name__ == "__main__":
    # Example usage: generate a dataset and collate it into a batch.
    states = split_states()["train"]
    examples = make_dataset(states, count=5, seed=42)
    batch = collate(examples)
    for i in range(len(examples)):
        print(f"Example {i}:")
        print(f"  Tokens: {decode(batch['tokens'][i].tolist())}")
        print(f"  Starts: {batch['starts'][i].tolist()}")
        print(f"  Ends: {batch['ends'][i].tolist()}")
        print(f"  Decision index: {batch['decision'][i].item()}")
        print(f"  Option mask: {batch['option_mask'][i].tolist()}")
        print(f"  Label index: {batch['labels'][i].item()}")