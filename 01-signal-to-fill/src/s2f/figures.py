"""Figures for the final report, drawn only from results files that are already written.

Usage  python -m s2f.figures

Reads results/ and writes PNG files to figures/. Nothing here computes a new statistic. Every point,
line and interval is a field read straight from a results json, so a figure changes only if a results
file changes. There is no randomness in the drawing, the seed below is set anyway, and the PNG
metadata carries no software version or date, so the same results give the same bytes.

  fig1_cost_by_delay.png        mean top of book shortfall by delay, random and signal decisions, each day
  fig2_passive_by_rule.png      fill probability and fixed price post then cross cost by delay, each rule, each day
  fig3_eight_day_table.png      every statistic in the eight day table with its 95% interval, each day
  fig4_placebos.png             H1 and H2 slopes against their registered placebos on the two test days
  fig5_placebo_calibration.png  the 200 H2 placebo slopes on the dev day, with the registered draw marked
"""
import json
import re

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

from .paths import ROOT, RESULTS, DEV_DAY  # noqa: E402
from .get_data import TEST_DAYS, BREADTH_DAYS  # noqa: E402

SEED = 20261121
OUT = ROOT / "figures"
DELAYS = [1, 2, 5, 10, 25, 50, 100, 250, 500]
RULES = ("front", "random", "back")
DAYS = TEST_DAYS + BREADTH_DAYS
TEST_STYLE = {"2026-10-01": dict(color="#c0392b", lw=2.2, zorder=3),
              "2026-11-01": dict(color="#1f5fa8", lw=2.2, zorder=3)}
BREADTH_STYLE = dict(color="#9a9a9a", lw=1.0, zorder=2)
META = {"Software": None}


def _load(p):
    return json.loads((RESULTS / p).read_text())


def _style(day):
    return TEST_STYLE.get(day, BREADTH_STYLE)


def _by_delay(d):
    return [d[str(k)] for k in DELAYS]


def _legend_handles():
    from matplotlib.lines import Line2D
    return [Line2D([], [], **TEST_STYLE["2026-10-01"], label="test day 2026-10-01"),
            Line2D([], [], **TEST_STYLE["2026-11-01"], label="test day 2026-11-01"),
            Line2D([], [], **BREADTH_STYLE, label="six breadth days")]


def _save(fig, name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, dpi=150, metadata=META)
    plt.close(fig)
    print(f"wrote figures/{name}")


def fig1_cost_by_delay():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    for ax, key, title in ((axes[0], "random", "Random decisions (H1 sample)"),
                           (axes[1], "signal", "Signal decisions, book imbalance (secondary)")):
        for day in BREADTH_DAYS + TEST_DAYS:
            f = _load(f"taker/followups_{day}.json")[key]
            ax.plot(DELAYS, _by_delay(f["mean_S_by_delay_ms"]), marker="o", ms=3, **_style(day))
        ax.set_xscale("log")
        ax.set_xticks(DELAYS)
        ax.set_xticklabels([str(d) for d in DELAYS])
        ax.set_xlabel("injected delay (ms)")
        ax.set_ylabel("mean top of book shortfall (bps)")
        ax.set_title(title, fontsize=11)
        ax.grid(alpha=0.3)
    fig.legend(handles=_legend_handles(), fontsize=9, loc="outside lower center", ncol=3, frameon=False)
    fig.suptitle("Taker shortfall by delay, 0.01 BTC, each of the eight days (y axes differ)", fontsize=12)
    _save(fig, "fig1_cost_by_delay.png")


def fig2_passive_by_rule():
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.6), constrained_layout=True)
    for j, rule in enumerate(RULES):
        for day in BREADTH_DAYS + TEST_DAYS:
            p = _load(f"passive/passive_{day}.json")["primary"]["by_rule"][rule]
            fp = _load(f"passive/fixed_price_{day}.json")["random_decisions"]["by_rule"][rule]
            axes[0, j].plot(DELAYS, [100 * v for v in _by_delay(p["fill_prob_by_delay"])],
                            marker="o", ms=3, **_style(day))
            axes[1, j].plot(DELAYS, _by_delay(fp["post_then_cross_cost_by_delay"]), marker="o", ms=3, **_style(day))
        axes[0, j].set_title(f"{rule} cancellation rule", fontsize=11)
        for i in range(2):
            ax = axes[i, j]
            ax.set_xscale("log")
            ax.set_xticks(DELAYS)
            ax.set_xticklabels([str(d) for d in DELAYS], fontsize=8)
            ax.grid(alpha=0.3)
        axes[1, j].set_xlabel("injected delay (ms)")
    axes[0, 0].set_ylabel("fill probability within 10 s of arrival (%)\nrepricing order (H2)")
    axes[1, 0].set_ylabel("post then cross cost (bps)\nfixed price order (H5)")
    fig.legend(handles=_legend_handles(), fontsize=9, loc="outside lower center", ncol=3, frameon=False)
    fig.suptitle("Passive orders by delay under each queue rule, each of the eight days", fontsize=12)
    _save(fig, "fig2_passive_by_rule.png")


def fig3_eight_day_table():
    t = _load("breadth/breadth_table.json")["table"]
    names = ["H1", "H1b", "H3", "H2 front", "H2 random", "H2 back", "H2b",
             "H2c front", "H2c random", "H2c back", "H5 front", "H5 random", "H5 back"]
    units = {"H1": "bps per log ms", "H1b": "bps", "H3": "bps", "H2b": "fill share",
             "H2": "fill share per log ms", "H2c": "bps", "H5": "bps per log ms"}
    fig, axes = plt.subplots(5, 3, figsize=(12, 15), constrained_layout=True)
    axes = axes.ravel()
    y = np.arange(len(DAYS))[::-1]
    for ax, name in zip(axes, names):
        row = t[name]
        for yi, day in zip(y, DAYS):
            r = row["by_day"][day]
            lo, hi = r["ci95"]
            c = _style(day)["color"]
            ax.plot([lo, hi], [yi, yi], color=c, lw=2 if day in TEST_STYLE else 1.3)
            ax.plot(r["est"], yi, "o", color=c, ms=4)
        ax.axvline(0, color="black", lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(DAYS, fontsize=7)
        ax.tick_params(axis="x", labelsize=7)
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
        ax.xaxis.get_offset_text().set_fontsize(7)
        ax.margins(x=0.08)
        c = row["counts"]
        ax.set_title(f"{name}, registered side {row['registered_side']} zero\n"
                     f"{c['registered']} registered, {c['opposite']} opposite, {c['covers zero']} cover zero",
                     fontsize=9)
        ax.set_xlabel(units[name.split()[0]], fontsize=8)
        ax.grid(alpha=0.3, axis="x")
    for ax in axes[len(names):]:
        ax.axis("off")
    axes[len(names)].legend(handles=_legend_handles(), loc="center", fontsize=9, frameon=False)
    fig.suptitle("Eight day table, estimate and 95% block bootstrap interval for each day", fontsize=12)
    # the scale goes into the axis label instead of the small offset text in the corner,
    # which is easy to miss once GitHub shrinks the image. Tick values are unchanged.
    fig.canvas.draw()
    for ax, name in zip(axes, names):
        offset = ax.xaxis.get_major_formatter().get_offset()
        m = re.fullmatch(r"1e([\u2212-]?\d+)", offset)
        assert offset == "" or m, f"unexpected axis offset {offset!r} on {name}"
        ax.xaxis.get_offset_text().set_visible(False)
        if m:
            k = int(m.group(1).replace("\u2212", "-"))
            ax.set_xlabel(f"{units[name.split()[0]]}, $\\times 10^{{{k}}}$", fontsize=8)
    _save(fig, "fig3_eight_day_table.png")


def fig4_placebos():
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.8), constrained_layout=True)
    panels = [("H1 taker, five level walk", "bps per log ms"),
              ("H2 front", "fill share per log ms"),
              ("H2 random", "fill share per log ms"),
              ("H2 back", "fill share per log ms")]
    for k, (ax, (title, unit)) in enumerate(zip(axes, panels)):
        labels, rows = [], []
        for day in TEST_DAYS:
            if k == 0:
                tk = _load(f"taker/taker_{day}.json")
                real = tk["primary_five_level_walk"]["slope_bps_per_logms"]
                plac = tk["placebo_shuffled_five_level_walk"]["slope_bps_per_logms"]
            else:
                rule = RULES[k - 1]
                ph = _load(f"robustness/placebo_h2_{day}.json")["by_rule"][rule]
                real = ph["unshuffled_H2_slope_fill_per_logms"]
                plac = ph["placebo_H2_slope_fill_per_logms"]
            rows += [(real, TEST_STYLE[day]["color"], "o"), (plac, TEST_STYLE[day]["color"], "s")]
            labels += [f"{day} real", f"{day} placebo"]
        ys = np.arange(len(rows))[::-1]
        for yi, (s, c, m) in zip(ys, rows):
            ax.plot(s["ci95"], [yi, yi], color=c, lw=2)
            ax.plot(s["est"], yi, m, color=c, ms=6, mfc="white" if m == "s" else c)
        ax.axvline(0, color="black", lw=0.8)
        ax.set_yticks(ys)
        ax.set_yticklabels(labels if k == 0 else [], fontsize=8)
        ax.set_ylim(-0.6, len(rows) - 0.4)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel(unit, fontsize=8)
        ax.tick_params(axis="x", labelsize=7)
        ax.ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
        ax.xaxis.get_offset_text().set_fontsize(7)
        ax.grid(alpha=0.3, axis="x")
    fig.suptitle("Slopes on log delay against the registered placebo (delay labels shuffled), 95% intervals",
                 fontsize=11)
    _save(fig, "fig4_placebos.png")


def fig5_placebo_calibration():
    c = _load(f"robustness/placebo_h2_calibration_dev_{DEV_DAY}.json")
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), constrained_layout=True, sharey=True)
    for ax, rule in zip(axes, RULES):
        r = c["by_rule"][rule]
        slopes = np.array(r["slope"])
        excl = np.array(r["excludes_zero"], dtype=bool)
        bins = np.linspace(slopes.min(), slopes.max(), 25)
        ax.hist(slopes[~excl], bins=bins, color="#9a9a9a", label="interval covers zero")
        ax.hist(slopes[excl], bins=bins, color="#c0392b", label="interval excludes zero")
        ax.axvline(slopes[0], color="black", lw=1.5, ls="--", label="registered draw (k = 0)")
        ax.set_title(f"{rule}, {int(excl.sum())} of {len(slopes)} exclude zero", fontsize=10)
        ax.set_xlabel("placebo H2 slope (fill share per log ms)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
        ax.xaxis.get_offset_text().set_fontsize(7)
    axes[0].set_ylabel("shuffles")
    axes[0].legend(fontsize=7, loc="upper left")
    fig.suptitle(f"H2 placebo over 200 shuffles on the dev day {DEV_DAY} (exploratory)", fontsize=11)
    _save(fig, "fig5_placebo_calibration.png")


def main():
    np.random.seed(SEED)
    plt.rcParams.update({"font.size": 9, "svg.hashsalt": str(SEED)})
    fig1_cost_by_delay()
    fig2_passive_by_rule()
    fig3_eight_day_table()
    fig4_placebos()
    fig5_placebo_calibration()


if __name__ == "__main__":
    main()
