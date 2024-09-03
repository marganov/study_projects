import matplotlib.pyplot as plt
import pandas as pd
from def_filter_data import filter_data

def plot_retention(
    retention: pd.DataFrame,
    retention_history: pd.DataFrame,
    horizon: int,
    window: int = 7
) -> None:
    """
    Визуализирует удержание пользователей в зависимости от их статуса платящего или неплатящего, 
    а также динамику удержания по времени.

    Параметры:
    ----------
    retention : pd.DataFrame
        Таблица удержания пользователей, где строки представляют собой когорты, 
        а столбцы — дни лайфтайма. Столбцы с размером когорты и первого дня удержания будут исключены.
    retention_history : pd.DataFrame
        Исторические данные удержания, где строки представляют собой когорты по дате, 
        а столбцы — дни лайфтайма. Столбец с размером когорты будет исключен, а оставшиеся данные 
        будут использованы для динамического анализа удержания.
    horizon : int
        День лайфтайма, на который строится график удержания.
    window : int, по умолчанию 7
        Размер окна для сглаживания динамики удержания.

    Возвращает:
    ----------
    None
        Функция не возвращает значения. Вместо этого она отображает графики удержания пользователей и их динамики.
    """
    # задаём размер сетки для графиков
    plt.figure(figsize=(15, 10))

    # исключаем размеры когорт и удержание первого дня
    retention = retention.drop(columns=['cohort_size', 0])
    # в таблице динамики оставляем только нужный лайфтайм
    retention_history = retention_history.drop(columns=['cohort_size'])[
        [horizon - 1]
    ]

    # если в индексах таблицы удержания только payer,
    # добавляем второй признак — cohort
    if retention.index.nlevels == 1:
        retention['cohort'] = 'All users'
        retention = retention.reset_index().set_index(['cohort', 'payer'])

    # в таблице графиков — два столбца и две строки, четыре ячейки
    # в первой строим кривые удержания платящих пользователей
    ax1 = plt.subplot(2, 2, 1)
    retention.query('payer == True').droplevel('payer').T.plot(
        grid=True, ax=ax1
    )
    plt.legend()
    plt.xlabel('Лайфтайм')
    plt.title('Удержание платящих пользователей')

    # во второй ячейке строим кривые удержания неплатящих
    # вертикальная ось — от графика из первой ячейки
    ax2 = plt.subplot(2, 2, 2, sharey=ax1)
    retention.query('payer == False').droplevel('payer').T.plot(
        grid=True, ax=ax2
    )
    plt.legend()
    plt.xlabel('Лайфтайм')
    plt.title('Удержание неплатящих пользователей')

    # в третьей ячейке — динамика удержания платящих
    ax3 = plt.subplot(2, 2, 3)
    # получаем названия столбцов для сводной таблицы
    columns = [
        name
        for name in retention_history.index.names
        if name not in ['dt', 'payer']
    ]
    # фильтруем данные и строим график
    filtered_data = retention_history.query('payer == True').pivot_table(
        index='dt', columns=columns, values=horizon - 1, aggfunc='mean'
    )
    filter_data(filtered_data, window).plot(grid=True, ax=ax3)
    plt.xlabel('Дата привлечения')
    plt.title(
        'Динамика удержания платящих пользователей на {}-й день'.format(
            horizon
        )
    )

    # в чётвертой ячейке — динамика удержания неплатящих
    ax4 = plt.subplot(2, 2, 4, sharey=ax3)
    # фильтруем данные и строим график
    filtered_data = retention_history.query('payer == False').pivot_table(
        index='dt', columns=columns, values=horizon - 1, aggfunc='mean'
    )
    filter_data(filtered_data, window).plot(grid=True, ax=ax4)
    plt.xlabel('Дата привлечения')
    plt.title(
        'Динамика удержания неплатящих пользователей на {}-й день'.format(
            horizon
        )
    )
    
    plt.tight_layout()
    plt.show()