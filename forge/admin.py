from django.contrib import admin
from .models import CodeEntry, CodeVersion


@admin.register(CodeEntry)
class CodeEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'category', 'status', 'organization', 'version', 'created_at')
    list_filter = ('type', 'status', 'organization')
    search_fields = ('name', 'description', 'category')
    readonly_fields = ('slug', 'view_count', 'copy_count', 'export_count', 'edit_count', 'last_used_at')


@admin.register(CodeVersion)
class CodeVersionAdmin(admin.ModelAdmin):
    list_display = ('code', 'version', 'created_by', 'created_at')
    list_filter = ('code',)
