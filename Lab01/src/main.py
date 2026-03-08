from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd
import os
import joblib


def prepare_data():
    dataset = fetch_california_housing()

    df = pd.DataFrame(data=dataset.data, columns=dataset.feature_names)
    df['target_price'] = dataset.target

    print(f"First 5 rows: {df.head()}\n")
    print(f"Shape: {df.shape[0]}x{df.shape[1]}\n")
    print(f"Memory usage: {df.memory_usage().sum() / 1024 / 1024 :.2f} MiB\n")
    print(f"Column types: \n{df.dtypes}")

    X = df.drop(columns=['target_price'])
    y = df['target_price']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)

    return model

def test_model(model, X_test, y_test):
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\nMetrics:")
    print(f"MAE: {mae:.2f}")
    print(f"MSE: {mse:.2f}")
    print(f"R2: {r2:.2f}")


def save_model(model, version="v1.0", dir="models"):
    os.makedirs(dir, exist_ok=True)
    
    model_name = f"model_lab01_{version}.joblib"
    model_path = os.path.join(dir, model_name)

    joblib.dump(model, model_path)


if (__name__ == "__main__"):
    X_train, X_test, y_train, y_test = prepare_data()
    model = train_model(X_train, y_train)
    test_model(model, X_test, y_test)
    save_model(model)
