# midi2beep

Convert MIDI files to a monophonic sequence of `beep` commands (Linux-style syntax).  
The result is copied to the clipboard for easy pasting into your terminal.

This project was mostly vibecoded, but uhhh it works so ye :)  
Man, chatgpt can generate very nice readme files, I'm impressed xdd

---

## Installation

```bash
pip install mido pyperclip argparse
````

### Python libraries used:

* `mido`: for parsing MIDI files
* `pyperclip`: for copying the output to clipboard
* `argparse`, `sys`, `os`: for argument parsing and file validation

---

## Usage

```bash
python midi2beep.py -file FILE [options]
```

### Flags:

| Option         | Description                                                                 |
| -------------- | --------------------------------------------------------------------------- |
| `-file FILE`   | Path to the input `.mid` file (required)                                    |
| `-speed FLOAT` | Playback speed multiplier (default: `1.0`)                                  |
| `-channel INT` | Target MIDI channel (default: `0`)                                          |
| `-merge`       | Merge all channels and choose notes by priority                             |
| `-reverse`     | Reverse channel priority (used with `-merge`, usually improves melody flow) |

---

## How to play the output

### Linux (PC speaker)
1. Install the `beep` utility.
2. Setup proper permissions on `/dev/input/by-path/platform-pcspkr-event-spkr` (or just `chmod 777` it lmao, bad advice but works)
3. Paste the generated beep sequence into the terminal.

### Windows
1. Use [my fork](https://github.com/Sucharek233/beep-on-windows/releases) ([Download the zip directly](https://github.com/Sucharek233/beep-on-windows/releases/download/1.0/beep.zip)) of [pc-beeper](https://github.com/cocafe/pc-beeper) adapted for Linux-compatible syntax:
2. Extract the zip file.
3. Open a command prompt as Administrator and navigate to the extracted folder.
4. Paste the output from this tool.

---

## Common Issues

### Getting no sound?

* Your system likely doesn't have a physical PC speaker.
* Most laptops use emulated beepers or none at all — and these may not produce any sound.
* This tool **requires** access to an actual or emulated PC speaker.

---

## Examples

* Convert channel 2 only:

  ```bash
  python midi2beep.py -file midi.mid -channel 2
  ```

* Convert entire file with all channels:

  ```bash
  python midi2beep.py -file midi.mid -merge
  ```

* Convert entire file and reverse channel priority (**recommended, usully gives better results**):

  ```bash
  python midi2beep.py -file midi.mid -merge -reverse
  ```

---

## How does it work?

* Parses the MIDI file using `mido`, collecting all events from all tracks.
* Merges and sorts events by absolute time (converted from ticks to seconds).
* Filters channels:
  * If `-channel` is set: processes only that channel.
  * If `-merge` is set: uses all channels, in priority order (optionally reversed).
* Plays only **one note at a time** (monophonic mode):
  * When a new note starts, the previous one is immediately cut off.
  * This compresses the melody line into a single stream but may lose overlapping harmonies.

* Adds delay for silent gaps between notes.
* Copies the result to your clipboard, ready to paste into a terminal for playback.