"""Tests for the list of numbers with no tag. Run from the repo root with `python -m unittest discover claimcheck/tests`."""

import contextlib
import io
import unittest
from pathlib import Path

from claimcheck.__main__ import EXIT_NOTHING_CHECKED, EXIT_PASS, main, verify
from claimcheck.untagged import scan_untagged, scan_untagged_text

FIXTURES = Path(__file__).parent / "fixtures"


def numbers(text, ignore=()):
    return [u.number for u in scan_untagged_text(text, ignore=ignore)]


class TestFixture(unittest.TestCase):
    def test_only_real_untagged_numbers_are_listed(self):
        found = scan_untagged(FIXTURES / "untagged")
        got = [(u.file, u.line, u.number) for u in found]
        self.assertEqual(
            got,
            [
                ("README.md", 6, "0.0114"),
                ("README.md", 6, "12.6%"),
                ("README.md", 19, "7"),
                ("LAB_NOTEBOOK.md", 2, "3,602,361"),
            ],
        )

    def test_warnings_do_not_fail_the_run(self):
        lines = []
        code = verify(FIXTURES / "untagged", out=lines.append)
        report = "\n".join(lines)
        self.assertEqual(code, EXIT_PASS, report)
        self.assertIn("Numbers with no tag (warning only, 4)", report)
        self.assertIn("WARN  README.md:6  0.0114", report)

    def test_listed_even_without_claims_file(self):
        lines = []
        code = verify(FIXTURES / "no_claims", out=lines.append)
        self.assertEqual(code, EXIT_NOTHING_CHECKED)
        self.assertIn("Numbers with no tag", "\n".join(lines))

    def test_flag_turns_the_list_off(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(main([str(FIXTURES / "untagged"), "--no-untagged"]), EXIT_PASS)
        self.assertNotIn("Numbers with no tag", buf.getvalue())

    def test_other_markdown_files_are_not_read(self):
        found = scan_untagged(FIXTURES / "untagged")
        self.assertFalse(any(u.file == "NOTES.md" for u in found))


def numbers_ignoring(text, ignore):
    return [u.number for u in scan_untagged_text(text, ignore=ignore)]


class TestRules(unittest.TestCase):
    def test_plain_results_are_listed(self):
        self.assertEqual(numbers("shortfall 0.0104 bps, fill 46.7%, negative \u22120.4 and -0.7"),
                         ["0.0104", "46.7%", "\u22120.4", "-0.7"])

    def test_tagged_and_marked_numbers(self):
        text = "a 0.0040 bps<!--c:x--> b 3.1%<!--c:y--> c 1.7 bps<!--cite--> d 500 ms<!--nc--> e 9"
        self.assertEqual(numbers(text), ["9"])

    def test_ignore_phrase_matches_only_whole(self):
        text = "waited 1 ms, then 0.1 ms, 21 ms and 1 ms."
        got = [u.number for u in scan_untagged_text(text, ignore=["1 ms"])]
        self.assertEqual(got, ["0.1", "21"])

    def test_longer_ignore_phrase_wins(self):
        text = "horizons of 1, 2 and 5 ms, and a 5 ms window"
        self.assertEqual(numbers_ignoring(text, ["5 ms", "1, 2 and 5 ms"]), [])

    def test_tag_must_touch_the_number(self):
        self.assertEqual(numbers("moved 0.004 <!--c:x-->"), ["0.004"])

    def test_dates_times_years(self):
        text = "2026-09-01, 18 November 2026, Nov 18, 2026, Sept 3rd, 10:00, 6:40 pm, in 2014 and 1999"
        self.assertEqual(numbers(text), [])

    def test_a_percent_that_looks_like_a_year_is_listed(self):
        self.assertEqual(numbers("about 2014% more"), ["2014%"])

    def test_references_and_ids(self):
        text = ("Table 7, Tables 2 and 3, Figure 4, Fig. 2, Section 5.1, \u00a7 3, p. 1078, pp. 12, 14 and 15, "
                "Proposition 4, Lemma 1, Step 6, seed 20261115, Python 3.10, H1b RQ3 v2 file_10.csv "
                "01-signal-to-fill 1301.T 007 p99.9 x/2")
        self.assertEqual(numbers(text), [])

    def test_citations_and_links(self):
        text = ("10.1093/qje/qjv027, arXiv:2609.13597v2, 2609.13597, 104(5):418-424, "
                "[label](https://a.com/x/123) https://b.org/9 www.c.com/7")
        self.assertEqual(numbers(text), [])

    def test_quotes_blockquotes_and_code(self):
        text = '> quoted 42\n"a 95% interval" \u201c3 days\u201d `0.25` real 5\n```\n0.99\n```\n~~~\n1.5\n~~~\nafter 6'
        self.assertEqual(numbers(text), ["5", "6"])

    def test_list_markers(self):
        self.assertEqual(numbers("1. first\n  2) second has 8 rows\n10. tenth"), ["8"])

    def test_thousands_and_trailing_commas(self):
        self.assertEqual(numbers("grid 1, 2, 5 and 36,920,623 rows"), ["1", "2", "5", "36,920,623"])

    def test_ignore_phrases(self):
        self.assertEqual(numbers("grid 250 ms and 0.3 bps", ignore=["250 ms"]), ["0.3"])

    def test_line_numbers_and_context(self):
        (u,) = scan_untagged_text("first\nsecond line has 0.5 here", "X.md")
        self.assertEqual((u.file, u.line), ("X.md", 2))
        self.assertIn("0.5", u.context)


if __name__ == "__main__":
    unittest.main()
