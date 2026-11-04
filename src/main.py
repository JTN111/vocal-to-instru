import numpy as np
import librosa
import argparse
import json
from pathlib import Path
from src.pitch.corrector import correct_pitch
from src.pitch.key_detector import estimate_key
from src.audio.loader import load_audio
from src.pitch.detector import detect_pitch
from src.pitch.segment import segment_notes
from src.midi.generator import create_midi
from src.sample_matching import match_samples
from src.ml_transcriber import transcribe_with_basic_pitch


def run_conversion(
    audio_path,
    approach,
    output_dir="outputs",
    sample_folder=None
):
    """Run the selected conversion approach."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    midi_path = output_dir / "generated_melody.mid"
    notes_path = output_dir / "detected_notes.json"

    matches = []

    if approach == "ml":

        notes = transcribe_with_basic_pitch(
            audio_path,
            midi_path
        )

    elif approach in ("sample", "synth"):

        audio, sample_rate = load_audio(audio_path)
        key_result = estimate_key(audio, sample_rate)

        times, midi_values, probability = detect_pitch(
            audio, sample_rate
        )

        notes = segment_notes(times, midi_values)

        if not notes:
            raise ValueError(
                "No notes detected. Try a clearer recording."
            )

        if approach == "sample":

            if not sample_folder:
                raise ValueError(
                    "Please select an instrument sample folder."
                )

            matches = match_samples(
                notes,
                sample_folder
            )

        create_midi(notes, midi_path)

    else:
        raise ValueError("Invalid conversion approach.")

    if not notes:
        raise ValueError("No musical notes were detected.")

    with open(notes_path, "w") as file:
        json.dump(notes, file, indent=4)

    if matches:
        with open(output_dir / "sample_matches.json", "w") as file:
            json.dump(matches, file, indent=4)

    return midi_path, notes, matches


def analyze_vocals(audio_path, autotune_enabled=False, autotune_level="Medium"):
    """Analyse vocal pitch and return information for the dashboard."""

    audio, sample_rate = load_audio(audio_path)

    times, midi_values, probability = detect_pitch(
        audio, sample_rate
    )

    # Check whether any valid vocal pitch was detected
    valid = np.isfinite(midi_values)

    if not np.any(valid):
        raise ValueError(
            "No clear vocal pitch detected. Try recording again."
        )

    # Estimate musical key and scale
    key_result = estimate_key(audio, sample_rate)

    # Apply Auto-Tune if enabled
    if autotune_enabled:
        corrected_midi_values = correct_pitch(
            midi_values,
            key_result["key"],
            key_result["scale"],
            level=autotune_level
        )
    else:
        corrected_midi_values = midi_values.copy()

    # Generate notes from original detected pitches
    notes = segment_notes(times, midi_values)

    # Convert MIDI pitches into frequencies
    frequencies = librosa.midi_to_hz(midi_values[valid])

    average_frequency = float(np.mean(frequencies))

    lowest_midi = int(round(np.min(midi_values[valid])))
    highest_midi = int(round(np.max(midi_values[valid])))

    lowest_note = librosa.midi_to_note(lowest_midi)
    highest_note = librosa.midi_to_note(highest_midi)

    # Calculate pitch confidence
    valid_probability = probability[valid]
    valid_probability = valid_probability[
        np.isfinite(valid_probability)
    ]

    confidence = (
        float(np.mean(valid_probability) * 100)
        if len(valid_probability) > 0
        else 0.0
    )

    # Prepare graph data
    graph_frequencies = np.full(len(midi_values), np.nan)

    graph_frequencies[valid] = librosa.midi_to_hz(
        midi_values[valid]
    )

    voiced_percentage = float(np.mean(valid) * 100)

    return {
        "estimated_key": key_result["key"],
        "estimated_scale": key_result["scale"],
        "key_confidence": key_result["score"],
        "notes": notes,
        "times": times.tolist(),
        "frequencies": graph_frequencies.tolist(),
        "average_frequency": round(average_frequency, 2),
        "lowest_note": lowest_note,
        "highest_note": highest_note,
        "confidence": round(confidence, 2),
        "voiced_percentage": round(voiced_percentage, 2),
        "note_count": len(notes),
        "duration": round(len(audio) / sample_rate, 2),
        "corrected_midi_values": corrected_midi_values.tolist(),
        "autotune_enabled": autotune_enabled,
        "autotune_level": autotune_level if autotune_enabled else "Off"
    }


def main():

    parser = argparse.ArgumentParser(
        description="Vocal to Instrument MIDI Converter"
    )

    parser.add_argument("audio")
    parser.add_argument(
        "--approach",
        choices=["sample", "synth", "ml"],
        default="synth"
    )
    parser.add_argument(
        "--samples",
        default=None
    )

    args = parser.parse_args()

    try:
        midi_path, notes, matches = run_conversion(
            args.audio,
            args.approach,
            sample_folder=args.samples
        )

        print("\nConversion successful!")
        print(f"Approach: {args.approach}")
        print(f"Detected notes: {len(notes)}")
        print(f"MIDI file: {midi_path}")

        if matches:
            print("\nSample matches:")
            for match in matches:
                print(
                    f"{match['detected_note']} -> "
                    f"{Path(match['sample_file']).name}"
                )

    except Exception as error:
        print(f"\nConversion failed: {error}")


if __name__ == "__main__":
    main()