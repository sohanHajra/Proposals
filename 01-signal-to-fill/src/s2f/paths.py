from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get("S2F_DATA", ROOT / "data"))
RAW = DATA / "raw"
RESULTS = ROOT / "results"
