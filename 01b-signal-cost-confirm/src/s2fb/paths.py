"""Where 01.b keeps things. The 01 code is imported from ../01-signal-to-fill/src and is never edited."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
S2F_SRC = REPO / "01-signal-to-fill" / "src"
if str(S2F_SRC) not in sys.path:
    sys.path.insert(0, str(S2F_SRC))

DATA = Path(os.environ.get("S2FB_DATA", ROOT / "data"))
RAW = DATA / "raw"
DERIVED = DATA / "derived"
RESULTS = Path(os.environ.get("S2FB_RESULTS", ROOT / "results"))

BUILD_DAY = "2026-09-01"
S2F_TAG = "v0.1-signal-to-fill"
