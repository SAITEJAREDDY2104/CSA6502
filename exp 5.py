from sklearn.metrics.pairwise import cosine_similarity

vector1 = [[1, 2, 3, 4]]
vector2 = [[2, 4, 6, 8]]

similarity = cosine_similarity(vector1, vector2)

print("Cosine Similarity:")
print(similarity)
