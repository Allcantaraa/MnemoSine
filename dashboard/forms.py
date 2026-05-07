from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
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
        fields = ['title', 'description','image', 'json', 'categories']

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Título do Dashboard',
                'class': 'form-input'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Descreva o objetivo e conteúdo deste dashboard...',
                'class': 'form-input',
                'rows': 4,
            }),
            'image': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'class': 'form-input'
            }),
            'json': forms.ClearableFileInput(attrs={
                'accept': '.json',
                'class': 'form-input'
            }),
            'categories': forms.SelectMultiple(attrs={
                'class': 'form-input'
            })
        }

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Título"
        self.fields['description'].label = "Descrição"
        self.fields['description'].required = False
        self.fields['image'].label = "Imagem"
        self.fields['json'].label = "Arquivo JSON"
        self.fields['categories'].label = "Categorias (Opcional)"
        self.fields['categories'].required = False
        
        # Filtrar categorias pela organização se fornecida
        if organization:
            self.fields['categories'].queryset = Categoria.objects.filter(organization=organization).order_by('name')

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('json') and not str(cleaned_data['json']).endswith('.json'):
            raise ValidationError('O arquivo deve ser um JSON válido.')

        return cleaned_data


class OrganizationUserCreateForm(forms.Form):
    username = forms.CharField(
        label='Usuário',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome de usuário',
            'class': 'form-input'
        })
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'email@exemplo.com',
            'class': 'form-input'
        })
    )
    password1 = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-input'
        })
    )
    password2 = forms.CharField(
        label='Confirmação de senha',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-input'
        })
    )
    role = forms.ChoiceField(
        label='Perfil na organização',
        choices=(
            ('administrador', 'Administrador'),
            ('membro', 'Membro'),
        ),
        initial='membro',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Já existe um usuário com este e-mail.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Já existe um usuário com este nome de usuário.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'As senhas não coincidem.')
            return cleaned_data

        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as exc:
                self.add_error('password1', exc)

        return cleaned_data
