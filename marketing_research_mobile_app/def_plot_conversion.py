import matplotlib.pyplot as plt
import pandas as pd
from def_filter_data import filter_data

def plot_conversion(
    conversion: pd.DataFrame,
    conversion_history: pd.DataFrame,
    horizon: int,
    window: int = 7
) -> None:
    """
    Визуализирует конверсию пользователей в зависимости от их статуса и динамику конверсии по времени.

    Параметры:
    ----------
    conversion : pd.DataFrame
        Таблица конверсии пользователей, где строки представляют собой когорты, 
        а столбцы — дни лайфтайма. Столбцы с размером когорты будут исключены.
    conversion_history : pd.DataFrame
        Исторические данные конверсии, где строки представляют собой когорты по дате, 
        а столбцы — дни лайфтайма. Столбец с размером когорты будет исключен, а оставшиеся данные 
        будут использованы для динамического анализа конверсии.
    horizon : int
        День лайфтайма, на который строится график конверсии.
    window : int, по умолчанию 7
        Размер окна для сглаживания динамики конверсии.

    Возвращает:
    ----------
    None
        Функция не возвращает значения. Вместо этого она отображает графики конверсии пользователей и их динамики.
    """
    # задаём размер сетки для графиков
    plt.figure(figsize=(15, 5))

    # исключаем размеры когорт
    conversion = conversion.drop(columns=['cohort_size'])
    # в таблице динамики оставляем только нужный лайфтайм
    conversion_history = conversion_history.drop(columns=['cohort_size'])[
        [horizon - 1]
    ]

    # первый график — кривые конверсии
    ax1 = plt.subplot(1, 2, 1)
    conversion.T.plot(grid=True, ax=ax1)
    plt.legend()
    plt.xlabel('Лайфтайм')
    plt.title('Конверсия пользователей')

    # второй график — динамика конверсии
    ax2 = plt.subplot(1, 2, 2, sharey=ax1)
    columns = [
        # столбцами сводной таблицы станут все столбцы индекса, кроме даты
        name for name in conversion_history.index.names if name not in ['dt']
    ]
    filtered_data = conversion_history.pivot_table(
        index='dt', columns=columns, values=horizon - 1, aggfunc='mean'
    )
    filter_data(filtered_data, window).plot(grid=True, ax=ax2)
    plt.xlabel('Дата привлечения')
    plt.title('Динамика конверсии пользователей на {}-й день'.format(horizon))

    plt.tight_layout()
    plt.show()