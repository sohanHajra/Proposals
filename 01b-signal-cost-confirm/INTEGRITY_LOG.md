# Integrity log, 01.b

After each work session I check three things and write down what I found.
1. **Logic:** Does every conclusion follow from what was actually run?
2. **Sources:** Does every number match its results file, and is every source described as deeply as I actually read it?
3. **Bias:** Did anything get chosen or changed after I saw an outcome?

## 2026-11-23 · build day
**Found and fixed**
- The first Bybit reader wrote top of book rows only on a change, so quiet stretches counted as feed gaps (1760<!--c:build.bybit.old.gap--> s on the build day) and decisions near them were dropped. Fixed before any Bybit test day was fetched. The first run is kept in results/build/old rather than deleted.
- The CryptoStruct build day needed about 4.3 GB<!--nc--> of memory, which a busier test day would not fit. The reader now loads one column at a time. A slow test checks it gives byte identical arrays to the old way.
- The preregistration said Bybit ob500. The files for every test day are ob200. Logged under Deviations before any Bybit test day was fetched.
- A first draft of the notebook said Binance's top of book stream skips updates, as the reason the two vendors' top of book rows differ. I hadn't checked that, so it now says it's a guess.

**Open**
- The full review after the preregistration and before any test data (a separate reread against my review checklist) has not been done. It has to happen before any test day is opened.
- The agreement rule for the loader (99% each way) was set by me on the build day, after looking at the file format and converting it, but before any comparison was run (commit 721f97f came before the comparison). It was not in the original preregistration.
- Bybit uses the frozen BTCUSDT threshold because the text freezes it for the symbol. A venue with different top of book sizes might deserve its own threshold. I read the text literally and wrote that reading down. Bybit is secondary either way.
- The ETHUSDT size rule (median mids) is my choice of how to read "the same notional", fixed before it was computed.
- The race rule can make a fill better as well as worse, since it takes the book 1 ms later. It is a sensitivity, not a pessimistic bound in every cell.
- Tardis is missing three short bursts of trades on the 01 dev day. 01's results on that day may move a little with the full feed. Not measured.

**Checked, no issue**
- The 01.b chain on Tardis BTCUSDT 2026-09-01 reproduces 01's dev day C1 and C2 numbers exactly, and its loader matches 01's loader array for array.
- No test day file is in the project. The runner refuses any day outside the list, and claimcheck finds no test day results.
- Every number in today's notebook entry is tagged to a results file, and claimcheck agrees.
- The 01 code is unchanged from tag `v0.1-signal-to-fill`.
