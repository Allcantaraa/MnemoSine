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
            }
        ),
        required=False
    )

    class Meta:
        model = User
        fields = ('email','username', 'profile_image')

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

class Login_Form(AuthenticationForm) :
        
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder' : 'Digite seu email'
    }), label='E-mail')
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Digite sua senha',
    }), label='Senha')

class CadastroForm(UserCreationForm) :
    
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={'placeholder': 'Nome de usuário'}),
        required=True
    )
    
    profile_image = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        required=False
    )
    
    email = forms.EmailField(
        label='E-mail',
        widget=(forms.EmailInput(attrs={'placeholder': 'Digite seu email'})),
        required=True
    )
    
    password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": 'form-control'}),
        required=False,
    )

    password2 = forms.CharField(
        label="Confirmação de senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": 'form-control mb-4'}),
        required=False,
    )
    
    class Meta :
        model = User
        fields = ('username', 'email', 'profile_image','password1', 'password2')
        
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