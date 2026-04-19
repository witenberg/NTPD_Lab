from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

def train_and_predict():
    # Zbiór Wine (analogicznie do Lab05)
    wine_data = load_wine()
    X = wine_data.data[:, :4] 
    y = wine_data.target
    
    # Podział na zbiór treningowy i testowy do walidacji
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    return preds, y_test

def get_accuracy():
    preds, y_test = train_and_predict()
    return accuracy_score(y_test, preds)

# Inicjalizacja modelu dla API
wine_data = load_wine()
X_train = wine_data.data[:, :4] 
y_train = wine_data.target
trained_model = RandomForestClassifier(random_state=42)
trained_model.fit(X_train, y_train)