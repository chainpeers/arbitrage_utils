На русском.
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
1. Указываем своего провайдера mainnet в settings.json
   (например https://mainnet.infura.io/v3/...)
2. Заполняем базу данных
    > db_filler = FillDb(provider, factory_address, factory_abi, pair_abi, token_abi, 19043530, 19043540)
    > db_filler.fill(TOKENS_TBL)
    Предварительно готовим адрес фабрики, и все abi
    Вызов всех функций swapget.py запрашивается при создании бд
    *Очень затратная процедура. Для 10 (n) токенов и глубины в 10 (m) уходит около 10 минут.
     асимптотическая сложность O(n^2*m)*
3. Запускаем функционал find_cycles.py
    > cycleexp = CycleExplorer(TOKENS_TBL)
    > data = cycleexp.find_positive_cycles_from_block_range(19043530, 19043540, 10)
    Последний аргумент - количество итераций улучшения точности оптимального входного значения.

    В data будет храниться словарь со всеми найденными положительными циклами в пределе блоков и статистикой


English
Brief Description: Obtaining positive exchange cycles in Uniswap using web3.py

How It Works:

1. create Uniswap pairs and extract their details using web3 | swapget.py
2. add pairs with their details to the database | fill_db_with_pairs.py
3. transfer pairs from the database to a graph for easier cycle finding | db_to_graph.py
4. find cycles using the graph framework networkx | find_cycles.py
5. calculate the values after the exchange in turn using calculate.py for each pair in the cycle and find the optimal input value using binary search
6. select cycles with a positive difference
Usage:

1. Specify your mainnet provider in settings.json (for example, https://mainnet.infura.io/v3/...)
2. Fill the database
    db_filler = FillDb(provider, factory_address, factory_abi, pair_abi, token_abi, 19043530, 19043540) db_filler.fill(TOKENS_TBL)
    We prepare the factory address and all abi's in advance.
    The call to all functions in swapget.py is requested when creating the database.
    *Very resource-intensive process. For 10 (n) tokens and a depth of 10 (m), it takes about 10 minutes.
    Asymptotic complexity O(n^2*m)*

3. Run the functionality of find_cycles.py
    cycleexp = CycleExplorer(TOKENS_TBL) data = cycleexp.find_positive_cycles_from_block_range(19043530, 19043540, 10)
    last argument is the number of iterations to improve the accuracy of the optimal input value.