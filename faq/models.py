from django.db import models


class FAQ(models.Model):
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'title']

    znuny_id = models.IntegerField(unique=True)
    f_number = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=500)
    category = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=10, default='pt')
    keywords = models.CharField(max_length=500, blank=True)
    symptom = models.TextField(blank=True)
    problem = models.TextField(blank=True)
    content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title