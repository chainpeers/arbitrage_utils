Краткое описание:
Получение положительных циклов обмена валют в uniswap используя web3.py

Механика работы:
1. Создаём пары uniswap и вытаскиваем их реквизиты используя web3 | swapget.py
2. Добавляем пары с их реквизитами в бд | fill_db_with_pairs.py
3. Переводим в пары из базы в граф для простоты нахождения циклов | db_to_graph.py
4. Находим циклы используя фреймворк графов networkx | find_cycles.py
5. Вычисляем значения после обмена поочерёдно используя calculate.py для каждой пары в цикле и
находим оптимальное входное значение двоичным поиском
6. Выбираем циклы только с положительной разницей

Использование:
1. Заполняем базу данных
    > db_filler = FillDb(provider, factory_address, factory_abi, pair_abi, token_abi, 19043530, 19043540)
    > db_filler.fill(TOKENS_TBL)
    Предварительно готовим адрес фабрики, провайдер, и все abi
    Вызов всех функций swapget.py запрашивается при создании бд
    *Очень затратная процедура. Для 10 (n) токенов и глубины в 10 (m) уходит около 10 минут.
     асимптотическая сложность O(n^2*m)*
2. Запускаем функционал find_cycles.py
    > cycleexp = CycleExplorer(TOKENS_TBL)
    > data = cycleexp.find_positive_cycles_from_block_range(19043530, 19043540, 10)
    Последний аргумент - количество итераций улучшения точности оптимального входного значения.

    В data будет храниться словарь со всеми найденными положительными циклами в пределе блоков и статистикой
