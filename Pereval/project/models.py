from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    fam = models.CharField(max_length=255, verbose_name='Фамилия')
    name = models.CharField(max_length=255, verbose_name='Имя')
    otc = models.CharField(max_length=255, verbose_name='Отчество', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.fam} {self.name} ({self.email})"

class Coords(models.Model):
    latitude = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        verbose_name='Широта'
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        verbose_name='Долгота'
    )
    height = models.IntegerField(verbose_name='Высота')

    class Meta:
        verbose_name = 'Координаты'
        verbose_name_plural = 'Координаты'

    def __str__(self):
        return f"({self.latitude}, {self.longitude}, {self.height})"

class Level(models.Model):
    DIFFICULTY_CHOICES = [
        ('', 'Не указано'),
        ('1A', '1A'),
        ('1B', '1B'),
        ('2A', '2A'),
        ('2B', '2B'),
        ('3A', '3A'),
        ('3B', '3B'),
    ]

    winter = models.CharField(max_length=2, choices=DIFFICULTY_CHOICES, blank=True, verbose_name='Зима')
    summer = models.CharField(max_length=2, choices=DIFFICULTY_CHOICES, blank=True, verbose_name='Лето')
    autumn = models.CharField(max_length=2, choices=DIFFICULTY_CHOICES, blank=True, verbose_name='Осень')
    spring = models.CharField(max_length=2, choices=DIFFICULTY_CHOICES, blank=True, verbose_name='Весна')

    class Meta:
        verbose_name = 'Уровень сложности'
        verbose_name_plural = 'Уровни сложности'

    def __str__(self):
        levels = []
        if self.winter: levels.append(f"Зима: {self.winter}")
        if self.summer: levels.append(f"Лето: {self.summer}")
        if self.autumn: levels.append(f"Осень: {self.autumn}")
        if self.spring: levels.append(f"Весна: {self.spring}")
        return ", ".join(levels) if levels else "Не указано"

class MountainPass(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('pending', 'На модерации'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]

    beauty_title = models.CharField(max_length=255, blank=True, verbose_name='Красивое название')
    title = models.CharField(max_length=255, verbose_name='Название')
    other_titles = models.CharField(max_length=255, blank=True, verbose_name='Другие названия')
    connect = models.TextField(blank=True, verbose_name='Что соединяет')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    coords = models.OneToOneField(Coords, on_delete=models.CASCADE, verbose_name='Координаты')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name='Уровень сложности')

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус модерации'
    )

    class Meta:
        verbose_name = 'Перевал'
        verbose_name_plural = 'Перевалы'
        ordering = ['-add_time']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

class Image(models.Model):
    mountain_pass = models.ForeignKey(
        MountainPass,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Перевал'
    )
    data = models.TextField(verbose_name='Данные изображения (base64)')
    title = models.CharField(max_length=255, verbose_name='Название изображения')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return self.title