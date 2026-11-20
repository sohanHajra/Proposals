"""Tests for the preregistration order check. Run from the repo root with `python -m unittest discover claimcheck/tests`.

Each test builds a small git repository in a temporary folder, so the history is exactly what the
test says it is.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from claimcheck.__main__ import EXIT_FAIL, EXIT_NOTHING_CHECKED, EXIT_PASS, verify
from claimcheck.prereg import check_prereg, heading_paths
from claimcheck.prereg import test_dates as read_test_dates

PREREG = """# Preregistration

## Data
| Role | Data | Days |
|---|---|---|
| Dev | files | 2026-09-01 |
| Test | same files | 2026-10-01 and 2026-11-01 |

## H1
The effect is above 0.1 bps on both test days.

## Deviations
"""


class Repo:
    """A throwaway git repository with a proposal folder inside it."""

    def __init__(self, sub="01-demo"):
        self.tmp = tempfile.TemporaryDirectory()
        self.top = Path(self.tmp.name)
        self.root = self.top / sub if sub else self.top
        self.root.mkdir(parents=True, exist_ok=True)
        self.n = 0
        self.git("init", "-q", "-b", "main")

    def git(self, *args):
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")
        subprocess.run(["git", "-C", str(self.top), *args], check=True, capture_output=True, env=env)

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def append(self, rel, text):
        p = self.root / rel
        p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")

    def replace(self, rel, old, new):
        p = self.root / rel
        p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def commit(self, msg="step"):
        self.n += 1
        # spaced dates so the order is clear in the log, though the check reads ancestry, not dates
        date = f"2026-11-{10 + self.n:02d}T12:00:00+00:00"
        self.git("add", "-A")
        os.environ["GIT_COMMITTER_DATE"] = date
        try:
            self.git("commit", "-q", "--date", date, "-m", msg)
        finally:
            del os.environ["GIT_COMMITTER_DATE"]

    def run(self):
        lines = []
        code = verify(self.root, out=lines.append, untagged=False, sources=False)
        return code, "\n".join(lines)

    def close(self):
        self.tmp.cleanup()


def fails(report):
    return [l.strip() for l in report.splitlines() if l.strip().startswith("FAIL")]


class PreregCase(unittest.TestCase):
    def setUp(self):
        self.r = Repo()
        self.r.write("README.md", "demo\n")
        self.r.write("results/dev/taker_dev_2026-09-01.json", "{}\n")

    def tearDown(self):
        self.r.close()


class TestOrder(PreregCase):
    def test_prereg_then_results_passes(self):
        self.r.commit("dev day")
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.commit("prereg")
        self.r.write("results/taker/taker_test_2026-10-01.json", "{}\n")
        self.r.commit("test day")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_PASS, report)
        self.assertEqual(fails(report), [])
        self.assertIn("results/taker/taker_test_2026-10-01.json first committed in", report)
        self.assertIn("after the preregistration", report)
        # the dev day file holds no test date and is not a test result
        self.assertNotIn("taker_dev", report)

    def test_results_before_prereg_fails(self):
        self.r.write("results/taker/taker_test_2026-11-01.json", "{}\n")
        self.r.commit("test day first")
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.commit("prereg after")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_FAIL)
        f = fails(report)
        self.assertEqual(len(f), 1, report)
        self.assertIn("taker_test_2026-11-01.json first committed in", f[0])
        self.assertIn("before the preregistration", f[0])
        self.assertIn("1 failure(s)", report)

    def test_same_commit_fails(self):
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.write("results/taker/taker_test_2026-10-01.json", "{}\n")
        self.r.commit("both at once")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_FAIL)
        self.assertIn("in the same commit as the preregistration", report)

    def test_prereg_not_committed_with_results_fails(self):
        self.r.commit("dev day")
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.write("results/taker/taker_test_2026-10-01.json", "{}\n")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_FAIL)
        self.assertIn("is not committed but test day results exist", report)

    def test_prereg_not_committed_alone_fails(self):
        self.r.commit("dev day")
        self.r.write("PREREGISTRATION.md", PREREG)
        code, report = self.r.run()
        self.assertEqual(code, EXIT_FAIL)
        self.assertIn("is not committed yet", report)

    def test_uncommitted_results_after_committed_prereg_pass(self):
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.commit("prereg")
        self.r.write("results/taker/taker_test_2026-10-01.json", "{}\n")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_PASS, report)
        self.assertIn("not committed yet, preregistration already is", report)

    def test_no_test_results_yet(self):
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.commit("prereg")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_PASS, report)
        self.assertIn("no test day results in the folder yet", report)

    def test_ignored_files_are_not_test_results(self):
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.commit("prereg")
        self.r.write(".gitignore", "data/\n")
        self.r.write("data/raw/2026-10-01.csv", "x\n")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_PASS, report)
        self.assertNotIn("data/raw", report)

    def test_patterns_file_adds_files(self):
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.write("claimcheck_tests.txt", "# breadth days\nresults/breadth/*.json\n")
        self.r.write("results/breadth/day_2026-03-01.json", "{}\n")
        self.r.commit("prereg and breadth result together")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_FAIL)
        self.assertIn("patterns results/breadth/*.json", report)
        self.assertIn("results/breadth/day_2026-03-01.json first committed in", report)

    def test_no_test_row_warns(self):
        self.r.write("PREREGISTRATION.md", "# Preregistration\n\n## H1\nSomething.\n\n## Deviations\n")
        self.r.commit("prereg")
        self.r.write("results/taker/taker_test_2026-10-01.json", "{}\n")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_PASS, report)
        self.assertIn("WARN  no test days named", report)

    def test_no_prereg_not_checked(self):
        self.r.commit("dev day")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_NOTHING_CHECKED)
        self.assertIn("no PREREGISTRATION.md, not checked", report)


class TestEditsAfterLock(PreregCase):
    def lock(self):
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.commit("prereg")
        self.r.append("PREREGISTRATION.md", "Before the test days, a note.\n")
        self.r.replace("PREREGISTRATION.md", "above 0.1 bps", "above 0.2 bps")
        self.r.commit("edits before any test day")
        self.r.write("results/taker/taker_test_2026-10-01.json", "{}\n")
        self.r.commit("test day")

    def test_edits_before_lock_are_fine(self):
        self.lock()
        code, report = self.r.run()
        self.assertEqual(code, EXIT_PASS, report)
        self.assertIn("no changes outside Deviations since test results arrived", report)

    def test_deviation_after_lock_passes(self):
        self.lock()
        self.r.append("PREREGISTRATION.md", "\n### 2026-11-21\nThe second day had a feed gap.\n")
        self.r.commit("deviation")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_PASS, report)
        self.assertIn("3 changed line(s) under Deviations", report)

    def test_edit_outside_deviations_after_lock_fails(self):
        self.lock()
        self.r.replace("PREREGISTRATION.md", "above 0.2 bps", "above 0.05 bps")
        self.r.commit("moved the bar")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_FAIL)
        f = fails(report)
        self.assertEqual(len(f), 2, report)
        self.assertIn("PREREGISTRATION.md:10 removed after test results arrived", f[0])
        self.assertIn("0.2 bps", f[0])
        self.assertIn("PREREGISTRATION.md:10 added", f[1])
        self.assertIn("0.05 bps", f[1])

    def test_uncommitted_edit_after_lock_fails(self):
        self.lock()
        self.r.replace("PREREGISTRATION.md", "## H1\n", "## H1\nOnly on the first day.\n")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_FAIL)
        f = fails(report)
        self.assertEqual(len(f), 1, report)
        self.assertIn("working tree  PREREGISTRATION.md:10 added", f[0])

    def test_renaming_a_section_to_deviations_fails(self):
        self.lock()
        self.r.replace("PREREGISTRATION.md", "## H1\n", "## Deviations from H1\n")
        self.r.commit("rename")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_FAIL)
        f = fails(report)
        # the old heading line is removed from under H1; the new one sits under Deviations and passes
        self.assertEqual(len(f), 1, report)
        self.assertIn("removed", f[0])
        self.assertIn("## H1", f[0])

    def test_uncommitted_results_lock_working_tree_edits(self):
        self.r.write("PREREGISTRATION.md", PREREG)
        self.r.commit("prereg")
        self.r.write("results/taker/taker_test_2026-10-01.json", "{}\n")
        self.r.replace("PREREGISTRATION.md", "above 0.1 bps", "above 0.3 bps")
        code, report = self.r.run()
        self.assertEqual(code, EXIT_FAIL)
        self.assertIn("working tree", report)


class TestPlaces(unittest.TestCase):
    def test_proposal_at_repo_root(self):
        r = Repo(sub="")
        try:
            r.write("PREREGISTRATION.md", PREREG)
            r.commit("prereg")
            r.write("results/x_2026-11-01.json", "{}\n")
            r.commit("test")
            code, report = r.run()
            self.assertEqual(code, EXIT_PASS, report)
            self.assertIn("results/x_2026-11-01.json first committed", report)
        finally:
            r.close()

    def test_other_proposal_files_are_not_read(self):
        r = Repo(sub="02-other")
        try:
            r.write("PREREGISTRATION.md", PREREG)
            r.commit("prereg in 02")
            sibling = r.top / "01-first" / "results"
            sibling.mkdir(parents=True)
            (sibling / "t_2026-10-01.json").write_text("{}\n")
            r.commit("old proposal results with the same date")
            code, report = r.run()
            self.assertEqual(code, EXIT_PASS, report)
            self.assertIn("no test day results in the folder yet", report)
        finally:
            r.close()

    def test_not_a_repo(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "PREREGISTRATION.md").write_text(PREREG)
            rep = check_prereg(d)
            self.assertTrue(rep.found)
            self.assertFalse(rep.in_git)
            self.assertEqual(rep.failures, 1)


class TestParsing(unittest.TestCase):
    def test_test_dates(self):
        self.assertEqual(read_test_dates(PREREG), ["2026-10-01", "2026-11-01"])
        self.assertEqual(read_test_dates("| **Test days** | 2025-01-02 |\n| Dev | 2025-01-01 |"), ["2025-01-02"])
        self.assertEqual(read_test_dates("| Testing note | 2025-01-02 |"), [])

    def test_heading_paths(self):
        text = "# P\n## Deviations\n### 2026-11-21\nx\n## After\n```\n## not a heading\n```\ny\n"
        paths = heading_paths(text)
        self.assertEqual(paths[4], ["P", "Deviations", "2026-11-21"])
        self.assertEqual(paths[5], ["P", "After"])
        self.assertEqual(paths[9], ["P", "After"])


if __name__ == "__main__":
    unittest.main()
