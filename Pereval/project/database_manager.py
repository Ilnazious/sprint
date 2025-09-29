import os
import psycopg2
import json
from typing import Dict, Any, Optional
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('FSTR_DB_HOST', 'localhost'),
            'port': os.getenv('FSTR_DB_PORT', '5433'),
            'user': os.getenv('FSTR_DB_LOGIN', 'fstr_user'),
            'password': os.getenv('FSTR_DB_PASS', 'password'),
            'database': os.getenv('FSTR_DB_NAME', 'fstr_db')
        }
        self.connection = None

    def connect(self):
        """Установка подключения к PostgreSQL"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
        except Exception as e:
            raise ConnectionError(f"Ошибка подключения к базе данных: {e}")

    def disconnect(self):
        """Закрытие подключения"""
        if self.connection:
            self.connection.close()

    def submit_pereval_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод для добавления данных о перевале
        Возвращает словарь с результатом операции
        """
        if not self.connection:
            self.connect()

        try:
            # Валидация обязательных полей
            validation_result = self._validate_data(data)
            if not validation_result['valid']:
                return {
                    'status': 400,
                    'message': f"Не хватает полей: {', '.join(validation_result['missing_fields'])}",
                    'id': None
                }

            # Формируем структуру raw_data согласно примеру
            raw_data = {
                "beauty_title": data.get("beauty_title", ""),
                "title": data.get("title", ""),
                "other_titles": data.get("other_titles", ""),
                "connect": data.get("connect", ""),
                "add_time": data.get("add_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "user": data.get("user", {}),
                "coords": data.get("coords", {}),
                "level": data.get("level", {})
            }

            # Формируем images
            images_data = None
            if "images" in data and data["images"]:
                images_data = {"images": data["images"]}

            with self.connection.cursor() as cursor:
                # Вставляем данные в таблицу pereval_added
                query = """
                    INSERT INTO pereval_added (date_added, raw_data, images)
                    VALUES (NOW(), %s, %s)
                    RETURNING id;
                """

                cursor.execute(query, (
                    json.dumps(raw_data, ensure_ascii=False),
                    json.dumps(images_data, ensure_ascii=False) if images_data else None
                ))

                new_id = cursor.fetchone()[0]
                self.connection.commit()

                return {
                    'status': 200,
                    'message': 'Отправлено успешно',
                    'id': new_id
                }

        except psycopg2.Error as e:
            if self.connection:
                self.connection.rollback()
            return {
                'status': 500,
                'message': f'Ошибка базы данных: {str(e)}',
                'id': None
            }
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return {
                'status': 500,
                'message': f'Ошибка при выполнении операции: {str(e)}',
                'id': None
            }

    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидация входящих данных
        """
        required_fields = ['title', 'user', 'coords', 'level']
        missing_fields = []

        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)

        # Валидация пользователя
        if 'user' in data:
            user_required = ['email', 'fam', 'name', 'phone']
            for field in user_required:
                if field not in data['user'] or not data['user'][field]:
                    missing_fields.append(f'user.{field}')

        # Валидация координат
        if 'coords' in data:
            coords_required = ['latitude', 'longitude', 'height']
            for field in coords_required:
                if field not in data['coords'] or not data['coords'][field]:
                    missing_fields.append(f'coords.{field}')

        return {
            'valid': len(missing_fields) == 0,
            'missing_fields': missing_fields
        }

    def get_pereval_by_id(self, pereval_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение данных перевала по ID
        """
        if not self.connection:
            self.connect()

        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM pereval_added WHERE id = %s;"
                cursor.execute(query, (pereval_id,))
                result = cursor.fetchone()

                if result:
                    columns = [desc[0] for desc in cursor.description]
                    pereval_dict = dict(zip(columns, result))

                    # Парсим JSON поля
                    if isinstance(pereval_dict['raw_data'], str):
                        pereval_dict['raw_data'] = json.loads(pereval_dict['raw_data'])
                    if pereval_dict.get('images') and isinstance(pereval_dict['images'], str):
                        pereval_dict['images'] = json.loads(pereval_dict['images'])

                    return pereval_dict
                return None

        except Exception as e:
            raise Exception(f"Ошибка при получении перевала: {e}")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()