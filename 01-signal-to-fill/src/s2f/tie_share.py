"""How often the taker tie rule can matter at all.

The tie flip only changes an outcome when t + d lands exactly on a book stamp. Decision times are
drawn in microseconds and book stamps are whole milliseconds, so this is rare by construction.
Writes results/taker/tie_share_dev_<day>.json.
"""
import json
import sys
import numpy as np

from .paths import ROOT
from .replay import load_day
from .taker import make_decisions, DELAYS_MS


def tie_share(book_ts, t):
    hits = []
    for d in DELAYS_MS:
        ta = t + int(d) * 1000
        lo = np.searchsorted(book_ts, ta, "left")
        hi = np.searchsorted(book_ts, ta, "right")
        hits.append(hi > lo)
    return np.array(hits).T          # decisions x delays, True where arrival sits on a book stamp


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    book, _ = load_day(day)
    t, side, _ = make_decisions(book)
    H = tie_share(book.ts, t)
    res = dict(n_decisions=int(len(t)),
               share_decision_delay_pairs_on_a_stamp=float(H.mean()),
               n_decisions_on_a_stamp_at_any_delay=int(H.any(1).sum()),
               share_decisions_on_a_stamp_at_any_delay=float(H.any(1).mean()),
               share_by_delay_ms={int(d): float(H[:, j].mean()) for j, d in enumerate(DELAYS_MS)},
               share_decision_times_whole_ms=float((t % 1000 == 0).mean()))
    out = ROOT / "results" / "taker"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"tie_share_dev_{day}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
