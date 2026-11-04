import librosa
import numpy as np
from scipy.ndimage import median_filter


def detect_pitch(audio, sample_rate):
    """Estimate fundamental vocal pitch over time."""

    hop_length = 256
    frame_length = 2048

    f0, voiced_flag, probability = librosa.pyin(
        audio,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sample_rate,
        frame_length=frame_length,
        hop_length=hop_length
    )

    midi_values = np.full(len(f0), np.nan)
    valid = voiced_flag & np.isfinite(f0)

    midi_values[valid] = librosa.hz_to_midi(f0[valid])

    if np.any(valid):
        filled = np.where(valid, midi_values, 0)
        smoothed = median_filter(filled, size=5)
        midi_values[valid] = smoothed[valid]

    times = librosa.frames_to_time(
        np.arange(len(f0)),
        sr=sample_rate,
        hop_length=hop_length
    )

    return times, midi_values, probability