import numpy as np

SCALE_INTERVALS = {
    "Major": [0, 2, 4, 5, 7, 9, 11],
    "Minor": [0, 2, 3, 5, 7, 8, 10]
}

NOTE_NAMES = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
]

AUTOTUNE_STRENGTHS = {
    "Low": 30,
    "Medium": 65,
    "High": 100
}


def correct_pitch(midi_values, key, scale, level="Medium"):

    if scale not in SCALE_INTERVALS:
        raise ValueError("Unsupported musical scale.")

    if key not in NOTE_NAMES:
        raise ValueError("Invalid musical key.")

    if level not in AUTOTUNE_STRENGTHS:
        raise ValueError("Invalid Auto-Tune level.")

    strength = AUTOTUNE_STRENGTHS[level] / 100

    corrected = np.array(midi_values, dtype=float).copy()

    root = NOTE_NAMES.index(key)

    allowed_notes = [
        (root + interval) % 12
        for interval in SCALE_INTERVALS[scale]
    ]

    for index, pitch in enumerate(corrected):

        if not np.isfinite(pitch):
            continue

        nearest = min(
            (round(pitch / 12) * 12 + note for note in allowed_notes),
            key=lambda candidate: abs(candidate - pitch)
        )

        corrected[index] = pitch + (nearest - pitch) * strength

    return corrected