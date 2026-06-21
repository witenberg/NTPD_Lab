import os
import socket

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# --- Konfiguracja ze zmiennych srodowiskowych (wstrzykiwana z ConfigMap w K8s) ---
APP_VERSION = os.getenv("APP_VERSION", "1.0")          # bake'owana w obrazie (v1 vs v2)
APP_ENV = os.getenv("APP_ENV", "local")                # z ConfigMap
MODEL_NAME = os.getenv("MODEL_NAME", "wine-rf-classifier")  # z ConfigMap
HOSTNAME = socket.gethostname()                        # nazwa poda (do obserwacji load-balancingu)

# --- Trenowanie modelu (klasyfikacja gatunkow wina, 4 cechy) ---
wine_data = load_wine()
X_train = wine_data.data[:, :4]
y_train = wine_data.target
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

app = FastAPI(
    title="LAB13 ML API",
    description="API klasyfikacji wina wdrazane na Kubernetes",
    version=APP_VERSION,
)


class WinePredictionInput(BaseModel):
    alcohol: float
    malic_acid: float
    ash: float
    alcalinity_of_ash: float


@app.get("/")
def read_root():
    return {"message": "ML API dziala", "version": APP_VERSION, "pod": HOSTNAME}


@app.post("/predict")
def predict(data: WinePredictionInput):
    try:
        features = np.array([[data.alcohol, data.malic_acid, data.ash, data.alcalinity_of_ash]])
        prediction = model.predict(features)
        return {
            "prediction": int(prediction[0]),
            "predicted_class": wine_data.target_names[prediction[0]],
            "version": APP_VERSION,
            "pod": HOSTNAME,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blad: {e}")


@app.get("/info")
def get_info():
    return {
        "model_type": type(model).__name__,
        "model_name": MODEL_NAME,
        "features": ["alcohol", "malic_acid", "ash", "alcalinity_of_ash"],
        "app_version": APP_VERSION,
        "app_env": APP_ENV,
        "pod": HOSTNAME,
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "version": APP_VERSION, "pod": HOSTNAME}
