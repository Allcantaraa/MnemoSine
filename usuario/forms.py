from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from usuario.models import Perfil

class RegisterUpdateForm(forms.ModelForm) :

    profile_image = forms.ImageField(
        widget=forms.ClearableFileInput(
            attrs={
                'accept': 'image/*',
                'class': 'form-input',
            }
        ),
        required=False
    )

    class Meta:
        model = User
        fields = ('email','username', 'profile_image')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'E-mail'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Usuário'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email

        if current_email != email:
            if User.objects.filter(email=email).exists():
                self.add_error(
                    'email',
                    ValidationError('Já existe este e-mail', code='invalid')
                )

        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['profile_image'].label = "Imagem de Perfil"
        self.fields['email'].label = "E-mail"
        self.fields['username'].label = "Usuário"

class Login_Form(AuthenticationForm) :

    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder' : 'Digite seu email',
        'class': 'form-input',
    }), label='E-mail')

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Digite sua senha',
        'class': 'form-input',
    }), label='Senha')

class CadastroForm(UserCreationForm) :

    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={'placeholder': 'Nome de usuário', 'class': 'form-input'}),
        required=True
    )

    profile_image = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'class': 'form-input',
            }
        ),
        required=False
    )

    email = forms.EmailField(
        label='E-mail',
        widget=(forms.EmailInput(attrs={'placeholder': 'Digite seu email', 'class': 'form-input'})),
        required=True
    )

    password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": 'form-input'}),
        required=False,
    )

    password2 = forms.CharField(
        label="Confirmação de senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": 'form-input'}),
        required=False,
    )

    class Meta :
        model = User
        fields = ('username', 'email', 'profile_image','password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['profile_image'].label = "Imagem de Perfil"

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        usuario = super().save(commit=False)
        password = cleaned_data.get('password1')

        if password:
            usuario.set_password(password)

        if commit:
            usuario.save()

        return usuario

    def clean(self) :
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 or password2 :

            if password1 != password2 :
                self.add_error(
                    'password2', ValidationError('Senhas não coincidem', code='invalid')
                )
        return super().clean()


    def clean_email(self) :
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists() :
            self.add_error(
                'email', ValidationError('Email já cadastrado!', code='invalid')
            )
        return email
