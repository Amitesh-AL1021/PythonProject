import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import tempfile
from openai import OpenAI
import webbrowser

# Initialize OpenAI client with your API key
API_KEY = "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"
client = OpenAI(api_key=API_KEY)

def speak_tts(text):
    tts = gTTS(text=text, lang='en')
    temp_file = tempfile.NamedTemporaryFile(delete=True)
    tts.save(temp_file.name + ".mp3")
    return temp_file.name + ".mp3"

def ask_gpt(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return completion.choices[0].message.content.strip()

WEBSITES = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "khan academy": "https://khanacademy.org",
    "coursera": "https://coursera.org",
    "wikipedia": "https://wikipedia.org",
}

def open_website_if_requested(text):
    text = text.lower()
    for key, url in WEBSITES.items():
        if key in text:
            return url
    return None

def listen_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 Listening... Please speak now.")
        audio = r.listen(source, phrase_time_limit=5)
    try:
        query = r.recognize_google(audio)
        st.success(f"🗣 You said: {query}")
        return query
    except Exception as e:
        st.error(f"Sorry, could not understand audio: {e}")
        return None

st.title("🎙 Amcoder AI Assistant")

if "chat" not in st.session_state:
    st.session_state.chat = []

def display_chat():
    # Display most recent messages first
    for i, (usr, resp) in enumerate(reversed(st.session_state.chat)):
        idx = len(st.session_state.chat) - 1 - i  # original index for unique keys
        st.markdown(f"*You:* {usr}")
        st.markdown(f"*Assistant:* {resp}")
        if st.button(f"🔊 Play Audio #{idx}", key=f"play_{idx}"):
            audio_file = speak_tts(resp)
            audio_bytes = open(audio_file, "rb").read()
            st.audio(audio_bytes, format='audio/mp3')

# Speech input button
if st.button("🎤 Speak"):
    speech_query = listen_speech()
    if speech_query:
        url = open_website_if_requested(speech_query)
        if url:
            st.markdown(f"Opening [{url}]({url})")
            st.session_state.chat.append((speech_query, f"Opening [{url}]({url})"))
            webbrowser.open(url)
        else:
            st.session_state.chat.append((speech_query, "[Waiting for your 'Get Response' click]"))
            st.session_state.pending_input = speech_query

# Text input box
text_input = st.text_input("Or type your message:")

input_to_use = None
if hasattr(st.session_state, "pending_input"):
    input_to_use = st.session_state.pending_input
elif text_input.strip() != "":
    input_to_use = text_input.strip()

if st.button("Get Response"):
    if not input_to_use:
        st.warning("Please speak or type a message first!")
    else:
        if hasattr(st.session_state, "pending_input"):
            del st.session_state.pending_input

        url = open_website_if_requested(input_to_use)
        if url:
            st.markdown(f"Opening [{url}]({url})")
            st.session_state.chat.append((input_to_use, f"Opening [{url}]({url})"))
            webbrowser.open(url)
        else:
            response = ask_gpt(input_to_use)
            st.session_state.chat.append((input_to_use, response))

display_chat()