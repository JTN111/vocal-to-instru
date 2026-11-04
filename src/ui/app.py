import pandas as pd
from src.main import run_conversion, analyze_vocals
import streamlit as st
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Page configuration
st.set_page_config(
    page_title="Vocal to Instrument Converter",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 Vocal to Instrument Converter")

st.write(
    "Record your voice, choose a conversion method "
    "and turn your melody into a MIDI file."
)

st.divider()

# STEP 1: Record vocals
st.subheader("1. Record Your Melody")

recording = st.audio_input(
    "Record your voice using your microphone"
)

audio_path = None

if recording is not None:

    # Save recording
    input_folder = PROJECT_ROOT / "data" / "input"

    input_folder.mkdir(parents=True, exist_ok=True)

    audio_path = input_folder / "user_recording.wav"

    audio_path.write_bytes(recording.getvalue())

    st.success("Recording saved successfully!")

    # Playback
    st.audio(recording)

    st.caption("Listen to your recording before converting.")

st.divider()

# STEP 2: Analyse vocals
st.subheader("2. Analyse Your Vocals")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if recording is not None:

    # Auto-Tune Settings
    st.subheader("🎤 Auto-Tune Settings")

    autotune_enabled = st.toggle(
        "Enable Auto-Tune",
        value=False
    )

    autotune_level = st.selectbox(
        "Correction Strength",
        ["Low", "Medium", "High"],
        disabled=not autotune_enabled
    )

    # Analyse Button
    if st.button("Analyse My Vocals", type="primary"):

        try:
            with st.spinner("Analysing your vocals..."):
                st.session_state.analysis_result = analyze_vocals(
                    str(audio_path),
                    autotune_enabled=autotune_enabled,
                    autotune_level=autotune_level
                )

            st.success("Vocal analysis completed!")

        except Exception as error:
            st.error(f"Analysis failed: {error}")

result = st.session_state.analysis_result

if result is not None:

    st.subheader("Vocal Analysis Report")

    # Statistics
    col1, col2 = st.columns(2)

    col1.metric(
        "Average Frequency",
        f"{result['average_frequency']} Hz"
    )

    col2.metric(
        "Detected Notes",
        result["note_count"]
    )

    col3, col4 = st.columns(2)

    col3.metric(
        "Pitch Range",
        f"{result['lowest_note']} – {result['highest_note']}"
    )

    col4.metric(
        "Recording Duration",
        f"{result['duration']} sec"
    )

    col5, col6 = st.columns(2)

    col5.metric(
        "Pitch Confidence",
        f"{result['confidence']}%"
    )

    col6.metric(
        "Voiced Audio",
        f"{result['voiced_percentage']}%"
    )

    # Musical key analysis
    st.subheader("Estimated Musical Key")

    key_col1, key_col2 = st.columns(2)

    key_col1.metric(
        "Estimated Key",
        result["estimated_key"]
    )

    key_col2.metric(
        "Scale",
        result["estimated_scale"]
    )
    st.caption(
        f"Key estimation score: {result['key_confidence']:.2f}"
    )

    # st.divider()
    # st.subheader("🎤 Auto-Tune Settings")

    # autotune_enabled = st.toggle(
    #     "Enable Auto-Tune",
    #     value=False
    # )

    # autotune_level = st.selectbox(
    #     "Correction Strength",
    #     ["Low", "Medium", "High"],
    #     disabled=not autotune_enabled
    # )

    # Pitch graph
    st.subheader("Pitch Over Time")

    graph_data = pd.DataFrame({
        "Time (seconds)": result["times"],
        "Frequency (Hz)": result["frequencies"]
    })

    st.line_chart(
        graph_data,
        x="Time (seconds)",
        y="Frequency (Hz)"
    )

    # Detected notes
    st.subheader("Detected Musical Notes")

    st.dataframe(
        result["notes"],
        use_container_width=True
    )

else:
    st.info("Record your vocals and click Analyse My Vocals.")

st.divider()

# STEP 3: Select conversion approach
st.subheader("3. Choose Conversion Approach")

approach = st.selectbox(
    "Select how you want to convert your melody",
    [
        "Sample-based",
        "Synthesizer-based",
        "ML-based"
    ]
)

sample_folder = None

if approach == "Sample-based":

    instrument_type = st.selectbox(
        "Choose instrument category",
        ["Brass", "Strings"]
    )

    if instrument_type == "Brass":
        instrument = st.selectbox(
            "Choose instrument",
            ["french horn", "trombone", "trumpet", "tuba"]
        )
        category_folder = "Brass(trumpet)"

    else:
        instrument = st.selectbox(
            "Choose instrument",
            [
                "banjo", "cello", "double bass",
                "guitar", "mandolin", "viola", "violin"
            ]
        )
        category_folder = "Strings(violin))"

    sample_folder = (
        PROJECT_ROOT / "data" / "samples"
        / category_folder / instrument
    )

elif approach == "Synthesizer-based":

    st.info(
        "Your detected notes will be converted into MIDI."
    )

elif approach == "ML-based":

    st.info(
        "Basic Pitch will transcribe your recording into MIDI."
    )

st.divider()

# STEP 4: Generate MIDI
st.subheader("4. Generate MIDI")

if st.button("Convert My Melody", type="primary"):

    if audio_path is None:
        st.warning("Please record your vocals first.")

    else:
        try:
            with st.spinner("Converting your melody..."):

                approach_map = {
                    "Sample-based": "sample",
                    "Synthesizer-based": "synth",
                    "ML-based": "ml"
                }

                midi_path, notes, matches = run_conversion(
                    audio_path=str(audio_path),
                    approach=approach_map[approach],
                    sample_folder=sample_folder
                )

            st.success("MIDI generated successfully!")

            st.subheader("Detected Musical Notes")
            st.dataframe(notes, use_container_width=True)

            if matches:
                st.subheader("Matched Instrument Samples")
                st.dataframe(matches, use_container_width=True)

            with open(midi_path, "rb") as file:
                st.download_button(
                    label="Download Your MIDI File",
                    data=file.read(),
                    file_name="my_melody.mid",
                    mime="audio/midi"
                )

        except Exception as error:
            st.error(f"Conversion failed: {error}")