from django.contrib import admin
from .models import User, Coords, Level, MountainPass, Image


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'fam', 'name', 'phone']
    search_fields = ['email', 'fam', 'name']

@admin.register(Coords)
class CoordsAdmin(admin.ModelAdmin):
    list_display = ['latitude', 'longitude', 'height']

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['winter', 'summer', 'autumn', 'spring']

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

@admin.register(MountainPass)
class MountainPassAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'add_time', 'user']
    list_filter = ['status', 'add_time']
    search_fields = ['title', 'beauty_title']
    inlines = [ImageInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'coords', 'level')