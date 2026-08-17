from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "Machine learning is used to predict data.",
    "Python is a popular programming language.",
    "Deep learning uses neural networks.",
    "Football is a popular outdoor sport."
]

query = "Artificial intelligence and machine learning"

# Generate embeddings
doc_embeddings = model.encode(documents)
query_embedding = model.encode([query])

# Calculate similarity
scores = cosine_similarity(query_embedding, doc_embeddings)[0]

# Display results
for i, score in enumerate(scores):
    print(documents[i], "->", round(score, 3))

best = scores.argmax()

print("\nMost Similar Document:")
print(documents[best])
