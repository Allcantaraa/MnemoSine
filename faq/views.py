import re
from html import unescape
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Case, When, IntegerField, Value
from django.http import JsonResponse
from django.urls import reverse
from dashboard.decorators import organization_required
from .models import FAQ
from . import sync


def _snippet(text, term, size=120):
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    idx = clean.lower().find(term.lower())
    if idx == -1:
        return clean[:size] + ('...' if len(clean) > size else '')
    start = max(0, idx - 40)
    end = min(len(clean), idx + len(term) + 80)
    prefix = '...' if start > 0 else ''
    suffix = '...' if end < len(clean) else ''
    return prefix + clean[start:end] + suffix


@login_required
@organization_required
def listar_faq(request):
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'title')
    return render(request, 'faq/listar.html', {'faqs': faqs})


@login_required
@organization_required
def buscar_faq_ajax(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    faqs = FAQ.objects.filter(is_active=True).filter(
        Q(title__icontains=q) |
        Q(keywords__icontains=q) |
        Q(symptom__icontains=q) |
        Q(problem__icontains=q) |
        Q(content__icontains=q)
    ).annotate(
        relevance=Case(
            When(title__icontains=q, then=Value(0)),
            When(keywords__icontains=q, then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by('relevance')[:10]

    results = []
    for faq in faqs:
        if q.lower() in faq.title.lower():
            match_field = 'Título'
            snippet = faq.title
        elif q.lower() in (faq.keywords or '').lower():
            match_field = 'Palavras-chave'
            snippet = _snippet(faq.keywords, q)
        elif q.lower() in (faq.symptom or '').lower():
            match_field = 'Sintoma'
            snippet = _snippet(faq.symptom, q)
        elif q.lower() in (faq.problem or '').lower():
            match_field = 'Problema'
            snippet = _snippet(faq.problem, q)
        else:
            match_field = 'Solução'
            snippet = _snippet(faq.content, q)

        results.append({
            'title': faq.title,
            'category': faq.category,
            'match_field': match_field,
            'snippet': snippet,
            'url': reverse('detalhe_faq', args=[faq.znuny_id]),
        })

    return JsonResponse({'results': results})


@login_required
@organization_required
def detalhe_faq(request, znuny_id):
    faq = get_object_or_404(FAQ, znuny_id=znuny_id, is_active=True)
    return render(request, 'faq/detalhe.html', {'faq': faq})


@login_required
@organization_required
def sincronizar_faq(request):
    if request.method != 'POST':
        return redirect('listar_faq')

    try:
        criados, atualizados = sync.sincronizar()
        messages.success(request, f'Sincronização concluída: {criados} nova(s), {atualizados} atualizada(s).')
    except Exception as e:
        messages.error(request, f'Erro na sincronização: {str(e)}')

    return redirect('listar_faq')