from typing import List, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def get_ltv(
    profiles: pd.DataFrame,
    purchases: pd.DataFrame,
    observation_date: datetime,
    horizon_days: int,
    dimensions: List[str] = [],
    ignore_horizon: bool = False,
) -> Tuple[
    pd.DataFrame,  # Сырые данные
    pd.DataFrame,  # Таблица LTV
    pd.DataFrame,  # Таблица динамики LTV
    pd.DataFrame,  # Таблица ROI
    pd.DataFrame   # Таблица динамики ROI
]:
    """
    Рассчитывает LTV (Lifetime Value) и ROI (Return on Investment) для пользователей на основе данных профилей и покупок.

    Параметры:
    ----------
    profiles : pd.DataFrame
        Датафрейм с данными профилей пользователей. Должен содержать столбцы:
        'user_id' - уникальный идентификатор пользователя,
        'dt' - дата профиля,
        'first_ts' - дата первой регистрации.
    purchases : pd.DataFrame
        Датафрейм с данными о покупках. Должен содержать столбцы:
        'user_id' - уникальный идентификатор пользователя,
        'event_dt' - дата события,
        'revenue' - выручка от покупки.
    observation_date : datetime
        Дата, на основе которой будет рассчитываться горизонт анализа.
    horizon_days : int
        Количество дней горизонта анализа (период времени для расчета LTV и ROI).
    dimensions : List[str], по умолчанию []
        Список столбцов, по которым будет производиться группировка данных.
    ignore_horizon : bool, по умолчанию False
        Флаг, указывающий, нужно ли игнорировать горизонт анализа. Если True, то горизонт не учитывается.

    Возвращает:
    ----------
    Tuple[
        pd.DataFrame,  # Сырые данные
        pd.DataFrame,  # Таблица LTV
        pd.DataFrame,  # Таблица динамики LTV
        pd.DataFrame,  # Таблица ROI
        pd.DataFrame   # Таблица динамики ROI
    ]
        Возвращает кортеж из пяти датафреймов:
        1. Сырые данные с добавленными данными о покупках и рассчитанным лайфтаймом пользователя.
        2. Таблица LTV, показывающая выручку на основе размеров когорт и лайфтаймов.
        3. Таблица динамики LTV, показывающая изменения LTV во времени.
        4. Таблица ROI, показывающая возврат на инвестиции на основе размеров когорт и лайфтаймов.
        5. Таблица динамики ROI, показывающая изменения ROI во времени.
    """
    # исключаем пользователей, не «доживших» до горизонта анализа
    last_suitable_acquisition_date = observation_date
    if not ignore_horizon:
        last_suitable_acquisition_date = observation_date - timedelta(
            days=horizon_days - 1
        )
    result_raw = profiles.query('dt <= @last_suitable_acquisition_date')
    # добавляем данные о покупках в профили
    result_raw = result_raw.merge(
        purchases[['user_id', 'event_dt', 'revenue']], on='user_id', how='left'
    )
    # рассчитываем лайфтайм пользователя для каждой покупки
    result_raw['lifetime'] = (
        result_raw['event_dt'] - result_raw['first_ts']
    ).dt.days
    # группируем по cohort, если в dimensions ничего нет
    if len(dimensions) == 0:
        result_raw['cohort'] = 'All users'
        dimensions = dimensions + ['cohort']

    # функция группировки по желаемым признакам
    def group_by_dimensions(df, dims, horizon_days):
        # строим «треугольную» таблицу выручки
        result = df.pivot_table(
            index=dims, columns='lifetime', values='revenue', aggfunc='sum'
        )
        # находим сумму выручки с накоплением
        result = result.fillna(0).cumsum(axis=1)
        # вычисляем размеры когорт
        cohort_sizes = (
            df.groupby(dims)
            .agg({'user_id': 'nunique'})
            .rename(columns={'user_id': 'cohort_size'})
        )
        # объединяем размеры когорт и таблицу выручки
        result = cohort_sizes.merge(result, on=dims, how='left').fillna(0)
        # считаем LTV: делим каждую «ячейку» в строке на размер когорты
        result = result.div(result['cohort_size'], axis=0)
        # исключаем все лайфтаймы, превышающие горизонт анализа
        result = result[['cohort_size'] + list(range(horizon_days))]
        # восстанавливаем размеры когорт
        result['cohort_size'] = cohort_sizes

        # собираем датафрейм с данными пользователей и значениями CAC, 
        # добавляя параметры из dimensions
        cac = df[['user_id', 'acquisition_cost'] + dims].drop_duplicates()

        # считаем средний CAC по параметрам из dimensions
        cac = (
            cac.groupby(dims)
            .agg({'acquisition_cost': 'mean'})
            .rename(columns={'acquisition_cost': 'cac'})
        )

        # считаем ROI: делим LTV на CAC
        roi = result.div(cac['cac'], axis=0)

        # удаляем строки с бесконечным ROI
        roi = roi[~roi['cohort_size'].isin([np.inf])]

        # восстанавливаем размеры когорт в таблице ROI
        roi['cohort_size'] = cohort_sizes

        # добавляем CAC в таблицу ROI
        roi['cac'] = cac['cac']

        # в финальной таблице оставляем размеры когорт, CAC
        # и ROI в лайфтаймы, не превышающие горизонт анализа
        roi = roi[['cohort_size', 'cac'] + list(range(horizon_days))]

        # возвращаем таблицы LTV и ROI
        return result, roi

    # получаем таблицы LTV и ROI
    result_grouped, roi_grouped = group_by_dimensions(
        result_raw, dimensions, horizon_days
    )

    # для таблиц динамики убираем 'cohort' из dimensions
    if 'cohort' in dimensions:
        dimensions = []

    # получаем таблицы динамики LTV и ROI
    result_in_time, roi_in_time = group_by_dimensions(
        result_raw, dimensions + ['dt'], horizon_days
    )

    return (
        result_raw,  # сырые данные
        result_grouped,  # таблица LTV
        result_in_time,  # таблица динамики LTV
        roi_grouped,  # таблица ROI
        roi_in_time,  # таблица динамики ROI
    )