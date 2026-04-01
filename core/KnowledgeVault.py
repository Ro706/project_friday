import cohere
import faiss
import numpy as np
import os
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Paths
VECTOR_DB_PATH = os.path.join("data", "VectorDB", "faiss_index.bin")
METADATA_PATH = os.path.join("data", "VectorDB", "metadata.pkl")

# Initialize Cohere
co = cohere.Client(COHERE_API_KEY)

class KnowledgeVault:
    def __init__(self):
        self.index = None
        self.metadata = []
        self.load_index()

    def load_index(self):
        """Loads the FAISS index and metadata from disk."""
        if os.path.exists(VECTOR_DB_PATH) and os.path.exists(METADATA_PATH):
            try:
                self.index = faiss.read_index(VECTOR_DB_PATH)
                with open(METADATA_PATH, "rb") as f:
                    self.metadata = pickle.load(f)
                # print(f"[KnowledgeVault]: Loaded index with {len(self.metadata)} chunks.")
            except Exception as e:
                print(f"[ERROR]: Failed to load Knowledge Vault index: {e}")
                self.index = None
        else:
            # print("[KnowledgeVault]: No existing index found.")
            self.index = None

    def get_relevant_context(self, query, top_k=3):
        """Retrieves the most relevant text snippets for a query."""
        if self.index is None or not self.metadata:
            return ""

        try:
            # Generate embedding for the query
            response = co.embed(
                texts=[query],
                model="embed-english-v3.0",
                input_type="search_query"
            )
            query_embedding = np.array(response.embeddings).astype("float32")

            # Search the index
            distances, indices = self.index.search(query_embedding, top_k)

            context_snippets = []
            for idx in indices[0]:
                if idx != -1 and idx < len(self.metadata):
                    context_snippets.append(self.metadata[idx])

            return "\n---\n".join(context_snippets)

        except Exception as e:
            print(f"[ERROR]: Failed to retrieve context from Knowledge Vault: {e}")
            return ""

if __name__ == "__main__":
    vault = KnowledgeVault()
    test_query = "What is the secret code?"
    context = vault.get_relevant_context(test_query)
    print(f"Context found:\n{context}")
