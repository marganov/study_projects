import re
import json

# функция для очистки названий населенных пунктов
def get_clean_locality_name_optimized(name: str) -> str:
    """
    Очищает название населенного пункта, используя регулярное выражение и словарь типов населенных пунктов.
    
    Параметры:
    name (str): Название населенного пункта.

    Возвращает:
    str: Очищенное название населенного пункта.
    """
    
    # Загрузка словаря типов населенных пунктов из JSON файла
    with open('locality_type_mapping.json', 'r', encoding='utf-8') as f:
        locality_type_mapping = json.load(f)
    
    match = re.match(r"^(.*?)([А-ЯЁ].*)$", name.strip())
    if match:
        locality_type, locality_name = match.groups()
        locality_type = locality_type.lower().strip()
        locality_name = locality_name.strip()

        for key in locality_type_mapping.keys():
            if key in locality_type:
                return locality_type_mapping[key] + ' ' + locality_name

    return name.strip()
