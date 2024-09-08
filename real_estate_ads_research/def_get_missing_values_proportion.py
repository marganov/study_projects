# Функция для вывода доли пропущенных значений в столбце
# column_name - (string) Название столбца
def get_missing_values_proportion(column_name):
    length = len(data.query(column_name + '.isnull()'))

    print('Пропущенных значений - {} ({:.2%})'.format(length, length / len(data)), sep='')