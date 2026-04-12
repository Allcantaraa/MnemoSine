from django.shortcuts import render, redirect
from usuario.forms import Login_Form, CadastroForm
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from usuario.models import Perfil
from .forms import RegisterUpdateForm

def login(request) :
    form = Login_Form(request)

    if request.method == 'POST' :
        form = Login_Form(request, data=request.POST)

        if form.is_valid() :
            usuario = form.get_user()
            auth.login(request, usuario)
            messages.success(request, 'Login realizado com sucesso')
            return redirect('index')
        messages.error(request, 'Login inválido')

    return render(request, 'login.html', {'form': form})

def logout(request) :
    auth.logout(request)
    return redirect('login')

def cadastro(request) :
    form = CadastroForm()

    if request.method == 'POST' :
        form = CadastroForm(request.POST)

        if form.is_valid() :
            user = form.save()
            profile_image = form.cleaned_data.get('profile_image')
            Perfil.objects.update_or_create(
                user=user,
                defaults={'profile_image': profile_image}
            )
            messages.success(request, 'Usuário criado com sucesso')
            return redirect('login')

    return render(request, 'cadastro.html', {'form': form})

@login_required()
def perfil(request):
    # Importar aqui para evitar import circular
    from dashboard.models import OrganizationMember

    # Pegar organizações do usuário
    org_memberships = OrganizationMember.objects.filter(user=request.user).select_related('organization')

    if request.method == 'POST':
        # Atualizar perfil do usuário
        form = RegisterUpdateForm(data=request.POST, files=request.FILES, instance=request.user)

        if form.is_valid():
            user = form.save()
            profile_image = form.cleaned_data.get('profile_image')
            if profile_image:
                Perfil.objects.update_or_create(
                    user=user,
                    defaults={'profile_image': profile_image}
                )

            # Atualizar organização ativa se selecionada
            org_id = request.POST.get('active_organization')
            if org_id:
                # Verificar se o usuário é membro desta organização
                if org_memberships.filter(organization_id=org_id).exists():
                    request.session['active_org_id'] = int(org_id)

            messages.success(request, 'Dados de usuário atualizados com sucesso')
            return redirect('perfil')

        messages.error(request, 'Erro ao atualizar o perfil. Verifique os campos abaixo.')
    else:
        form = RegisterUpdateForm(instance=request.user)

    # Pegar organização ativa da sessão
    active_org_id = request.session.get('active_org_id')

    return render(request, 'perfil.html', {
        'form': form,
        'org_memberships': org_memberships,
        'active_org_id': active_org_id
    })
