from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
from dotenv import load_dotenv
import os

# Load the OpenAI API key from environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware to allow requests from the frontend
origins = [
    "http://localhost:3000",  # Update this if your frontend is running on a different port
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Store session context
session_memory = {}

class ChatRequest(BaseModel):
    session_id: str
    text: str

@app.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id

    # Retrieve or create chat history
    if session_id not in session_memory:
        session_memory[session_id] = []

    # Append user input to chat history
    session_memory[session_id].append(f"User: {request.text}")

    # Format context
    context = "\n".join(session_memory[session_id])

    # Get response from OpenAI API (Using GPT-3.5-turbo model)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Change model to GPT-3.5-turbo
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},  # System message with developer role
            {"role": "user", "content": context}  # User message
        ]
    )

    # Access the response correctly using the new 'message' structure
    bot_response = response['choices'][0]['message']['content']

    # Store bot response in session memory
    session_memory[session_id].append(f"Bot: {bot_response}")

    return {"response": bot_response}
