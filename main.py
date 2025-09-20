import streamlit as st
import pyttsx3
import speech_recognition as sr
import tempfile
import requests

st.title("📞 Voice Agent Chatbot")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

BACKEND_URL = "http://127.0.0.1:8000"

# Initialize pyttsx3
engine = pyttsx3.init()

# --- Text Input ---
user_input = st.text_input("Type a message:")
if st.button("Send") and user_input.strip():
    st.session_state["chat_history"].append(("You", user_input))
    res = requests.post(f"{BACKEND_URL}/chat", json={"user_input": user_input})
    reply_text = res.json().get("response", "No response from server.")
    st.session_state["chat_history"].append(("Agent", reply_text))

    # Convert text to speech on frontend
    engine.say(reply_text)
    engine.runAndWait()

# --- Voice Input ---
st.subheader("🎤 Record your voice")
audio_file = st.audio_input("Click to record your voice")

if audio_file:
    tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_wav.write(audio_file.read())
    tmp_wav.close()

    # Transcribe voice
    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_wav.name) as source:
        audio = recognizer.record(source)
    try:
        text_from_audio = recognizer.recognize_google(audio)
    except Exception as e:
        text_from_audio = f"[Error recognizing audio: {e}]"

    st.text_area("Transcribed Text", value=text_from_audio, height=100)

    if text_from_audio.strip() and not text_from_audio.startswith("[Error"):
        st.session_state["chat_history"].append(("You", text_from_audio))
        res = requests.post(f"{BACKEND_URL}/chat", json={"user_input": text_from_audio})
        reply_text = res.json().get("response", "No response from server.")
        st.session_state["chat_history"].append(("Agent", reply_text))

        # Frontend TTS
        engine.say(reply_text)
        engine.runAndWait()

    # Clean up
    import os
    os.remove(tmp_wav.name)

# --- Display chat history ---
st.subheader("💬 Chat History")
for role, msg in st.session_state["chat_history"]:
    st.markdown(f"**{role}:** {msg}")
