from rest_framework import serializers
from .models import User, Coords, Level, MountainPass, Image


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'fam', 'name', 'otc', 'phone']


class CoordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coords
        fields = ['latitude', 'longitude', 'height']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['winter', 'summer', 'autumn', 'spring']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['data', 'title']


class MountainPassCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model = MountainPass
        fields = [
            'beauty_title', 'title', 'other_titles', 'connect',
            'add_time', 'user', 'coords', 'level', 'images'
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        level_data = validated_data.pop('level')
        images_data = validated_data.pop('images', [])

        # Создаем или обновляем пользователя
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        if not created:
            # Обновляем данные существующего пользователя
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Создаем координаты
        coords = Coords.objects.create(**coords_data)

        # Создаем уровень сложности
        level = Level.objects.create(**level_data)

        # Создаем перевал
        mountain_pass = MountainPass.objects.create(
            user=user,
            coords=coords,
            level=level,
            **validated_data
        )

        # Создаем изображения
        for image_data in images_data:
            Image.objects.create(mountain_pass=mountain_pass, **image_data)

        return mountain_pass


class MountainPassSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = ImageSerializer(many=True)

    class Meta:
        model = MountainPass
        fields = [
            'id', 'beauty_title', 'title', 'other_titles', 'connect',
            'add_time', 'user', 'coords', 'level', 'images', 'status'
        ]
        read_only_fields = ['id', 'status', 'add_time']