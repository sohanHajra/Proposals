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

## 2026-11-23, later · full reread before any test data
A separate reread of 01.b against my review checklist, done before any test day was copied in. It found one thing that has to be fixed first and seventeen smaller ones. Nothing here has been fixed yet unless it says so.

**Must fix before any test day**
- The preregistration says a data script refuses to fetch a listed day until the preregistration is in git. There's no such script. Files come from my Drive by hand, and the checksums of the twelve bought test days aren't in the repo.

**Open**
- The C2 placebo interval already sits above zero on the build day for Bybit under all three rules and for CryptoStruct under back. Every day and rule also reuses the same shuffle, since the seed is fixed. How a test day placebo miss is read needs writing down before any test result exists.
- The 99% loader rule was set after the CryptoStruct trade count was known, and 01 had published Tardis's, so the count gap (0.56%<!--nc-->) was knowable when I chose 99%.
- The Bybit reader changed on the build day after its first run, and on Bybit the gap rule runs on send time. That isn't under Deviations yet.
- The C1 fee check adds a flat 5 bps, which cancels out of ΔS, so it can't change the slope.
- The race rule is a sensitivity, not a bound, and the write up has to call it that.
- The count of surviving days for the verdict isn't coded yet, and neither is leaving out a day whose download fails.
- The converters can open a test day outside the runner.
- The 01 shortfall range quoted in the preregistration is top of book, not the walk.
- Smaller wording fixes in the notebook, README and MANIFEST, and claimcheck's guard knows only the twelve primary dates.

**Found and fixed**
- Bybit's threshold. The frozen Binance value picked far fewer moments on Bybit than on Binance, so Bybit now gets its own 90th percentile from 2026-09-01, like ETHUSDT. This came after I had seen Bybit's build day results under the frozen value, and the Deviation says so. It was pushed before Bybit's value was computed, and the frozen version runs next to it on every Bybit test day.

**Checked, no issue**
- The registered text is unchanged since b81f5f6, and every Deviation went in before the data it governs.
- The 01 code is unchanged from its tag, and the runner matches the preregistration.
- The ETHUSDT threshold was recomputed from the raw file and matches the stored value exactly.
- No test day file is anywhere in the project, and nothing derived from the free samples exists.
- Every raw file in the manifest matches its checksum.

## 2026-11-23, afternoon · acting on the reread
**Found and fixed**
- The missing fetch guard. The MD5 and size of all twelve bought test files are committed, the runner checks each file against them, and the converters and loader refuse a test day outside the runner. Written under Deviations first.
- A day whose file fails can now be left out through the runner, and it then counts for the ETHUSDT wait.
- The verdict count is code with tests.
- The Bybit reader change and its gap rule on Bybit's own message time are now under Deviations.
- How a C2 placebo miss is read was fixed under Deviations, then the 200<!--c:cal.n--> shuffle check was run once per source on the build day. It fails the cut on CryptoStruct back and on every Bybit rule.
- The C1 fee line, the race rule wording, the quoted 01 range, the loader rule timing, the burst note, the gap rule share, the memory figure, the README status, the MANIFEST wording and claimcheck's list of days are all fixed or said plainly.

**Open**
- The placebo can't back up C2 under back on CryptoStruct or on Bybit. The block interval may run a little narrow there, which would also make C2's own intervals under back slightly easier to clear. Reported with the results, method unchanged.
- The copy from Drive is still by hand. The MD5 check catches a wrong file, not an early look.

**Checked, no issue**
- The first of the 200<!--c:cal.n--> shuffles gives back the registered placebo exactly on all four sources and rules.
- 25 tests pass and claimcheck agrees. No test day file is in the project.

## 2026-11-24 · secondary days and the write up
**Found and fixed**
- The README said C1 "holds" on the secondary days. Holds is verdict language and those days aren't in a verdict, so it now says C1 shows up on every secondary day.
- "C2 never turns negative" was looser than what was checked. It now says no C2 slope estimate is below zero.

**Open**
- The two read errors during the secondary runs are a guess at the disk, not checked.
- C2 under back still leans on intervals that are probably a little narrow.

**Checked, no issue**
- Every number in the README and the new notebook entry is tagged and matches its results file.
- The secondary tally and the test day checks summary use the same per day rules as the verdict code, and neither feeds the verdict.
- Every secondary day ran through the runner on its registered list. Nothing was left out by the gap rule.
