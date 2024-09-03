from datetime import timedelta
import pandas as pd

def get_conversion(
    profiles: pd.DataFrame, 
    purchases: pd.DataFrame, 
    observation_date: pd.Timestamp, 
    horizon_days: int, 
    dimensions: list = [], 
    ignore_horizon: bool = False
) -> tuple:
    """
    Функция для расчёта конверсии пользователей на основе профилей, данных о покупках и временного горизонта анализа.
    Она выполняет следующие задачи:
    - Рассчитывает количество дней, прошедших с момента первого посещения до первой покупки.
    - Определяет, какие пользователи достигли заданного горизонта анализа.
    - Группирует пользователей по различным признакам для анализа конверсии и создаёт когорты.

    Параметры:
    profiles (pd.DataFrame): DataFrame с профилями пользователей, содержащий столбцы 'user_id', 'first_ts' (дата первого визита) и 'dt'.
    purchases (pd.DataFrame): DataFrame с информацией о покупках пользователей, содержащий столбцы 'user_id' и 'event_dt' (дата и время покупки).
    observation_date (pd.Timestamp): Дата наблюдения для анализа, определяющая максимальную дату, до которой учитываются данные.
    horizon_days (int): Количество дней, определяющее горизонт анализа конверсии.
    dimensions (list): Список признаков для группировки данных при анализе конверсии (по умолчанию пустой список).
    ignore_horizon (bool): Флаг, указывающий, игнорировать ли горизонт анализа (по умолчанию False).

    Возвращает:
    tuple: Кортеж из трёх элементов:
        - result_raw (pd.DataFrame): «Сырые» данные для расчёта конверсии, включающие столбцы 'user_id', 'first_ts', 'event_dt', 'lifetime' и другие.
        - result_grouped (pd.DataFrame): Таблица конверсии, агрегированная по указанным признакам, с расчётами долей конверсии.
        - result_in_time (pd.DataFrame): Таблица динамики конверсии с учётом временного среза (дата первой покупки).
    """
    

    # исключаем пользователей, не «доживших» до горизонта анализа
    last_suitable_acquisition_date = observation_date
    if not ignore_horizon:
        last_suitable_acquisition_date = observation_date - timedelta(
            days=horizon_days - 1
        )
    result_raw = profiles.query('dt <= @last_suitable_acquisition_date')

    # определяем дату и время первой покупки для каждого пользователя
    first_purchases = (
        purchases.sort_values(by=['user_id', 'event_dt'])
        .groupby('user_id')
        .agg({'event_dt': 'first'})
        .reset_index()
    )

    # добавляем данные о покупках в профили
    result_raw = result_raw.merge(
        first_purchases[['user_id', 'event_dt']], on='user_id', how='left'
    )

    # рассчитываем лайфтайм для каждой покупки
    result_raw['lifetime'] = (
        result_raw['event_dt'] - result_raw['first_ts']
    ).dt.days

    # группируем по cohort, если в dimensions ничего нет
    if len(dimensions) == 0:
        result_raw['cohort'] = 'All users' 
        dimensions = dimensions + ['cohort']

    # функция для группировки таблицы по желаемым признакам
    def group_by_dimensions(df, dims, horizon_days):
        result = df.pivot_table(
            index=dims, columns='lifetime', values='user_id', aggfunc='nunique'
        )
        result = result.fillna(0).cumsum(axis = 1)
        cohort_sizes = (
            df.groupby(dims)
            .agg({'user_id': 'nunique'})
            .rename(columns={'user_id': 'cohort_size'})
        )
        result = cohort_sizes.merge(result, on=dims, how='left').fillna(0)
        # делим каждую «ячейку» в строке на размер когорты
        # и получаем conversion rate
        result = result.div(result['cohort_size'], axis=0)
        result = result[['cohort_size'] + list(range(horizon_days))]
        result['cohort_size'] = cohort_sizes
        return result

    # получаем таблицу конверсии
    result_grouped = group_by_dimensions(result_raw, dimensions, horizon_days)

    # для таблицы динамики конверсии убираем 'cohort' из dimensions
    if 'cohort' in dimensions: 
        dimensions = []

    # получаем таблицу динамики конверсии
    result_in_time = group_by_dimensions(
        result_raw, dimensions + ['dt'], horizon_days
    )

    # возвращаем обе таблицы и сырые данные
    return result_raw, result_grouped, result_in_time