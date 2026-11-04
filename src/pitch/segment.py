import librosa
import numpy as np


def segment_notes(times, midi_values, min_duration=0.08):
    """Convert pitch frames into individual note events."""

    notes = []

    if len(times) == 0:
        return notes

    frame_duration = (
        float(times[1] - times[0])
        if len(times) > 1 else 0.01
    )

    current_note = None
    start_time = None

    def save_note(note, start, end):
        if note is None or end - start < min_duration:
            return

        notes.append({
            "note": int(note),
            "note_name": librosa.midi_to_note(int(note)),
            "start": round(float(start), 3),
            "end": round(float(end), 3),
            "duration": round(float(end - start), 3)
        })

    for time, midi in zip(times, midi_values):

        if not np.isfinite(midi):
            if current_note is not None:
                save_note(current_note, start_time, time)

            current_note = None
            start_time = None
            continue

        note_number = int(round(midi))

        if current_note is None:
            current_note = note_number
            start_time = float(time)

        elif note_number != current_note:
            save_note(current_note, start_time, time)

            current_note = note_number
            start_time = float(time)

    if current_note is not None:
        save_note(
            current_note,
            start_time,
            float(times[-1]) + frame_duration
        )

    return notes