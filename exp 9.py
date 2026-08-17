from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "AI is used in medical diagnosis.",
    "Machine learning predicts future outcomes.",
    "Deep learning uses multiple neural network layers.",
    "Cloud computing provides online computing services.",
    "Cybersecurity protects computer systems.",
    "Natural language processing works with text."
]

# Generate embeddings
vectors = model.encode(documents).astype("float32")

# Normalize vectors
faiss.normalize_L2(vectors)

# FAISS database
index = faiss.IndexFlatIP(vectors.shape[1])
index.add(vectors)

# Query
query = "How is AI used in medicine?"

query_vector = model.encode([query]).astype("float32")
faiss.normalize_L2(query_vector)

# Top-k
k = 3
scores, ids = index.search(query_vector, k)

print("\nTop", k, "Results:")

for rank, (score, idx) in enumerate(
    zip(scores[0], ids[0]), 1
):
    print("\nRank:", rank)
    print("Document:", documents[idx])
    print("Score:", round(score, 3))
