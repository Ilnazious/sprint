О проекте
REST API для управления данными о горных перевалах. Этот проект разработан в рамках учебного задания с использованием Django и Django REST Framework.

Основной функционал:
Добавление новых перевалов
Получение информации о перевалах
Редактирование существующих записей
Поиск перевалов по email пользователя

Локальная разработка
Клонируйте репозиторий:
git clone <your-repository-url>
cd Pereval

Создайте виртуальное окружение:
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
Установите зависимости:
pip install -r requirements.txt

Настройте базу данных в файле .env:
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here

# Database Configuration
FSTR_DB_HOST=localhost
FSTR_DB_PORT=5432
FSTR_DB_LOGIN=postgres
FSTR_DB_PASS=password
FSTR_DB_NAME=pereval_db

Выполните миграции:
python manage.py makemigrations
python manage.py migrate

Запустите сервер:
python manage.py runserver
API будет доступно по адресу: http://localhost:8000/api/
1.  Добавление нового перевала
POST /api/submitData/

Добавляет новую запись о горном перевале в систему.
Тело запроса:
{
    "beauty_title": "пер. ",
    "title": "Пик Талгар",
    "other_titles": "Ташкентский перевал",
    "connect": "Соединяет долины рек",
    "user": {
        "email": "user@example.com",
        "fam": "Иванов",
        "name": "Иван",
        "otc": "Иванович",
        "phone": "+79990000000"
    },
    "coords": {
        "latitude": 43.1234,
        "longitude": 77.5678,
        "height": 3500
    },
    "level": {
        "winter": "1A",
        "summer": "1B",
        "autumn": "",
        "spring": ""
    },
    "images": [
        {
            "data": "base64_encoded_image_data",
            "title": "Вид на перевал"
        }
    ]
}

Ответ при успехе:
{
    "status": 200,
    "message": "Отправлено успешно",
    "id": 1
}

Ответ при ошибке:
{
    "status": 400,
    "message": "Отсутствует обязательное поле: title",
    "id": null
}

2 Получение перевала по ID
GET /api/submitData/<id>/

Возвращает полную информацию о перевале по его идентификатору.
Пример запроса:

curl -X GET http://localhost:8000/api/submitData/1/

Ответ:
{
    "id": 1,
    "beauty_title": "пер. ",
    "title": "Пик Талгар",
    "other_titles": "Ташкентский перевал",
    "connect": "Соединяет долины рек",
    "add_time": "2024-01-15T10:30:00Z",
    "status": "Новый",
    "user": {
        "email": "user@example.com",
        "fam": "Иванов",
        "name": "Иван",
        "otc": "Иванович",
        "phone": "+79990000000"
    },
    "coords": {
        "latitude": 43.1234,
        "longitude": 77.5678,
        "height": 3500
    },
    "level": {
        "winter": "1A",
        "summer": "1B",
        "autumn": "",
        "spring": ""
    },
    "images": [
        {
            "data": "base64_encoded_image_data",
            "title": "Вид на перевал"
        }
    ]
}

3.  Редактирование перевала
PATCH /api/submitData/<id>/
Редактирует существующую запись о перевале. Доступно только для записей со статусом "new".

Ограничения:
Нельзя редактировать данные пользователя (ФИО, email, телефон)
Нельзя редактировать время добавления
Только для статуса "new"

Пример запроса:
curl -X PATCH http://localhost:8000/api/submitData/1/ \
-H "Content-Type: application/json" \
-d '{
    "title": "Обновленное название",
    "connect": "Обновленное описание",
    "coords": {
        "latitude": 44.4444,
        "longitude": 79.9999,
        "height": 4000
    }
}'

Ответ при успехе:
{
    "state": 1,
    "message": "Запись успешно обновлена"
}

Ответ при ошибке:
{
    "state": 0,
    "message": "Редактирование запрещено: перевал не в статусе 'new'"
}

4 Получение перевалов по email пользователя
GET /api/submitData/list/?user__email=<email>

Возвращает список всех перевалов, добавленных пользователем с указанным email.

Пример запроса:
curl -X GET "http://localhost:8000/api/submitData/list/?user__email=user@example.com"

Ответ:
[
    {
        "id": 1,
        "beauty_title": "пер. ",
        "title": "Пик Талгар",
        "other_titles": "Ташкентский перевал",
        "connect": "Соединяет долины рек",
        "add_time": "2024-01-15T10:30:00Z",
        "status": "Новый",
        "user": {
            "email": "user@example.com",
            "fam": "Иванов",
            "name": "Иван",
            "otc": "Иванович",
            "phone": "+79990000000"
        },
        "coords": {
            "latitude": 43.1234,
            "longitude": 77.5678,
            "height": 3500
        },
        "level": {
            "winter": "1A",
            "summer": "1B",
            "autumn": "",
            "spring": ""
        },
        "images": []
    }
]
