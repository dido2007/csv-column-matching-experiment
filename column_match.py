"""Small, deterministic experiment in one-to-one CSV column matching.

This is independent toy code, not OneSchema code or a benchmark of its product.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


TARGETS = (
    "contact_email", "billing_email", "order_date", "ship_date",
    "amount_usd", "tax_usd", "customer_id", "postal_code",
)
GENERIC_PAIRS = (
    ("contact_email", "billing_email", "email"),
    ("order_date", "ship_date", "date"),
    ("amount_usd", "tax_usd", "usd"),
)


@dataclass(frozen=True)
class Column:
    header: str
    truth: str


def score(header: str, target: str) -> float:
    """A deliberately simple header score; generic labels are ambiguous."""
    h, t = header.lower().replace(" ", "_"), target.lower()
    if h == t:
        return 1.0
    if h in t.split("_"):
        return 0.55
    hs, ts = set(h.split("_")), set(t.split("_"))
    return 0.25 * len(hs & ts) / len(hs | ts)


def workloads(n: int = 120) -> list[list[Column]]:
    result = []
    for i in range(n):
        cols = []
        for p, (specific, generic_truth, generic_label) in enumerate(GENERIC_PAIRS):
            if (i + p) % 8 == 1:
                # Duplicate headers contain no information about which is which.
                pair = (specific, generic_truth)
                if (i // 8) % 2:
                    pair = pair[::-1]
                cols.extend(Column(generic_label, truth) for truth in pair)
            elif (i + p) % 4 == 0:
                # A generic column arrives first, followed by an exact clue.
                cols.extend((Column(generic_label, generic_truth), Column(specific, specific)))
            else:
                cols.extend((Column(specific, specific), Column(generic_truth, generic_truth)))
        cols.extend((Column("customer_id", "customer_id"), Column("postal_code", "postal_code")))
        result.append(cols)
    return result


def greedy(columns: list[Column]) -> list[int]:
    unused = set(range(len(TARGETS)))
    chosen = []
    for col in columns:
        j = max(unused, key=lambda k: (score(col.header, TARGETS[k]), -k))
        chosen.append(j)
        unused.remove(j)
    return chosen


def global_match(columns: list[Column]) -> list[int]:
    n = len(columns)

    @lru_cache(None)
    def solve(i: int, used: int) -> tuple[float, tuple[int, ...]]:
        if i == n:
            return 0.0, ()
        options = []
        for j in range(n):
            if not used & (1 << j):
                later, tail = solve(i + 1, used | (1 << j))
                options.append((score(columns[i].header, TARGETS[j]) + later, (j,) + tail))
        return max(options, key=lambda item: (item[0], tuple(-x for x in item[1])))

    return list(solve(0, 0)[1])


def metrics() -> dict[str, float]:
    cases = workloads()
    total = sum(map(len, cases))
    greedy_ok = global_ok = auto_ok = auto_n = 0
    for cols in cases:
        g, m = greedy(cols), global_match(cols)
        greedy_ok += sum(TARGETS[j] == c.truth for c, j in zip(cols, g))
        global_ok += sum(TARGETS[j] == c.truth for c, j in zip(cols, m))
        for c, j in zip(cols, m):
            if score(c.header, TARGETS[j]) >= 0.70:
                auto_n += 1
                auto_ok += TARGETS[j] == c.truth
    return {
        "imports": len(cases), "columns": total,
        "greedy_accuracy": greedy_ok / total,
        "global_accuracy": global_ok / total,
        "review_coverage": auto_n / total,
        "review_accuracy": auto_ok / auto_n,
        "sent_to_review": total - auto_n,
    }


if __name__ == "__main__":
    for name, value in metrics().items():
        print(f"{name}: {value:.3f}" if isinstance(value, float) else f"{name}: {value}")
