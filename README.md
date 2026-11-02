# clipboard-picker

An `fzf` clipboard history picker with a preview pane, backed by
`cliphist` and `wl-clipboard`.

The list shows one entry per line. Text entries preview in full. Image
entries render through kitty's Unicode placeholder protocol, which fzf
can erase on redraw. Selecting an entry copies it back to the clipboard.

## Requirements

- Python 3.11 or newer
- `cliphist`, `wl-clipboard` (`wl-copy`), `fzf`, and ImageMagick (`magick`)
- `kitty` for image previews and for the floating window when the picker
  is started without a terminal
- `notify-send` for error notifications

## Usage

```sh
./bin/clipboard
```

`PICKER_NO_RELAUNCH=1` stops the picker from relaunching itself inside
kitty when stdout is not a terminal.

## Tests

```sh
make check
```

That runs the linter, the formatter check, the type checker, and the whole
test suite. To run only the tests:

```sh
PYTHONPATH=lib python3 -m unittest discover -s lib/picker_lib/tests
```

## Layout

- `lib/picker_lib/backend.py` defines the clipboard store protocol.
  `cliphist.py` is the Wayland implementation, and an X11 backend can be
  added without touching the UI.
- `lib/picker_lib/ui.py` owns the `fzf` invocation.
- `lib/picker_lib/preview.py` renders text and image previews.
- `lib/picker_lib/tests/` covers the backend, model, preview, and UI.

## License

MIT. See `LICENSE`.
