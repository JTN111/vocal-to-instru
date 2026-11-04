import pretty_midi


def create_midi(notes, output_path, instrument_name="Piano"):
    """Create a MIDI file from detected musical notes."""

    midi = pretty_midi.PrettyMIDI()

    # Default MIDI program is acoustic grand piano.
    instrument = pretty_midi.Instrument(program=0)

    for item in notes:
        start = float(item["start"])
        end = float(item["end"])

        if end <= start:
            continue

        instrument.notes.append(
            pretty_midi.Note(
                velocity=100,
                pitch=int(item["note"]),
                start=start,
                end=end
            )
        )

    midi.instruments.append(instrument)
    midi.write(str(output_path))

    return output_path