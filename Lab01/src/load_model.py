import joblib
import os
import numpy as np


def load_model(name="model_lab01_v1.0.joblib", dir="models"):
    path = os.path.join(dir, name)

    model = joblib.load(path)

    # First row from dataset
    example_record = np.array([[8.32, 41.0, 6.98, 1.02, 322.0, 2.55, 37.88, -122.23]])

    # Prediction should be around 4,5
    pred = model.predict(example_record)
    print(f"Prediction: {pred[0]:.2f}")


if (__name__ == "__main__"):
    load_model()