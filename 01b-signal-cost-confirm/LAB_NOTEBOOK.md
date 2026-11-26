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
- The review against my integrity checks hasn't happened yet. It needs a separate reread before any test day is opened.
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

## 2026-11-23, evening. The twelve test days

I copied the twelve bought test days in from my Drive one at a time and ran each through the runner, every step once. *(Corrected 2026-11-24. One step was rerun, see below.)* Every file matched its MD5. None was left out by the gap rule, so all 12<!--c:test.surviving--> days survive. The tally comes from `python -m s2fb.verdict`, which wrote results/verdict/verdict_BTCUSDT.json.

**C1 holds.** The slope interval is above zero on 12<!--c:test.c1.above--> of 12<!--nc--> days and below zero on none, and mean ΔS at 500 ms clears 0.1 bps on every day. Day slopes run from 0.077<!--c:test.c1.slope.min--> (2026-05-13) to 0.110<!--c:test.c1.slope.max--> (2026-06-18) bps per log ms, and mean ΔS at 500 ms from 0.48<!--c:test.c1.dS500.min--> to 0.68<!--c:test.c1.dS500.max--> bps. That sits inside the range 01 saw on Tardis. *(Corrected 2026-11-24, see the late morning entry.)*

**C2 holds, with a catch under back.** Under front and random the slope interval is above zero on every day. Under back it is above zero on 11<!--c:test.c2.back.above--> days and covers zero on 2026-02-18, which the 10 of 12 rule allows. The back slopes are the smallest of the three rules on every day. This is the rule where the build day placebo check ran a little hot, so the back intervals may be slightly too narrow. I'm not changing the verdict for that, but I'd read C2 under back as the weakest part of the result.

One step didn't go cleanly. On 2026-06-18 the c1 step stopped once with no output and wrote no file. I ran it again on its own and it finished. Its peak memory, in its result file, is well under what the machine has, so I don't know what stopped it. Nothing was read from the first try.

### Limits and gaps
- The verdict is one source (CryptoStruct), one symbol, one day a month for a year.
- The C2 back intervals carry the placebo caveat above.
- Bybit, the free CryptoStruct samples, the Tardis first of month days and ETHUSDT are still to run. None of them is in the verdict.

## 2026-11-23, late evening. A closer look at C2 under back, exploratory

I came back to the back rule after writing up the tally, because it's the weakest part of C2. Everything below came after I had seen the test day results, so it's exploratory. It doesn't change C2 or its verdict.

**The registered placebo on the test days.** Of the 36<!--c:test.placebo.intervals--> placebo intervals (twelve days, three rules), 2<!--c:test.placebo.miss.total--> miss zero, and both are under back (2<!--c:test.placebo.miss.back-->). One sits just above zero on 2026-04-15 and one just below on 2026-10-14. Misses on both sides fit intervals that are a little too narrow better than they fit a hidden effect. Under the rule I wrote before the test days, back is the rule where the placebo can't back up C2 anyway, so I read these two as saying nothing either way.

**A rough widening.** The build day calibration had back missing zero on 19<!--c:cal.cs.back--> of 200<!--c:cal.n--> shuffles, which makes its 95%<!--nc--> intervals behave more like 90%<!--nc--> ones. As a rough check I widened each back interval around its estimate by the ratio of the two normal quantiles, about 1.17<!--c:expl.widen.ratio-->. The interval still sits above zero on 11<!--c:expl.widen.above--> days, the same days as before. On 2026-09-16 it now only just clears zero. This assumes the intervals are close to normal and that the build day miss rate carries over to the test days. Neither is checked, so I'd treat it as a sense of scale and nothing more. The code is src/s2fb/explore_back_widen.py.

How I'd put it. Delay raises passive cost under all three cancellation rules on this year of days. Front and random carry that. Under back the effect is the smallest of the three, close to the noise, and its intervals are probably a bit tight, so I'd lean on it less. *(Corrected 2026-11-24, see the late morning entry.)*

### Limits and gaps
- The widening is a rough fix on a known problem, not a corrected bootstrap. A proper fix would rebuild the block bootstrap, and I haven't done that.
- One calibration day per source.

## 2026-11-24, early morning. The secondary days

I ran every secondary day through the runner, one day at a time, each step once. *(Corrected 2026-11-24. One step was rerun, see below.)* That's the CryptoStruct stress day and the three recent days, the twelve Tardis first of month days on BTCUSDT and on ETHUSDT, and Bybit on the twelve test days. That's 40<!--c:sec.days--> days in all. None was left out by the gap rule. None of this is in the verdict, and each source is reported on its own.

**C1 holds on every one.** *(Corrected 2026-11-24, see the late morning entry.)* The slope interval is above zero and mean ΔS at 500<!--nc--> ms clears 0.1<!--nc--> bps on all 40<!--c:sec.c1.holds--> days. Bybit's slopes are the lowest, 0.039<!--c:sec.by.c1.min--> to 0.060<!--c:sec.by.c1.max--> bps per log ms, against 0.055<!--c:sec.tz.c1.min--> to 0.111<!--c:sec.tz.c1.max--> on Tardis BTCUSDT and 0.052<!--c:sec.eth.c1.min--> to 0.126<!--c:sec.eth.c1.max--> on ETHUSDT. Bybit under the frozen Binance threshold, the version I kept alongside after changing its threshold, comes out positive on all 12<!--c:sec.by.frozen.holds--> days too.

**C2 is weaker, and weakest on Bybit.** No slope estimate is below zero on any day or under any rule. The table counts the days where the interval sits above zero.

| Source | Days | Front | Random | Back |
|---|---|---|---|---|
| CryptoStruct stress and recent | 4<!--c:sec.cs.days--> | 4<!--c:sec.cs.front--> | 4<!--c:sec.cs.random--> | 2<!--c:sec.cs.back--> |
| Tardis BTCUSDT | 12<!--c:sec.tz.days--> | 12<!--c:sec.tz.front--> | 11<!--c:sec.tz.random--> | 10<!--c:sec.tz.back--> |
| Tardis ETHUSDT | 12<!--c:sec.eth.days--> | 12<!--c:sec.eth.front--> | 11<!--c:sec.eth.random--> | 10<!--c:sec.eth.back--> |
| Bybit BTCUSDT | 12<!--c:sec.by.days--> | 10<!--c:sec.by.front--> | 5<!--c:sec.by.random--> | 5<!--c:sec.by.back--> |

On both Tardis symbols the misses fall on the same days, 2025-05-01 under random and back and 2025-09-01 under back. The placebo check behaved on Tardis under every rule, so I'd read these as days where the effect is too small to see. *(Corrected 2026-11-24, see the late morning entry.)* On CryptoStruct the two misses are 2026-11-14 and 2026-11-15, both under back, both weekend days. The stress day clears zero under all three rules.

Bybit is the one I'd read most carefully. Front holds on most days, but random and back are above zero on fewer than half. Two things get in the way of saying more. Bybit's book moves in steps of about 100<!--nc--> ms, so most of the short delays see the same book. And the placebo check was already off on Bybit under every rule. So Bybit can't say much about C2 in either direction.

**Steps that didn't go cleanly.** The machine restarted partway through converting the stress day, and I ran it again from the start. On 2026-11-13 the C1 step and on 2026-11-14 the data check each stopped with a read error and wrote nothing. I ran each again on its own and both finished. On 2026-11-14 the first conversion step had also started before 2026-11-13 was rerun. I stopped it after about two minutes, before it wrote anything, and redid it from the start. I think the read errors were the disk, but I haven't checked that.

How I'd put it. Taker cost rising with delay shows up on every source, symbol and venue I tried. The passive side agrees in direction everywhere, but it's clear under front, thinner under back, and mostly lost in the noise on Bybit.

### Limits and gaps
- None of these days is in the verdict.
- The Tardis days are one a month and include four weekends and New Year's Day. The recent CryptoStruct days include two weekend days.
- Bybit's 100<!--nc--> ms book steps and its placebo problem make it a weak check on C2.
- The read errors are a guess at a cause, not a finding.

## 2026-11-24, late morning. Corrections after a second full reread

I reread all of 01.b against my integrity checks before calling the write up done. The verdict counts came out the same when I recounted them from the per day intervals. What follows are the places where my write up said less, or more, than the results.

**The drift and arrival split.** The preregistration promised it per day for C1 and I hadn't reported it. It's now a table in the README. Drift is larger than the whole ΔS at 500<!--nc--> ms on all 12<!--c:chk.c1.drift.above--> test days, running 0.50<!--c:chk.c1.drift.min--> to 0.69<!--c:chk.c1.drift.max--> bps, and arrival is a little negative, between −0.029<!--c:chk.c1.arr.min--> and −0.011<!--c:chk.c1.arr.max--> bps. So the C1 cost is the predicted move happening while the order waits. The book at arrival takes a hair of it back. That's the most useful thing in this entry, and I should have had it in last night.

**Corrections to earlier entries, marked in place.**
- The test day entry says C1 sits inside the range 01 saw. That holds for the slope. 01's 0.47<!--c:prior.sig.S500.min--> to 0.76<!--c:prior.sig.S500.max--> bps at 500 ms was a top of book level, not walk ΔS, so the two aren't the same thing.
- The late evening entry says delay raises passive cost. C2 describes the orders that were kept, and which ones are kept depends on delay. The better wording is that among the orders kept, passive cost is higher at longer delays.
- This morning's entry says C1 holds on every secondary day. Holds is the word for the verdict, and these days aren't in it. C1's day rule passes on every one.
- This morning's entry also says the placebo behaved on Tardis under every rule. That was the build day check. On the secondary days themselves 7<!--c:sec.plac.miss--> of 160<!--c:sec.plac.n--> placebo intervals miss zero, one of them on Tardis BTCUSDT (2025-11-01 random) and two on ETHUSDT (2025-12-01, C1 and random). That's close to what chance gives, but it isn't nothing. *(Corrected 2026-11-25. They all reuse one seed, so they aren't 160<!--c:sec.plac.n--> separate draws and the count can't be compared with chance.)*

**Things now reported that weren't.**
- Each CryptoStruct secondary day gets its own row. I had pooled the stress day with the recent days, and the preregistration says each is reported alone.
- Bybit under the frozen Binance threshold has its own row. Its slopes are higher on all 12<!--c:sec.by.frozen.higher--> days than under Bybit's own threshold. So the threshold change I made after seeing Bybit's build day made its C1 smaller.
- The race rule's share of cells made worse and made better. I had called the rule pessimistic in the README draft, and the preregistration already says it isn't a bound.
- The C1 fee level, and a sense of scale for C2. From 1 ms to 500 ms C2 adds a few hundredths of a bp, small next to fees.
- The C2 tie flip gives exactly the main numbers on 10<!--c:chk.c2.tie.same--> of 12<!--nc--> days, so I took it out of the README table and said why.
- data/MANIFEST.md now has the SHA256 of every Tardis and Bybit file the secondary days read. Those hashes were taken when the files were fetched during last night's runs. The files themselves aren't kept, so I can't hash them again from here.

The code that gathers these is src/s2fb/test_checks.py and src/s2fb/secondary_tally.py. Neither feeds the verdict.

### Limits and gaps
- None of this changes C1, C2 or the verdict. It changes how much they say.
- The MANIFEST hashes for the secondary files were taken at fetch time by the same runs that used them, so they show what was read, not when it was first seen.
- The gap count in each test day's data check and the one in its C1 results differ by 1<!--nc--> or 2<!--nc--> on five<!--nc--> days. My guess is that they count at different stages of reading the feed, but I haven't checked.

## 2026-11-25. Released

I read the write up once more and put 01.b out, tagged `v0.1-signal-cost-confirm`. No analysis was run today. No hypothesis, threshold, day or result moved. The verdict is the one in the README. C1 and C2 both hold on the twelve test days, and C2 is small and weakest under the back rule.

### Limits and gaps
- The verdict rests on twelve days of one symbol on one venue. The secondary days back it up but aren't in it.
- C2 describes the passive orders that were kept, so it isn't a causal cost of delay.
- Bybit's 100<!--nc--> ms book steps and its placebo problem leave C2 there mostly unread.
- The replay still has no real race for the touch. The race rule is a sensitivity, not a bound.
- Under back the C2 intervals are probably a little narrow.
- Anything I find from here goes in a new dated entry.

## 2026-11-25, afternoon. Reread after release

I went through the released folder once more and recomputed the headline numbers from the twelve per day files rather than the summaries. They all match. A few things were said less clearly than they should be, so I fixed them without touching the tag.

The biggest is C2 with fees. I'd written that C2 is small next to fees, which is true, but it hid that fees make C2 larger. A longer wait turns some maker fills into taker crossings, so with fees the 1<!--nc--> to 500<!--nc--> ms cost is 0.063<!--c:chk.c2.feescale.front.min--> to 0.281<!--c:chk.c2.feescale.front.max--> bps under front, 0.014<!--c:chk.c2.feescale.random.min--> to 0.126<!--c:chk.c2.feescale.random.max--> under random and 0.002<!--c:chk.c2.feescale.back.min--> to 0.045<!--c:chk.c2.feescale.back.max--> under back. Without fees front was 0.021<!--c:chk.c2.scale.front.min--> to 0.090<!--c:chk.c2.scale.front.max--> bps. It's still well under a bp.

I hadn't noticed that the back day under the line moves. With fees it's 2026-08-12 and 2026-02-18 clears. In every other check it's 2026-02-18. Same count, different day, and it fits back sitting at the edge.

Smaller things. The rerun line in the README now says to move a day's results aside first, since the runner won't overwrite a step. The secondary C1 line uses the day rule wording. The placebo limit now says it comes from the build day check. The earlier comparison of the 7<!--c:sec.plac.miss--> of 160<!--c:sec.plac.n--> placebo misses with chance is marked in place, since they share one seed.

src/s2fb/test_checks.py now also writes the fee inclusive cost range and the days not above zero for each check. Nothing else in its output changed, and it still doesn't feed the verdict.

### Limits and gaps
- The fee inclusive C2 ranges come from the registered fee check. I haven't looked at how much of the change is fees moving versus fills moving.
- The release tag points at the text before these fixes. The fixes are in the commit after it.


## 2026-11-26. A rule for one more look at C2, written before it runs

This is exploratory and comes after release. It doesn't touch C1, C2 or the verdict.

C2 keeps only the random decisions that are never marketable on arrival at any delay. That takes out the free option the replay hands a stale order, but it picks orders by where the price goes next. 01's H5 keeps every order and keeps the free option, which pulls its cost down at longer delays. I wanted the third reading, where every order stays in and the free option goes the other way.

The rule. Every random decision is kept. A cell that arrives marketable is treated as if a faster trader took the stale price. It gets no fill at arrival and crosses at the far touch 10 s after arrival, the same cross price the replay already uses for anything left unfilled. Every other cell keeps its stored cost. I take the slope on log d under front, random and back with the same block bootstrap and seed, on the twelve test days with the primary tie rule, once each, through `python -m s2fb.run cryptostruct BTCUSDT DAY explore c2_lose_race`. The step reads the stored replay arrays and the day's book and writes results/exploratory/c2_lose_race/.

How I'll read it. Next to C2 and H5 it shows how much of C2 comes from which orders are kept. It isn't a bound, since a real order would sometimes win that race. One run, one table, reported whatever it shows. I first wrote a filter on distance from the far touch at decision time, then saw that our price always starts at its own touch, so the filter would keep every order. I replaced it before running anything.

It ran on the build day only, to check the code. Other cells match the stored cost exactly.

### Limits and gaps
- Losing every race is as unrealistic as winning every race. The truth sits somewhere between, and this doesn't say where.
- The data was seen before this rule was written, so whatever it shows is a description, not a test.

## 2026-11-26, later. The lose the race look, run once

It ran once on each of the twelve test days. Other cells matched the stored cost on every day. The share of cells that arrive marketable goes from 0.03<!--c:exp.lr.mk1.min-->% to 0.2<!--c:exp.lr.mk1.max-->% at 1<!--nc--> ms to 4.7<!--c:exp.lr.mk500.min-->% to 14.5<!--c:exp.lr.mk500.max-->% at 500<!--nc--> ms.

The sign flips. Under this rule cost falls with delay. Below zero on 11<!--c:exp.lr.front.below--> of 12<!--c:exp.lr.days--> days under front (one covers zero), and on all twelve under random and back. Under front the slope runs from −0.025<!--c:exp.lr.front.slope.min--> to −0.003<!--c:exp.lr.front.slope.max--> bps per log ms, and the 1<!--nc--> to 500<!--nc--> ms change from −0.174<!--c:exp.lr.front.chg.min--> to −0.023<!--c:exp.lr.front.chg.max--> bps. C2 had all three rules above zero on most days.

My reading, not checked. An order that arrives marketable does so because the price moved its way. Crossing 10 s later still keeps most of that move, so the rule doesn't take the free option away the way I meant it to. It hands it over late. So this isn't the pessimistic side I described this morning, and it doesn't bracket C2 with H5. What it does show is that C2's sign depends on which orders are kept. That is the weak spot already listed for C2, now with a number on it.

I'm not trying a harsher rule. The stop point was one run.

### Limits and gaps
- The reason the sign flips is my guess. I haven't split the marketable cells' costs to check it.
- The data was seen before the rule was written, so this is a description, not a test.
