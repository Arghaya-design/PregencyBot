import streamlit as st
import requests
import datetime
import speech_recognition as sr
import pyttsx3
import threading
from functools import lru_cache

# Page Configuration
st.set_page_config(page_title="Pregnancy Guide", page_icon="🤰", layout="wide")

# Function to calculate pregnancy week
@lru_cache(maxsize=50)
def get_pregnancy_week(due_date):
    today = datetime.date.today()
    return max(0, min(40, 40 - ((due_date - today).days // 7)))

# Sidebar - Logo and Pregnancy Tracker
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>Pregnancy AI</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: grey;'>Your Intelligent Pregnancy Companion</h4>", unsafe_allow_html=True)

    try:
        st.image("logo.png", width=250)
    except Exception:
        st.warning("Logo not found. Please check the file path.")

    st.title("Pregnancy Tracker")
    due_date = st.date_input("Select Your Due Date")
    if due_date:
        st.write(f"**Week {get_pregnancy_week(due_date)}** of pregnancy! 👶")

# API Configuration (Replace with a valid API key)
API_KEY = "YOUR_OPENROUTER_API_KEY"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize TTS Engine
tts_engine = pyttsx3.init()

# Store chat history and mood log
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# Function to handle Text-to-Speech (TTS)
def speak(text):
    def run():
        tts_engine.say(text)
        tts_engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

# Function to handle Speech Recognition
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Speech not recognized. Try again."
        except sr.RequestError:
            return "Speech recognition service unavailable."
        except Exception as e:
            return f"Error: {str(e)}"

# Function to chat with AI
def chat_with_ai(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "system", "content": "Pregnancy assistant AI"},
                     {"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response.")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to AI: {str(e)}"

# Main Sections
tab1, tab2, tab3 = st.tabs(["💬 Chat with AI", "📋 Personalized Advice", "🧘 Mood Tracker"])

# Chat with AI
with tab1:
    st.write("### Chat with AI")

    predefined_questions = {
        "Nutrition": [
            "What are the best foods during pregnancy?",
            "How much water should I drink daily?",
            "What nutrients are essential for my baby?"
        ],
        "Exercise": [
            "What exercises are safe during pregnancy?",
            "Can I do yoga while pregnant?",
            "How can I stay active safely?"
        ],
        "Common Concerns": [
            "Is it normal to feel tired all the time?",
            "How do I manage morning sickness?",
            "What should I avoid during pregnancy?"
        ]
    }

    category = st.selectbox("Choose a category", list(predefined_questions.keys()))
    question = st.selectbox("Choose a question", predefined_questions[category])

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Ask AI", use_container_width=True):
            ai_response = chat_with_ai(question)
            st.session_state.chat_history.append(f"👩‍🦰 You: {question}")
            st.session_state.chat_history.append(f"🤖 AI: {ai_response}")
            st.write(f"🤖 **AI Response:** {ai_response}")
            speak(ai_response)

    user_input = st.text_input("Or type your question", key="user_input")
    with col2:
        if st.button("Send", use_container_width=True):
            if user_input:
                ai_response = chat_with_ai(user_input)
                st.session_state.chat_history.append(f"👩‍🦰 You: {user_input}")
                st.session_state.chat_history.append(f"🤖 AI: {ai_response}")
                st.write(f"🤖 **AI Response:** {ai_response}")
                speak(ai_response)

    with st.expander("📜 Chat History"):
        for msg in st.session_state.chat_history[::-1]:
            st.write(msg)

# Personalized Advice
with tab2:
    st.write("### Personalized Advice")

    col1, col2 = st.columns(2)
    with col1:
        age = st.slider("Your Age", 18, 45, 25)
        weight = st.number_input("Your Weight (kg)", 40, 120, 60)
    with col2:
        height = st.number_input("Your Height (cm)", 140, 200, 165)
        exercise = st.selectbox("Do you exercise regularly?", ["Yes", "No"])
    diet = st.selectbox("Are you following a pregnancy diet?", ["Yes", "No"])

    question = st.text_input("Ask a question about your pregnancy")
    if st.button("Get Advice", use_container_width=True):
        advice = f"At age {age}, maintaining a healthy weight of {weight}kg is crucial. "
        if exercise == "No":
            advice += "Regular prenatal exercises can help with delivery and reduce stress. "
        if diet == "No":
            advice += "Consider a balanced diet rich in folic acid, iron, and calcium."
        if question:
            advice += f"\n\n**Your Question:** {question}\n**AI Response:** {chat_with_ai(question)}"
        st.success(advice)

# Mood Tracker
with tab3:
    st.write("### Mood Tracker")
    mood = st.selectbox("How are you feeling today?", ["😊 Happy", "😢 Sad", "😴 Tired", "😡 Stressed", "🤗 Excited"])
    if st.button("Log Mood"):
        st.session_state.mood_log.append(f"{datetime.date.today()}: {mood}")
        st.success("Mood logged successfully!")

    with st.expander("📜 Mood History"):
        for entry in st.session_state.mood_log[::-1]:
            st.write(entry)

st.write("👶 Stay healthy and enjoy your pregnancy journey! 💖")
