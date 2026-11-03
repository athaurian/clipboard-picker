# clipboard-picker

Hi. This is a simple clipboard history picker for Wayland that uses the `kitty`
terminal. Here's how it works:

- In the background, `cliphist` records what you copy.
- The interface uses `fzf` to present the clipboard history with a preview pane.
- When you select an entry, the program runs `wl-copy` to put it back on the
  clipboard.

Let's say you copy a command from a terminal, then an image, then a URL. The
clipboard now holds only the URL, but the picker remembers everything you
copied, so you can bring each one back, or look at the image through the
preview pane before choosing it.

I use this in [my setup](https://github.com/athaurian/dotfiles).

## Terms

Here are some terms that will be used throughout this page:

| Term         | Meaning                                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------- |
| History      | The clipboard entries `cliphist` has stored. Copying something new adds an entry and leaves the older ones in place.      |
| Entry        | One item in the history, identified by a numeric id.                                                                      |
| Backend      | The program that supplies the history and copies entries back. `cliphist` is the Wayland implementation and the only one. |
| Preview pane | The right-hand half of the picker that shows the highlighted entry.                                                       |

Below, "history" means clipboard history, and "picker" means this program.

## Requirements

- Python 3.11 or newer.
- A Wayland session with `WAYLAND_DISPLAY` set. There is no X11 backend.
- `cliphist` for the history, `wl-clipboard` (`wl-copy`) for copying back, and
  `fzf` for the interface.
- ImageMagick (`magick`) to recognize images, and `kitten` from kitty to draw
  them.
- `kitty` to open the picker window when it starts without a terminal.
- `notify-send` for error and empty-history messages. Notifications are
  skipped silently when it is missing.

## Install

Install the package to get a `clipboard` command on `PATH`:

```sh
uv tool install git+https://github.com/athaurian/clipboard-picker
```

Or keep `bin/` and `lib/` together and run the checkout directly:

```sh
git clone https://github.com/athaurian/clipboard-picker
cd clipboard-picker
./bin/clipboard
```

To call a checkout by name without installing, symlink `bin/clipboard` into
`~/.local/bin`:

```sh
ln -s "$PWD/bin/clipboard" ~/.local/bin/clipboard
```

## Usage

Start the picker from a terminal:

```sh
./bin/clipboard
```

| Key                              | Action                               |
| -------------------------------- | ------------------------------------ |
| Type                             | Filter entries by their summary      |
| `Up`, `Down`, `Ctrl-p`, `Ctrl-n` | Move the highlight                   |
| `Return`                         | Copy the highlighted entry and close |
| `Esc`, `Ctrl-C`                  | Close without copying                |

If the selected entry has been removed from the history since the list was
drawn, the picker says so in a notification and leaves the clipboard alone.

When run normally, the picker exits 0 after copying, canceling, or reporting
an empty history, and 1 when a dependency is missing or the backend fails.

### Preview fallbacks

| Content                       | Shown as                   |
| ----------------------------- | -------------------------- |
| Text (UTF-8)                  | The full text              |
| Text (UTF-16 without a BOM)   | The decoded text           |
| Image                         | The image, inline          |
| Image that cannot be rendered | `[image: N bytes]`         |
| Anything else                 | `[N bytes of binary data]` |

Browsers sometimes put copied content on the clipboard as UTF-16 without a
byte-order mark, so the preview decodes that rather than showing a binary blob.

### Options

| Option           | Effect                                                                                        |
| ---------------- | --------------------------------------------------------------------------------------------- |
| `--backend NAME` | Use a specific backend. `cliphist` is the only one.                                           |
| `--db-path PATH` | Use a specific `cliphist` database instead of `cliphist`'s default.                           |
| `--preview ID`   | Print the preview for an entry and exit. `fzf` calls this, so it is not normally run by hand. |

### Environment

| Variable             | Effect                                                                                                                                     |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `PICKER_NO_RELAUNCH` | Any non-empty value stops the relaunch into kitty when stdout is not a terminal.                                                           |
| `CLIPBOARD_BACKEND`  | Backend to use when `--backend` is not given.                                                                                              |
| `WAYLAND_DISPLAY`    | Session detection. When set, the `cliphist` backend is selected. When unset, the picker reports that the session has no supported backend. |

`--backend` wins over `CLIPBOARD_BACKEND`, which wins over detection.

## Running from a keybinding

`fzf` needs a terminal. Started from a window manager keybinding, the picker's
stdout is not a terminal, so it re-executes itself inside a floating `kitty`
window titled `clipboard_term`. The title lets the compositor float and mark
the window. On Sway, add these lines to the config:

```conf
for_window [app_id="kitty" title="clipboard_term"] floating enable, resize set width 75 ppt height 70 ppt, move position center
bindsym $mod+Ctrl+v exec ~/.local/bin/clipboard
```

If kitty is not installed, the picker sends a notification instead of opening
a window.

## Development

The `Makefile` provides these targets:

| Target        | Action                                                                                    |
| ------------- | ----------------------------------------------------------------------------------------- |
| `make check`  | Runs the linter, formatter check, type check, and unit tests. Stops at the first problem. |
| `make lint`   | Runs the linter, formatter check, and type check without modifying files.                 |
| `make format` | Applies ruff fixes and formatting.                                                        |
| `make test`   | Runs the unit tests.                                                                      |

The targets use `uv` to pull pinned versions of `ruff` and `mypy` on demand, so
no project virtual environment is needed.

To run the unit tests without `make`:

```sh
PYTHONPATH=lib python3 -m unittest discover -s lib/picker_lib/tests
```

## License

Released under the MIT license. See [LICENSE](LICENSE) for the full text.
