from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model) :
    class Meta :
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='pictures/%Y/%m/', blank=True)
    
    def __str__(self):
        return self.user.username
    
    @receiver(post_save, sender=User)
    def criar_perfil(sender, instance, created, **kwargs) :
        if created :
            Perfil.objects.create(user=instance)
            
    @receiver(post_save, sender=User)
    def salvar_perfil(sender, instance,**kwargs) :
        if hasattr(instance, 'perfil') :
            instance.perfil.save()