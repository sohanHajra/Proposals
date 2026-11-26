"""Gathers the exploratory c2_lose_race step over the twelve test days. Doesn't feed the verdict."""
import glob
import json

from .paths import RESULTS


def main():
    rows = [json.load(open(f)) for f in sorted(glob.glob(str(RESULTS / "exploratory" / "c2_lose_race" / "cryptostruct_BTCUSDT_*.json")))]
    rows = [r for r in rows if r["role"] == "test"]
    out = dict(days=len(rows), other_cells_unchanged_all=all(r["other_cells_unchanged"] for r in rows),
               marketable_pct_1ms=[round(100 * min(r["marketable_share_by_delay"]["1"] for r in rows), 2),
                                   round(100 * max(r["marketable_share_by_delay"]["1"] for r in rows), 2)],
               marketable_pct_500ms=[round(100 * min(r["marketable_share_by_delay"]["500"] for r in rows), 1),
                                     round(100 * max(r["marketable_share_by_delay"]["500"] for r in rows), 1)])
    for q in ("front", "random", "back"):
        s = [r[q]["slope_bps_per_logms"] for r in rows]
        ch = [r[q]["cost_by_delay"]["500"] - r[q]["cost_by_delay"]["1"] for r in rows]
        out[q] = dict(above=sum(x["ci95"][0] > 0 for x in s), below=sum(x["ci95"][1] < 0 for x in s),
                      covers=sum(x["ci95"][0] <= 0 <= x["ci95"][1] for x in s),
                      slope=[min(x["est"] for x in s), max(x["est"] for x in s)], change_1_to_500=[min(ch), max(ch)])
    p = RESULTS / "exploratory" / "c2_lose_race" / "summary_BTCUSDT.json"
    p.write_text(json.dumps(out, indent=1))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
