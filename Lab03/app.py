from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Trenowanie modelu
wine_data = load_wine()

# Dla łatwiejszego testowania bierzemy tylko 4 pierwsze cechy
X_train = wine_data.data[:, :4] 
y_train = wine_data.target

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Stworzenie aplikacji
app = FastAPI(
    title="Laboratorium 03",
    description="API do serwowania modelu klasyfikacji gatunków wina",
    version="1.0.0"
)

# Klasa do walidacji danych wejściowych 
class WinePredictionInput(BaseModel):
    alcohol: float
    malic_acid: float
    ash: float
    alcalinity_of_ash: float

# Endpoint główny
@app.get("/")
def read_root():
    return {"message": "Hello world!"}

# Endpoint predykcji
@app.post("/predict")
def predict(data: WinePredictionInput):
    # FastAPI automatycznie waliduje dane i zwróci błąd jeśli czegoś brakuje
    try:
        # Przygotowanie danych w odpowiednim formacie
        features = np.array([[data.alcohol, data.malic_acid, data.ash, data.alcalinity_of_ash]])
        prediction = model.predict(features)
        predicted_class_name = wine_data.target_names[prediction[0]]
        
        # Wynik jako JSON
        return {
            "prediction": int(prediction[0]), 
            "predicted_class": predicted_class_name,
            "message": "Predykcja zakończona sukcesem",
            "input_data": data.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wystąpił błąd: {str(e)}")

# Endpoint info
@app.get("/info")
def get_info():
    return {
        "model_type": type(model).__name__,
        "features_count": model.n_features_in_,
        "feature_names": ["alcohol", "malic_acid", "ash", "alcalinity_of_ash"],
        "dataset": "Wine Dataset (scikit-learn)",
        "description": "Model klasyfikujący odmianę wina (0, 1 lub 2) na podstawie 4 parametrów."
    }

# Endpoint health
@app.get("/health")
def health_check():
    return {"status": "ok"}