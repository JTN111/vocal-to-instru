import pretty_midi
import soundfile as sf


def render_midi(midi_path, soundfont_path, output_path):
    """Render a MIDI file to WAV using a SoundFont."""

    midi = pretty_midi.PrettyMIDI(str(midi_path))

    audio = midi.fluidsynth(
        fs=22050,
        sf2_path=str(soundfont_path)
    )

    sf.write(
        str(output_path),
        audio,
        22050
    )

    return output_path