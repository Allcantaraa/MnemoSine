from django import forms
from django.core.exceptions import ValidationError
from dashboard.models import Cliente

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