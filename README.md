<div align="center">
<img src="monogram.svg" alt="clipboard-picker monogram" width="128">

# clipboard-picker

</div>

Hi. This is a clipboard history picker for Wayland.

The picker is built around `cliphist`, `fzf`, and the `kitty` terminal. It supports previewing text, binary payloads, and inline images (via `kitten icat`). Selected entries may either be copied back to the system's clipboard or deleted in place.

## Requirements

- A Wayland session (`WAYLAND_DISPLAY` set) with `wl-copy` and an active `cliphist` watcher (for example, `wl-paste --watch cliphist store`)
- `kitty` (with `kitten`), `fzf`, and ImageMagick (`magick`, used to query image dimensions and convert formats for preview)
- `notify-send` (optional, for desktop error notifications when launched without a terminal)
- Python `3.11+`

## Installation

Install the `clipboard` command with `uv`:

```bash
uv tool install git+https://github.com/athaurian/clipboard-picker
```

Or run directly from a checkout via `./bin/clipboard` (for example, by symlinking `./bin/clipboard` to `~/.local/bin/clipboard`).

## Usage and Sway integration

```bash
clipboard
```

When you run `clipboard` from an interactive terminal, `fzf` opens directly in that terminal. When triggered from a window-manager keybinding (where stdout/stdin are not attached to a TTY), `clipboard` automatically relaunches itself inside a dedicated `kitty` window with `--title clipboard_term` so you can bind it directly in Sway:

```ini
for_window [app_id="kitty" title="^clipboard_term$"] floating enable, resize set 900 600, move position center
bindsym $mod+Ctrl+v exec clipboard
```

### Keys inside the picker

| Key                 | Action                                                            |
| :------------------ | :---------------------------------------------------------------- |
| `Enter`             | Copy the highlighted entry to the Wayland clipboard and exit      |
| `Delete` / `Ctrl-D` | Delete the highlighted entry from `cliphist` and refresh the list |
| `Esc` / `Ctrl-C`    | Exit without modifying the current clipboard                      |

## Preview behavior

- **Images**: Rendered inline with `kitten icat` when running inside `kitty`, or summarized by format and pixel dimensions via `magick` in other terminals.
- **Text and UTF-16 fallbacks**: Decodes UTF-8 first, then inspects byte patterns to decode UTF-16LE/BE payloads even when the source application omitted a Byte Order Mark (BOM).
- **Binary data**: Summarizes payload size instead of dumping raw control bytes to the terminal.

## Options and environment

| Flag / Variable                   | Default            | Description                                                                 |
| :-------------------------------- | :----------------- | :-------------------------------------------------------------------------- |
| `--backend` / `CLIPBOARD_BACKEND` | `cliphist`         | Clipboard history backend to query                                          |
| `--db-path PATH`                  | `cliphist` default | Path to a custom `cliphist` database file                                   |
| `PICKER_NO_RELAUNCH=1`            | Unset              | Do not spawn a new `kitty` window when invoked without a TTY (fail instead) |

### Exit codes

- `0`: Entry copied, or user cancelled cleanly in `fzf`
- `1`: Runtime or backend error (missing binary, unreadable database, or absent `WAYLAND_DISPLAY`)
- `2`: Invalid CLI arguments

## Development

```bash
make test
make lint
make format
```

## License

MIT
