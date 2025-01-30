import os
import requests
import streamlit as st
from fastapi import FastAPI, HTTPException
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatAnthropic
from langchain.vectorstores import Pinecone
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from datasets import load_dataset
from dotenv import load_dotenv
from pinecone import Pinecone
from PIL import Image

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# API Keys
PINECONE_API_KEY = os.getenv("pcsk_7QKLEa_RCEnZawP7NgzW9FhfbjX8szFb66WYpcturDk5EHpvHHH97REiXKcgyqrhuuYH1d")
PINECONE_ENV = os.getenv("us-east-1")
INDEX_NAME = "agenticrag"

if not PINECONE_API_KEY:
    raise ValueError("Pinecone API Key is missing. Please set it in environment variables.")

# Initialize Hugging Face Embeddings & Pinecone
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
pc = Pinecone(api_key=PINECONE_API_KEY)
vector_store = Pinecone.from_existing_index(index_name=INDEX_NAME, embedding=embeddings)

# Load LLM & Memory
llm = ChatAnthropic(model="claude-2", temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Build RAG Chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(),
    memory=memory,
    return_source_documents=True
)

@app.post("/query/")
async def query_agent(query: str):
    try:
        response = qa_chain.run(query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Agentic RAG Legal Assistant!"}

# Load dataset
dataset = load_dataset("c4lliope/us-congress")
chunks = [str(text) for text in dataset['train']['text']]
embedding_vectors = embeddings.embed_documents(chunks)
pinecone_data = [(str(i), embedding_vectors[i], {"text": chunks[i]}) for i in range(len(chunks))]
vector_store.upsert(vectors=pinecone_data)

# Streamlit UI
st.set_page_config(page_title="Agentic RAG Legal Assistant", layout="wide")

bg_image = "https://source.unsplash.com/1600x900/?law,court"
sidebar_image = "https://source.unsplash.com/400x600/?law,justice"

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

st.sidebar.title("⚖️ Legal AI Assistant")
st.sidebar.markdown("Your AI-powered legal research assistant.")

st.markdown("# 🏛️ Agentic RAG Legal Assistant")
st.markdown("### Your AI-powered assistant for legal research and case analysis.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_query = st.text_input("🔍 Enter your legal question:", "")
API_URL = "http://127.0.0.1:8000/query/"

if st.button("Ask AI") and user_query:
    with st.spinner("Fetching response..."):
        try:
            response = requests.post(API_URL, json={"query": user_query})
            response_json = response.json()
            ai_response = response_json.get("response", "Error: No response received.")
        except Exception as e:
            ai_response = f"Error: {e}"
    
    st.session_state.chat_history.append((user_query, ai_response))

st.markdown("---")
st.markdown("### 📜 Chat History")
for user_q, ai_r in st.session_state.chat_history:
    st.markdown(f"**🧑‍⚖️ You:** {user_q}")
    st.markdown(f"**🤖 AI:** {ai_r}")
    st.markdown("---")

st.markdown("---")
st.markdown("🚀 Powered by Anthropic Claude, Pinecone, and LangChain.")
