from django.urls import path
from . import views

app_name = 'forge'

urlpatterns = [
    path('', views.home, name='home'),
    path('biblioteca/', views.biblioteca, name='biblioteca'),
    path('novo/', views.novo_codigo, name='novo_codigo'),
    path('buscar/', views.buscar, name='buscar'),
    path('categorias/criar/', views.create_category, name='create_category'),
    path('bulk/', views.bulk_action, name='bulk_action'),
    path('<slug:slug>/favoritar/', views.toggle_favorite, name='toggle_favorite'),
    path('<slug:slug>/', views.detalhes, name='detalhes'),
    path('<slug:slug>/editar/', views.editar_codigo, name='editar_codigo'),
    path('<slug:slug>/exportar/', views.exportar, name='exportar'),
    path('<slug:slug>/track/', views.track_action, name='track'),
]
