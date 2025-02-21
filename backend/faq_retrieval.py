import chromadb
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class FAQRetriever:
    def __init__(self, db_path="./vector_store", faq_path="faq.json"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection("faq")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  # Efficient embedding model
        self.faq_data = self.load_faq(faq_path)

    def load_faq(self, faq_path):
        """Loads FAQ data into ChromaDB and stores the original order."""
        with open(faq_path, "r") as file:
            faq_data = json.load(file)

        for i, entry in enumerate(faq_data):
            questions = entry["question"]
            answers = entry["answer"]

            for question in questions:
                embedding = self.model.encode(question).tolist()
                self.collection.add(
                    ids=[f"q_{i}_{questions.index(question)}"],
                    embeddings=[embedding],
                    documents=[json.dumps({"answer": answers, "index": i})],
                    metadatas=[{"question": question}]
                )

        return faq_data  # Store FAQ data to maintain order



    def get_best_answer(self, query, session_history):
        """Retrieves the best matching FAQ answer, ensuring high similarity before responding."""

        # Encode user query
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=3)

        print(results)
        # Ensure we have valid results and metadata
        if not results or not results.get("documents") or not results["documents"][0]:
            return "Sorry, I don't have an answer for that."

        # Extract matched answers
        matched_answers = json.loads(results["documents"][0][0])  

        print(matched_answers)
        # Ensure metadatas exist and have a question field
        if not results.get("metadatas") or not results["metadatas"][0]:
            return "Sorry, I don't have an answer for that."

        # Extract stored FAQ question safely
        matched_metadata = results["metadatas"][0][0]

        matched_question = matched_metadata.get("question")

        if not matched_question:
            return "Sorry, I don't have an answer for that."

        # Compute similarity between user input and matched question
        matched_question_embedding = self.model.encode(matched_question).tolist()
        similarity = cosine_similarity([query_embedding], [matched_question_embedding])[0][0]

        # Set a similarity threshold
        SIMILARITY_THRESHOLD = 0.8
        if similarity < SIMILARITY_THRESHOLD:
            return "Sorry, I don't have an answer for that."

        # Find the last bot response in session history
        last_bot_response = None
        for message in reversed(session_history):
            if message["role"] == "assistant":
                last_bot_response = message["content"]
                break

        # Load the FAQ dataset to preserve order
        with open("faq.json", "r") as file:
            faq_data = json.load(file)

        # Check if last bot response exists in FAQ and find next entry
        for i, entry in enumerate(faq_data):
            if last_bot_response in entry["answer"] and i + 1 < len(faq_data):
                next_question_set = faq_data[i + 1]["question"]

                # Check if user's input matches the next expected question
                if any(self.is_relevant_match(query, q) for q in next_question_set):
                    return faq_data[i + 1]["answer"][0]  # Pick first answer from next FAQ

        return matched_answers["answer"][0]  # Default to best match if no sequence match found



    def is_relevant_match(self, user_input, expected_question):
        """Checks if the user input is relevant to the expected question."""
        user_embedding = self.model.encode(user_input).tolist()
        expected_embedding = self.model.encode(expected_question).tolist()

        similarity_score = sum(a * b for a, b in zip(user_embedding, expected_embedding))  # Cosine similarity approximation

        return similarity_score > 0.99  # Threshold for relevance


