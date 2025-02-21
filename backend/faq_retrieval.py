import json
import chromadb
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load FAQ data
def load_faq():
    with open("faq.json", "r") as f:
        return json.load(f)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./vector_store")
collection = chroma_client.get_or_create_collection("faq")

# Load and store FAQs
faq_data = load_faq()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# Process each FAQ
for item in faq_data:
    collection.add(
        documents=[item["question"] + " " + item["answer"]],
        metadatas=[{"source": "faq"}],
        ids=[item["question"]]
    )

print("FAQ data stored in vector DB!")
