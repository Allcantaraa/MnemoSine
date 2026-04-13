from django.urls import path
from dashboard import views, organization_views

urlpatterns = [
    # Index
    path('', views.index, name='index'),

    # Dashboard listings
    path('clientes/<slug:slug>/', views.dashboards, name='cliente_dashboard'),
    path('dashboard/<slug:slug>/', views.dashboard, name='detalhes_dashboard'),

    # Clientes CRUD
    path('clientes/criar', views.criar_cliente, name='criar_cliente'),
    path('clientes/<slug:slug>/atualizar/', views.atualizar_cliente, name='atualizar_cliente'),
    path('clientes/<slug:slug>/deletar/', views.deletar_cliente, name='deletar_cliente'),

    # Categorias CRUD
    path('categoria/<slug:client_slug>/criar', views.criar_categoria, name='criar_categoria'),
    path('categoria/<slug:client_slug>/atualizar/<slug:categoria_slug>', views.atualizar_categoria, name='atualizar_categoria'),
    path('categoria/<slug:client_slug>/deletar/<slug:categoria_slug>', views.deletar_categoria, name='deletar_categoria'),

    # Dashboards CRUD
    path('clientes/<slug:client_slug>/dashboard/criar', views.criar_dashboard, name='criar_dashboard'),
    path('clientes/<slug:client_slug>/dashboard/editar/<slug:slug>', views.atualizar_dashboard, name='atualizar_dashboard'),
    path('clientes/<slug:client_slug>/dashboard/deletar/<slug:dashboard_slug>', views.deletar_dashboard, name='deletar_dashboard'),
    path('clientes/<slug:client_slug>/dashboard/baixar/<slug:dashboard_slug>', views.baixar_dashboard_json, name='baixar_dashboard_json'),

    # Organization management
    path('organization/criar', organization_views.criar_organizacao, name='criar_organizacao'),
    path('organization/membros', organization_views.listar_membros, name='listar_membros'),
    path('organization/membros/<int:user_id>/role', organization_views.alterar_role_membro, name='alterar_role_membro'),
    path('organization/membros/<int:user_id>/remover', organization_views.remover_membro, name='remover_membro'),
    path('organization/codigo-novo', organization_views.gerar_novo_codigo, name='gerar_novo_codigo'),
    path('organization/entrar', organization_views.entrar_organizacao, name='entrar_organizacao'),
    path('organization/selecionar', organization_views.selecionar_organizacao, name='selecionar_organizacao'),
    path('organization/sair', organization_views.sair_organizacao, name='sair_organizacao'),
    path('organization/deletar', organization_views.deletar_organizacao, name='deletar_organizacao'),
]
