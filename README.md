<div align="center">

# Proposals

**Research questions, each taken from a one page proposal to running code.**
Hypotheses are written down before results. Dead ends stay in the log. Null results get published.

*Sohan Hajra · UIUC B.S. Mathematics & Computer Science · [sohanhajra.github.io](https://sohanhajra.github.io)*

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
| 01 | [From Signal to Fill](01-signal-to-fill/) | When market conditions are the same, does extra delay between decision and order outcome cost price or fills? | 🟡 In progress, data audited | No result yet |

<details>
<summary><b>01 · From Signal to Fill</b> · what I believed, what I tried, what broke, what I believe now</summary>

**What I believed.** Latency costs takers through price drift and costs makers through lost queue position.

**What I tried.** Turned the proposal into two arms: replaying the *same* decision moment at controlled delays on public Binance BTCUSDT data, and real order lifecycles from Nasdaq LOBSTER samples.

**What broke.** LOBSTER's main site serves an HTML shell where sample zips used to be. A 2025 live-trading study on Binance and Bybit turned out to be close to my first research question, so I narrowed what I claim is new.

**What I believe now.** Measured: BTCUSDT's spread is one tick on 95.5% of book updates on the dev day. Hypothesis, not yet tested: that makes queue position, and so the passive side, where delay should cost most. Full history in the [lab notebook](01-signal-to-fill/LAB_NOTEBOOK.md).

</details>

## Rules this repo holds itself to
- Every number comes from code in the repo, rerunnable with `make reproduce` (pinned environment, fixed seeds).
- Test data stays locked until the preregistration is committed; the download script refuses otherwise.
- Out of sample checks, trading costs and alternative specifications before any claim.
- A proposal that isn't good enough ships late rather than thin.
- Each proposal keeps an [integrity log](01-signal-to-fill/INTEGRITY_LOG.md). Logic, sources and bias are checked after every work session, with what was found and fixed.
