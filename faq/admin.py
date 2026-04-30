from django.contrib import admin
from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'language', 'is_active', 'synced_at')
    list_filter = ('category', 'language', 'is_active')
    search_fields = ('title', 'keywords', 'content')
    readonly_fields = ('znuny_id', 'synced_at', 'created_at')