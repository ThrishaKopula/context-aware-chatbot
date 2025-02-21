import chromadb
import json
from sentence_transformers import SentenceTransformer

class FAQRetriever:
    def __init__(self, db_path="./vector_store"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection("faq")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  # Efficient embedding model
        self.load_faq()

    def load_faq(self):
        """Loads FAQ data into ChromaDB"""
        with open("faq.json", "r") as file:
            faq_data = json.load(file)

        for i, entry in enumerate(faq_data):
            questions = entry["question"]
            answers = entry["answer"]

            # Store multiple variations of questions in the vector DB
            for question in questions:
                embedding = self.model.encode(question).tolist()
                self.collection.add(
                    ids=[f"q_{i}_{questions.index(question)}"],
                    embeddings=[embedding],
                    documents=[json.dumps(answers)]  # Store multiple answers
                )

    def get_best_answer(self, query):
        """Retrieves the best matching FAQ answer"""
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=3)

        if results["documents"]:
            answers = json.loads(results["documents"][0][0])  # Extract stored answers
            return answers  # Return all variations of the answer
        else:
            return ["Sorry, I don't have an answer for that."]

