from django.urls import path
from dashboard import views
urlpatterns = [
    path('', views.index, name='index'),
    path('clientes/<slug:slug>/', views.dashboards, name='cliente_dashboard'),
    path('clientes/criar', views.criar_cliente, name='criar_cliente'),
    path('clientes/<slug:slug>/atualizar/', views.atualizar_cliente, name='atualizar_cliente'),
    path('clientes/<slug:slug>/deletar/', views.deletar_cliente, name='deletar_cliente'),
    path('dashboard/<slug:slug>/', views.dashboard, name='detalhes_dashboard'),
]