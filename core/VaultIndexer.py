import os
import pickle
import cohere
import faiss
import numpy as np
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Paths
VAULT_DIR = os.path.join("data", "Vault")
VECTOR_DB_PATH = os.path.join("data", "VectorDB", "faiss_index.bin")
METADATA_PATH = os.path.join("data", "VectorDB", "metadata.pkl")

# Initialize Cohere
co = cohere.Client(COHERE_API_KEY)

def extract_text(file_path):
    """Extracts text from a file based on its extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt" or ext == ".md":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            print(f"[ERROR]: Failed to parse PDF {file_path}: {e}")
        return text
    return ""

def chunk_text(text, chunk_size=500, overlap=100):
    """Splits text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += (chunk_size - overlap)
    return chunks

def index_vault():
    """Indexes all supported files in the vault."""
    all_chunks = []
    
    # Iterate through all files in the vault
    for filename in os.listdir(VAULT_DIR):
        file_path = os.path.join(VAULT_DIR, filename)
        if os.path.isfile(file_path):
            print(f"[VaultIndexer]: Processing {filename}...")
            text = extract_text(file_path)
            if text:
                chunks = chunk_text(text)
                all_chunks.extend(chunks)

    if not all_chunks:
        print("[VaultIndexer]: No documents found to index.")
        return

    print(f"[VaultIndexer]: Generating embeddings for {len(all_chunks)} chunks...")
    
    # Generate embeddings in batches of 96 (Cohere's limit for co.embed is usually larger, but 96 is safe)
    batch_size = 90
    embeddings = []
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        response = co.embed(
            texts=batch,
            model="embed-english-v3.0",
            input_type="search_document"
        )
        embeddings.extend(response.embeddings)

    embeddings = np.array(embeddings).astype("float32")

    # Create and save FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save to disk
    os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
    faiss.write_index(index, VECTOR_DB_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(all_chunks, f)

    print(f"[VaultIndexer]: Indexing complete. Saved to {VECTOR_DB_PATH}")

if __name__ == "__main__":
    index_vault()
