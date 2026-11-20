"""Preregistration order, read from git history.

1. PREREGISTRATION.md must be in git history, and the commit that first added it must come before
   (be a strict ancestor of) the first commit of every test day results file. A test day results
   file that exists but is not committed yet counts as arriving now, so the preregistration must
   already be committed.
2. Once the first test day results file is committed, every later change to PREREGISTRATION.md
   (in a commit, or still uncommitted in the working tree) must sit under a heading with the word
   Deviations in it, or under a subheading of one. A changed or removed line anywhere else fails.

Which files are test day results. Under the proposal's results/ folder, any file whose path holds
one of the test dates. The dates are read from the preregistration itself, from a markdown table
row whose first cell is "Test" or "Test days". A proposal can add more with claimcheck_tests.txt,
one glob per line relative to the proposal folder (# starts a comment), for days or files the
table does not name.

What it cannot do. It trusts commit order, which a rebase or a rewritten history can change, and
it follows a file by its path, so a results file renamed into place is dated by the rename. It
can't tell whether a test day was looked at before the preregistration was written, only whether
its results were committed before.
"""

import fnmatch
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

PREREG_FILE = "PREREGISTRATION.md"
TESTS_FILE = "claimcheck_tests.txt"
RESULTS_DIR = "results"
DEVIATION_WORD = re.compile(r"deviation", re.I)
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
ISO_DATE = re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2})(?!\d)")
TEST_ROW = re.compile(r"^\s*\|\s*\**\s*test(?:\s+days?)?\s*\**\s*\|", re.I)
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


class GitError(Exception):
    """A git command failed."""


@dataclass
class Commit:
    sha: str
    date: str

    @property
    def short(self):
        return self.sha[:7]


@dataclass
class TestFile:
    path: str            # relative to the proposal folder
    commit: Commit = None  # None when the file is not committed yet


@dataclass
class Edit:
    where: str           # commit short sha, or "working tree"
    line: int
    kind: str            # "added" or "removed"
    text: str
    heading: str
    ok: bool = False     # True when the line sits under a Deviations heading


@dataclass
class PreregReport:
    found: bool = False
    in_git: bool = True
    prereg_commit: Commit = None
    test_dates: list = field(default_factory=list)
    patterns: list = field(default_factory=list)
    tests: list = field(default_factory=list)
    lock: TestFile = None
    early: list = field(default_factory=list)      # test files not after the prereg commit
    edits: list = field(default_factory=list)      # changes outside Deviations after the lock
    allowed_edits: int = 0                         # changed lines under Deviations after the lock
    problems: list = field(default_factory=list)

    @property
    def failures(self):
        return len(self.problems) + len(self.early) + len(self.edits)


def _git(top, *args, check=True):
    p = subprocess.run(["git", "-C", str(top), *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p


def repo_top(path):
    p = _git(path, "rev-parse", "--show-toplevel", check=False)
    if p.returncode != 0:
        return None
    return Path(p.stdout.strip()).resolve()


def first_commit(top, relpath):
    """The commit that first added relpath, or None if it was never committed."""
    out = _git(top, "log", "--reverse", "--diff-filter=A", "--format=%H %cI", "--", relpath).stdout.split("\n")
    out = [l for l in out if l.strip()]
    if not out:
        return None
    sha, date = out[0].split(" ", 1)
    return Commit(sha, date)


def is_ancestor(top, a, b):
    """True when commit a is an ancestor of commit b (a == b counts)."""
    return _git(top, "merge-base", "--is-ancestor", a, b, check=False).returncode == 0


def test_dates(text):
    """ISO dates on markdown table rows whose first cell is Test or Test days."""
    dates = []
    for line in text.splitlines():
        if TEST_ROW.match(line):
            for d in ISO_DATE.findall(line):
                if d not in dates:
                    dates.append(d)
    return dates


def load_patterns(root):
    f = Path(root) / TESTS_FILE
    if not f.is_file():
        return []
    pats = []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            pats.append(line)
    return pats


def heading_paths(text):
    """For each line (1 based index), the list of headings it sits under. Code fences are skipped."""
    stack = []
    paths = [None]
    in_code = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_code = not in_code
        m = None if in_code else HEADING.match(line)
        if m:
            level = len(m.group(1))
            stack = [(l, t) for l, t in stack if l < level] + [(level, m.group(2))]
        paths.append([t for _, t in stack])
    return paths


def under_deviations(path):
    return bool(path) and any(DEVIATION_WORD.search(t) for t in path)


def _show(top, rev, relpath):
    p = _git(top, "show", f"{rev}:{relpath}", check=False)
    return p.stdout if p.returncode == 0 else ""


def diff_edits(diff, old_text, new_text, where):
    """Split a -U0 diff of one file into changed lines, each with the headings it sits under."""
    old_paths = heading_paths(old_text)
    new_paths = heading_paths(new_text)
    edits = []
    old_no = new_no = 0
    for line in diff.splitlines():
        m = HUNK.match(line)
        if m:
            old_no = int(m.group(1))
            new_no = int(m.group(3))
            continue
        if line.startswith(("---", "+++")):
            continue
        if line.startswith("-"):
            path = old_paths[old_no] if 0 < old_no < len(old_paths) else []
            edits.append(Edit(where, old_no, "removed", line[1:], " > ".join(path or []), under_deviations(path)))
            old_no += 1
        elif line.startswith("+"):
            path = new_paths[new_no] if 0 < new_no < len(new_paths) else []
            edits.append(Edit(where, new_no, "added", line[1:], " > ".join(path or []), under_deviations(path)))
            new_no += 1
    return edits


def candidate_files(top, root):
    """Files in the proposal folder, committed or not (ignored ones left out), relative to the folder."""
    prefix = root.resolve().relative_to(top).as_posix()
    prefix = "" if prefix == "." else prefix + "/"
    tracked = _git(top, "ls-files", "--", prefix or ".").stdout.splitlines()
    untracked = _git(top, "ls-files", "--others", "--exclude-standard", "--", prefix or ".").stdout.splitlines()
    out = {}
    for f in tracked:
        out[f[len(prefix):]] = True
    for f in untracked:
        out.setdefault(f[len(prefix):], False)
    return prefix, out


def is_test_file(rel, dates, patterns):
    if rel.startswith(RESULTS_DIR + "/") and any(d in rel for d in dates):
        return True
    return any(fnmatch.fnmatch(rel, p) for p in patterns)


def check_prereg(root):
    root = Path(root)
    rep = PreregReport()
    prereg = root / PREREG_FILE
    if not prereg.is_file():
        return rep
    rep.found = True
    top = repo_top(root)
    if top is None:
        rep.in_git = False
        rep.problems.append(f"{root} is not inside a git repository, so the order can't be checked")
        return rep

    rep.test_dates = test_dates(prereg.read_text(encoding="utf-8"))
    rep.patterns = load_patterns(root)
    prefix, files = candidate_files(top, root)
    prereg_rel = prefix + PREREG_FILE
    rep.prereg_commit = first_commit(top, prereg_rel)

    for rel in sorted(files):
        if not is_test_file(rel, rep.test_dates, rep.patterns):
            continue
        tf = TestFile(rel, first_commit(top, prefix + rel) if files[rel] else None)
        rep.tests.append(tf)

    if rep.prereg_commit is None:
        if rep.tests:
            rep.problems.append(f"{PREREG_FILE} is not committed but test day results exist")
        else:
            rep.problems.append(f"{PREREG_FILE} is not committed yet")
        return rep

    for tf in rep.tests:
        if tf.commit is None:
            continue  # arrives now, after a committed prereg
        if tf.commit.sha == rep.prereg_commit.sha or not is_ancestor(top, rep.prereg_commit.sha, tf.commit.sha):
            rep.early.append(tf)

    committed = [t for t in rep.tests if t.commit is not None]
    if committed:
        # the lock is the earliest committed test file in history order
        lock = committed[0]
        for t in committed[1:]:
            if is_ancestor(top, t.commit.sha, lock.commit.sha):
                lock = t
        rep.lock = lock
    elif rep.tests:
        rep.lock = rep.tests[0]

    if rep.lock is None or rep.early:
        # with test results committed before (or with) the preregistration, its whole text came after
        # them, so line by line edits say nothing more than the order failure already does
        return rep

    edits = []
    if rep.lock.commit is not None:
        lock_sha = rep.lock.commit.sha
        shas = _git(top, "log", "--reverse", "--format=%H", "--", prereg_rel).stdout.split()
        for sha in shas:
            if not is_ancestor(top, lock_sha, sha):
                continue
            parent = _git(top, "rev-parse", "--verify", "--quiet", f"{sha}^", check=False).stdout.strip()
            diff = _git(top, "diff", "-U0", parent or EMPTY_TREE, sha, "--", prereg_rel).stdout
            edits += diff_edits(diff, _show(top, parent, prereg_rel) if parent else "", _show(top, sha, prereg_rel), sha[:7])
    # uncommitted changes count once any test results exist, committed or not
    diff = _git(top, "diff", "-U0", "HEAD", "--", prereg_rel, check=False).stdout
    if diff:
        edits += diff_edits(diff, _show(top, "HEAD", prereg_rel), prereg.read_text(encoding="utf-8"), "working tree")

    for e in edits:
        if e.ok:
            rep.allowed_edits += 1
        else:
            rep.edits.append(e)
    return rep
