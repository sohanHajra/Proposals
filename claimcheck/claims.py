"""Load claims.yaml and compare each claim with the field it points to in its results file."""

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REQUIRED = ("file", "path", "value", "tol")
KNOWN = set(REQUIRED) | {"unit", "scale"}


class ClaimsFileError(Exception):
    """claims.yaml could not be read or is not a mapping of claim ids to entries."""


@dataclass
class Claim:
    id: str
    file: str = ""
    path: str = ""
    value: float = math.nan
    tol: float = math.nan
    unit: str = ""
    scale: float = 1.0
    errors: list = field(default_factory=list)


@dataclass
class DataResult:
    claim: Claim
    ok: bool
    stored: object = None
    reason: str = ""


def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def load_claims(claims_path):
    """Return {claim_id: Claim}. Entries with bad fields keep their problems in Claim.errors."""
    claims_path = Path(claims_path)
    try:
        raw = yaml.safe_load(claims_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ClaimsFileError(f"{claims_path} is not valid YAML: {exc}") from exc
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ClaimsFileError(f"{claims_path} must map claim ids to entries")

    claims = {}
    for cid, entry in raw.items():
        cid = str(cid)
        c = Claim(id=cid)
        if not isinstance(entry, dict):
            c.errors.append("entry is not a mapping")
            claims[cid] = c
            continue
        missing = [k for k in REQUIRED if k not in entry]
        if missing:
            c.errors.append("missing " + ", ".join(missing))
        extra = sorted(set(entry) - KNOWN)
        if extra:
            c.errors.append("unknown field " + ", ".join(map(str, extra)))
        c.file = str(entry.get("file", ""))
        c.path = str(entry.get("path", ""))
        c.unit = str(entry.get("unit", "") or "")
        for name in ("value", "tol", "scale"):
            if name not in entry:
                continue
            v = entry[name]
            if not _is_number(v):
                c.errors.append(f"{name} is not a number")
            else:
                setattr(c, name, float(v))
        if "tol" in entry and _is_number(entry["tol"]) and entry["tol"] < 0:
            c.errors.append("tol is negative")
        claims[cid] = c
    return claims


def resolve(data, dotted):
    """Follow a dotted path through nested dicts and lists. Raises KeyError with the part that failed."""
    node = data
    walked = []
    for part in dotted.split("."):
        walked.append(part)
        if isinstance(node, dict):
            if part not in node:
                raise KeyError(".".join(walked))
            node = node[part]
        elif isinstance(node, list):
            if not part.lstrip("-").isdigit():
                raise KeyError(".".join(walked))
            i = int(part)
            if not -len(node) <= i < len(node):
                raise KeyError(".".join(walked))
            node = node[i]
        else:
            raise KeyError(".".join(walked))
    return node


def check_data(claim, proposal_dir, _cache=None):
    """Compare a claim's value with its results field. Returns a DataResult."""
    if claim.errors:
        return DataResult(claim, False, reason="bad entry in claims.yaml: " + "; ".join(claim.errors))
    cache = _cache if _cache is not None else {}
    fpath = Path(proposal_dir) / claim.file
    if fpath not in cache:
        if not fpath.is_file():
            cache[fpath] = FileNotFoundError(claim.file)
        else:
            try:
                cache[fpath] = json.loads(fpath.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                cache[fpath] = ValueError(f"{claim.file} is not valid JSON ({exc})")
    data = cache[fpath]
    if isinstance(data, FileNotFoundError):
        return DataResult(claim, False, reason=f"results file not found: {claim.file}")
    if isinstance(data, ValueError):
        return DataResult(claim, False, reason=str(data))
    try:
        stored = resolve(data, claim.path)
    except KeyError as exc:
        return DataResult(claim, False, reason=f"field not found: {exc.args[0]} in {claim.file}")
    if not _is_number(stored):
        return DataResult(claim, False, stored=stored, reason=f"field {claim.path} is not a number ({stored!r})")
    scaled = stored * claim.scale
    gap = abs(scaled - claim.value)
    if gap > claim.tol:
        return DataResult(
            claim, False, stored=scaled,
            reason=f"file has {scaled:.10g}, claim says {claim.value:.10g}, off by {gap:.3g} (tol {claim.tol:g})",
        )
    return DataResult(claim, True, stored=scaled)
