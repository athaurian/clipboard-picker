"""Clipboard history picker combining cliphist, fzf, and a preview pane.

The full entry appears in the preview pane; images render through kitty's
Unicode placeholder protocol, which fzf can erase on redraw. A selection
is copied back with wl-copy. ``fzf`` needs a terminal for its interface:
when stdout is not a terminal (for example when started from a window
manager keybind, whose stdin is the login VT and not the Wayland
session), the picker relaunches itself inside a floating kitty window
unless ``PICKER_NO_RELAUNCH`` is set.
"""

import argparse
import os
import shlex
import shutil
import sys
from pathlib import Path
from signal import SIG_DFL, SIGPIPE, signal

from picker_lib import backend, model, notify, preview, ui
from picker_lib.backend import EntryNotFoundError

APP_NAME = "clipboard"


def relaunch_command() -> list[str]:
    """Return the command that re-runs the picker for fzf and kitty."""
    entry = shutil.which(sys.argv[0]) or sys.argv[0]
    return [sys.executable, str(Path(entry).resolve())]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse picker options."""
    parser = argparse.ArgumentParser(description="Pick clipboard history.")
    parser.add_argument(
        "--preview",
        metavar="ID",
        default=None,
        help="print the preview for entry ID and exit (fzf hook)",
    )
    parser.add_argument(
        "--backend",
        default=None,
        help="clipboard backend (default: autodetect from the session)",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="cliphist database path (defaults to cliphist's own)",
    )
    return parser.parse_args(argv)


def preview_mode(eid: str, db_path: str | None, backend_name: str | None) -> int:
    """Render the preview for entry ``eid``.

    Fzf calls this once per highlighted entry.
    """
    # Fzf closes the pipe every time the highlight changes, so a preview
    # that outlives its reader must exit quietly instead of tracebacking.
    signal(SIGPIPE, SIG_DFL)
    if not eid.isdigit():
        print(f"error: preview id must be numeric: {eid!r}", file=sys.stderr)
        return 2
    store = backend.get_backend(backend_name)
    if store is None:
        print("error: no clipboard backend for this session", file=sys.stderr)
        return 1
    try:
        data = store.decode(eid.encode(), db_path)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    preview.render(data)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the clipboard picker and return the process exit status."""
    raw_args = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(raw_args)
    if args.preview is not None:
        return preview_mode(args.preview, args.db_path, args.backend)

    store = backend.get_backend(args.backend)
    if store is None:
        notify.send(
            "no clipboard backend for this session",
            app_name=APP_NAME,
            urgency="critical",
        )
        return 1
    if not store.available():
        notify.send(
            f"{store.name} not installed", app_name=APP_NAME, urgency="critical"
        )
        return 1
    if not ui.have("fzf"):
        notify.send("fzf not installed", app_name=APP_NAME, urgency="critical")
        return 1

    # Check history before relaunching into kitty, so an empty history
    # notifies directly instead of flashing a terminal first.
    try:
        entries = store.list_entries(args.db_path)
    except (FileNotFoundError, RuntimeError) as exc:
        notify.send(str(exc), app_name=APP_NAME, urgency="critical")
        return 1
    if not entries:
        notify.send("clipboard history empty", app_name=APP_NAME)
        return 0

    if not sys.stdout.isatty() and not os.environ.get("PICKER_NO_RELAUNCH"):
        relaunch = [*relaunch_command(), *raw_args]
        if ui.relaunch_in_kitty(relaunch):
            return 0  # pragma: no cover - process replaced by kitty
        notify.send(
            "kitty is required to show the picker",
            app_name=APP_NAME,
            urgency="critical",
        )
        return 1

    lines = [model.format_entry(eid, display) for eid, display in entries]
    preview_argv = [*relaunch_command(), "--preview", "{1}"]
    if args.backend is not None:
        preview_argv += ["--backend", args.backend]
    if args.db_path is not None:
        preview_argv += ["--db-path", args.db_path]
    selected = ui.run_fzf(
        lines,
        prompt=ui.FZF_PROMPT_CLIPBOARD,
        header="clipboard history",
        preview_cmd=shlex.join(preview_argv),
    )
    if not selected:
        return 0

    try:
        data = store.decode(selected.encode(), args.db_path)
    except EntryNotFoundError:
        notify.send("clipboard entry no longer available", app_name=APP_NAME)
        return 0
    except (FileNotFoundError, RuntimeError) as exc:
        notify.send(str(exc), app_name=APP_NAME, urgency="critical")
        return 1
    try:
        store.copy_to_clipboard(data)
    except (FileNotFoundError, RuntimeError) as exc:
        notify.send(str(exc), app_name=APP_NAME, urgency="critical")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
