"""Source checks on a proposal's LITERATURE_REVIEW.md.

1. Reading depth. Every row of a table in LITERATURE_REVIEW.md that has a depth column (header
   "Read at", "Reading depth" or "Depth") must say how deeply the work was read. The cell must contain
   one of the depth words below. The first one in the cell is the depth reported.
2. Unverified not cited. Each bullet under a heading containing "Unverified" names a work I have not
   opened. Its first author's surname and year are read from the bullet, and every other markdown file
   in the proposal is searched for that surname followed by the year on the same line (within 60
   characters). A match outside the Unverified section fails, unless <!--unread--> follows the citation,
   which says the mention is context and not evidence.

Skipped. Fenced code and inline code. INTEGRITY_LOG.md, because recording what was and was not read
is what that file is for. Anything under data/ or a dot folder.

What it cannot do. It can't tell whether the depth written down is true, or whether a mention without
a year (just a surname) leans on an unread source. A person still reads those.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

REVIEW_FILE = "LITERATURE_REVIEW.md"
SKIP_FILES = ("INTEGRITY_LOG.md",)
DEPTH_HEADERS = ("read at", "reading depth", "depth")
DEPTH_WORDS = ("full text", "abstract", "listing")
UNREAD_MARK = "<!--unread-->"
WINDOW = 60

HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`+[^`]*`+")
BULLET = re.compile(r"^\s*[-*+]\s+(?P<body>.+)$")
AUTHOR_YEAR = re.compile(r"^(?P<authors>[^()]+?)\s*\((?P<year>(?:19|20)\d\d)[a-z]?\)")
SEPARATOR = re.compile(r"^:?-{3,}:?$")


@dataclass
class DepthRow:
    line: int
    work: str
    depth: str = ""        # the depth word found, empty when none
    cell: str = ""


@dataclass
class UnverifiedEntry:
    line: int
    text: str
    surname: str = ""
    year: str = ""
    problem: str = ""


@dataclass
class Citation:
    file: str
    line: int
    entry: UnverifiedEntry
    context: str
    marked: bool = False   # <!--unread--> follows it


@dataclass
class SourceReport:
    found: bool = False                       # LITERATURE_REVIEW.md exists
    depth_table: bool = False                 # at least one table with a depth column
    unverified_section: bool = False          # an Unverified heading exists
    rows: list = field(default_factory=list)
    unverified: list = field(default_factory=list)
    citations: list = field(default_factory=list)
    problems: list = field(default_factory=list)   # file level problems, as strings

    @property
    def failures(self):
        n = len(self.problems)
        n += sum(1 for r in self.rows if not r.depth)
        n += sum(1 for e in self.unverified if e.problem)
        n += sum(1 for c in self.citations if not c.marked)
        return n


def _blank_inline_code(line):
    return INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line)


def _cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _depth_of(cell):
    low = cell.lower()
    hits = [(low.find(w), w) for w in DEPTH_WORDS if w in low]
    return min(hits)[1] if hits else ""


def _work_name(cell):
    m = AUTHOR_YEAR.match(cell.strip())
    if m:
        return f"{m.group('authors').strip()} ({m.group('year')})"
    return cell.strip()[:60]


def _first_surname(authors):
    first = re.split(r",|&|\band\b|\bet al\.?", authors)[0].strip()
    return first.strip("*_ ")


def read_review(text):
    """Parse depth tables and the Unverified list.

    Returns (rows, entries, unverified_lines, problems, depth_table, found_section).
    """
    lines = text.splitlines()
    rows, entries, problems = [], [], []
    unverified_lines = set()
    depth_table = False
    in_fence = False
    section_level = None          # heading level of the Unverified section while inside it
    found_section = False
    i = 0
    while i < len(lines):
        line = lines[i]
        lineno = i + 1
        if FENCE.match(line):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue
        h = HEADING.match(line)
        if h:
            level = len(h.group(1))
            if section_level is not None and level <= section_level:
                section_level = None
            if "unverified" in h.group(2).lower():
                section_level = level
                found_section = True
                unverified_lines.add(lineno)
            i += 1
            continue
        if section_level is not None:
            unverified_lines.add(lineno)
            b = BULLET.match(line)
            if b:
                body = b.group("body").strip()
                e = UnverifiedEntry(lineno, body[:80])
                m = AUTHOR_YEAR.match(body)
                if m:
                    e.surname = _first_surname(m.group("authors"))
                    e.year = m.group("year")
                if not e.surname or not e.year:
                    e.problem = "can't read a first author and (year) at the start of this entry"
                entries.append(e)
            i += 1
            continue
        # a table: header row, separator row, then body rows
        if line.lstrip().startswith("|") and i + 1 < len(lines):
            sep = _cells(lines[i + 1])
            if sep and all(SEPARATOR.match(c.replace(" ", "")) for c in sep if c):
                header = [c.lower().strip("*_ ") for c in _cells(line)]
                col = next((k for k, c in enumerate(header) if c in DEPTH_HEADERS), None)
                j = i + 2
                while j < len(lines) and lines[j].lstrip().startswith("|"):
                    if col is not None:
                        cells = _cells(lines[j])
                        cell = cells[col] if col < len(cells) else ""
                        rows.append(DepthRow(j + 1, _work_name(cells[0] if cells else ""), _depth_of(cell), cell))
                    j += 1
                if col is not None:
                    depth_table = True
                i = j
                continue
        i += 1
    if not depth_table:
        problems.append(f"{REVIEW_FILE} has no table with a 'Read at' column")
    if not found_section:
        problems.append(f"{REVIEW_FILE} has no Unverified section (an empty one is fine)")
    return rows, entries, unverified_lines, problems, depth_table, found_section


def _citation_pattern(entry):
    return re.compile(
        r"(?<!\w)" + re.escape(entry.surname) + r"(?!\w)" + r"[^\n]{0,%d}?(?<!\d)" % WINDOW + entry.year + r"[a-z]?(?!\d)"
    )


def find_citations(text, fname, entries, skip_lines=()):
    found = []
    pats = [(e, _citation_pattern(e)) for e in entries if e.surname and e.year]
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or lineno in skip_lines:
            continue
        line = _blank_inline_code(line)
        for e, pat in pats:
            for m in pat.finditer(line):
                after = line[m.end():]
                marked = re.match(r"^\)?\s*" + re.escape(UNREAD_MARK), after) is not None
                ctx = line[max(0, m.start() - 20): m.end() + 20].strip()
                found.append(Citation(fname, lineno, e, ctx, marked))
    return found


def check_sources(proposal_dir):
    root = Path(proposal_dir)
    rep = SourceReport()
    review = root / REVIEW_FILE
    if not review.is_file():
        return rep
    rep.found = True
    text = review.read_text(encoding="utf-8")
    (rep.rows, rep.unverified, unverified_lines, rep.problems,
     rep.depth_table, rep.unverified_section) = read_review(text)

    # an unverified work that also has a row in a depth table is listed as both read and unread
    for e in rep.unverified:
        if e.problem:
            continue
        for r in rep.rows:
            if r.work.startswith(e.surname) and f"({e.year})" in r.work:
                e.problem = f"also listed as read ({r.depth or 'no depth'}) on line {r.line}"

    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if any(part.startswith(".") or part == "data" for part in rel.parts[:-1]):
            continue
        if rel.name in SKIP_FILES and len(rel.parts) == 1:
            continue
        body = p.read_text(encoding="utf-8")
        if rel == Path(REVIEW_FILE):
            # everything in the review outside the Unverified section is read, table rows included
            rep.citations.extend(find_citations(body, str(rel), rep.unverified, unverified_lines))
        else:
            rep.citations.extend(find_citations(body, str(rel), rep.unverified))
    return rep
