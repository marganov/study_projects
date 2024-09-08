import re
import json

# Функция для очистки названий населенных пунктов
def clean_locality_type(name: str, type_pattern: dict) -> str:
    """
    Функция, которая принимает название населенного пункта
    и возвращает стандартный тип населенного пункта на основе словаря сопоставлений.

    Параметры:
    name: str - Название населенного пункта.
    type_pattern: dict - Словарь с шаблонами для сопоставления типов.

    Возвращает:
    str - Стандартный тип населенного пункта, если найдено совпадение, иначе 'undefined'.
    """
    for pattern, locality_type in type_pattern.items():
        if re.search(rf'\\b{pattern}\\b', name, re.IGNORECASE):
            return locality_type
    return 'undefined'

# Загрузка данных из JSON-файла и создание словаря для обратного отображения
def load_locality_type_map(json_path: str) -> dict:
    """
    Загрузка словаря сопоставлений типов населенных пунктов из JSON-файла
    и создание обратного отображения для замещения.

    Параметры:
    json_path: str - Путь к JSON-файлу с данными.

    Возвращает:
    dict - Словарь с обратным отображением шаблонов типов.
    """
    with open(json_path, 'r', encoding='utf-8') as file:
        locality_type_map = json.load(file)
    return {pattern: key for key, patterns in locality_type_map.items() for pattern in patterns}
