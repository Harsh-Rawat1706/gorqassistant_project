import streamlit as st
import openai
import os
import requests
from dotenv import load_dotenv
import time
import threading
from utils.chat import get_headlines
from streamlit_js_eval import streamlit_js_eval

# Load env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")

# OpenAI client
client = openai.OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

# Groq Chat function
def chat_with_groq(user_prompt):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# News
def get_news(category="general"):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={news_api_key}"
    try:
        response = requests.get(url)
        news_data = response.json()
        return news_data.get("articles", [])
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

#def display_news():
    #while True:
        #category = st.sidebar.selectbox("News Category", ["general", "business", "technology", "sports", "health", "entertainment", "science"])
        #headlines = get_news(category)
        #st.session_state.news = headlines if headlines else [{"title": "No news", "url": "#", "description": ""}]
        #time.sleep(30)

# Streamlit UI
st.set_page_config(page_title="Groq AI News Chatbot", layout="centered")
st.title("🧠 Groq Voice/Text Chatbot with News")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message['role'] == 'user':
        st.markdown(f"<div class='user-bubble'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai-bubble'><strong>AI:</strong> {message['content']}</div>", unsafe_allow_html=True)

# Text input
user_input = st.text_input("📝 Type your question:")

# Browser Voice Input
st.markdown("### 🎙️ Or Speak (Browser-based)")

result = streamlit_js_eval(js_expressions="window.SpeechRecognition || window.webkitSpeechRecognition", key="check_speech_api")
if result:
    js_code = """
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();
    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        window.parent.postMessage({streamlitMessage: text}, "*");
    }
    """
    streamlit_js_eval(js_expressions=js_code, key="voice_input_run")
    voice_input = st.text_input("🎤 Say something (browser)", key="voice_input")
    if voice_input:
        st.success(f"You said: {voice_input}")
        user_input = voice_input
else:
    st.warning("Your browser does not support Web Speech API. Please use Chrome or Edge.")

# Process input
if user_input:
    with st.spinner("Thinking..."):
        response = chat_with_groq(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown(f"<div class='ai-bubble'><strong>AI:</strong> {response}</div>", unsafe_allow_html=True)

# News sidebar
if st.sidebar.button("📡 Start News"):
    threading.Thread(target=display_news, daemon=True).start()

if "news" in st.session_state:
    st.sidebar.markdown("### 📰 Breaking News")
    for article in st.session_state.news:
        st.sidebar.markdown(f"**{article['title']}**")
        st.sidebar.markdown(f"[Read more]({article['url']})")
        if article["description"]:
            st.sidebar.markdown(f"*{article['description']}*")

# Styling
st.markdown("""
<style>
.user-bubble {
    background-color: #e0f7fa;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
}
.ai-bubble {
    background-color: #000000;
    color: white;
    padding: 10px;
    border-radius: 10px;
    text-align: right;
    margin-bottom: 8px;
}
.stTextInput input {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
    font-size: 16px;
}
.stButton button {
    background-color: #1e90ff;
    color: white;
    border-radius: 8px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

