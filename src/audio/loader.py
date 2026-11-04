import librosa
import numpy as np
from pathlib import Path


def load_audio(file_path, target_sr=22050):
    """Load an audio recording as mono audio."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    audio, sample_rate = librosa.load(
        str(path),
        sr=target_sr,
        mono=True
    )

    if audio.size == 0:
        raise ValueError("Audio file is empty.")

    if np.max(np.abs(audio)) < 1e-5:
        raise ValueError("Audio recording is silent.")

    return audio, sample_rate