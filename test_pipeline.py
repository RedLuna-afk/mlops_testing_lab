import pytest
import pandas as pd
import pandera as pa
from scipy.stats import ks_2samp

from data_validation import validate_data, validate_with_great_expectations


# Загружаем реальный датасет (убедитесь, что файл лежит в корне проекта)
def get_taxi_data():
    df = pd.read_csv("taxi_trip_pricing.csv")
    # Оставляем только числовые колонки для тестов
    numeric_cols = ["Trip_Distance_km", "Passenger_Count", "Base_Fare", "Per_Km_Rate", "Trip_Duration_Minutes",
                    "Trip_Price"]
    return df[numeric_cols].dropna()


# --- 1. ТЕСТЫ ВАЛИДАЦИИ СХЕМЫ (PANDERA) ---
def test_valid_data_pandera():
    raw_data = get_taxi_data()
    validated_df = validate_data(raw_data)
    assert not validated_df.empty


def test_invalid_data_pandera():
    invalid_df = pd.DataFrame({
        "Trip_Distance_km": [-5.0],  # Отрицательное расстояние!
        "Passenger_Count": [2.0],
        "Base_Fare": [3.5],
        "Per_Km_Rate": [1.0],
        "Trip_Duration_Minutes": [15.0],
        "Trip_Price": [20.0]
    })
    with pytest.raises(pa.errors.SchemaError):
        validate_data(invalid_df)


# --- 2. ТЕСТЫ GREAT EXPECTATIONS ---
def test_great_expectations_checks():
    raw_data = get_taxi_data()
    assert validate_with_great_expectations(raw_data) == True


# --- 3. ТЕСТ НА ОБНАРУЖЕНИЕ ДРЕЙФА ДАННЫХ (KS-ТЕСТ) ---
def test_data_drift_detection():
    df = get_taxi_data()
    reference = df.sample(frac=0.5, random_state=42)
    current_normal = df.drop(reference.index)

    for col in reference.columns:
        p_value = ks_2samp(reference[col], current_normal[col]).pvalue
        assert p_value > 0.01  # Дрейф отсутствует


def test_simulated_drift_failure():
    df = get_taxi_data()
    reference = df.sample(frac=0.5, random_state=42)

    # Имитируем дрейф (например, цены внезапно выросли в 3 раза)
    current_drifted = df.drop(reference.index).copy()
    current_drifted["Trip_Price"] *= 3.0

    p_value = ks_2samp(reference["Trip_Price"], current_drifted["Trip_Price"]).pvalue
    assert p_value < 0.05  # Дрейф успешно обнаружен