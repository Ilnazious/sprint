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
            'user', 'coords', 'level', 'images'
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        level_data = validated_data.pop('level')
        images_data = validated_data.pop('images', [])

        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        if not created:
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        coords = Coords.objects.create(**coords_data)

        level = Level.objects.create(**level_data)

        mountain_pass = MountainPass.objects.create(
            user=user,
            coords=coords,
            level=level,
            **validated_data
        )

        for image_data in images_data:
            Image.objects.create(mountain_pass=mountain_pass, **image_data)

        return mountain_pass

class MountainPassSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    coords = CoordsSerializer(read_only=True)
    level = LevelSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MountainPass
        fields = [
            'id', 'beauty_title', 'title', 'other_titles', 'connect',
            'add_time', 'user', 'coords', 'level', 'images', 'status'
        ]
        read_only_fields = ['id', 'add_time', 'status', 'user']

class MountainPassUpdateSerializer(serializers.ModelSerializer):
    coords = CoordsSerializer(required=False)
    level = LevelSerializer(required=False)
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model = MountainPass
        fields = [
            'beauty_title', 'title', 'other_titles', 'connect',
            'coords', 'level', 'images'
        ]

    def update(self, instance, validated_data):
        coords_data = validated_data.pop('coords', None)
        level_data = validated_data.pop('level', None)
        images_data = validated_data.pop('images', None)

        if coords_data:
            coords_serializer = CoordsSerializer(instance.coords, data=coords_data, partial=True)
            if coords_serializer.is_valid():
                coords_serializer.save()

        if level_data:
            level_serializer = LevelSerializer(instance.level, data=level_data, partial=True)
            if level_serializer.is_valid():
                level_serializer.save()

        if images_data is not None:
            instance.images.all().delete()
            for image_data in images_data:
                Image.objects.create(mountain_pass=instance, **image_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance