import pandas as pd

def get_profiles(visits: pd.DataFrame, orders: pd.DataFrame, ad_costs: pd.DataFrame) -> pd.DataFrame:
    """
    Функция создаёт профили пользователей на основе данных о визитах, заказах и рекламных расходах.
    Она выполняет следующие задачи:
    - Определяет данные первого посещения (время, канал, устройство и регион) для каждого пользователя.
    - Преобразует время первого посещения в дату и месяц для когортного анализа.
    - Добавляет флаг, указывающий, совершал ли пользователь покупку.
    - Рассчитывает количество уникальных пользователей по дате и каналу привлечения.
    - Объединяет рекламные расходы с профилями пользователей, рассчитывает стоимость привлечения на одного пользователя
      и добавляет эту информацию в профили пользователей.
    - Устанавливает нулевую стоимость привлечения для органических пользователей (пользователей без затрат на рекламу).

    Параметры:
    visits (pd.DataFrame): DataFrame с данными о визитах пользователей, включая идентификатор пользователя (user_id),
                           время начала сессии (session_start), канал (channel), устройство (device) и регион (region).
    orders (pd.DataFrame): DataFrame с данными о заказах, включая идентификатор пользователя (user_id).
    ad_costs (pd.DataFrame): DataFrame с данными о рекламных расходах, включая дату (dt), канал (channel) и затраты (costs).

    Возвращает:
    pd.DataFrame: DataFrame с профилями пользователей, включая данные первого посещения, статус покупателя
                  и информацию о стоимости привлечения.
    """

    # находим параметры первых посещений
    profiles = (
        visits.sort_values(by=['user_id', 'session_start'])
        .groupby('user_id')
        .agg(
            {
                'session_start': 'first',
                'channel': 'first',
                'device': 'first',
                'region': 'first',
            }
        )
        .rename(columns={'session_start': 'first_ts'})
        .reset_index()
    )

    # для когортного анализа определяем дату первого посещения
    # и первый день месяца, в который это посещение произошло
    profiles['first_ts'] = pd.to_datetime(profiles['first_ts'])
    profiles['dt'] = profiles['first_ts'].dt.date  
    profiles['month'] = profiles['first_ts'].dt.month  

    # добавляем признак платящих пользователей
    profiles['payer'] = profiles['user_id'].isin(orders['user_id'].unique())

    # считаем количество уникальных пользователей
    # с одинаковыми источником и датой привлечения
    new_users = (
        profiles.groupby(['dt', 'channel'])
        .agg({'user_id': 'nunique'})
        .rename(columns={'user_id': 'unique_users'})
        .reset_index()
    )

    ad_costs['dt'] = ad_costs['dt'].dt.date
    # объединяем траты на рекламу и число привлечённых пользователей
    ad_costs = ad_costs.merge(new_users, on=['dt', 'channel'], how='left')

    # делим рекламные расходы на число привлечённых пользователей
    ad_costs['acquisition_cost'] = ad_costs['costs'] / ad_costs['unique_users']

    # добавляем стоимость привлечения в профили
    profiles = profiles.merge(
        ad_costs[['dt', 'channel', 'acquisition_cost']],
        on=['dt', 'channel'],
        how='left',
    )

    # стоимость привлечения органических пользователей равна нулю
    profiles['acquisition_cost'] = profiles['acquisition_cost'].fillna(0)

    return profiles