from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI
app = FastAPI()

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

    # Initialize session history if not exists
    if session_id not in session_memory:
        print("not in")
        session_memory[session_id] = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
    
    # if len(session_memory)==0:
    #     session_memory.append({"role": "system", "content": "You are a helpful AI assistant."})

    # Append user message
    session_memory[session_id].append({"role": "user", "content": user_input})
    # session_memory.append({"role": "user", "content": user_input})

    # Debugging: Print session memory
    print(f"Session Memory for {session_id}: {session_memory[session_id]}")

    # Get AI response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=session_memory[session_id]
    )

    # Extract response correctly
    bot_response = response.choices[0].message.content

    # Append bot response
    session_memory[session_id].append({"role": "assistant", "content": bot_response})

    return {"response": bot_response}
