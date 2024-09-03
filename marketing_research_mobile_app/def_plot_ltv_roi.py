import matplotlib.pyplot as plt
import pandas as pd
from def_filter_data import filter_data

def plot_ltv_roi(
    ltv: pd.DataFrame,
    ltv_history: pd.DataFrame,
    roi: pd.DataFrame,
    roi_history: pd.DataFrame,
    horizon: int,
    window: int = 7
) -> None:
    """
    Визуализирует LTV и ROI, а также их динамику по времени.

    Параметры:
    ----------
    ltv : pd.DataFrame
        Таблица LTV, где строки представляют собой когорты, а столбцы — дни лайфтайма. 
        Столбцы с размером когорты будут исключены из графиков.
    ltv_history : pd.DataFrame
        Исторические данные LTV, где строки представляют собой когорты по дате, 
        а столбцы — дни лайфтайма. Столбец с размером когорты будет исключен, 
        оставленные данные будут использованы для динамического анализа.
    roi : pd.DataFrame
        Таблица ROI, где строки представляют собой когорты, а столбцы — дни лайфтайма. 
        Столбцы с размером когорты и CAC будут исключены из графиков.
    roi_history : pd.DataFrame
        Исторические данные ROI, где строки представляют собой когорты по дате, 
        а столбцы — дни лайфтайма. Столбцы с размером когорты и CAC будут исключены, 
        оставленные данные будут использованы для динамического анализа.
    horizon : int
        День лайфтайма, на который строится график LTV и ROI.
    window : int, по умолчанию 7
        Размер окна для сглаживания динамики LTV и ROI.

    Возвращает:
    ----------
    None
        Функция не возвращает значения. Она отображает графики LTV, динамики LTV, 
        динамики стоимости привлечения (CAC), ROI, а также динамики ROI.
    """
    # задаём сетку отрисовки графиков
    plt.figure(figsize=(20, 10))

    # из таблицы ltv исключаем размеры когорт
    ltv = ltv.drop(columns=['cohort_size'])
    # в таблице динамики ltv оставляем только нужный лайфтайм
    ltv_history = ltv_history.drop(columns=['cohort_size'])[[horizon - 1]]

    # стоимость привлечения запишем в отдельный фрейм
    cac_history = roi_history[['cac']]

    # из таблицы roi исключаем размеры когорт и cac
    roi = roi.drop(columns=['cohort_size', 'cac'])
    # в таблице динамики roi оставляем только нужный лайфтайм
    roi_history = roi_history.drop(columns=['cohort_size', 'cac'])[
        [horizon - 1]
    ]

    # первый график — кривые ltv
    ax1 = plt.subplot(2, 3, 1)
    ltv.T.plot(grid=True, ax=ax1)
    plt.legend()
    plt.xlabel('Лайфтайм')
    plt.title('LTV')

    # второй график — динамика ltv
    ax2 = plt.subplot(2, 3, 2, sharey=ax1)
    # столбцами сводной таблицы станут все столбцы индекса, кроме даты
    columns = [name for name in ltv_history.index.names if name not in ['dt']]
    filtered_data = ltv_history.pivot_table(
        index='dt', columns=columns, values=horizon - 1, aggfunc='mean'
    )
    filter_data(filtered_data, window).plot(grid=True, ax=ax2)
    plt.xlabel('Дата привлечения')
    plt.title('Динамика LTV пользователей на {}-й день'.format(horizon))

    # третий график — динамика cac
    ax3 = plt.subplot(2, 3, 3, sharey=ax1)
    # столбцами сводной таблицы станут все столбцы индекса, кроме даты
    columns = [name for name in cac_history.index.names if name not in ['dt']]
    filtered_data = cac_history.pivot_table(
        index='dt', columns=columns, values='cac', aggfunc='mean'
    )
    filter_data(filtered_data, window).plot(grid=True, ax=ax3)
    plt.xlabel('Дата привлечения')
    plt.title('Динамика стоимости привлечения пользователей')

    # четвёртый график — кривые roi
    ax4 = plt.subplot(2, 3, 4)
    roi.T.plot(grid=True, ax=ax4)
    plt.axhline(y=1, color='red', linestyle='--', label='Уровень окупаемости')
    plt.legend()
    plt.xlabel('Лайфтайм')
    plt.title('ROI')

    # пятый график — динамика roi
    ax5 = plt.subplot(2, 3, 5, sharey=ax4)
    # столбцами сводной таблицы станут все столбцы индекса, кроме даты
    columns = [name for name in roi_history.index.names if name not in ['dt']]
    filtered_data = roi_history.pivot_table(
        index='dt', columns=columns, values=horizon - 1, aggfunc='mean'
    )
    filter_data(filtered_data, window).plot(grid=True, ax=ax5)
    plt.axhline(y=1, color='red', linestyle='--', label='Уровень окупаемости')
    plt.xlabel('Дата привлечения')
    plt.title('Динамика ROI пользователей на {}-й день'.format(horizon))

    plt.tight_layout()
    plt.show()