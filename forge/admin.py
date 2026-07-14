from django.contrib import admin
from .models import CodeEntry, CodeVersion, AgentLog


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


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'organization', 'prompt_preview')
    list_filter = ('organization', 'user')
    search_fields = ('prompt', 'reply')
    readonly_fields = ('organization', 'user', 'prompt', 'reply', 'created_at')

    def prompt_preview(self, obj):
        return obj.prompt[:80] + '…' if len(obj.prompt) > 80 else obj.prompt
    prompt_preview.short_description = 'Prompt'

    def has_add_permission(self, _request):
        return False
