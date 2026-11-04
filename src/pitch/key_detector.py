import librosa
import numpy as np


MAJOR_PROFILE = np.array([
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
    2.52, 5.19, 2.39, 3.66, 2.29, 2.88
])

MINOR_PROFILE = np.array([
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
    2.54, 4.75, 3.98, 2.69, 3.34, 3.17
])

NOTE_NAMES = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
]


def estimate_key(audio, sample_rate):

    chroma = librosa.feature.chroma_stft(
        y=audio,
        sr=sample_rate
    )

    profile = np.mean(chroma, axis=1)

    scores = []

    for scale, template in [
        ("Major", MAJOR_PROFILE),
        ("Minor", MINOR_PROFILE)
    ]:

        for shift in range(12):

            rotated = np.roll(template, shift)

            correlation = np.corrcoef(
                profile, rotated
            )[0, 1]

            scores.append({
                "key": NOTE_NAMES[shift],
                "scale": scale,
                "score": float(correlation)
            })

    scores.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    best = scores[0]

    return {
        "key": best["key"],
        "scale": best["scale"],
        "score": round(best["score"], 3)
    }
