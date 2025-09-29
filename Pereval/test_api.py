import requests
import json

# Правильные URL для тестирования
urls = [
    "http://127.0.0.1:8000/submitData/",
    "http://localhost:8000/submitData/"
]

# Данные для отправки
data = {
    "title": "Тестовый перевал",
    "user": {
        "email": "test@mail.ru",
        "fam": "Иванов",
        "name": "Иван",
        "phone": "+7 999 999 99 99"
    },
    "coords": {
        "latitude": "45.1234",
        "longitude": "7.5678",
        "height": "1500"
    },
    "level": {
        "winter": "",
        "summer": "1А",
        "autumn": "1А",
        "spring": ""
    }
}

print("Тестируем API...")

for url in urls:
    try:
        print(f"\nПробуем URL: {url}")
        response = requests.post(url, json=data, timeout=5)
        print(f"Статус код: {response.status_code}")

        if response.status_code == 200:
            print("✅ Успех! Ответ сервера:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            break
        elif response.status_code == 404:
            print("❌ Страница не найдена (404)")
        else:
            print(f"Ответ: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
    except requests.exceptions.Timeout:
        print("❌ Таймаут подключения")
    except Exception as e:
        print(f"❌ Ошибка: {e}")