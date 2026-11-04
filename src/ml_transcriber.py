from basic_pitch.inference import predict


def transcribe_with_basic_pitch(audio_path, output_path):
    """Transcribe audio into MIDI using Basic Pitch."""

    model_output, midi_data, note_events = predict(
        str(audio_path)
    )

    midi_data.write(str(output_path))

    notes = []

    for instrument in midi_data.instruments:
        for item in instrument.notes:
            notes.append({
                "note": int(item.pitch),
                "start": round(float(item.start), 3),
                "end": round(float(item.end), 3),
                "duration": round(
                    float(item.end - item.start), 3
                )
            })

    return notes