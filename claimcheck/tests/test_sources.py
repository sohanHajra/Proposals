"""Tests for the source checks. Run from the repo root with `python -m unittest discover claimcheck/tests`."""

import unittest
from pathlib import Path

from claimcheck.__main__ import EXIT_FAIL, EXIT_PASS, verify
from claimcheck.sources import UnverifiedEntry, check_sources, find_citations, read_review

FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    lines = []
    code = verify(FIXTURES / name, out=lines.append, untagged=False)
    return code, "\n".join(lines)


def fail_lines(report):
    return [l.strip() for l in report.splitlines() if l.strip().startswith("FAIL")]


def entry(surname, year):
    return UnverifiedEntry(1, f"{surname} ({year})", surname, year)


class TestSourceFixtures(unittest.TestCase):
    def test_pass(self):
        code, report = run("sources_pass")
        self.assertEqual(code, EXIT_PASS, report)
        self.assertEqual(fail_lines(report), [])
        self.assertIn("Lee & Park (2020)  read at full text", report)
        self.assertIn("Ortiz (2018)  read at abstract", report)
        self.assertIn("Ng et al. (2021)  read at listing", report)
        self.assertIn("README.md:3  Smith 2019 is unverified, marked as not relied on", report)
        self.assertIn("not cited elsewhere: Kowalski 2015", report)
        # INTEGRITY_LOG.md names Smith (2019) and is skipped on purpose
        self.assertNotIn("INTEGRITY_LOG", report)

    def test_fail(self):
        code, report = run("sources_fail")
        self.assertEqual(code, EXIT_FAIL)
        fails = fail_lines(report)
        self.assertEqual(len(fails), 7, report)
        joined = "\n".join(fails)
        self.assertIn("LITERATURE_REVIEW.md:6  Ortiz (2018)  no reading depth", joined)
        self.assertIn("LITERATURE_REVIEW.md:7  Ng et al. (2021)  no reading depth", joined)
        self.assertIn("also listed as read (abstract) on line 8", joined)
        self.assertIn("can't read a first author and (year)", joined)
        self.assertIn("LAB_NOTEBOOK.md:4  Smith 2019 is on the Unverified list but cited here", joined)
        self.assertIn("LITERATURE_REVIEW.md:8  Smith 2019 is on the Unverified list", joined)
        self.assertIn("LITERATURE_REVIEW.md:10  Kowalski 2015 is on the Unverified list", joined)
        self.assertIn("7 failure(s)", report)

    def test_missing_column_and_section(self):
        code, report = run("sources_missing")
        self.assertEqual(code, EXIT_FAIL)
        fails = fail_lines(report)
        self.assertEqual(len(fails), 2, report)
        self.assertIn("no table with a 'Read at' column", fails[0])
        self.assertIn("no Unverified section", fails[1])

    def test_no_review_is_not_checked(self):
        rep = check_sources(FIXTURES / "pass")
        self.assertFalse(rep.found)
        self.assertEqual(rep.failures, 0)
        code, report = run("pass")
        self.assertEqual(code, EXIT_PASS, report)
        self.assertIn("Sources: no LITERATURE_REVIEW.md, not checked", report)


class TestCitations(unittest.TestCase):
    def cites(self, text, e):
        return find_citations(text, "x.md", [e])

    def test_forms_that_count(self):
        e = entry("Smith", "2019")
        for text in ("Smith (2019) found", "Smith 2019 found", "Smith, 2019", "Smith et al. (2019)",
                     "Smith & Jones (2019b)", "Smith and Jones, writing in 2019, found"):
            self.assertEqual(len(self.cites(text, e)), 1, text)

    def test_forms_that_do_not(self):
        e = entry("Smith", "2019")
        for text in ("Smithson (2019)", "McSmith (2019)", "Smith (2017)", "Smith 20190", "Smith on its own",
                     "2019 Smith", "`Smith (2019)`",
                     "Smith " + "x" * 70 + " 2019"):
            self.assertEqual(self.cites(text, e), [], text)

    def test_code_fence_skipped(self):
        e = entry("Smith", "2019")
        text = "```\nSmith (2019)\n```\nSmith (2019)"
        found = self.cites(text, e)
        self.assertEqual([c.line for c in found], [4])

    def test_unread_mark(self):
        e = entry("Smith", "2019")
        self.assertTrue(self.cites("Smith (2019)<!--unread--> says", e)[0].marked)
        self.assertTrue(self.cites("Smith 2019 <!--unread-->", e)[0].marked)
        self.assertFalse(self.cites("Smith (2019) says so <!--unread-->", e)[0].marked)

    def test_non_ascii_surname(self):
        e = entry("Sağlam", "2013")
        self.assertEqual(len(self.cites("as Sağlam (2013) put it", e)), 1)


class TestReadReview(unittest.TestCase):
    def test_depth_column_headers(self):
        for header in ("Read at", "Reading depth", "**Depth**"):
            text = f"| Work | {header} |\n|---|---|\n| A (2001) | abstract |\n\n## Unverified\n"
            rows, *_ = read_review(text)
            self.assertEqual([(r.work, r.depth) for r in rows], [("A (2001)", "abstract")], header)

    def test_first_depth_word_wins(self):
        text = "| Work | Read at |\n|---|---|\n| A (2001) | abstract only, full text not opened |\n\n## Unverified\n"
        rows, *_ = read_review(text)
        self.assertEqual(rows[0].depth, "abstract")

    def test_unverified_section_ends_at_next_heading(self):
        text = "| Work | Read at |\n|---|---|\n| A (2001) | full text |\n\n## Unverified\n- B (2002), x\n\n## Notes\n- C (2003), y\n"
        rows, entries, lines, problems, has_table, has_section = read_review(text)
        self.assertEqual([(e.surname, e.year) for e in entries], [("B", "2002")])
        self.assertEqual(problems, [])
        self.assertTrue(has_table and has_section)

    def test_subheading_stays_inside(self):
        text = "| Work | Read at |\n|---|---|\n| A (2001) | full text |\n\n## Unverified\n### Older\n- B (2002), x\n## Notes\n"
        _, entries, *_ = read_review(text)
        self.assertEqual([e.surname for e in entries], ["B"])

    def test_first_author_only(self):
        text = "| Work | Read at |\n|---|---|\n\n## Unverified\n- Maglaras, Moallemi & Wang (2022), x\n- Gu et al. (2013), y\n- Almgren & Chriss (2001), z\n"
        _, entries, *_ = read_review(text)
        self.assertEqual([(e.surname, e.year) for e in entries],
                         [("Maglaras", "2022"), ("Gu", "2013"), ("Almgren", "2001")])


if __name__ == "__main__":
    unittest.main()
