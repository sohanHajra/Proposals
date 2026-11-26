"""Gathers the exploratory follow ups over the twelve test days. Neither feeds the verdict."""
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



def fee_split():
    """How much of the 1 to 500 ms C2 change with fees is fees and how much is prices. Reads the
    stored c2 results of the twelve test days, nothing is rerun. An accounting split of the kept orders."""
    from .days import TEST_DAYS
    out = dict(days=0)
    per = {q: [] for q in ("front", "random", "back")}
    for d in TEST_DAYS:
        f = RESULTS / "test" / f"cryptostruct_BTCUSDT_{d}" / "c2.json"
        if not f.exists():
            continue
        c = json.load(open(f))["C2"]
        out["days"] += 1
        for q in per:
            p, w = c["primary"][q]["cost_by_delay"], c["fees"][q]["cost_by_delay"]
            price = p["500"] - p["1"]
            total = w["500"] - w["1"]
            per[q].append(dict(day=d, price=price, fee=total - price, total=total,
                               fee_share=(total - price) / total if total > 0 else None))
    for q, rows in per.items():
        sh = [r["fee_share"] for r in rows if r["fee_share"] is not None]
        out[q] = dict(price=[min(r["price"] for r in rows), max(r["price"] for r in rows)],
                      fee=[min(r["fee"] for r in rows), max(r["fee"] for r in rows)],
                      total=[min(r["total"] for r in rows), max(r["total"] for r in rows)],
                      fee_share_pct=[round(100 * min(sh)), round(100 * max(sh))],
                      total_not_above_zero=sum(r["total"] <= 0 for r in rows), by_day=rows)
    p = RESULTS / "exploratory" / "c2_fee_split" / "summary_BTCUSDT.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main()
    fee_split()
