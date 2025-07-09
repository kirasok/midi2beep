import mido
import sys
import argparse
import os


def note_to_freq(note: int) -> float:
    return 440.0 * 2 ** ((note - 69) / 12)


def extract_monophonic_notes(
    midi_path: str, target_channel: int = 0, merge: int = 0, reverse: int = 0
):
    mid = mido.MidiFile(midi_path)
    ticks_per_beat = mid.ticks_per_beat
    default_tempo = 500_000  # µs per beat = 120 BPM

    # Merge all events from all tracks into one timeline
    events = []
    for track in mid.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            events.append((abs_tick, msg))

    # Sort all by absolute time (tick)
    if reverse:
        events.reverse()
    events.sort(key=lambda x: x[0])

    current_tick = 0
    current_time = 0.0
    current_tempo = default_tempo

    timeline = []
    last_event_time = 0.0

    active_note = None
    active_note_start_time = 0.0

    for abs_tick, msg in events:
        delta_ticks = abs_tick - current_tick
        delta_time = mido.tick2second(delta_ticks, ticks_per_beat, current_tempo)
        current_time += delta_time
        current_tick = abs_tick

        # Skip if channel doesn't match (if filtering)
        if not merge:
            if hasattr(msg, "channel") and target_channel is not None:
                if msg.channel != target_channel:
                    continue

        if msg.type == "set_tempo":
            current_tempo = msg.tempo

        elif msg.type == "note_on" and msg.velocity > 0:
            # New note starts

            # First, stop the currently active note if one is playing
            if active_note is not None:
                duration = current_time - active_note_start_time
                if active_note_start_time > last_event_time:
                    delay = active_note_start_time - last_event_time
                    timeline.append((0, 1, round(delay, 6)))
                timeline.append(
                    (
                        active_note,
                        round(note_to_freq(active_note), 2),
                        round(duration, 6),
                    )
                )
                last_event_time = current_time

            # Start the new note
            active_note = msg.note
            active_note_start_time = current_time

        elif msg.type in ("note_off", "note_on") and (
            msg.type == "note_off" or msg.velocity == 0
        ):
            # Stop the note only if it is currently active
            if active_note == msg.note:
                duration = current_time - active_note_start_time
                if active_note_start_time > last_event_time:
                    delay = active_note_start_time - last_event_time
                    timeline.append((0, 1, round(delay, 6)))
                timeline.append(
                    (
                        active_note,
                        round(note_to_freq(active_note), 2),
                        round(duration, 6),
                    )
                )
                last_event_time = current_time
                active_note = None

    # If any note was left hanging, close it at end of track
    if active_note is not None:
        duration = current_time - active_note_start_time
        if active_note_start_time > last_event_time:
            delay = active_note_start_time - last_event_time
            timeline.append((0, 1, round(delay, 6)))
        timeline.append(
            (active_note, round(note_to_freq(active_note), 2), round(duration, 6))
        )

    return timeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a MIDI file into a beep sequence. Output will be copied to clipboard."
    )

    parser.add_argument("-file", required=True, help="Path to the input MIDI file")
    parser.add_argument("-out", required=True, help="Path to the output script")
    parser.add_argument(
        "-speed", type=float, default=1.0, help="Speed multiplier (default: 1.0)"
    )
    parser.add_argument("-channel", type=int, help="Target MIDI channel (default: 0)")
    parser.add_argument("-merge", action="store_true", help="Merge all channels")
    parser.add_argument(
        "-reverse",
        action="store_true",
        help="Reverse channel priority (Use with merge). Usually gives better results if enabled",
    )

    args = parser.parse_args()

    if not args.file or not args.out:
        parser.print_help()
        sys.exit(1)

    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' not found or not readable.")
        sys.exit(1)

    notes = extract_monophonic_notes(args.file, args.channel, args.merge, args.reverse)

    speed = 1000 * args.speed
    final = f"beep "
    for n, f, d in notes:
        if d == 0:
            continue
        if f == 1:
            final += f"-D {d * speed} "
        else:
            final += f"-n -f {f} -l {d * speed} "

    with open(args.out, "w") as f:
        if not f.writable():
            print(f"Error: File '{args.out}' is not writable")
            sys.exit(1)

        f.write(final)
    print(f"Wrote beep script to path {args.out}")
