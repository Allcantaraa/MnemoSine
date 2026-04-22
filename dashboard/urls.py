from django.urls import path
from dashboard import views, organization_views

urlpatterns = [
    # Index
    path('', views.index, name='index'),
    path('clientes/<slug:slug>/favoritar/', views.toggle_favorite_cliente, name='toggle_favorite_cliente'),
    
    path('clientes/bulk/mover/', views.mover_clientes_bulk, name='mover_clientes_bulk'),
    path('clientes/bulk/duplicar/', views.duplicar_clientes_bulk, name='duplicar_clientes_bulk'),
    path('clientes/bulk/favoritar/', views.favoritar_clientes_bulk, name='favoritar_clientes_bulk'),
    path('clientes/bulk/deletar/', views.deletar_clientes_bulk, name='deletar_clientes_bulk'),

    # Dashboard listings
    path('clientes/<slug:slug>/', views.dashboards, name='cliente_dashboard'),
    path('dashboard/<slug:slug>/', views.dashboard, name='detalhes_dashboard'),
    path('clientes/<slug:client_slug>/dashboard/favoritar/<slug:dashboard_slug>/', views.toggle_favorite_dashboard, name='toggle_favorite_dashboard'),
    path('api/dashboards/recomendacoes/', views.api_recomendacoes_dashboards, name='api_recomendacoes_dashboards'),

    # Clientes CRUD
    path('clientes/criar', views.criar_cliente, name='criar_cliente'),
    path('clientes/<slug:slug>/atualizar/', views.atualizar_cliente, name='atualizar_cliente'),
    path('clientes/<slug:slug>/deletar/', views.deletar_cliente, name='deletar_cliente'),

    # Categorias CRUD
    path('categoria/<slug:client_slug>/criar/', views.criar_categoria, name='criar_categoria'),
    path('categoria/<slug:client_slug>/atualizar/<slug:categoria_slug>/', views.atualizar_categoria, name='atualizar_categoria'),
    path('categoria/<slug:client_slug>/deletar/<slug:categoria_slug>/', views.deletar_categoria, name='deletar_categoria'),

    # Dashboards CRUD
    path('clientes/<slug:client_slug>/dashboard/criar', views.criar_dashboard, name='criar_dashboard'),
    path('clientes/<slug:client_slug>/dashboard/editar/<slug:slug>', views.atualizar_dashboard, name='atualizar_dashboard'),
    path('clientes/<slug:client_slug>/dashboard/deletar/<slug:dashboard_slug>', views.deletar_dashboard, name='deletar_dashboard'),
    path('clientes/<slug:client_slug>/dashboard/baixar/<slug:dashboard_slug>', views.baixar_dashboard_json, name='baixar_dashboard_json'),
    path('clientes/<slug:client_slug>/dashboards/criar-massa/', views.criar_dashboards_massa, name='criar_dashboards_massa'),

    # Bulk operations
    path('clientes/<slug:client_slug>/dashboards/mover/', views.mover_dashboards, name='mover_dashboards'),
    path('clientes/<slug:client_slug>/dashboards/deletar-bulk/', views.deletar_dashboards_bulk, name='deletar_dashboards_bulk'),
    path('clientes/<slug:client_slug>/dashboards/duplicar-bulk/', views.duplicar_dashboards_bulk, name='duplicar_dashboards_bulk'),
    path('clientes/<slug:client_slug>/dashboards/favoritar-bulk/', views.favoritar_dashboards_bulk, name='favoritar_dashboards_bulk'),

    # Organization management
    path('organization/membros', organization_views.listar_membros, name='listar_membros'),
    path('organization/usuarios/criar', organization_views.criar_usuario_organizacao, name='criar_usuario_organizacao'),
    path('organization/membros/<int:user_id>/role', organization_views.alterar_role_membro, name='alterar_role_membro'),
    path('organization/membros/<int:user_id>/remover', organization_views.remover_membro, name='remover_membro'),
    path('organization/selecionar', organization_views.selecionar_organizacao, name='selecionar_organizacao'),
    path('organization/importar-csv', organization_views.importar_usuarios_csv, name='importar_usuarios_csv'),

    # Notifications & Deletion Requests
    path('notificacoes/', views.listar_notificacoes, name='listar_notificacoes'),
    path('notificacoes/<int:request_id>/revisar/', views.revisar_solicitacao, name='revisar_solicitacao'),
]
