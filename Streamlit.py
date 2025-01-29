import streamlit as st
import requests
from PIL import Image

# Hugging Face Deployment Compatibility
st.set_page_config(page_title="Agentic RAG Legal Assistant", layout="wide")

# Load background and sidebar images
bg_image = "https://source.unsplash.com/1600x900/?law,court"  # Background image
sidebar_image = "https://source.unsplash.com/400x600/?law,justice"  # Sidebar image

# Custom CSS for background styling
st.markdown(
    f"""
    <style>
    .stApp {{
        background: url({bg_image}) no-repeat center center fixed;
        background-size: cover;
    }}
    .sidebar .sidebar-content {{
        background: url({sidebar_image}) no-repeat center center;
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar Title
st.sidebar.title("⚖️ Legal AI Assistant")
st.sidebar.markdown("Your AI-powered legal research assistant.")

# Main Heading
st.markdown("# 🏛️ Agentic RAG Legal Assistant")
st.markdown("### Your AI-powered assistant for legal research and case analysis.")

# Initialize conversation history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_query = st.text_input("🔍 Enter your legal question:", "")

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/query/"  # Change this to your deployed FastAPI URL

if st.button("Ask AI") and user_query:
    with st.spinner("Fetching response..."):
        try:
            response = requests.post(API_URL, json={"query": user_query})
            response_json = response.json()
            ai_response = response_json.get("response", "Error: No response received.")
        except Exception as e:
            ai_response = f"Error: {e}"
    
    # Update chat history
    st.session_state.chat_history.append((user_query, ai_response))

# Display chat history
st.markdown("---")
st.markdown("### 📜 Chat History")
for user_q, ai_r in st.session_state.chat_history:
    st.markdown(f"**🧑‍⚖️ You:** {user_q}")
    st.markdown(f"**🤖 AI:** {ai_r}")
    st.markdown("---")

# Footer
st.markdown("---")
st.markdown("🚀 Powered by OpenAI, Pinecone, and LangChain.")
