"""Tests for the numbers check. Run from the repo root with `python -m unittest discover claimcheck/tests`.

Each folder under fixtures/ is a tiny proposal with its own claims.yaml, results file and markdown.
"""

import tempfile
import unittest
from pathlib import Path

from claimcheck.__main__ import EXIT_FAIL, EXIT_NOTHING_CHECKED, EXIT_PASS, main, verify
from claimcheck.claims import ClaimsFileError, check_data, load_claims, resolve
from claimcheck.scan import printed_matches, scan_text

FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    lines = []
    code = verify(FIXTURES / name, out=lines.append)
    return code, "\n".join(lines)


def fail_lines(report):
    return [l.strip() for l in report.splitlines() if l.strip().startswith("FAIL")]


class TestFixtures(unittest.TestCase):
    def test_pass(self):
        code, report = run("pass")
        self.assertEqual(code, EXIT_PASS, report)
        self.assertEqual(fail_lines(report), [])
        # three claims, four tags (the same number cited in two files), code blocks ignored
        self.assertIn("3 claims in claims.yaml, 4 tags in markdown", report)
        self.assertNotIn("not.a.claim", report)
        self.assertNotIn("also.not", report)
        self.assertIn("NOTES.md:1  taker.dS500", report)

    def test_wrong_number_in_prose(self):
        code, report = run("wrong_number")
        self.assertEqual(code, EXIT_FAIL)
        fails = fail_lines(report)
        self.assertEqual(len(fails), 1, report)
        self.assertIn("prose says 0.0041, claim value is 0.004", fails[0])
        self.assertIn("README.md:1", fails[0])

    def test_stale_results_file(self):
        code, report = run("stale_file")
        self.assertEqual(code, EXIT_FAIL)
        fails = fail_lines(report)
        self.assertEqual(len(fails), 1, report)
        self.assertIn("file has 0.0061, claim says 0.004", fails[0])
        # the prose still agrees with claims.yaml, so the tag itself passes
        self.assertIn("PASS  README.md:1  taker.dS500", report)

    def test_missing_field(self):
        code, report = run("missing_field")
        self.assertEqual(code, EXIT_FAIL)
        fails = fail_lines(report)
        self.assertEqual(len(fails), 1, report)
        self.assertIn("field not found: by_delay.1000", fails[0])

    def test_unknown_tag(self):
        code, report = run("unknown_tag")
        self.assertEqual(code, EXIT_FAIL)
        fails = fail_lines(report)
        self.assertEqual(len(fails), 1, report)
        self.assertIn("taker.dS250  tag has no entry in claims.yaml", fails[0])
        self.assertIn("README.md:2", fails[0])

    def test_missing_results_file(self):
        code, report = run("missing_file")
        self.assertEqual(code, EXIT_FAIL)
        self.assertIn("results file not found: results/gone.json", report)

    def test_bad_tags(self):
        code, report = run("bad_tags")
        self.assertEqual(code, EXIT_FAIL)
        fails = fail_lines(report)
        self.assertEqual(len(fails), 2, report)
        self.assertIn("malformed tag", fails[0])
        self.assertIn("no number right before the tag", fails[1])
        # the claim is never validly cited, so it is also listed as unused
        self.assertIn("WARN  taker.dS500", report)

    def test_no_claims_file(self):
        code, report = run("no_claims")
        self.assertEqual(code, EXIT_NOTHING_CHECKED)
        self.assertIn("no claims.yaml", report)

    def test_cli_exit_codes(self):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(FIXTURES / "pass")]), EXIT_PASS)
            self.assertEqual(main([str(FIXTURES / "stale_file")]), EXIT_FAIL)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main([str(FIXTURES / "no_such_folder")]), EXIT_NOTHING_CHECKED)


class TestClaimsFile(unittest.TestCase):
    def _load(self, text):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "claims.yaml"
            p.write_text(text, encoding="utf-8")
            return load_claims(p)

    def test_bad_entries_keep_their_problems(self):
        claims = self._load(
            "a: {file: r.json, path: x, value: 1.0}\n"
            "b: {file: r.json, path: x, value: one, tol: 0.1}\n"
            "c: {file: r.json, path: x, value: 1.0, tol: -0.1}\n"
            "d: {file: r.json, path: x, value: 1.0, tol: 0.1, colour: red}\n"
            "e: just a string\n"
        )
        self.assertIn("missing tol", claims["a"].errors)
        self.assertIn("value is not a number", claims["b"].errors)
        self.assertIn("tol is negative", claims["c"].errors)
        self.assertIn("unknown field colour", claims["d"].errors)
        self.assertIn("entry is not a mapping", claims["e"].errors)
        r = check_data(claims["a"], ".")
        self.assertFalse(r.ok)
        self.assertTrue(r.reason.startswith("bad entry in claims.yaml"))

    def test_bool_is_not_a_number(self):
        claims = self._load("a: {file: r.json, path: x, value: true, tol: 0}\n")
        self.assertIn("value is not a number", claims["a"].errors)

    def test_not_a_mapping(self):
        with self.assertRaises(ClaimsFileError):
            self._load("- just\n- a list\n")

    def test_invalid_yaml(self):
        with self.assertRaises(ClaimsFileError):
            self._load("a: [unclosed\n")

    def test_empty_file(self):
        self.assertEqual(self._load(""), {})

    def test_non_numeric_field_and_bad_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "r.json").write_text('{"x": "0.5", "y": null}', encoding="utf-8")
            (root / "bad.json").write_text("{not json", encoding="utf-8")
            (root / "claims.yaml").write_text(
                "x: {file: r.json, path: x, value: 0.5, tol: 0}\n"
                "y: {file: r.json, path: y, value: 0.5, tol: 0}\n"
                "z: {file: bad.json, path: x, value: 0.5, tol: 0}\n",
                encoding="utf-8",
            )
            claims = load_claims(root / "claims.yaml")
            rx, ry, rz = (check_data(claims[k], root) for k in "xyz")
        self.assertIn("is not a number ('0.5')", rx.reason)
        self.assertIn("is not a number (None)", ry.reason)
        self.assertIn("is not valid JSON", rz.reason)

    def test_tolerance_edge(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "r.json").write_text('{"x": 0.25}', encoding="utf-8")
            (root / "claims.yaml").write_text(
                "inside: {file: r.json, path: x, value: 0.2, tol: 0.05}\n"
                "outside: {file: r.json, path: x, value: 0.2, tol: 0.04}\n",
                encoding="utf-8",
            )
            claims = load_claims(root / "claims.yaml")
            self.assertTrue(check_data(claims["inside"], root).ok)
            self.assertFalse(check_data(claims["outside"], root).ok)


class TestResolve(unittest.TestCase):
    DATA = {"a": {"b": [10, {"c": 3}]}, "500": {"m": 1}}

    def test_paths(self):
        self.assertEqual(resolve(self.DATA, "a.b.0"), 10)
        self.assertEqual(resolve(self.DATA, "a.b.1.c"), 3)
        self.assertEqual(resolve(self.DATA, "a.b.-1.c"), 3)
        self.assertEqual(resolve(self.DATA, "500.m"), 1)

    def test_failures_name_the_part(self):
        for path, part in [("a.x", "a.x"), ("a.b.5", "a.b.5"), ("a.b.first", "a.b.first"), ("a.b.0.z", "a.b.0.z")]:
            with self.assertRaises(KeyError) as cm:
                resolve(self.DATA, path)
            self.assertEqual(cm.exception.args[0], part)


class TestScan(unittest.TestCase):
    def test_number_forms(self):
        tags = scan_text(
            "a \u22120.12<!--c:neg--> b 1,204<!--c:big--> c 3.1%<!--c:pct--> d 7 ms<!--c:unit--> e +2<!--c:plus-->"
        )
        got = {t.claim_id: (t.printed, t.pct, t.unit) for t in tags}
        self.assertEqual(got["neg"], ("-0.12", False, ""))
        self.assertEqual(got["big"], ("1204", False, ""))
        self.assertEqual(got["pct"], ("3.1", True, ""))
        self.assertEqual(got["unit"], ("7", False, "ms"))
        self.assertEqual(got["plus"], ("+2", False, ""))
        self.assertTrue(all(not t.problem for t in tags))

    def test_word_negative_is_a_sign(self):
        tags = scan_text(
            "interval negative 0.0034<!--c:a--> to 0.0114<!--c:b-->, Negative 1.0 bps<!--c:c-->,"
            " nonnegative 2<!--c:d--> and negative \u22123<!--c:e-->"
        )
        got = {t.claim_id: (t.printed, t.unit, t.problem) for t in tags}
        self.assertEqual(got["a"], ("-0.0034", "", ""))
        self.assertEqual(got["b"], ("0.0114", "", ""))
        self.assertEqual(got["c"], ("-1.0", "bps", ""))
        self.assertEqual(got["d"], ("2", "", ""))
        self.assertIn("sign written twice", got["e"][2])

    def test_space_before_tag_is_not_a_number(self):
        (t,) = scan_text("moved 0.004 <!--c:x-->")
        self.assertEqual(t.problem, "no number right before the tag")

    def test_number_glued_to_a_word_is_not_read(self):
        (t,) = scan_text("version v2<!--c:x-->")
        self.assertEqual(t.problem, "no number right before the tag")

    def test_fences_and_inline_code(self):
        text = "```\n1.0<!--c:a-->\n```\n~~~\n2.0<!--c:b-->\n~~~\n`3.0<!--c:c-->` 4.0<!--c:d-->\n"
        tags = scan_text(text)
        self.assertEqual([t.claim_id for t in tags], ["d"])
        self.assertEqual(tags[0].line, 7)

    def test_printed_matches(self):
        self.assertTrue(printed_matches("0.0040", 0.0040))
        self.assertTrue(printed_matches("0.004", 0.0040))
        self.assertFalse(printed_matches("0.0041", 0.0040))
        self.assertTrue(printed_matches("0.13", 0.125))   # half rounds up
        self.assertFalse(printed_matches("0.12", 0.125))
        self.assertTrue(printed_matches("1204", 1204))
        self.assertTrue(printed_matches("-0.12", -0.12))
        self.assertFalse(printed_matches("0.12", -0.12))
        self.assertTrue(printed_matches("0.0040", 0.00395))   # rounds up to the printed 0.0040
        self.assertFalse(printed_matches("0.0040", 0.003949))


if __name__ == "__main__":
    unittest.main()
