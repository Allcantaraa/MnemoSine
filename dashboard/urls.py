from django.urls import path
from dashboard import views
urlpatterns = [
    path('', views.index, name='index'),
    path('clientes/<slug:slug>/', views.dashboards, name='cliente_dashboard'),
    path('clientes/criar', views.criar_cliente, name='criar_cliente'),
    path('clientes/<slug:slug>/atualizar/', views.atualizar_cliente, name='atualizar_cliente'),
    path('clientes/<slug:slug>/deletar/', views.deletar_cliente, name='deletar_cliente'),
    
    path('categoria/<slug:client_slug>/criar', views.criar_categoria, name='criar_categoria'),
    path('categoria/<slug:client_slug>/atualizar/<slug:categoria_slug>', views.atualizar_categoria, name='atualizar_categoria'),
    path('categoria/<slug:client_slug>/deletar/<slug:categoria_slug>', views.deletar_categoria, name='deletar_categoria'),
    
    path('dashboard/<slug:slug>/', views.dashboard, name='detalhes_dashboard'),
]