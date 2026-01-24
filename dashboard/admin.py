from django.contrib import admin
from .models import Cliente, Categoria, Dashboard, DashboardImage

class DashboardImageInline(admin.TabularInline):
    model = DashboardImage
    extra = 1
    fields = ('images',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_vip', 'created_at', 'updated_at')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_per_page = 50
    ordering = ('-id',)
    list_editable = ('is_vip',)
    readonly_fields = ('updated_at', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'client', 'category', 'status', 'created_at')
    list_display_links = ('title',)
    list_filter = ('status', 'client', 'category', 'analytical_or_macro')
    search_fields = ('title', 'purpose', 'kpis_displayed', 'data_source')
    list_editable = ('status',)
    inlines = [DashboardImageInline]
    ordering = ('-created_at',)
    list_per_page = 20
    prepopulated_fields = {
        'slug': ('title',),
    }