from django.urls import path
from . import views

urlpatterns = [
    path('faq/', views.listar_faq, name='listar_faq'),
    path('faq/buscar/', views.buscar_faq_ajax, name='buscar_faq_ajax'),
    path('faq/<int:znuny_id>/', views.detalhe_faq, name='detalhe_faq'),
    path('faq/sincronizar/', views.sincronizar_faq, name='sincronizar_faq'),
]