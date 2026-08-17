
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "Machine learning is a part of artificial intelligence.",
    "Deep learning uses neural networks.",
    "Python is used for data science.",
    "Natural language processing understands text.",
    "Computer vision processes images."
]

# Create embeddings
embeddings = model.encode(documents)
embeddings = np.array(embeddings).astype("float32")

# Normalize
faiss.normalize_L2(embeddings)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)

# Store vectors
index.add(embeddings)

query = input("Enter query: ")

query_embedding = model.encode([query]).astype("float32")
faiss.normalize_L2(query_embedding)

# Search
scores, indices = index.search(query_embedding, 3)

print("\nRetrieved Documents:")

for i in range(3):
    print(
        i + 1,
        documents[indices[0][i]],
        "Score:",
        round(scores[0][i], 3)
    )
