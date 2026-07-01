import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.http import require_POST

from dashboard.decorators import organization_required, organization_member_or_admin_required
from .models import Category, CodeEntry, CodeVersion


@login_required
@organization_required
def home(request):
    org = request.organization
    category_filter = request.GET.get('category', '').strip()

    total = CodeEntry.objects.filter(organization=org).count()
    html_graphics_count = CodeEntry.objects.filter(organization=org, type=CodeEntry.Type.HTML_GRAPHICS).count()
    dashboard_json_count = CodeEntry.objects.filter(organization=org, type=CodeEntry.Type.DASHBOARD_JSON).count()
    total_interactions = sum(
        CodeEntry.objects.filter(organization=org).values_list('view_count', flat=True)
    ) + sum(
        CodeEntry.objects.filter(organization=org).values_list('copy_count', flat=True)
    ) + sum(
        CodeEntry.objects.filter(organization=org).values_list('export_count', flat=True)
    )

    base_qs = CodeEntry.objects.filter(organization=org).annotate(
        is_favorite=Count('favorited_by', filter=Q(favorited_by=request.user))
    )
    if category_filter:
        base_qs = base_qs.filter(category=category_filter)

    all_codes = list(base_qs)
    favorites = [c for c in all_codes if c.is_favorite]
    most_used = sorted(all_codes, key=lambda c: c.score, reverse=True)[:6]
    recent = list(base_qs.order_by('-created_at')[:6])

    type_icon_map = {
        'html_graphics': 'fa-code',
        'html_text': 'fa-file-lines',
        'business_text': 'fa-align-left',
        'dashboard_json': 'fa-table-columns',
        'sql': 'fa-database',
        'javascript': 'fa-square-js',
        'css': 'fa-palette',
        'svg': 'fa-vector-square',
    }
    counts_by_type = {
        item['type']: item['count']
        for item in CodeEntry.objects.filter(organization=org).values('type').annotate(count=Count('id'))
    }
    type_breakdown = [
        {
            'label': label,
            'count': counts_by_type.get(value, 0),
            'icon': type_icon_map.get(value, 'fa-file-code'),
        }
        for value, label in CodeEntry.Type.choices
    ]

    return render(request, 'forge/home.html', {
        'total': total,
        'type_breakdown': type_breakdown,
        'favorites': favorites,
        'most_used': most_used,
        'recent': recent,
        'categories': _get_categories(org),
        'category_filter': category_filter,
    })


@login_required
@organization_required
def biblioteca(request):
    org = request.organization

    search = request.GET.get('search', '').strip()
    type_filter = request.GET.get('type', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    codes = CodeEntry.objects.filter(organization=org).annotate(
        is_favorite=Count('favorited_by', filter=Q(favorited_by=request.user))
    )

    if search:
        codes = codes.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search) |
            Q(content__icontains=search)
        )
    if type_filter:
        codes = codes.filter(type=type_filter)
    if category_filter:
        codes = codes.filter(category=category_filter)
    if status_filter:
        codes = codes.filter(status=status_filter)

    codes = codes.order_by('-created_at')

    categories = _get_categories(org)

    return render(request, 'forge/biblioteca.html', {
        'codes': codes,
        'categories': categories,
        'create_category_url': '/forge/categorias/criar/',
        'type_choices': CodeEntry.Type.choices,
        'status_choices': CodeEntry.Status.choices,
        'search': search,
        'type_filter': type_filter,
        'category_filter': category_filter,
        'status_filter': status_filter,
    })


@login_required
@organization_member_or_admin_required
def novo_codigo(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code_type = request.POST.get('type', '')
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', CodeEntry.Status.DRAFT)
        version = request.POST.get('version', '1.0.0').strip()
        content_raw = request.POST.get('content', '').strip()
        thumbnail = request.FILES.get('thumbnail')

        if not name or not code_type or not content_raw:
            messages.error(request, 'Nome, tipo e conteúdo são obrigatórios.')
            categories = _get_categories(request.organization)
            return render(request, 'forge/novo_codigo.html', {
                'type_choices': CodeEntry.Type.choices,
                'status_choices': CodeEntry.Status.choices,
                'categories': categories,
                'form_data': request.POST,
            })

        try:
            content = json.loads(content_raw)
        except json.JSONDecodeError:
            content = {'raw': content_raw}

        code = CodeEntry(
            organization=request.organization,
            name=name,
            type=code_type,
            category=category,
            description=description,
            status=status,
            version=version,
            content=content,
            created_by=request.user,
        )
        if thumbnail:
            code.thumbnail = thumbnail
        code.save()

        CodeVersion.objects.create(
            code=code,
            version=version,
            content=content,
            changelog='Versão inicial',
            created_by=request.user,
        )

        messages.success(request, f'Código "{name}" criado com sucesso.')
        return redirect('forge:detalhes', slug=code.slug)

    categories = _get_categories(request.organization)
    return render(request, 'forge/novo_codigo.html', {
        'type_choices': CodeEntry.Type.choices,
        'status_choices': CodeEntry.Status.choices,
        'categories': categories,
    })


@login_required
@organization_required
def detalhes(request, slug):
    code = get_object_or_404(CodeEntry, slug=slug, organization=request.organization)
    code.view_count += 1
    code.last_used_at = timezone.now()
    code.save(update_fields=['view_count', 'last_used_at'])

    versions = code.versions.order_by('-created_at')

    return render(request, 'forge/detalhes.html', {
        'code': code,
        'versions': versions,
        'content_json': json.dumps(code.content, indent=2, ensure_ascii=False),
    })


@login_required
@organization_member_or_admin_required
def editar_codigo(request, slug):
    code = get_object_or_404(CodeEntry, slug=slug, organization=request.organization)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code_type = request.POST.get('type', '')
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', code.status)
        version = request.POST.get('version', code.version).strip()
        content_raw = request.POST.get('content', '').strip()
        thumbnail = request.FILES.get('thumbnail')
        changelog = request.POST.get('changelog', '').strip()

        if not name or not code_type or not content_raw:
            messages.error(request, 'Nome, tipo e conteúdo são obrigatórios.')
            categories = _get_categories(request.organization)
            return render(request, 'forge/editar_codigo.html', {
                'code': code,
                'type_choices': CodeEntry.Type.choices,
                'status_choices': CodeEntry.Status.choices,
                'categories': categories,
                'content_json': json.dumps(code.content, indent=2, ensure_ascii=False),
            })

        try:
            content = json.loads(content_raw)
        except json.JSONDecodeError:
            content = {'raw': content_raw}

        old_content = code.content
        code.name = name
        code.type = code_type
        code.category = category
        code.description = description
        code.status = status
        code.version = version
        code.content = content
        code.edit_count += 1
        if thumbnail:
            code.thumbnail = thumbnail
        code.save()

        if content != old_content:
            CodeVersion.objects.create(
                code=code,
                version=version,
                content=content,
                changelog=changelog or f'Atualizado para v{version}',
                created_by=request.user,
            )

        messages.success(request, f'Código "{name}" atualizado.')
        return redirect('forge:detalhes', slug=code.slug)

    categories = _get_categories(request.organization)
    return render(request, 'forge/editar_codigo.html', {
        'code': code,
        'type_choices': CodeEntry.Type.choices,
        'status_choices': CodeEntry.Status.choices,
        'categories': categories,
        'content_json': json.dumps(code.content, indent=2, ensure_ascii=False),
    })


@login_required
@organization_required
def exportar(request, slug):
    code = get_object_or_404(CodeEntry, slug=slug, organization=request.organization)
    code.export_count += 1
    code.last_used_at = timezone.now()
    code.save(update_fields=['export_count', 'last_used_at'])

    payload = json.dumps(code.content, indent=2, ensure_ascii=False)
    response = HttpResponse(payload, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{code.slug}.json"'
    return response


@login_required
@organization_required
def track_action(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    code = get_object_or_404(CodeEntry, slug=slug, organization=request.organization)
    action = request.POST.get('action', '')

    field_map = {
        'copy': 'copy_count',
        'export': 'export_count',
        'view': 'view_count',
    }

    if action in field_map:
        setattr(code, field_map[action], getattr(code, field_map[action]) + 1)
        code.last_used_at = timezone.now()
        code.save(update_fields=[field_map[action], 'last_used_at'])

    return JsonResponse({'ok': True})


def _get_categories(org):
    model_cats = set(Category.objects.filter(organization=org).values_list('name', flat=True))
    code_cats = set(
        CodeEntry.objects.filter(organization=org)
        .exclude(category='')
        .values_list('category', flat=True)
    )
    return sorted(model_cats | code_cats)


@login_required
@organization_required
@require_POST
def create_category(request):
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'error': 'Nome obrigatório'}, status=400)
    cat, created = Category.objects.get_or_create(organization=request.organization, name=name)
    return JsonResponse({'success': True, 'name': cat.name, 'created': created})


@login_required
@organization_required
def buscar(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    from django.urls import reverse
    org = request.organization
    codes = CodeEntry.objects.filter(organization=org).filter(
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(category__icontains=q) |
        Q(content__icontains=q)
    )[:8]

    results = [
        {
            'name': c.name,
            'type': c.get_type_display(),
            'category': c.category or '',
            'initial': c.name[0].upper() if c.name else '?',
            'url': reverse('forge:detalhes', args=[c.slug]),
        }
        for c in codes
    ]
    return JsonResponse({'results': results})


@login_required
@organization_required
@require_POST
def bulk_action(request):
    action = request.POST.get('action')
    ids = request.POST.getlist('ids[]')
    org = request.organization

    if not ids or action not in ('delete', 'duplicate', 'favorite'):
        return JsonResponse({'error': 'Parâmetros inválidos'}, status=400)

    codes = CodeEntry.objects.filter(id__in=ids, organization=org)

    if action == 'delete':
        count = codes.count()
        codes.delete()
        return JsonResponse({'success': True, 'count': count})

    if action == 'duplicate':
        count = 0
        for code in codes:
            CodeEntry.objects.create(
                organization=org,
                name=f'{code.name} (cópia)',
                type=code.type,
                category=code.category,
                description=code.description,
                status=code.status,
                content=code.content,
                version=code.version,
                created_by=request.user,
            )
            count += 1
        return JsonResponse({'success': True, 'count': count})

    if action == 'favorite':
        count = 0
        for code in codes:
            code.favorited_by.add(request.user)
            count += 1
        return JsonResponse({'success': True, 'count': count})


@login_required
@organization_required
@require_POST
def toggle_favorite(request, slug):
    code = get_object_or_404(CodeEntry, slug=slug, organization=request.organization)
    if request.user in code.favorited_by.all():
        code.favorited_by.remove(request.user)
        is_favorite = False
    else:
        code.favorited_by.add(request.user)
        is_favorite = True
    return JsonResponse({'success': True, 'is_favorite': is_favorite})
