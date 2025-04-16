# 🧠 Groq Voice & Text Chatbot with Live News

Welcome to the **Groq AI Assistant** — an intelligent chatbot built using **Groq's LLaMA 3 models** and **Streamlit**, with support for both **voice and text interactions**. This project also delivers **live breaking news updates** using the NewsAPI, all in a slick UI powered by Streamlit.

---

## 🚀 Features

✨ **AI-Powered Conversations**  
Chat with the latest Groq-powered LLaMA 3 models — ask questions, get help, or explore creative ideas.

🎤 **Voice Input**  
Speak to the assistant using your microphone, and get spoken responses with built-in text-to-speech.

📰 **Live Breaking News Feed**  
Stay updated with real-time news across categories like business, technology, sports, and more.

💬 **Beautiful Chat Interface**  
Styled user interface with distinct formatting for user and assistant messages.

🧠 **Custom System Prompt**  
Assistant is guided to be helpful and focused on real-world problems and Q&A.

---

📸 Preview
## ![groqassistant](https://github.com/user-attachments/assets/2b567ca3-0a8d-4979-b4be-04118eff94ce)

## 📦 Tech Stack

- **[Streamlit](https://streamlit.io/)** – UI framework
- **[Groq API](https://groq.com/)** – LLaMA 3 powered chat completions
- **[OpenAI Python SDK](https://github.com/openai/openai-python)** – for integrating with Groq's API
- **[SpeechRecognition](https://pypi.org/project/SpeechRecognition/)** – for capturing voice input
- **[pyttsx3](https://pypi.org/project/pyttsx3/)** – for text-to-speech
- **[NewsAPI](https://newsapi.org/)** – for real-time headlines
- **dotenv** – for secure API key handling

---

## 📁 Project Structure
**🧠 App Overview (app.py)**
This is the main entry point of the application. It integrates voice recognition, text-to-speech, Groq’s LLaMA 3 models, and live news updates into a clean and interactive UI using Streamlit.

🔍 Key Functionalities
🌐 API Integration

Loads secure API keys using dotenv.

Connects to Groq’s OpenAI-compatible endpoint for generating AI responses.

Connects to NewsAPI to fetch real-time headlines by category.

🗣️ Voice Interaction

Uses SpeechRecognition to capture and process voice input.

Uses pyttsx3 for converting AI responses to speech output.

Users can talk to the assistant via a "🎙️ Use Voice" button.

💬 Conversational AI

Supports both text and voice input.

Sends user input to Groq’s LLaMA 3 model (llama3-8b-8192) and displays responses.

Messages are stored and displayed in a chat-like interface with custom styling.

📰 Live News Sidebar

Users can start a real-time news stream from categories like business, sports, tech, etc.

Headlines are updated every 30 seconds and shown in the sidebar.

🎨 Custom UI Styling

Styled input fields and buttons.

Enhanced chat display with left/right-aligned messages for user and AI.

Sidebar displays breaking news headlines with descriptions and links.


```python
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
```
**📡 News Fetching Module (utils/chat.py)**
This module handles all the logic related to fetching and extracting breaking news from the NewsAPI:

Loads the News API key securely using dotenv.

Defines a function fetch_news() to fetch top headlines by country and category.

Defines get_headlines() to extract just the news titles from the full articles, ideal for showing quick summaries or sidebar headlines.
```python
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/top-headlines"

def fetch_news(country="us", category="general"):
    """Fetch breaking news from NewsAPI"""
    url = f"{BASE_URL}?country={country}&category={category}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["articles"]
    else:
        return []

def get_headlines():
    """Extract and return just the headlines from the fetched articles."""
    articles = fetch_news()
    return [article["title"] for article in articles]
```
## 📦 Modules & Libraries Used
streamlit — UI framework for the web app

openai — used for Groq API integration

speech_recognition — to capture voice input

pyttsx3 — for text-to-speech responses

dotenv — to manage environment variables securely

requests — for fetching news from NewsAPI
