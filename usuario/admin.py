from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin) :
    list_display = ('user', 'profile_image')
    search_fields = ('user__username',)