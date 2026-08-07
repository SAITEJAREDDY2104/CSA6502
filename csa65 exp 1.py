import pandas as pd

data = {
    "Name": ["Asha", "Ravi", "John", "Meena", "Kiran"],
    "Marks": [85, None, 90, 78, None]
}

df = pd.DataFrame(data)

print("Original Dataset")
print(df)

df["Marks"] = df["Marks"].fillna(df["Marks"].mean())

print("\nCleaned Dataset")
print(df)

print("\nAverage Marks:", df["Marks"].mean())
print("Highest Marks:", df["Marks"].max())
