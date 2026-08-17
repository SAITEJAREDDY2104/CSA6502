from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "Artificial intelligence is changing healthcare.",
    "Machine learning helps computers learn from data.",
    "Cloud computing provides computing resources over the internet.",
    "Solar energy is a renewable energy source.",
    "Natural language processing deals with human language."
]

query = input("Enter your search query: ")

doc_vectors = model.encode(documents)
query_vector = model.encode([query])

similarity = cosine_similarity(query_vector, doc_vectors)[0]

# Sort by similarity
results = sorted(
    zip(documents, similarity),
    key=lambda x: x[1],
    reverse=True
)

print("\nSemantic Search Results:")

for doc, score in results:
    print(round(score, 3), "->", doc)
