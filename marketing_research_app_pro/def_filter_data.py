from typing import Union
import pandas as pd

def filter_data(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Применяет сглаживание данных с помощью скользящего среднего для всех столбцов датафрейма.

    Параметры:
    ----------
    df : pd.DataFrame
        Датафрейм с данными, к которым будет применяться сглаживание. Все столбцы в датафрейме будут обработаны.
    window : int
        Размер окна для вычисления скользящего среднего. Определяет количество точек для усреднения.

    Возвращает:
    ----------
    pd.DataFrame
        Датафрейм с теми же столбцами, но с примененным сглаживанием. Значения в каждом столбце заменяются на
        скользящее среднее с указанным размером окна.
    """
    # для каждого столбца применяем скользящее среднее
    for column in df.columns.values:
        df[column] = df[column].rolling(window).mean() 
    return df