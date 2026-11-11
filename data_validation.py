import pandas as pd
import pandera as pa
from pandera import Column, Check
import great_expectations as ge

# Декларативная схема валидации Pandera для данных Такси
taxi_schema = pa.DataFrameSchema({
    "Trip_Distance_km": Column(float, Check.ge(0.0), nullable=True),
    "Passenger_Count": Column(float, Check.ge(0.0), nullable=True),
    "Base_Fare": Column(float, Check.ge(0.0), nullable=True),
    "Per_Km_Rate": Column(float, Check.ge(0.0), nullable=True),
    "Trip_Duration_Minutes": Column(float, Check.ge(0.0), nullable=True),
    "Trip_Price": Column(float, Check.ge(0.0), nullable=True),
})


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Проверяет DataFrame по схеме и выбрасывает SchemaError при нарушениях."""
    return taxi_schema.validate(df)


def validate_with_great_expectations(df: pd.DataFrame) -> bool:
    """Проверяет качественные правила (Expectations) с помощью Great Expectations."""
    ge_df = ge.from_pandas(df)

    # 1. Проверка существования колонки
    res1 = ge_df.expect_column_to_exist("Trip_Distance_km")
    # 2. Проверка отсутствия пропусков в цене (в датасете есть пропуски, но мы проверим, что цена не null)
    res2 = ge_df.expect_column_values_to_not_be_null("Trip_Price")
    # 3. Проверка значений в физически допустимом интервале (пассажиры от 0 до 6)
    res3 = ge_df.expect_column_values_to_be_between("Passenger_Count", min_value=0, max_value=6)

    return res1.success and res2.success and res3.success