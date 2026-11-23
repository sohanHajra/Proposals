# Lab notebook, 01.b

## 2026-11-22

Wrote the preregistration and committed it before downloading or opening any 01.b day. It names twelve mid month Wednesdays as test days, one per month from December 2025 to November 2026. June 17 is swapped for June 18 because the seller shows a notice that most of that day's files start late. There are two primary checks. C1 asks whether signal decisions keep paying for delay. C2 asks whether the fixed price passive slope stays above zero once marketable orders are left out. Each needs 10 of 12 days. The numbers from 01 that it quotes are tagged back to 01's results files.

I added two things that weren't in my first draft. Every data file gets a checksum in a manifest when it lands. The CryptoStruct and Tardis files for 2026-09-01 are compared before I build anything on the new loader.

Next is buying the twelve test days and the 2026-09-01 file, copying in the two free samples, and building the runner, the loader and the race sensitivity on 2026-09-01.

### Limits and gaps

Nothing run yet. If the purchase falls through, the test set falls back to free first of month days, which are weaker since four of them are weekends.

## 2026-11-22, later
Copied in the free samples for 2026-07-06 and 2026-11-13. Both MD5s matched the Drive listing, and the SHA256s are in data/MANIFEST.md. I also decided to use the free 2026-11-14 and 2026-11-15 days, and logged that under Deviations before opening anything. They're secondary, reported alone, like 2026-11-13.

Limits and gaps. Three of the recent free days sit back to back, including a weekend, so they're not independent of each other and say little on their own. No file has been opened yet.

## 2026-11-23

Build day. Everything today used 2026-09-01 only. No test day was downloaded or opened.

**The CryptoStruct file.** I read the format notes on the CryptoStruct site and looked at the start of the 2026-09-01 file before writing the reader. Each line is one message with a type number, two event ids, a capture time and an exchange time in nanoseconds. The file starts a few minutes before midnight and ends just after the next one. It carries trades, a top of book stream, and a depth stream that opens with a 10,000<!--nc--> level snapshot per side and then sends level changes. There's no five level file like Tardis has, so I rebuild the book from the depth stream and write a five level row whenever the top five change. Before comparing anything I wrote down under Deviations what would count as agreement with Tardis and the other details the preregistration hadn't pinned down.

**Against Tardis.** Tardis has 3,602,361<!--c:load.trades.tardis--> trades on the day and CryptoStruct 3,622,828<!--c:load.trades.cs-->. The first and last trades are the same in both, same id, time, price and size. 100%<!--c:load.share.tardis--> of Tardis trades have a match on time, price and size, and 99.4%<!--c:load.share.cs--> of CryptoStruct trades do, so the loader passes the rule I set. The surprise is the other direction. CryptoStruct has 20,467<!--c:load.extra.cs--> trades that Tardis doesn't, and almost all of them sit in three bursts of about a second each, around 13:06:49, 16:36:57 and 18:27:23 UTC. Those look like big sweeps that the Tardis recording missed. So the 01 dev day was missing a few of its busiest seconds. 01's random decisions come one every 10 s on average, so only a handful could land near them. Signal decisions fire at extreme imbalance and could gather in sweeps like these, though the C1 slopes on the two copies of the day barely differ (0.103<!--c:build.cs.c1.slope--> and 0.104<!--c:build.tz.c1.slope-->). I haven't measured either and I'm not going to chase it here. It's on my list. *(Corrected 2026-11-23, see the afternoon entry.)* The top of book streams agree less, about 78%<!--c:load.ticker.share--> of rows match on all five fields. I haven't looked into why. My guess, not checked, is that two recorders on separate connections don't receive exactly the same top of book messages. It isn't part of the agreement rule, and the replay reads its top of book from whichever source the day comes from.

**The runner.** `python -m s2fb.run SOURCE SYM DAY next` runs one step of one listed day and writes it to its own file. It refuses a day that isn't listed, refuses any step whose file already exists, runs the steps in order, stops a day the gap rule leaves out and writes that decision in the audit file, and refuses ETHUSDT days until every BTCUSDT test day has finished or been left out. It also refuses anything but the build day if the 01 code differs from tag `v0.1-signal-to-fill`. Each step runs in its own process because the machine stops any job after 20 minutes. Tests cover the day list, the order, the refusals and the ETHUSDT wait.

**Does it give back 01?** I ran the whole chain on Tardis BTCUSDT 2026-09-01. The C1 numbers (signal walk slope 0.104<!--c:build.tz.c1.slope--> bps per log ms) and the C2 slopes under all three rules match 01's dev day files exactly, and the new loader gives arrays identical to 01's own loader. On the CryptoStruct copy of the same day the C1 slope is 0.103<!--c:build.cs.c1.slope-->, with the same signs everywhere.

**Race rule.** On the Tardis build day the race rule changed the fill in 10%<!--c:build.tz.race.changed--> of cells and the C1 slope went from 0.104<!--c:build.tz.c1.slope--> to 0.097<!--c:build.tz.race.slope-->. Most of the change makes fills worse, a few make them better, since the book 1 ms later can have moved my way. The drift and arrival split says almost all of ΔS(500 ms) is the mid moving, 0.65<!--c:build.tz.drift--> bps of drift against -0.014<!--c:build.tz.arrival--> bps of arrival cost. That fits a signal that already predicts the move.

**ETHUSDT and Bybit.** The ETHUSDT threshold from 2026-09-01 is 0.9863<!--c:build.eth.thr--> and the size is 0.319<!--c:build.eth.size--> ETH, both stored once. Bybit's free book file is 200 levels, not the 500<!--nc--> I wrote, and it updates about every 100 ms. On the build day the Bybit walk shortfall is flat at 0.057<!--c:build.bybit.S1--> bps from 1<!--nc--> to 50 ms and only moves at 100 ms (0.18<!--c:build.bybit.S100--> bps), which is the 100 ms book showing through. The C1 slope there is 0.052<!--c:build.bybit.c1.slope-->. Bybit can say something about 100<!--nc--> to 500 ms and almost nothing below. I logged the 200 level file under Deviations.

**A bug I caught on the build day.** My first Bybit reader wrote a top of book row only when the best price or size changed. Quiet stretches then looked like feed gaps, adding up to 1760<!--c:build.bybit.old.gap--> s, which threw away decisions near them and used about half of the one hour the gap rule allows. *(Corrected 2026-11-23, see the afternoon entry.)* Now every book message writes a row. The first run is kept in results/build/old.

**Memory.** The CryptoStruct day peaked at 4294<!--c:build.cs.mem--> MB in the C1 step. The biggest test day file is about 1.4<!--nc--> times the build day and the 2026-11-13 sample about 1.8<!--nc--> times, which wouldn't fit. I changed the parquet reader to load one column at a time, checked that it gives byte identical arrays, and a check run on the build day peaked around 3.2 GB<!--nc-->. That run's figure isn't stored in a results file. *(Corrected 2026-11-23, see the afternoon entry.)* Days still have to run one step at a time with nothing else going.

### Limits and gaps
- The review against my review checklist hasn't happened yet. It needs a separate reread before any test day is opened.
- Bybit's 100 ms book makes it a weak check below 100 ms, and Bybit has no capture time, so its gap rule runs on message send times.
- The C2 tie flip barely does anything on random decisions, since they fall between whole milliseconds and the book never ties with them. 01 saw the same. It's reported, but it isn't a real check of C2.
- The race rule is one simple version of a race. It can't say who would have won the touch.
- The missing Tardis bursts mean 01's dev day differs a little from the full feed. I haven't measured how much that matters for 01.
- The largest free sample may still be close to the memory limit even with the leaner reader.

## 2026-11-23, later

**Bybit's threshold.** Under the frozen Binance value Bybit 2026-09-01 gave 11,178<!--c:build.bybit.c1.n--> signal decisions against 16,738<!--c:build.tz.c1.n--> on Tardis BTCUSDT. Bybit's book moves in 100 ms steps, so its imbalance is spread differently and the same number doesn't pick the same top tenth of moments. ETHUSDT already gets its own 90th percentile from 2026-09-01, so I gave Bybit the same rule. I wrote that under Deviations and pushed it before computing Bybit's value, and it says I had already seen Bybit's build day results under the frozen value. The frozen value still runs on every Bybit test day as its own row.

Bybit's own threshold is 0.9543<!--c:build.bybit.own.thr-->. On the build day it gives 18,316<!--c:build.bybit.own.n--> decisions and a C1 slope of 0.044<!--c:build.bybit.own.slope--> bps per log ms, a little lower than the 0.052<!--c:build.bybit.c1.slope--> under the frozen value. Same sign, and it's still the build day, so it says nothing about the test days.

### Limits and gaps
- The change came after a look at Bybit's build day results. Running both versions on every test day is the guard against that, but it isn't the same as having decided before looking.
- Bybit is still a weak check below 100 ms and stays out of every verdict.

## 2026-11-23, afternoon

I went back over 01.b line by line against my checklist before copying in any test day. The main gap was that the preregistration promises a data script that refuses to fetch a day too early, and there isn't one. My files come from Drive by hand. So I wrote down under Deviations how they do come in, and committed the MD5 and size of all twelve bought test files to data/MANIFEST.md before copying any of them. The runner now checks each file against that MD5 before its first step. The converters and the loader refuse any day but 2026-09-01 unless the runner calls them. A day whose file fails can be left out through the runner, with the reason in its audit. The verdict count for C1 and C2 is now code with its own tests, so nobody counts days by hand at the end. All of this was written down under Deviations first and pushed before the code.

**The C2 placebo on the build day.** I hadn't said this before. The registered placebo interval already misses zero on 2026-09-01 for Bybit under all three cancellation rules, and for CryptoStruct under back. Tardis BTCUSDT and ETHUSDT cover zero under every rule. The shuffle uses one fixed seed, so every day reuses the same draws. To see whether that's one bad draw or something wrong with the check, I ran it over 200<!--c:cal.n--> shuffles on each source, the same way 01 did on its dev day, with the reading fixed under Deviations before running.

| Source | Front | Random | Back |
|---|---|---|---|
| Tardis BTCUSDT | 13<!--c:cal.tz.front--> | 11<!--c:cal.tz.random--> | 12<!--c:cal.tz.back--> |
| CryptoStruct BTCUSDT | 17<!--c:cal.cs.front--> | 10<!--c:cal.cs.random--> | 19<!--c:cal.cs.back--> |
| Tardis ETHUSDT | 15<!--c:cal.eth.front--> | 7<!--c:cal.eth.random--> | 11<!--c:cal.eth.back--> |
| Bybit BTCUSDT | 21<!--c:cal.by.front--> | 19<!--c:cal.by.random--> | 28<!--c:cal.by.back--> |

Each cell is how many of 200<!--c:cal.n--> placebo intervals exclude zero. The cut was 17<!--nc--> or fewer. So the check is fine on both Tardis sources and on CryptoStruct under front and random. It isn't under back on CryptoStruct or under any rule on Bybit. The surprise is CryptoStruct back, since CryptoStruct is where the C2 verdict comes from. Across shuffles the mean placebo slope sits close to zero on every source, so the shuffle itself isn't tilted. What the extra misses point to is the 5<!--nc--> minute block interval being a bit too narrow on those arrays. The registered draw is also an unlucky one. It ranks 4th<!--c:cal.cs.back.rank--> highest of 200<!--c:cal.n--> on CryptoStruct back and 1st<!--c:cal.by.random.rank--> on Bybit random.

What follows from the rule I wrote first. On CryptoStruct back and on Bybit, a test day placebo miss says nothing either way, and the write up gives this as a limit. Elsewhere a miss is read as one draw. C2 and its verdict don't change. One thing I'll keep in mind and say plainly with the results. If the block interval runs a little narrow on CryptoStruct back, C2's intervals under back could too, which would make "above zero" a bit easier to reach there.

**Smaller things I fixed.**
- The C1 fee check adds a flat 5<!--nc--> bps to every fill, which cancels in ΔS. It shifts the level of S and can't move the slope, so I won't call it a check on C1. The C2 fee check does change cost by delay.
- The race rule is a sensitivity, not a bound. It can help a fill as well as hurt it.
- The 01 shortfall range quoted at the top of the preregistration is 01's top of book number, not the five level walk.
- I set the 99%<!--nc--> loader rule after the CryptoStruct conversion had shown its trade count, and 01 had already published Tardis's. So the count gap was knowable when I picked the rule. Nothing in the history shows that arithmetic was done, and nothing rules it out.
- Three small corrections in this morning's entry are marked in place.

### Limits and gaps
- The placebo is off on CryptoStruct back and on Bybit, so it can't back up C2 there.
- The guard is code that I wrote, and the copy from Drive is still by hand. The MD5 check catches a wrong file, not an early look.
- The calibration is one day per source.
