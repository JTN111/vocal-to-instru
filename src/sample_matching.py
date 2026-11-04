import re
from pathlib import Path
import librosa


AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".aiff", ".aif", ".flac"
}


def get_sample_notes(sample_folder):
    """Read note names from instrument sample filenames."""

    folder = Path(sample_folder)

    if not folder.exists():
        raise FileNotFoundError(
            f"Sample folder not found: {folder}"
        )

    samples = []

    pattern = re.compile(
        r"(?<![A-Za-z])([A-G](?:#|b)?-?\d)(?!\d)",
        re.IGNORECASE
    )

    for file in folder.rglob("*"):
        if file.suffix.lower() not in AUDIO_EXTENSIONS:
            continue

        match = pattern.search(file.stem)

        if match:
            note_name = match.group(1).upper()

            try:
                pitch = librosa.note_to_midi(note_name)

                samples.append({
                    "file": str(file),
                    "note_name": note_name,
                    "pitch": int(pitch)
                })
            except Exception:
                continue

    return samples


def match_samples(notes, sample_folder):
    """Find the closest available sample for each detected note."""

    samples = get_sample_notes(sample_folder)

    if not samples:
        raise ValueError(
            "No note-labelled samples found. "
            "Include note names such as C4 or F#3 in filenames."
        )

    matches = []

    for note in notes:
        closest = min(
            samples,
            key=lambda sample: abs(
                sample["pitch"] - note["note"]
            )
        )

        matches.append({
            "detected_note": note["note_name"],
            "sample_note": closest["note_name"],
            "sample_file": closest["file"],
            "pitch_difference": (
                note["note"] - closest["pitch"]
            ),
            "start": note["start"],
            "duration": note["duration"]
        })

    return matches