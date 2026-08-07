import numpy as np

A = np.array([[2, 4],
              [1, 3]])

B = np.array([[5, 2],
              [6, 1]])

print("Matrix A:")
print(A)

print("\nMatrix B:")
print(B)

print("\nAddition:")
print(A + B)

print("\nSubtraction:")
print(A - B)

print("\nMultiplication:")
print(np.dot(A, B))

print("\nTranspose of A:")
print(A.T)

print("\nInverse of A:")
print(np.linalg.inv(A))
