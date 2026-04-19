from model import train_and_predict, get_accuracy

def test_predictions_not_none():
    """
    Test 1: Sprawdza, czy otrzymujemy jakąkolwiek predykcję.
    """
    preds, _ = train_and_predict()
    assert preds is not None, "Predictions should not be None."

def test_predictions_length():
    """
    Test 2: Sprawdza, czy długość listy predykcji jest większa od 0 
    i czy odpowiada przewidywanej liczbie próbek testowych.
    """
    preds, y_test = train_and_predict()
    assert len(preds) > 0, "Długość predykcji powinna być większa od zera."
    assert len(preds) == len(y_test), "Liczba predykcji różni się od liczby próbek testowych."

def test_predictions_value_range():
    """
    Test 3: Sprawdza, czy wartości w predykcjach mieszczą się w spodziewanym zakresie 
    (3 klasy: 0, 1, 2 dla zbioru Wine).
    """
    preds, _ = train_and_predict()
    expected_classes = {0, 1, 2}
    unique_preds = set(preds)
    assert unique_preds.issubset(expected_classes), f"Znaleziono nieoczekiwane wartości predykcji: {unique_preds - expected_classes}"

def test_model_accuracy():
    """
    Test 4: Sprawdza, czy model osiąga co najmniej 70% dokładności.
    """
    accuracy = get_accuracy()
    assert accuracy >= 0.70, f"Dokładność modelu to {accuracy:.2f}, co jest poniżej wymaganych 0.70."