from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from .models import Cliente, Categoria, Dashboard, DashboardImage
from django.core.exceptions import ValidationError

class DashboardImageFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if self.instance.status == 'cn':
            count = 0
            for form in self.forms:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    count += 1
            
            if count == 0:
                raise ValidationError(
                    'Um Dashboard concluído precisa de pelo menos uma imagem anexada.'
                )


class DashboardImageInline(admin.TabularInline):
    model = DashboardImage
    formset = DashboardImageFormSet
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
    
    def save_related(self, request, form, formsets, change):
        status = form.cleaned_data.get('status')
        
        if status == 'cn' :
            tem_imagem = False
            for formset in formsets:
                if isinstance(formset.model, type(DashboardImage)):
                    if any(f.cleaned_data and not f.cleaned_data.get('DELETE') for f in formset.forms):
                        tem_imagem = True
            
            if not tem_imagem:
                pass

        super().save_related(request, form, formsets, change)