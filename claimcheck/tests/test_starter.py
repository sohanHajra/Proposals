"""The starter folder a new proposal copies has to pass as it stands, and fail once a number drifts.

Run from the repo root with `python -m unittest discover claimcheck/tests`.
"""

import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from claimcheck.__main__ import EXIT_FAIL, EXIT_PASS, verify

STARTER = Path(__file__).resolve().parent.parent / "starter"


def git(top, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", "-C", str(top), *args], check=True, capture_output=True, env=env)


class StarterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.top = Path(self.tmp.name)
        self.root = self.top / "02-demo"
        shutil.copytree(STARTER, self.root)
        git(self.top, "init", "-q", "-b", "main")
        git(self.top, "add", "02-demo/PREREGISTRATION.md")
        git(self.top, "commit", "-q", "-m", "prereg")
        git(self.top, "add", "-A")
        git(self.top, "commit", "-q", "-m", "dev day")

    def tearDown(self):
        self.tmp.cleanup()

    def run_verify(self):
        buf = io.StringIO()
        code = verify(self.root, out=lambda *a: print(*a, file=buf))
        return code, buf.getvalue()

    def test_starter_passes_clean(self):
        code, report = self.run_verify()
        self.assertEqual(code, EXIT_PASS, report)
        self.assertIn("Numbers with no tag: none", report)

    def test_changed_number_fails(self):
        p = self.root / "README.md"
        p.write_text(p.read_text(encoding="utf-8").replace("0.42 bps", "0.43 bps"), encoding="utf-8")
        code, report = self.run_verify()
        self.assertEqual(code, EXIT_FAIL, report)
        self.assertIn("prose says 0.43", report)

    def test_rerun_that_moves_the_result_fails(self):
        p = self.root / "results/dev/example_dev_2030-01-01.json"
        p.write_text(p.read_text(encoding="utf-8").replace("0.4213", "0.4391"), encoding="utf-8")
        code, report = self.run_verify()
        self.assertEqual(code, EXIT_FAIL, report)


if __name__ == "__main__":
    unittest.main()
