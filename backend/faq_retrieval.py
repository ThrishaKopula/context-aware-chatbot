import chromadb
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI  # Or use another LLM provider like Hugging Face
import numpy as np
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class FAQRetriever:
    def __init__(self, db_path="./vector_store", faq_path="faq.json", model_name="gpt-3.5-turbo"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection("faq")
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.faq_data = self.load_faq(faq_path)
        self.model_name = model_name

    def load_faq(self, faq_path):
        """Loads FAQ data into ChromaDB and stores the original order."""
        with open(faq_path, "r") as file:
            faq_data = json.load(file)

        for i, entry in enumerate(faq_data):
            for question in entry["question"]:
                embedding = self.encoder.encode(question).tolist()
                self.collection.add(
                    ids=[f"q_{i}_{entry['question'].index(question)}"],
                    embeddings=[embedding],
                    documents=[json.dumps({"answer": entry["answer"], "index": i})],
                    metadatas=[{"question": question}]
                )
        return faq_data

    def retrieve_faq_entries(self, query, n_results=3):
        """Retrieves top N relevant FAQ entries based on similarity."""
        query_embedding = self.encoder.encode(query).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        
        if not results or not results.get("documents") or not results["documents"][0]:
            return []
        
        retrieved_entries = []
        for doc in results["documents"][0]:
            retrieved_entries.append(json.loads(doc))
        
        return retrieved_entries

    def generate_response(self, query, retrieved_entries):
        """Uses LLM to generate a response based on retrieved FAQ entries."""
        context = "\n".join(["- " + " ".join(entry["answer"]) for entry in retrieved_entries])
        prompt = (
            "You are a helpful chatbot using retrieved FAQ data to answer questions. "
            "Use the following information to respond to the user's query.\n\n"
            f"Retrieved FAQ Data:\n{context}\n\nUser Query: {query}\n\nResponse: "
        )

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()

    def get_best_answer(self, query, session_history):
        """Retrieves FAQ answers and uses an LLM to generate a response."""
        retrieved_entries = self.retrieve_faq_entries(query, n_results=3)
        
        if not retrieved_entries:
            return "Sorry, I don't have an answer for that."
        
        return self.generate_response(query, retrieved_entries)
