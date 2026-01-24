from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model) :
    class Meta :
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='pictures/%Y/%m/', blank=True)
    
    def __str__(self):
        return self.user.username