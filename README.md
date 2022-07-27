# logs_sds-services
### Проект по оповещению в телеграмм группу о неполадках (из логов).

Скрипт получает от watchdog информацию что файл модифирован и ищет ключевые слова такие как: Error, Exception. Сохраняет номер посследней прочитанной строк в БД SQLite рядом со скриптом.
Строки с ошибками шлет в Телеграм.

Requirements:
- os **(include in Python)**
- sys **(include in Python)**
- sqlite3 **(include in Python)**
- time **(include in Python)**
- requests **(include in Python)**
- threading **(include in Python)**
- **watchdog**

## Launch:
> main.py _path1,path2,path3_

В аргументы _path_ указываем ДИРЕКТОРИИ, рекурсия включена.
Сколько директории можно указывать **min**:1    **max**:возможности вашего ЦП 