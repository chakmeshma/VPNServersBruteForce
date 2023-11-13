import pickle

with open('results', 'rb') as file_object:
    results = pickle.load(file_object)

for result in results:
    print(f"{result[0]} {result[1]}")
