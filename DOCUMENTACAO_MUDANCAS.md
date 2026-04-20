# Documentação de Mudanças Críticas - MnemoSine

## 1. Novo Modelo de Controle de Acesso
O sistema de níveis de acesso foi simplificado de três níveis para um modelo binário:
- **Administrador**: Possui permissão total sobre a organização, incluindo gerenciamento de membros, adição/edição de conteúdo e exclusão direta.
- **Membro**: Pode visualizar, adicionar e editar clientes, categorias e dashboards, mas **não possui permissão para excluir itens diretamente**.

## 2. Restrição de Organizações
O sistema agora opera sob um modelo fixo de organizações:
- Apenas as organizações **"Principal"** e **"Modelos"** são permitidas.
- A criação de novas organizações e a exclusão das existentes foi **bloqueada permanentemente** para todos os usuários através de validações no modelo.
- O sistema de convites por código foi removido, assim como as telas de criação e entrada em organizações.

## 3. Sistema de Solicitação de Exclusão
Para garantir a integridade dos dados, usuários com o nível de "Membro" não podem mais excluir itens. Em vez disso:
- Ao tentar excluir um Cliente, Categoria ou Dashboard, o Membro deve fornecer uma justificativa.
- Uma **Solicitação de Exclusão** é criada e enviada para revisão.
- Administradores visualizam essas solicitações na nova tela de **Notificações**.

## 4. Tela de Notificações (Administradores)
Uma nova interface foi desenvolvida para que administradores gerenciem o fluxo de exclusão:
- **Listagem de Pendências**: Exibe todas as solicitações que aguardam revisão.
- **Aprovação/Rejeição**: O administrador pode aprovar (o que executa a exclusão definitiva) ou rejeitar a solicitação, com a opção de adicionar notas de revisão.
- **Histórico**: Listagem das últimas 20 ações realizadas para auditoria.

## 5. Mudanças Técnicas
- **Modelos**: Adição do modelo `DeletionRequest` e atualização de `Organization` e `OrganizationMember`.
- **Decorators**: Atualização de `organization_admin_required` e `organization_member_or_admin_required` para refletir os novos roles.
- **Frontend**:
    - Sidebar atualizada com link para Notificações.
    - Modais de exclusão atualizados para suportar o fluxo de solicitação com campo de justificativa.
    - Remoção de templates obsoletos de gerenciamento de organização.
- **Segurança**: Bloqueio de endpoints legados de criação/convite de organizações.
- **Testes**: Implementação de testes unitários em `dashboard/tests_permissions.py` cobrindo o novo modelo de permissões e restrições.
