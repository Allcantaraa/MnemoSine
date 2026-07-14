import json
import os
from django.conf import settings
from .models import CodeEntry, Category


SYSTEM_PROMPT = """Você é o assistente do FlowPanel — uma biblioteca de painéis Grafana. \
Você tem duas funções: (1) responder perguntas sobre os painéis existentes e (2) criar novos painéis. \
Use sempre as ferramentas disponíveis. Responda em português, de forma concisa.

━━━ COMO RESPONDER PERGUNTAS ━━━
- "Temos algum gauge?" → use search_panels ou list_panels e responda com o que encontrou
- "Quais painéis existem?" → use list_panels
- "Quais categorias temos?" → use list_categories
- Se não encontrar nada, diga claramente e ofereça criar
- Ao listar painéis, mostre: nome, tipo e categoria

━━━ COMO CRIAR PAINÉIS ━━━
- Só chame create_panel quando o usuário pedir explicitamente para criar
- Se o nome já existir (search_panels retornar resultado), avise antes de criar
- Sempre confirme com nome e tipo após criar

━━━ TIPOS E SCHEMAS ━━━

### html_graphics
{
  "html": "<div>...</div><script>(function(){ /* lógica/animação aqui */ })();</script>",
  "css": "body{display:flex;align-items:center;justify-content:center;height:100%;margin:0;}",
  "rootCss": "",
  "onRender": "/* APENAS para buscar data.series e atualizar o DOM */",
  "renderOnMount": true
}
REGRAS html_graphics:
- Lógica e animação SEMPRE no <script> embutido no HTML, nunca no onRender
- Layout SEMPRE em body{display:flex;...}
- renderOnMount: true OBRIGATÓRIO
- Para gauges: SVG com linearGradient + requestAnimationFrame count-up
- Valor demo fixo no script, ex: var VALUE = 75

EXEMPLO de gauge 270° (speedômetro SVG):
{
  "html": "<div class=\\"gw\\"><svg class=\\"gs\\" viewBox=\\"0 0 200 200\\"><defs><linearGradient id=\\"gg\\" x1=\\"0%\\" y1=\\"0%\\" x2=\\"100%\\" y2=\\"0%\\"><stop offset=\\"0%\\" stop-color=\\"#51cf66\\"/><stop offset=\\"100%\\" stop-color=\\"#ff6b6b\\"/></linearGradient></defs><circle class=\\"gb\\" cx=\\"100\\" cy=\\"100\\" r=\\"75\\"/><circle class=\\"gf\\" cx=\\"100\\" cy=\\"100\\" r=\\"75\\"/><text class=\\"gv\\" id=\\"gVal\\" x=\\"100\\" y=\\"98\\" text-anchor=\\"middle\\">0</text><text class=\\"gu\\" x=\\"100\\" y=\\"118\\" text-anchor=\\"middle\\">%</text></svg></div><script>(function(){var V=75,MAX=100,C=471.24,ARC=353.43;var f=document.querySelector('.gf'),v=document.getElementById('gVal');if(!f||!v)return;var cur=0,step=V/40;function tick(){cur=Math.min(cur+step,V);f.style.strokeDasharray=(cur/MAX*ARC)+' '+C;v.textContent=Math.round(cur);if(cur<V)requestAnimationFrame(tick);}setTimeout(function(){requestAnimationFrame(tick);},150);})();</script>",
  "css": "body{display:flex;align-items:center;justify-content:center;height:100%;margin:0;font-family:-apple-system,sans-serif}.gw{width:200px}.gs{width:100%;overflow:visible}.gb{fill:none;stroke:#252d3a;stroke-width:14;stroke-linecap:round;stroke-dasharray:353.43 471.24;transform:rotate(135deg);transform-origin:100px 100px}.gf{fill:none;stroke:url(#gg);stroke-width:14;stroke-linecap:round;stroke-dasharray:0 471.24;transform:rotate(135deg);transform-origin:100px 100px}.gv{font-size:2.5rem;font-weight:700;fill:#51cf66}.gu{font-size:.95rem;fill:#6b7280}",
  "rootCss": "",
  "onRender": "var f=data.series[0]?.fields[1];var raw=f?.values?.get(f.values.length-1)??75;var V=Math.round(raw),MAX=100,C=471.24,ARC=353.43;var el=document.querySelector('.gf'),v=document.getElementById('gVal');if(el&&v){el.style.strokeDasharray=(Math.min(V,MAX)/MAX*ARC)+' '+C;v.textContent=V;}",
  "renderOnMount": true
}

### html_text
{"html": "<div>...</div>"}

### business_text
{"content": "Markdown/HTML", "afterContentReady": "", "beforeContentReady": "", "defaultContent": ""}

### business_charts
{"code": "// JavaScript ECharts/Chart.js"}

### dashboard_json, canvas, sql, javascript, css, svg
Objeto com o conteúdo livre no formato correspondente.

━━━ FLUXO ━━━
1. Se precisar de categoria, chame list_categories primeiro
2. Gere o conteúdo completo e funcional
3. Chame create_panel para salvar
4. Confirme com nome e tipo do painel criado
"""


def execute_tool(tool_name, tool_input, organization, user):
    if tool_name == 'list_categories':
        cats = list(
            CodeEntry.objects.filter(organization=organization)
            .values_list('category', flat=True)
            .distinct()
            .order_by('category')
        )
        return {'categories': [c for c in cats if c]}

    if tool_name == 'list_panels':
        category = tool_input.get('category', '')
        type_ = tool_input.get('type', '')
        qs = CodeEntry.objects.filter(organization=organization)
        if category:
            qs = qs.filter(category__iexact=category)
        if type_:
            qs = qs.filter(type=type_)
        results = list(qs.values('name', 'type', 'category', 'description', 'slug').order_by('name')[:20])
        return {'total': qs.count(), 'results': results}

    if tool_name == 'search_panels':
        query = tool_input.get('query', '')
        results = list(
            CodeEntry.objects.filter(organization=organization, name__icontains=query)
            .values('name', 'type', 'category', 'description', 'slug')[:8]
        )
        return {'count': len(results), 'results': results}

    if tool_name == 'create_panel':
        name = (tool_input.get('name') or '').strip()
        type_ = tool_input.get('type', '')
        content = tool_input.get('content', {})
        category = tool_input.get('category') or ''
        description = tool_input.get('description') or ''
        version = tool_input.get('version') or '1.0.0'

        if not name or not type_ or not content:
            return {'success': False, 'error': 'name, type e content são obrigatórios'}

        valid_types = [t[0] for t in CodeEntry.Type.choices]
        if type_ not in valid_types:
            return {'success': False, 'error': f"Tipo '{type_}' inválido. Use: {valid_types}"}

        if CodeEntry.objects.filter(organization=organization, name__iexact=name).exists():
            return {'success': False, 'error': f"Já existe um painel com o nome '{name}'"}

        code = CodeEntry.objects.create(
            organization=organization,
            name=name,
            type=type_,
            content=content,
            category=category,
            description=description,
            version=version,
            status=CodeEntry.Status.DRAFT,
            created_by=user,
        )
        return {'success': True, 'name': code.name, 'slug': code.slug, 'type': code.type}

    return {'error': f"Tool '{tool_name}' desconhecida"}


def run_agent(prompt, organization, user):
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return 'Pacote google-genai não instalado. Execute: pip install google-genai'

    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return 'GEMINI_API_KEY não configurada.'

    client = genai.Client(api_key=api_key)

    S = types.Schema
    tool = types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name='list_categories',
            description='Lista todas as categorias existentes na organização',
            parameters=S(type='OBJECT', properties={})
        ),
        types.FunctionDeclaration(
            name='list_panels',
            description='Lista painéis da biblioteca, com filtro opcional por categoria ou tipo',
            parameters=S(
                type='OBJECT',
                properties={
                    'category': S(type='STRING', description='Filtrar por categoria (opcional)'),
                    'type':     S(type='STRING', description='Filtrar por tipo (opcional)'),
                },
            )
        ),
        types.FunctionDeclaration(
            name='search_panels',
            description='Busca painéis pelo nome (busca parcial)',
            parameters=S(
                type='OBJECT',
                properties={'query': S(type='STRING', description='Termo de busca')},
                required=['query'],
            )
        ),
        types.FunctionDeclaration(
            name='create_panel',
            description='Cria e salva um novo painel no FlowPanel',
            parameters=S(
                type='OBJECT',
                properties={
                    'name':        S(type='STRING'),
                    'type':        S(type='STRING',
                                    description='html_graphics | html_text | business_text | '
                                                'business_charts | canvas | dashboard_json | '
                                                'sql | javascript | css | svg'),
                    'content':     S(type='OBJECT', description='Conteúdo JSON do painel'),
                    'category':    S(type='STRING'),
                    'description': S(type='STRING'),
                    'version':     S(type='STRING'),
                },
                required=['name', 'type', 'content'],
            )
        ),
    ])

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[tool],
    )

    contents = [types.Content(role='user', parts=[types.Part(text=prompt)])]

    for _ in range(10):
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=contents,
            config=config,
        )

        fn_calls = [
            part.function_call
            for part in response.candidates[0].content.parts
            if part.function_call
        ]

        if not fn_calls:
            try:
                return response.text
            except Exception:
                return 'Resposta inválida do modelo.'

        contents.append(response.candidates[0].content)

        fn_parts = []
        for fc in fn_calls:
            result = execute_tool(fc.name, dict(fc.args), organization, user)
            fn_parts.append(types.Part(
                function_response=types.FunctionResponse(
                    name=fc.name,
                    response={'result': json.dumps(result, ensure_ascii=False)},
                )
            ))
        contents.append(types.Content(role='user', parts=fn_parts))

    return 'O agente atingiu o limite de iterações.'
