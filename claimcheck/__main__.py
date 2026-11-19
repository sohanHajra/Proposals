"""Command line entry point. Run from the repo root as `python -m claimcheck <proposal_dir>`."""

import argparse
import sys
from pathlib import Path

from . import __version__

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_NOTHING_CHECKED = 2


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="claimcheck",
        description="Check that numbers in a proposal's markdown match its results files.",
    )
    parser.add_argument("proposal_dir", help="proposal folder, for example 01-signal-to-fill")
    parser.add_argument("--version", action="version", version=f"claimcheck {__version__}")
    args = parser.parse_args(argv)

    root = Path(args.proposal_dir)
    if not root.is_dir():
        print(f"claimcheck: {root} is not a folder", file=sys.stderr)
        return EXIT_NOTHING_CHECKED

    claims_file = root / "claims.yaml"
    if not claims_file.is_file():
        print(f"claimcheck: no claims.yaml in {root}, nothing checked")
        return EXIT_NOTHING_CHECKED

    print(f"claimcheck: found {claims_file}, but no checks are built yet, nothing checked")
    return EXIT_NOTHING_CHECKED


if __name__ == "__main__":
    sys.exit(main())
