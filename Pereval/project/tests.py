import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Coords, Level, MountainPass, Image


class BasicSetupTest(TestCase):
    """Базовый тест для проверки настроек"""

    def test_basic_model_creation(self):
        """Тест создания базовых моделей"""
        user = User.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Иван",
            phone="+79990000000"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(str(user), "Иванов Иван (test@example.com)")


class MountainPassAPITests(APITestCase):
    """Тесты API методов"""

    def setUp(self):
        """Создание тестовых данных"""
        # Создаем пользователя
        self.user = User.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Иван",
            otc="Иванович",
            phone="+79990000000"
        )

        # Создаем координаты
        self.coords = Coords.objects.create(
            latitude=43.1234,
            longitude=77.5678,
            height=3500
        )

        # Создаем уровень сложности
        self.level = Level.objects.create(
            winter="1A",
            summer="1B",
            autumn="",
            spring=""
        )

        # Создаем перевал
        self.mountain_pass = MountainPass.objects.create(
            beauty_title="пер. ",
            title="Пик Талгар",
            other_titles="Ташкентский перевал",
            connect="Соединяет долины рек",
            user=self.user,
            coords=self.coords,
            level=self.level,
            status='new'
        )

    def test_get_mountain_pass_by_id_success(self):
        """GET /submitData/<id> - успешное получение перевала по ID"""
        url = reverse('submit-data-detail', kwargs={'pk': self.mountain_pass.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Пик Талгар")
        self.assertEqual(response.data['status'], "Новый")

    def test_get_mountain_pass_by_id_not_found(self):
        """GET /submitData/<id> - перевал не найден"""
        url = reverse('submit-data-detail', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 0)
        self.assertIn('не найден', response.data['message'])

    def test_patch_mountain_pass_success(self):
        """PATCH /submitData/<id> - успешное редактирование перевала"""
        url = reverse('submit-data-detail', kwargs={'pk': self.mountain_pass.id})

        update_data = {
            "title": "Обновленное название",
            "connect": "Обновленное описание соединения"
        }

        response = self.client.patch(
            url,
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 1)
        self.assertEqual(response.data['message'], "Запись успешно обновлена")

        # Проверяем, что данные обновились
        updated_pass = MountainPass.objects.get(id=self.mountain_pass.id)
        self.assertEqual(updated_pass.title, "Обновленное название")

    def test_patch_mountain_pass_not_new_status(self):
        """PATCH /submitData/<id> - запрет редактирования для статуса не 'new'"""
        # Меняем статус перевала
        self.mountain_pass.status = 'accepted'
        self.mountain_pass.save()

        url = reverse('submit-data-detail', kwargs={'pk': self.mountain_pass.id})
        update_data = {"title": "Новое название"}

        response = self.client.patch(
            url,
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['state'], 0)
        self.assertIn('не в статусе', response.data['message'])

    def test_get_mountain_passes_by_email_success(self):
        """GET /submitData/?user__email=<email> - успешное получение списка"""
        url = reverse('submit-data-list') + '?user__email=test@example.com'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Пик Талгар")
        self.assertEqual(response.data[0]['user']['email'], "test@example.com")

    def test_get_mountain_passes_by_email_user_not_found(self):
        """GET /submitData/?user__email=<email> - пользователь не найден"""
        url = reverse('submit-data-list') + '?user__email=nonexistent@example.com'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 0)
        self.assertIn('не найден', response.data['message'])

    def test_get_mountain_passes_by_email_no_parameter(self):
        """GET /submitData/?user__email=<email> - отсутствует параметр email"""
        url = reverse('submit-data-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 0)
        self.assertIn('Не указан параметр', response.data['message'])