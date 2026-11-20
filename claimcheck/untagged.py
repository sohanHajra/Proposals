"""List numbers in a proposal's public prose that carry no claim tag.

These are warnings, not failures. Many numbers in prose are not results (a delay I chose, a count of
data levels, a page number), so the list is something to work down by hand, either by tagging the
number, marking it, or adding a phrase to the proposal's ignore file.

Read: README.md, LAB_NOTEBOOK.md and FINAL_REPORT.md at the top of the proposal folder.

Skipped without a warning
- fenced code blocks, inline code, HTML comments, link targets and bare URLs
- blockquote lines and text inside double quotes, since those are someone else's words
- ISO dates, dates written with a month name, clock times, and four digit years from 1900 to 2099
- DOIs, arXiv ids and journal volume(issue) pairs
- numbers glued to letters, underscores, slashes or hyphens (H1b, RQ3, v2, file_10.csv, 01-signal)
- integers with a leading zero (01, 007), which are ids or numbering
- ordered list markers, and numbers right after Table, Figure, Section, page, Step, Appendix, Proposition, Lemma, seed and similar words
- numbers glued to a dot and a letter, like the ticker 1301.T
- numbers followed by a claim tag, by <!--cite--> (a number quoted from a paper) or by <!--nc--> (not a result)
- any number inside a phrase listed in the proposal's claimcheck_ignore.txt (one phrase per line, # for comments),
  matched as a whole, so a phrase never hides part of a longer number
"""

import re
from dataclasses import dataclass
from pathlib import Path

PUBLIC_FILES = ("README.md", "LAB_NOTEBOOK.md", "FINAL_REPORT.md")
IGNORE_FILE = "claimcheck_ignore.txt"

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`+[^`]*`+")
COMMENT = re.compile(r"<!--.*?-->")
LINK_TARGET = re.compile(r"\]\([^)]*\)")
URL = re.compile(r"(?:https?://|www\.)\S+|<[^>\s]+@[^>\s]+>")
QUOTED = re.compile(r"\"[^\"]*\"|\u201c[^\u201d]*\u201d")
BLOCKQUOTE = re.compile(r"^\s*>")
LIST_MARKER = re.compile(r"^(\s*)\d+[.)](?=\s)")
DOI = re.compile(r"\b10\.\d{4,9}/\S+")
ARXIV = re.compile(r"(?:arXiv:\s*)?\b\d{4}\.\d{4,5}(?:v\d+)?\b", re.IGNORECASE)
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"
DATE_WORDS = re.compile(
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTH}(?:,?\s+\d{{4}})?|\b{MONTH}\s+\d{{1,2}}(?:st|nd|rd|th)?\b(?:,?\s+\d{{4}})?"
)
VOLUME = re.compile(r"\b\d+\(\d+\)(?::\d+(?:-\d+)?)?")
CLOCK = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[ap]\.?m\.?)?", re.IGNORECASE)
REF_WORDS = re.compile(
    r"\b(?:Tables?|Fig(?:ure)?s?\.?|Sections?|Steps?|Appendix|Chapters?|Eq(?:uation)?s?\.?|pp?\.|pages?|"
    r"No\.|Python|version|Proposal|Proposition|Lemma|Definition|Corollary|Theorem|seed)\s*\d+(?:\.\d+)*(?:\s*(?:,|and|to)\s*\d+(?:\.\d+)*)*|§\s*\d+(?:\.\d+)*",
    re.IGNORECASE,
)
NUMBER = re.compile(
    r"(?<![\w.,/:#\\\-\u2212+])(?P<num>[-+\u2212]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)(?P<pct>%)?"
    r"(?![\w/\\]|\.\w|[,:]\d|-\w)"
)
# what may follow a number for it to count as tagged or marked
FOLLOW = re.compile(r"^%?(?:[ \u00a0]?[A-Za-z\u00b5]{1,12})?<!--(?:c:[A-Za-z0-9_.]+|cite|nc)-->")
YEAR = re.compile(r"^(?:19|20)\d\d$")
LEADING_ZERO = re.compile(r"^0\d+$")


@dataclass
class Untagged:
    file: str
    line: int
    number: str
    context: str


def _blank(pattern, text):
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def load_ignore(proposal_dir):
    p = Path(proposal_dir) / IGNORE_FILE
    if not p.is_file():
        return []
    phrases = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if s and not s.startswith("#"):
            phrases.append(s)
    return phrases


def _context(line, start, end, width=30):
    a = max(0, start - width)
    b = min(len(line), end + width)
    s = COMMENT.sub("", line[a:b]).strip()
    return ("..." if a > 0 else "") + s + ("..." if b < len(line) else "")


def scan_untagged_text(text, fname="<text>", ignore=()):
    found = []
    in_fence = False
    # a phrase only matches as a whole, so "1 ms" does not hide part of "0.1 ms" or "21 ms";
    # longer phrases go first so "5 ms" does not break up "1, 2 and 5 ms"
    ignore_res = [re.compile(r"(?<![\w.,])" + re.escape(p) + r"(?![\w%])") for p in sorted(ignore, key=len, reverse=True)]
    for lineno, original in enumerate(text.splitlines(), start=1):
        if FENCE.match(original):
            in_fence = not in_fence
            continue
        if in_fence or BLOCKQUOTE.match(original):
            continue
        # keep comments in `kept` so a tag after a number can be seen, blank them in `line`
        kept = _blank(INLINE_CODE, original)
        line = _blank(COMMENT, kept)
        for pat in (LINK_TARGET, URL, QUOTED, DOI, ARXIV, DATE_WORDS, VOLUME, CLOCK, REF_WORDS, *ignore_res):
            line = _blank(pat, line)
        line = LIST_MARKER.sub(lambda m: " " * len(m.group(0)), line)
        for m in NUMBER.finditer(line):
            num = m.group("num")
            digits = num.lstrip("+-\u2212")
            if YEAR.match(digits) and not m.group("pct"):
                continue
            if LEADING_ZERO.match(digits):
                continue
            if FOLLOW.match(kept[m.start("num") + len(num):]):
                continue
            found.append(Untagged(fname, lineno, num + (m.group("pct") or ""), _context(original, m.start(), m.end())))
    return found


def scan_untagged(proposal_dir):
    root = Path(proposal_dir)
    ignore = load_ignore(root)
    found = []
    for name in PUBLIC_FILES:
        p = root / name
        if p.is_file():
            found.extend(scan_untagged_text(p.read_text(encoding="utf-8"), name, ignore))
    return found
