import pickle

with open("docs/vector_db.pkl", "rb") as f:
    data = pickle.load(f)

print(data[0])