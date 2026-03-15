import mlflow.sklearn
from sklearn.datasets import load_breast_cancer

mlflow.set_tracking_uri("file:./mlruns")

# RUN ID z najlepszego eksperymentu
run_id = "bfedd360749f4b33bcc120ccd11d8774"
model_uri = f"runs:/{run_id}/model"

print(f"wczytywanie modelu z: {model_uri}")
loaded_model = mlflow.sklearn.load_model(model_uri)

# próbka do testów
dataset = load_breast_cancer()
X_sample = dataset.data[0:10]
y_true = dataset.target[0:10]

predictions = loaded_model.predict(X_sample)
probabilities = loaded_model.predict_proba(X_sample)

print(f"prawdziwe etykiety:\n{y_true}")
print(f"przewidywane etykiety:\n{predictions}")
print(f"prawdopodobieństwa klas (klasa 0, klasa 1): \n{probabilities}")