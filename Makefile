# Local git hooks (not versioned in .git, so `make hooks` after every fresh clone)
hooks:
	printf '#!/bin/sh\nexec python3 "$$(git rev-parse --show-toplevel)/scripts/guard" commit-msg "$$1"\n' > .git/hooks/commit-msg
	printf '#!/bin/sh\nexec python3 "$$(git rev-parse --show-toplevel)/scripts/guard" pre-commit\n' > .git/hooks/pre-commit
	chmod +x .git/hooks/commit-msg .git/hooks/pre-commit

.PHONY: hooks
