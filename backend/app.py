import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from faq_retrieval import FAQRetriever  # Your retrieval system
from openai import OpenAI 
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI app
app = FastAPI()
retriever = FAQRetriever()

# Load OpenAI API key (ensure it's set as an environment variable or config)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    session_id: str
    message: str

# In-memory session storage
session_memory = {}

@app.post("/chat")
def chat(user_input: UserInput):
    session_id = user_input.session_id
    query = user_input.message
    
    # Ensure session history exists
    if session_id not in session_memory:
        session_memory[session_id] = []

    # Retrieve relevant FAQ answers
    retrieved_answer = retriever.get_best_answer(query, session_memory[session_id])
    
    # Construct LLM prompt with retrieved context
    prompt = f"""
    You are a helpful AI assistant. Here is some relevant context to answer the user's question:
    {retrieved_answer}
    
    Now answer the following user query based on the context:
    User: {query}
    Assistant: """
    
    # Generate response from LLM
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use the appropriate OpenAI model
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    
    bot_response = response.choices[0].message.content
    
    # Store conversation history
    session_memory[session_id].append({"role": "user", "content": query})
    session_memory[session_id].append({"role": "assistant", "content": bot_response})
    
    return {"response": bot_response}
