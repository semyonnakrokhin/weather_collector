# Weather Collector

Простое приложение для получения данных о погоде в 20 самых крупных городах мира и их сохранения этих данных в различных хранилищах.

## Описание

Приложение состоит из двух компонентов, представляющих собой пару контроллер - сервис:

1. **Получение данных о погоде (APIClientService):**
   - Контроллер: `controller_openweathermapapi`
   - Сервис: `OpenweathermapByCityAPIClient`

2. **Ззагрузки данных в хранилища (StorageService):**
   - **Сохранение данных в базу данных:**
     - Контроллер: `controller_storage`
     - Сервис: `WeatherServiceDB`
   - **Сохранение данных в текстовый файл и json:**
     - Контроллер: `controller_storage`
     - Сервис: `FileService`

Каждый сервис обладает своим контроллером, который обеспечивает взаимодействие с внешним миром. Все контроллеры объединены в функции `process_city`, который последовательно обращается к каждому контроллеру.

## Обычная установка и запуск на локальном хосте

1. Перейдите в директорию с вашими проектами.
2. Склонируйте репозиторий на свой локальный компьютер:

```shell
# Windows
> git clone https://github.com/semyonnakrokhin/weather_collector.git
```

3. Перейдите в каталог проекта:

```shell
# Windows
> cd weather_collector
```

4. Создайте виртуальное окружение python. Придумайте ему название, например venv_weather:

```shell
# Windows
> python -m venv venv_weather
```

5. Активируйте виртуальное окружение (не забудьте изменить имя виртуального окружения на свое):

```shell
# Windows
> .\venv_weather\Scripts\activate
```

6. Установите зависимости:

```shell
# Windows
> pip install -r requirements.txt
```

7. Установите PostgreSQL или убедитесь, что PostgreSQL установлен на вашей машине. Вы можете загрузить и установить PostgreSQL с официального веб-сайта.
8. Создайте новую базу данных PostgreSQL для вашего проекта (убедитесь, что процесс postgres запущен).

- Подключитесь к PostgreSQL (при помощи какого либо клиента) используя стандартного суперпользователя и стандартной базы данных
- Создайте новую базу данных (например, weather_db):

```sql
CREATE DATABASE weather_db;
```

- Если желаете, можете создать нового пользователя (например weather_user) и придумать ему пароль (например qwerty), от которого будете ходить в эту бд:

```sql
CREATE USER weather_user WITH PASSWORD 'qwerty';
```

- Дайте новому пользователю все привилегии для работы с базой данных:

```sql
GRANT ALL PRIVILEGES ON DATABASE weather_db TO weather_user;
```

9. Создайте в корневом каталоге файл .env и заполните его переменными для доступа к бд. Имена переменных не менять, значения вставьте свои:

```dotenv
MODE=DEV

DB_HOST=localhost
DB_PORT=5432
DB_USER=weather_user
DB_PASS=qwerty
DB_NAME=weather_db
```
</code></pre>

10. Находясь в корневом каталоге, выполните миграции:

```shell
# Windows
> alembic upgrade head
```

11. Запустите приложение, используя команду:

```shell
# Windows
> python src/main.py
```
