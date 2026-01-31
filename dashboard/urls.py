from django.urls import path
from dashboard import views
urlpatterns = [
    path('', views.index, name='index'),
    path('clientes/<slug:slug>/', views.dashboards, name='cliente_dashboard'),
    
    #filtros
    path('clientes/<slug:slug>/em_execucao', views.dashboards_em_execucao, name='dashboards_em_execucao'),
    path('clientes/<slug:slug>/novos', views.dashboards_novos, name='dashboards_novos'),
    path('clientes/<slug:slug>/concluidos', views.dashboards_concluidos, name='dashboards_concluidos'),
    
    path('clientes/criar', views.criar_cliente, name='criar_cliente'),
    path('clientes/<slug:slug>/atualizar/', views.atualizar_cliente, name='atualizar_cliente'),
    path('clientes/<slug:slug>/deletar/', views.deletar_cliente, name='deletar_cliente'),
    
    path('categoria/<slug:client_slug>/criar', views.criar_categoria, name='criar_categoria'),
    path('categoria/<slug:client_slug>/atualizar/<slug:categoria_slug>', views.atualizar_categoria, name='atualizar_categoria'),
    path('categoria/<slug:client_slug>/deletar/<slug:categoria_slug>', views.deletar_categoria, name='deletar_categoria'),
    
    path('clientes/<slug:client_slug>/dashboard/criar', views.criar_dashboard, name='criar_dashboard'),
    path('clientes/<slug:client_slug>/dashboard/editar/<slug:slug>', views.atualizar_dashboard, name='atualizar_dashboard'),
    path('clientes/<slug:client_slug>/dashboard/deletar/<slug:dashboard_slug>', views.deletar_dashboard, name='deletar_dashboard'),
    
    path('dashboard/<slug:slug>/', views.dashboard, name='detalhes_dashboard'),
]