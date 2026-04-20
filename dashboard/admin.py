from django.contrib import admin
from .models import Organization, OrganizationMember, Cliente, Categoria, Dashboard, DeletionRequest

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    ordering = ('-created_at',)

@admin.register(DeletionRequest)
class DeletionRequestAdmin(admin.ModelAdmin):
    list_display = ('object_name', 'content_type', 'status', 'requested_by', 'created_at')
    list_filter = ('status', 'content_type', 'organization')
    search_fields = ('object_name', 'reason', 'requested_by__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'joined_at')
    list_display_links = ('user',)
    list_filter = ('role', 'organization')
    search_fields = ('user__username', 'organization__name')
    readonly_fields = ('joined_at',)
    list_per_page = 50
    ordering = ('-joined_at',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'tier', 'created_at', 'updated_at')
    list_display_links = ('name',)
    list_filter = ('organization', 'tier')
    search_fields = ('name', 'organization__name')
    list_per_page = 50
    ordering = ('-created_at',)
    list_editable = ('tier',)
    readonly_fields = ('updated_at', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'slug')
    list_filter = ('organization',)
    list_display_links = ('name',)
    search_fields = ('name', 'organization__name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'client', 'get_categories', 'created_at')
    list_display_links = ('title',)
    list_filter = ('organization', 'client', 'categories')
    search_fields = ('title',)
    ordering = ('-created_at',)
    list_per_page = 20
    prepopulated_fields = {
        'slug': ('title',),
    }
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='Categories')
    def get_categories(self, obj):
        return ", ".join(obj.categories.values_list('name', flat=True)) or "-"
