# audiobook_translator_streamlit.py

import streamlit as st
import os
import numpy as np
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile

st.set_page_config(page_title="Audiobook Translator", layout="centered")
st.title("📚 Audiobook Translator")
st.write("Translate and listen to audio in multiple languages")

# Language mapping
languages = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Swahili": "sw",
    "Hausa": "ha",
    "Yoruba": "yo",
    "Igbo": "ig",
    "Zulu": "zu",
    "Xhosa": "xh",
    "Somali": "so",
    "Arabic": "ar",
    "Chinese": "zh-cn",
    "Japanese": "ja",
    "Russian": "ru",
    "Portuguese": "pt"
}

# Sidebar settings
st.sidebar.header("Settings")
source_lang = st.sidebar.selectbox("Source Language", list(languages.keys()), index=0)
target_lang = st.sidebar.selectbox("Target Language", list(languages.keys()), index=1)
speech_rate = st.sidebar.slider("Speech Rate", 0.5, 1.5, 1.0, 0.1)

# Upload audio
st.subheader("Upload Audio File")
uploaded_file = st.file_uploader("Choose a WAV audio file", type=["wav"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio = recognizer.record(source)

    try:
        st.info("Recognizing speech...")
        source_lang_code = languages[source_lang]
        target_lang_code = languages[target_lang]

        text = recognizer.recognize_google(audio, language=source_lang_code)
        st.text_area("Original Text", text, height=150)

        st.info("Translating text...")
        translator = Translator()
        translated_text = translator.translate(text, src=source_lang_code, dest=target_lang_code).text
        st.text_area("Translated Text", translated_text, height=150)

        st.info("Generating speech...")
        tts = gTTS(translated_text, lang=target_lang_code, slow=False)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as speech_file:
            tts.save(speech_file.name)
            audio = AudioSegment.from_mp3(speech_file.name)
            audio = audio.speedup(playback_speed=speech_rate)
            st.audio(speech_file.name)

    except Exception as e:
        st.error(f"Error: {str(e)}")
