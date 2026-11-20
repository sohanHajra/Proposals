"""Find claim tags in markdown and the number printed right before each one.

Fenced code blocks and inline code are skipped, so examples of the tag format in docs are not read as claims.
Numbers with no tag are listed by untagged.py.
"""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

TAG_START = re.compile(r"<!--\s*c:")
TAG = re.compile(r"<!--c:(?P<id>[A-Za-z0-9_.]+)-->")
# optional word "negative", number, optional %, optional short unit word, then the tag with nothing in between
NUMBER_BEFORE_TAG = re.compile(
    r"(?:(?<![\w.])(?P<neg>[Nn]egative)[ \u00a0]+)?"
    r"(?<![\w.])(?P<num>[-+\u2212]?\d[\d,]*(?:\.\d+)?)(?P<pct>%)?(?:[ \u00a0]?(?P<unit>[A-Za-z\u00b5]{1,12}))?$"
)
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`+[^`]*`+")


@dataclass
class Tag:
    file: str
    line: int
    claim_id: str
    printed: str = ""       # the number as written, without % or unit
    pct: bool = False
    unit: str = ""
    problem: str = ""       # set when the tag itself is malformed or has no number before it


def _blank_inline_code(line):
    return INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line)


def scan_text(text, fname="<text>"):
    tags = []
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = _blank_inline_code(line)
        good_starts = set()
        for m in TAG.finditer(line):
            good_starts.add(m.start())
            t = Tag(fname, lineno, m.group("id"))
            before = NUMBER_BEFORE_TAG.search(line[: m.start()])
            if before is None:
                t.problem = "no number right before the tag"
            else:
                t.printed = before.group("num").replace("\u2212", "-").replace(",", "")
                if before.group("neg"):
                    if t.printed[0] in "+-":
                        t.problem = "sign written twice (the word negative and a sign)"
                    else:
                        t.printed = "-" + t.printed
                t.pct = bool(before.group("pct"))
                t.unit = before.group("unit") or ""
            tags.append(t)
        for m in TAG_START.finditer(line):
            if m.start() not in good_starts:
                tags.append(Tag(fname, lineno, "?", problem="malformed tag (expected <!--c:id-->)"))
    return tags


def scan_dir(proposal_dir):
    """Scan every .md file under the proposal folder. Paths in the result are relative to it."""
    root = Path(proposal_dir)
    tags = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if any(part.startswith(".") or part == "data" for part in rel.parts[:-1]):
            continue
        tags.extend(scan_text(p.read_text(encoding="utf-8"), str(rel)))
    return tags


def printed_matches(printed, value):
    """True when value, rounded to the decimals printed, equals the printed number."""
    try:
        p = Decimal(printed)
        v = Decimal(repr(float(value)))
    except InvalidOperation:
        return False
    exp = p.as_tuple().exponent
    q = Decimal(1).scaleb(exp)
    return v.quantize(q, rounding=ROUND_HALF_UP) == p
