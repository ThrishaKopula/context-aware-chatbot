from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI
from dotenv import load_dotenv
import chromadb
from faq_retrieval import FAQRetriever
import random

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI
app = FastAPI()

# Initialize ChromaDB client and FAQ retriever
chroma_client = chromadb.PersistentClient(path="./vector_store")
faq_retriever = FAQRetriever()

# CORS Setup
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Storage
session_memory = {}

# Request Model
class ChatRequest(BaseModel):
    session_id: str
    text: str

@app.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id
    user_input = request.text

    # Initialize session history if it does not exist
    if session_id not in session_memory:
        session_memory[session_id] = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
    
    # Retrieve FAQ-based responses
    faq_answers = faq_retriever.get_best_answer(user_input)

    if faq_answers and faq_answers != ["Sorry, I don't have an answer for that."]:
        bot_response = random.choice(faq_answers)
    else:
        # Construct prompt with the query when FAQ doesn't have an answer
        prompt = f"User: {user_input}\nAI:"

        # Append user message
        session_memory[session_id].append({"role": "user", "content": user_input})

        # Debugging: Print session memory
        print(f"Session Memory for {session_id}: {session_memory[session_id]}")

        # Get AI response from OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session_memory[session_id] + [{"role": "system", "content": prompt}]
        )

        # Extract AI-generated response
        bot_response = response.choices[0].message.content

    # Append bot response to session memory
    session_memory[session_id].append({"role": "assistant", "content": bot_response})

    return {"response": bot_response}
