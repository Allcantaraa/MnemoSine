from django import forms
from django.core.exceptions import ValidationError
from dashboard.models import Cliente, Categoria, Dashboard

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('name', 'logo', 'description', 'tier')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Escreva o nome do cliente',
                'class': 'form-input'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'class': 'form-input'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Descrição do cliente',
                'class': 'form-input'
            }),
            'tier': forms.Select(attrs={
                'class': 'form-input'
            })
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ('name', )
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nome da categoria',
                'class': 'form-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Nome"

class DashboardForm(forms.ModelForm):
    class Meta:
        model = Dashboard
        fields = ['title', 'image', 'json', 'category']

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Título do Dashboard',
                'class': 'form-input'
            }),
            'image': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'class': 'form-input'
            }),
            'json': forms.ClearableFileInput(attrs={
                'accept': '.json',
                'class': 'form-input'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input'
            })
        }

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Título"
        self.fields['image'].label = "Imagem"
        self.fields['json'].label = "Arquivo JSON"
        self.fields['category'].label = "Categoria (Opcional)"
        self.fields['category'].required = False
        
        # Deixar categoria em branco por padrão
        self.fields['category'].empty_label = "Sem categoria"
        
        # Filtrar categorias pela organização se fornecida
        if organization:
            self.fields['category'].queryset = Categoria.objects.filter(organization=organization).order_by('name')

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('json') and not str(cleaned_data['json']).endswith('.json'):
            raise ValidationError('O arquivo deve ser um JSON válido.')

        return cleaned_data
