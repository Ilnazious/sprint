from django.contrib import admin
from .models import User, Coords, Level, MountainPass, Image

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'fam', 'name', 'otc', 'phone')
    search_fields = ('email', 'fam', 'name')

@admin.register(Coords)
class CoordsAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'height')

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('winter', 'summer', 'autumn', 'spring')

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

@admin.register(MountainPass)
class MountainPassAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'add_time')
    list_filter = ('status', 'add_time')
    search_fields = ('title', 'user__email')
    inlines = [ImageInline]

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'mountain_pass')
    search_fields = ('title', 'mountain_pass__title')