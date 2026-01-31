from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from dashboard.models import Cliente, Categoria, Dashboard, DashboardImage

class ClienteForm(forms.ModelForm) :
    
    class Meta :
        model = Cliente
        
        fields = ('name', 'logo', 'description', 'is_vip')
        widgets = {
            'name' : forms.TextInput(attrs={
                'placeholder': 'Escreva o nome do cliente'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'accept': 'image/*'
            }),
            'description' : forms.Textarea(attrs={
                'placeholder': 'Descrição do cliente'
            }),
            'is_vip' : forms.CheckboxInput(attrs={
                'help_text': 'O cliente é vip?'
            })
        }

class CategoriaForm(forms.ModelForm) :
    class Meta :
        model = Categoria
        fields = ('name', )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['name'].label = "Nome"

class DashboardForm(forms.ModelForm) :
    class Meta: 
        model = Dashboard
        fields = ['title', 'category', 'status', 'purpose', 'target_audience', 'kpis_displayed', 'analytical_or_macro', 'data_source', 'panel_preference', 'color_preference', 'screen_resolution', 'json']
        
        widgets = {
            'title' : forms.TextInput(attrs={
                'placeholder': 'Escreva o titulo do Dashboard'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].label = "Titulo"
        self.fields['category'].label = "Categoria"
        self.fields['purpose'].label = "Objetivo"
        self.fields['target_audience'].label = "Publico alvo"
        self.fields['kpis_displayed'].label = "KPIS exibidos"
        self.fields['analytical_or_macro'].label = "Tipo de visão"
        self.fields['data_source'].label = "Fonte dos dados"
        self.fields['panel_preference'].label = "Preferencia de painél"
        self.fields['color_preference'].label = "Preferencia de cor"
        self.fields['screen_resolution'].label = "Resolução da Tela"
        self.fields['json'].label = "Arquivo JSON"
        
    

DashboardImageFormSet = inlineformset_factory(
    Dashboard, DashboardImage, fields=('images',), extra=5
)