import pandas as pd

def data_analysis(data: pd.DataFrame) -> pd.DataFrame:
    """
    Функция для анализа данных, которая выводит основную информацию о наборе данных, 
    статистические показатели, список столбцов, дубликаты и отображает гистограммы.

    Параметры:
    data (pd.DataFrame): Набор данных, содержащий признаки и целевые переменные.

    Возвращает:
    pd.DataFrame: Возвращает исходный набор данных после проведения анализа.
    """
    # Вывод основной информации о данных
    print("Информация о данных:")
    print(data.info())
    print("\n")
    
    # Вывод основных статистических показателей данных
    print("Статистические показатели данных:")
    print(data.describe())
    print("\n")
    
    # Вывод всех столбцов
    print("Все столбцы данных:")
    print(data)
    print("\n")
    
    # Поиск и вывод дубликатов
    duplicated_rows = data[data.duplicated()]
    if not duplicated_rows.empty:
        print("Найдены дубликаты:")
        print(duplicated_rows)
        print("\n")
    else:
        print("Дубликатов не найдено.")

    # Вывод гистограммы для всех столбцов
    print("Гистограмма данных:")
    data.hist(figsize=(15, 20))
    return data
