import math as mth
import scipy.stats as st

def z_test(group1, group2, alpha, event_group, user_group):
    """
    Функция принимает на вход названия групп, уровень значимости, данные о событиях и количество пользователей.
    Проверяет статистическую значимость разницы между долями успехов в группах с помощью Z-теста.
    """
    print('Проверка групп:', group1, 'и', group2)
    print('при уровне значимости: {:.0%}'.format(alpha))

    for i in event_group.index:
        # пропорция успехов в первой группе:
        p1 = event_group[group1][i] / user_group[group1]

        # пропорция успехов во второй группе:
        p2 = event_group[group2][i] / user_group[group2]

        # пропорция успехов в комбинированном датасете:
        p_combined = (event_group[group1][i] + event_group[group2][i]) / (user_group[group1] + user_group[group2])

        # разница пропорций в датасетах:
        difference = p1 - p2

        # считаем статистику Z
        z_value = (difference / mth.sqrt(p_combined * (1 - p_combined) *
                    (1 / user_group[group1] + 1 / user_group[group2])))

        # задаем стандартное нормальное распределение
        distr = st.norm(0, 1)

        # расчет P-value
        p_value = (1 - distr.cdf(abs(z_value))) * 2

        print('--------------------------------')
        print()
        print('Событие >', event_group['event'][i])
        print()
        print('Уровень P-value:', p_value)

        if p_value < alpha:
            print("Разница между тест группами есть")
        else:
            print("Разницы между тест группами нет")
            
        print()
