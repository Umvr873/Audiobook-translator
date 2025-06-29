import streamlit as st
import sounddevice as sd
import wave
import numpy as np
import speech_recognition as sr
from googletrans import Translator
import pyttsx3
import tempfile
import os
import io
from pydub import AudioSegment
import threading
import time

# Configure page
st.set_page_config(
    page_title="Audiobook Translator",
    page_icon="🎧",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .audio-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .translation-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

class AudiobookTranslator:
    def __init__(self):
        self.languages = {
            "English": "en",
            "French": "fr", 
            "Spanish": "es",
            "German": "de",
            "Italian": "it",
            "Swahili": "sw",
            "Hausa": "ha",
            "Yoruba": "yo",
            "Arabic": "ar",
            "Chinese": "zh-cn",
            "Japanese": "ja",
            "Russian": "ru",
            "Portuguese": "pt"
        }
        
        # Initialize session state
        if 'original_text' not in st.session_state:
            st.session_state.original_text = ""
        if 'translated_text' not in st.session_state:
            st.session_state.translated_text = ""
        if 'recording' not in st.session_state:
            st.session_state.recording = False
        if 'audio_data' not in st.session_state:
            st.session_state.audio_data = []

    def recognize_speech_from_audio(self, audio_file, source_lang_code):
        """Convert audio to text using speech recognition"""
        recognizer = sr.Recognizer()
        
        # Handle different audio formats
        if audio_file.type.startswith('audio/'):
            # Convert to wav if needed
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_file.read()))
            wav_buffer = io.BytesIO()
            audio_segment.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            
            with sr.AudioFile(wav_buffer) as source:
                audio = recognizer.record(source)
        else:
            # Direct wav file
            with sr.AudioFile(io.BytesIO(audio_file.read())) as source:
                audio = recognizer.record(source)
        
        # Recognize speech
        text = recognizer.recognize_google(audio, language=source_lang_code)
        return text

    def translate_text(self, text, source_lang, target_lang):
        """Translate text using Google Translate"""
        translator = Translator()
        translated = translator.translate(
            text,
            src=self.languages[source_lang],
            dest=self.languages[target_lang]
        )
        return translated.text

    def text_to_speech(self, text, rate=150, volume=1.0):
        """Convert text to speech and return audio bytes"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_filename = tmp_file.name
            
            # Save speech to file
            engine.save_to_file(text, tmp_filename)
            engine.runAndWait()
            
            # Read the audio file
            with open(tmp_filename, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up
            os.unlink(tmp_filename)
            
            return audio_bytes
        except Exception as e:
            st.error(f"Text-to-speech error: {str(e)}")
            return None

def main():
    translator_app = AudiobookTranslator()
    
    # Header
    st.markdown("<h1 class='main-header'>🎧 Audiobook Translator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Translate and listen to audio in multiple languages</p>", unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Language selection
        st.subheader("Language Settings")
        source_lang = st.selectbox(
            "Source Language:",
            options=list(translator_app.languages.keys()),
            index=0
        )
        
        target_lang = st.selectbox(
            "Target Language:",
            options=list(translator_app.languages.keys()),
            index=1
        )
        
        # Voice settings
        st.subheader("Voice Settings")
        speech_rate = st.slider("Speech Rate", 50, 300, 150)
        volume = st.slider("Volume", 0.0, 1.0, 1.0, 0.1)
        
        # Instructions
        st.markdown("---")
        st.subheader("📋 How to Use")
        st.markdown("""
        1. **Upload Audio**: Choose an audio file to translate
        2. **Record Audio**: Use the microphone to record speech
        3. **Select Languages**: Choose source and target languages
        4. **Get Translation**: View original and translated text
        5. **Listen**: Play the translated audio
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎵 Audio Input")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Audio File",
            type=['wav', 'mp3', 'm4a', 'ogg'],
            help="Supported formats: WAV, MP3, M4A, OGG"
        )
        
        if uploaded_file is not None:
            st.audio(uploaded_file, format='audio/wav')
            
            if st.button("🔄 Translate Audio File", type="primary"):
                with st.spinner("Processing audio..."):
                    try:
                        # Speech recognition
                        st.info("🔍 Recognizing speech...")
                        original_text = translator_app.recognize_speech_from_audio(
                            uploaded_file, translator_app.languages[source_lang]
                        )
                        st.session_state.original_text = original_text
                        
                        # Translation
                        st.info("🔄 Translating text...")
                        translated_text = translator_app.translate_text(
                            original_text, source_lang, target_lang
                        )
                        st.session_state.translated_text = translated_text
                        
                        st.success("✅ Translation complete!")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing audio: {str(e)}")
        
        # Recording section
        st.markdown("---")
        st.subheader("🎙️ Record Audio")
        
        # Note about recording limitations
        st.warning("⚠️ **Note**: Audio recording in web browsers has limitations. For best results, upload pre-recorded audio files.")
        
        record_col1, record_col2 = st.columns(2)
        
        with record_col1:
            if st.button("🔴 Start Recording", disabled=True):
                st.info("Recording functionality requires additional setup for web deployment.")
        
        with record_col2:
            if st.button("⏹️ Stop Recording", disabled=True):
                st.info("Recording functionality requires additional setup for web deployment.")
    
    with col2:
        st.subheader("📝 Translation Results")
        
        # Original text
        with st.container():
            st.markdown("**Original Text:**")
            if st.session_state.original_text:
                st.markdown(f"<div class='translation-box'>{st.session_state.original_text}</div>", 
                           unsafe_allow_html=True)
            else:
                st.info("Upload and process an audio file to see the original text")
        
        st.markdown("---")
        
        # Translated text
        with st.container():
            st.markdown("**Translated Text:**")
            if st.session_state.translated_text:
                st.markdown(f"<div class='translation-box'>{st.session_state.translated_text}</div>", 
                           unsafe_allow_html=True)
                
                # Text-to-speech for translation
                if st.button("🔊 Play Translation", type="secondary"):
                    with st.spinner("Generating audio..."):
                        try:
                            audio_bytes = translator_app.text_to_speech(
                                st.session_state.translated_text, 
                                speech_rate, 
                                volume
                            )
                            if audio_bytes:
                                st.audio(audio_bytes, format='audio/wav')
                                st.success("🎵 Audio generated successfully!")
                        except Exception as e:
                            st.error(f"❌ Error generating audio: {str(e)}")
            else:
                st.info("Process an audio file to see the translation")
    
    # Manual text input section
    st.markdown("---")
    st.subheader("✏️ Manual Text Translation")
    
    text_col1, text_col2 = st.columns(2)
    
    with text_col1:
        manual_text = st.text_area(
            f"Enter text in {source_lang}:",
            height=100,
            placeholder=f"Type your text in {source_lang} here..."
        )
        
        if st.button("🔄 Translate Text") and manual_text.strip():
            with st.spinner("Translating..."):
                try:
                    translated_manual = translator_app.translate_text(
                        manual_text, source_lang, target_lang
                    )
                    st.session_state.manual_translation = translated_manual
                    st.success("✅ Translation complete!")
                except Exception as e:
                    st.error(f"❌ Translation error: {str(e)}")
    
    with text_col2:
        if hasattr(st.session_state, 'manual_translation'):
            st.text_area(
                f"Translation in {target_lang}:",
                value=st.session_state.manual_translation,
                height=100,
                disabled=True
            )
            
            if st.button("🔊 Play Manual Translation"):
                with st.spinner("Generating audio..."):
                    try:
                        audio_bytes = translator_app.text_to_speech(
                            st.session_state.manual_translation,
                            speech_rate,
                            volume
                        )
                        if audio_bytes:
                            st.audio(audio_bytes, format='audio/wav')
                    except Exception as e:
                        st.error(f"❌ Error generating audio: {str(e)}")
        else:
            st.text_area(
                f"Translation in {target_lang}:",
                value="",
                height=100,
                disabled=True,
                placeholder="Translation will appear here..."
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666; font-size: 0.8em;'>"
        "Built with Streamlit • Support for 13+ languages • Real-time translation"
        "</p>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
