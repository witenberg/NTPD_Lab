from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("Lab02")

dataset = load_breast_cancer()
X, y = dataset.data, dataset.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

objective = 'binary:logistic'

n_estimators = [32, 128]
depths = [3, 7]
learning_rates = [0.1, 1]

for estimators in n_estimators:
    for max_depth in depths:
        for lr in learning_rates:
            with mlflow.start_run():
                model = XGBClassifier(
                    n_estimators=estimators, 
                    max_depth=max_depth, 
                    learning_rate=lr, 
                    objective=objective
                )

                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                acc = accuracy_score(y_test, y_pred)

                mlflow.log_param("estimators", estimators)
                mlflow.log_param("max_depth", max_depth)
                mlflow.log_param("learning_rate", lr)

                mlflow.log_metric("accuracy", acc)
                
                mlflow.sklearn.log_model(model, name="model")

                print(f"Zakonczono run: max_depth={max_depth}, lr={lr}, accuracy={acc:.4f}")

print("Trening zakonczony")
