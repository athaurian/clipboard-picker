# AGENTS.md

## Repository

Wayland clipboard history picker. `cliphist` records copies, `fzf` presents
them with a preview, and `wl-copy` restores the selected entry. The picker
relaunches inside a floating `kitty` window when it starts without a terminal.

## Commands

```bash
make check    # lint, format check, mypy, unit tests
make lint     # no writes
make format   # apply ruff fixes and formatting
make test
```

## Rules

- Clipboard history is sensitive. Never print, log, copy, or commit an entry,
  a database, or a preview image from a real session.
- Tests must use fixtures and a temporary database. Never read or write the
  user's live `cliphist` database or clipboard.
- `cliphist` is the only backend. Do not add a second backend without a
  concrete requirement.
- Do not write history or previews into the repository or `/tmp/opencode/`
  from a real session.

## Constraints

- Wayland only; there is no X11 backend.
- Requires `cliphist`, `wl-clipboard`, `fzf`, `kitty`, ImageMagick `magick`,
  and `kitten`.
- `make` pulls pinned `ruff` and `mypy` through `uv`; no project virtualenv is
  needed.
