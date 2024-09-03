from datetime import timedelta
import pandas as pd

def get_retention(
    profiles: pd.DataFrame, 
    sessions: pd.DataFrame, 
    observation_date: pd.Timestamp, 
    horizon_days: int, 
    dimensions: list = [], 
    ignore_horizon: bool = False
) -> tuple:
    """
    Функция для расчёта удержания пользователей на основе профилей, сессий и временного горизонта анализа.
    Она выполняет следующие задачи:
    - Рассчитывает количество дней, проведённых пользователями с момента первого посещения.
    - Определяет, какие пользователи достигли заданного горизонта анализа.
    - Группирует пользователей по различным признакам для анализа удержания и создаёт когорты.

    Параметры:
    profiles (pd.DataFrame): DataFrame с профилями пользователей, содержащий столбцы 'user_id', 'first_ts' (дата первого визита) и 'dt'.
    sessions (pd.DataFrame): DataFrame с информацией о сессиях пользователей, содержащий столбцы 'user_id' и 'session_start' (время начала сессии).
    observation_date (pd.Timestamp): Дата наблюдения для анализа, определяющая максимальную дату, до которой учитываются данные.
    horizon_days (int): Количество дней, определяющее горизонт анализа удержания.
    dimensions (list): Список признаков для группировки данных при анализе удержания (по умолчанию пустой список).
    ignore_horizon (bool): Флаг, указывающий, игнорировать ли горизонт анализа (по умолчанию False).

    Возвращает:
    tuple: Кортеж из трёх элементов:
        - result_raw (pd.DataFrame): «Сырые» данные для расчёта удержания, включающие столбцы 'user_id', 'first_ts', 'session_start', 'lifetime' и другие.
        - result_grouped (pd.DataFrame): Таблица удержания, агрегированная по указанным признакам, с расчётами долей удержания.
        - result_in_time (pd.DataFrame): Таблица динамики удержания с учётом временного среза (дата первого визита).
    """

    # добавляем столбец payer в передаваемый dimensions список
    dimensions = ['payer'] + dimensions

    # исключаем пользователей, не «доживших» до горизонта анализа
    last_suitable_acquisition_date = observation_date
    if not ignore_horizon:
        last_suitable_acquisition_date = observation_date - timedelta(
            days=horizon_days - 1
        )
    result_raw = profiles.query('dt <= @last_suitable_acquisition_date')

    # собираем «сырые» данные для расчёта удержания
    result_raw = result_raw.merge(
        sessions[['user_id', 'session_start']], on='user_id', how='left'
    )
    result_raw['lifetime'] = (
        result_raw['session_start'] - result_raw['first_ts']
    ).dt.days

    # функция для группировки таблицы по желаемым признакам
    def group_by_dimensions(df, dims, horizon_days):
        result = df.pivot_table(
            index=dims, columns='lifetime', values='user_id', aggfunc='nunique'
        )
        cohort_sizes = (
            df.groupby(dims)
            .agg({'user_id': 'nunique'})
            .rename(columns={'user_id': 'cohort_size'})
        )
        result = cohort_sizes.merge(result, on=dims, how='left').fillna(0)
        result = result.div(result['cohort_size'], axis=0)
        result = result[['cohort_size'] + list(range(horizon_days))]
        result['cohort_size'] = cohort_sizes
        return result

    # получаем таблицу удержания
    result_grouped = group_by_dimensions(result_raw, dimensions, horizon_days)

    # получаем таблицу динамики удержания
    result_in_time = group_by_dimensions(
        result_raw, dimensions + ['dt'], horizon_days
    )

    # возвращаем обе таблицы и сырые данные
    return result_raw, result_grouped, result_in_time