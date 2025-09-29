from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializers import MountainPassCreateSerializer, MountainPassSerializer
from .models import MountainPass


class SubmitDataView(APIView):
    """
    API endpoint для добавления данных о перевале
    POST /submitData/
    """

    def post(self, request):
        try:
            # Валидация обязательных полей
            required_fields = ['title', 'user', 'coords', 'level']
            for field in required_fields:
                if field not in request.data:
                    return Response({
                        "status": 400,
                        "message": f"Отсутствует обязательное поле: {field}",
                        "id": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Валидация полей пользователя
            user_fields = ['email', 'fam', 'name', 'phone']
            for field in user_fields:
                if field not in request.data['user']:
                    return Response({
                        "status": 400,
                        "message": f"Отсутствует поле пользователя: {field}",
                        "id": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Валидация координат
            coord_fields = ['latitude', 'longitude', 'height']
            for field in coord_fields:
                if field not in request.data['coords']:
                    return Response({
                        "status": 400,
                        "message": f"Отсутствует поле координат: {field}",
                        "id": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Создание перевала в транзакции
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


class MountainPassDetailView(APIView):
    """
    API endpoint для получения данных о перевале
    GET /mountain-passes/<id>/
    """

    def get(self, request, pk):
        try:
            mountain_pass = MountainPass.objects.get(pk=pk)
            serializer = MountainPassSerializer(mountain_pass)
            return Response(serializer.data)
        except MountainPass.DoesNotExist:
            return Response({
                "message": "Перевал не найден"
            }, status=status.HTTP_404_NOT_FOUND)