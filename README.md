<div align="center">

# Proposals

**Research questions, each taken from a one page proposal to running code.**
I write the hypotheses down before I look at any test results. Dead ends stay in the log, and a null result gets published like any other.

*Sohan Hajra · UIUC B.S. Mathematics & Computer Science · [sohanhajra.github.io](https://sohanhajra.github.io)*

[![claimcheck](https://github.com/sohanHajra/Proposals/actions/workflows/claimcheck.yml/badge.svg)](https://github.com/sohanHajra/Proposals/actions/workflows/claimcheck.yml)

</div>

## How each proposal is run

```mermaid
flowchart LR
    A[One page proposal] --> B[Literature review<br/>what published work already shows]
    B --> C[Preregistration<br/>hypotheses, metrics, pass/fail<br/>committed before test data]
    C --> D[Dev data<br/>build and debug]
    D --> E[Locked test data<br/>run once]
    E --> F{Result}
    F -->|holds out of sample| G[Finding<br/>plus what it does not prove]
    F -->|does not hold| H[Null result<br/>published as is]
    D -.dead ends, revisions.-> L[(Lab notebook)]
    E -.-> L
```

## The proposals

| # | Proposal | The question | Status | Headline |
|---|---|---|---|---|
| 01 | [From Signal to Fill](01-signal-to-fill/) | When market conditions are the same, does extra delay between decision and order outcome cost price or fills? | 🟢 Released 2026-11-22 | H1, H2 and H4 null, H1 and H2 by design. A taker acting on book imbalance loses roughly half to three quarters of a bp by 500 ms, an upper end |
| 01.b | [Signal Cost Confirm](01b-signal-cost-confirm/) | Do the two leads from 01 hold on twelve days I haven't seen, with the rules written first? | 🟡 Preregistered 2026-11-22 | Nothing run yet |

<details>
<summary><b>01 · From Signal to Fill</b> · what I believed, what I tried, what broke, what I believe now</summary>

**What I believed:** Latency costs takers through price drift and costs makers through lost queue position.

**What I tried:** I turned the proposal into two arms. One replays the *same* decision moment at controlled delays on public Binance BTCUSDT data, and the other reads real order lifecycles from Nasdaq LOBSTER samples.

**What broke:** LOBSTER's main site serves an HTML shell where sample zips used to be. A 2025 live trading study on Binance and Bybit turned out to be close to my first research question, so I narrowed what I claim is new.

**What I believe now:** I thought the passive side would be where delay costs most, since BTCUSDT's spread is one tick almost all the time and queue position should matter. On random decisions neither side shows a cost, but that test couldn't show one by design, so it doesn't settle the question. The cost that does show up is a taker acting on book imbalance, roughly half to three quarters of a bp by 500 ms on every day I ran, and that is an upper end because my replay has no race for the touch. The [report](01-signal-to-fill/FINAL_REPORT.md) has the numbers and the full history is in the [lab notebook](01-signal-to-fill/LAB_NOTEBOOK.md).

</details>

## Rules I hold this repo to
- Every number comes from code in the repo, with a pinned environment and fixed seeds. `make reproduce` reruns the dev day work. Locked test days rerun one at a time with their own command, as each proposal's README explains, and a live measurement like a broker latency can't be rerun.
- Test data stays locked until the preregistration is committed. The download script refuses to fetch it before then.
- No claim before out of sample checks, trading costs and a few alternative specifications.
- A proposal that isn't good enough ships late rather than thin.
- Every result number in a proposal's notes carries a hidden tag that points to the field in the results file it came from. [claimcheck](claimcheck/) rereads those files and fails when a number in the prose and the file disagree. It also checks that every source says how deeply I read it and that the preregistration was committed before any test day result. Run it with `make verify` in a proposal folder. It also runs on every push, and the badge at the top shows the last result. It can't tell whether a result is right, only that the notes report what the code wrote. Every new proposal uses it from the start, following [this guide](claimcheck/ADOPTING.md).
- Each proposal keeps an [integrity log](01-signal-to-fill/INTEGRITY_LOG.md). When I finish a piece of work I go back over the logic, the sources and any bias, and write down what I found and what I fixed.
