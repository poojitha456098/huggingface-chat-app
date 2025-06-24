import streamlit as st
import requests
import time

# Hugging Face API URL (using Zephyr-7B)
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

# Load Hugging Face token from Streamlit secrets
headers = {
    "Authorization": f"Bearer {st.secrets['hf_token']}"
}

# Set Streamlit page configuration
st.set_page_config(page_title="🤖 Hugging Face Chatbot", page_icon="🤖")
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>🤖 Hugging Face Zephyr Chatbot</h1>
    <p style='text-align: center;'>Chat with a friendly LLM assistant!</p>
    <hr style="border: 1px solid #f0f0f0;">
""", unsafe_allow_html=True)

# Sidebar features
with st.sidebar:
    st.header("🛠️ Chat Settings")
    
    # Personality selector
    personality = st.selectbox("Assistant Personality", ["Helpful", "Funny", "Formal", "Sarcastic"])
    personality_prompts = {
        "Helpful": "You are a helpful assistant.",
        "Funny": "You tell jokes and respond in a humorous way.",
        "Formal": "You are a polite, formal assistant.",
        "Sarcastic": "You respond with witty sarcasm."
    }
    
    # Chat memory toggle
    use_memory = st.checkbox("Enable Chat Memory", value=True)
    
    # Clear chat button
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.success("Chat history cleared.")

    # Download chat button
    if st.session_state.get("chat_history"):
        full_chat = ""
        for msg in st.session_state.chat_history:
            role = "You" if msg["role"] == "user" else "Assistant"
            full_chat += f"{role}: {msg['content']}\n"
        st.download_button("📄 Download Chat", full_chat, file_name="chat_history.txt")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to build Zephyr-style prompt
def build_prompt(messages, system_prompt):
    prompt = f"<|system|>{system_prompt}"
    for msg in messages:
        if msg["role"] == "user":
            prompt += f"<|user|>{msg['content']}"
        elif msg["role"] == "assistant":
            prompt += f"<|assistant|>{msg['content']}"
    prompt += "<|assistant|>"
    return prompt

# Chat input
user_input = st.chat_input("Say something...")

# Process input
if user_input:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Build prompt (with or without memory)
    history = st.session_state.chat_history if use_memory else [{"role": "user", "content": user_input}]
    prompt = build_prompt(history, personality_prompts[personality])
    payload = {"inputs": prompt}

    # Send request
    with st.spinner("Thinking..."):
        response = requests.post(API_URL, headers=headers, json=payload)

    # Handle response
    if response.status_code == 200:
        try:
            result = response.json()
            full_output = result[0]["generated_text"]
            reply = full_output.split("<|assistant|>")[-1].strip()
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
        except Exception:
            st.error("⚠️ Could not parse model response.")
    else:
        st.error(f"❌ API error {response.status_code}: {response.text}")

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])
