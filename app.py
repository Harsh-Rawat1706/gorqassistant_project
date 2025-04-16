import streamlit as st
import openai
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
import os
from utils.chat import get_headlines  # Import the get_headlines function
import threading
import time
import requests

# Load API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")  # Make sure to add this in your .env

# Configure OpenAI client to point to Groq's endpoint
client = openai.OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1",  # Groq's API base URL
)

# Text-to-speech engine
tts_engine = pyttsx3.init()

def speak(text):
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except RuntimeError:
        pass  # Prevent "run loop already started" error in Streamlit

# Voice input
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except Exception as e:
        return f"Could not understand audio: {e}"

# Chat with Groq
def chat_with_groq(user_prompt):
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # You can also try "llama3-70b-8192" if needed
        messages=[
            {"role": "system", "content": "You are a helpful assistant that solves real-world and Q/A problems."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Function to display breaking news
def get_news(category="general"):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={news_api_key}"
    try:
        response = requests.get(url)
        news_data = response.json()
        if news_data["status"] == "ok":
            return news_data["articles"]
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

# Function to display the latest breaking news in the sidebar
def display_news():
    while True:
        category = st.sidebar.selectbox("Select News Category", ["general", "business", "technology", "sports", "health", "entertainment", "science"])
        headlines = get_news(category)
        
        if headlines:
            st.session_state.news = headlines  # Store news in session state
        else:
            st.session_state.news = [{"title": "No news found!", "url": "#", "description": ""}]
        
        time.sleep(30)  # Refresh news every 30 seconds

# Streamlit UI Setup
st.set_page_config(page_title="Groq Chatbot with News", layout="centered")
st.title("🧠 Groq Voice & Text Chatbot with Live News")

# Chat UI enhancements
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chatbot conversation
for message in st.session_state.messages:
    if message['role'] == 'user':
        st.markdown(f"<div style='text-align: left;'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: right;'><strong>AI:</strong> {message['content']}</div>", unsafe_allow_html=True)

# Add text input box for chat
user_input = st.text_input("📝 Type your question:")

# Voice Input Button
if st.button("🎙️ Use Voice"):
    user_input = listen()
    st.success(f"You said: {user_input}")

# Display thinking status while waiting for AI response
if user_input:
    with st.spinner("Thinking..."):
        answer = chat_with_groq(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.markdown(f"<div style='text-align: right;'><strong>AI:</strong> {answer}</div>", unsafe_allow_html=True)
    speak(answer)  # Convert response to speech

# Start news stream in the background when the button is clicked
if st.sidebar.button("📡 Start News Stream"):
    threading.Thread(target=display_news, daemon=True).start()

# Show live breaking news in sidebar
if "news" in st.session_state:
    st.sidebar.markdown("### 📰 Breaking News")
    for article in st.session_state.news:
        if article["title"]:
            st.sidebar.markdown(f"**{article['title']}**")
            st.sidebar.markdown(f"[Read more]({article['url']})")
            if article["description"]:
                st.sidebar.markdown(f"*{article['description']}*")
else:
    st.sidebar.markdown("No news available yet...")

# Custom Styling 
st.markdown("""
    <style>
        /* Style for the text input box */
        .stTextInput input {
            background-color: #f0f0f0;
            color: black;  /* Ensure text is visible */
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 16px;
        }

        .stTextInput label {
            font-weight: bold;
        }

        /* Style for buttons */
        .stButton button {
            background-color: #1e90ff;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
        }

        /* Style for chat bubbles */
        .stMarkdown div {
            margin-top: 10px;
        }

        .stMarkdown div strong {
            font-size: 14px;
            color: #555;
        }

        .stMarkdown div {
            font-size: 16px;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)
