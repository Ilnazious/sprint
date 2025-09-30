from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import MountainPass, User
from .serializers import (
    MountainPassCreateSerializer,
    MountainPassSerializer,
    MountainPassUpdateSerializer
)


class SubmitDataAPIView(APIView):
    """
    POST /submitData/ - Добавление нового перевала
    """

    def post(self, request):
        try:
            # Базовая валидация обязательных полей
            required_fields = ['title', 'user', 'coords', 'level']
            for field in required_fields:
                if field not in request.data:
                    return Response({
                        "status": 400,
                        "message": f"Отсутствует обязательное поле: {field}",
                        "id": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Валидация пользователя
            user_fields = ['email', 'fam', 'name', 'phone']
            for field in user_fields:
                if field not in request.data.get('user', {}):
                    return Response({
                        "status": 400,
                        "message": f"Отсутствует поле пользователя: {field}",
                        "id": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Валидация координат
            coord_fields = ['latitude', 'longitude', 'height']
            for field in coord_fields:
                if field not in request.data.get('coords', {}):
                    return Response({
                        "status": 400,
                        "message": f"Отсутствует поле координат: {field}",
                        "id": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Создание в транзакции
            with transaction.atomic():
                serializer = MountainPassCreateSerializer(data=request.data)

                if serializer.is_valid():
                    mountain_pass = serializer.save()
                    return Response({
                        "status": 200,
                        "message": "Отправлено успешно",
                        "id": mountain_pass.id
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "status": 400,
                        "message": f"Ошибка валидации данных: {serializer.errors}",
                        "id": None
                    }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Внутренняя ошибка сервера: {str(e)}",
                "id": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitDataDetailAPIView(APIView):
    """
    GET /submitData/<id>/ - Получение перевала по ID
    PATCH /submitData/<id>/ - Редактирование перевала
    """

    def get(self, request, pk):
        """GET /submitData/<id>/ - Получить перевал по ID"""
        try:
            mountain_pass = MountainPass.objects.get(pk=pk)
            serializer = MountainPassSerializer(mountain_pass)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MountainPass.DoesNotExist:
            return Response({
                "status": 0,
                "message": f"Перевал с id {pk} не найден"
            }, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        """PATCH /submitData/<id>/ - Редактировать перевал"""
        try:
            mountain_pass = MountainPass.objects.get(pk=pk)

            # Проверяем статус перевала
            if mountain_pass.status != 'new':
                return Response({
                    "state": 0,
                    "message": "Редактирование запрещено: перевал не в статусе 'new'"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Проверяем, что не пытаются изменить данные пользователя
            if 'user' in request.data:
                return Response({
                    "state": 0,
                    "message": "Редактирование данных пользователя запрещено"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Обновляем перевал
            serializer = MountainPassUpdateSerializer(
                mountain_pass,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "state": 1,
                    "message": "Запись успешно обновлена"
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "state": 0,
                    "message": f"Ошибка валидации данных: {serializer.errors}"
                }, status=status.HTTP_400_BAD_REQUEST)

        except MountainPass.DoesNotExist:
            return Response({
                "state": 0,
                "message": f"Перевал с id {pk} не найден"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "state": 0,
                "message": f"Ошибка при обновлении: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitDataListAPIView(APIView):
    """
    GET /submitData/?user__email=<email> - Список перевалов по email пользователя
    """

    def get(self, request):
        email = request.GET.get('user__email')

        if not email:
            return Response({
                "status": 0,
                "message": "Не указан параметр user__email"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Находим пользователя
            user = User.objects.get(email=email)

            # Находим перевалы пользователя
            mountain_passes = MountainPass.objects.filter(user=user)

            if not mountain_passes.exists():
                return Response([], status=status.HTTP_200_OK)

            serializer = MountainPassSerializer(mountain_passes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                "status": 0,
                "message": f"Пользователь с email {email} не найден"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": 0,
                "message": f"Ошибка при получении данных: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)