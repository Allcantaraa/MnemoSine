from django.contrib import admin
from .models import Organization, OrganizationMember, Cliente, Categoria, Dashboard

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_by', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'code')
    readonly_fields = ('code', 'created_at', 'updated_at')
    list_per_page = 50
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
    list_display = ('title', 'organization', 'client', 'category', 'created_at')
    list_display_links = ('title',)
    list_filter = ('organization', 'client', 'category', 'analytical_or_macro')
    search_fields = ('title', 'purpose', 'kpis_displayed', 'data_source')
    ordering = ('-created_at',)
    list_per_page = 20
    prepopulated_fields = {
        'slug': ('title',),
    }
    readonly_fields = ('created_at', 'updated_at')
