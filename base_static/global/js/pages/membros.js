function copyInviteCode() {
        const codeElement = document.getElementById('inviteCode');
        if (!codeElement) return;
        navigator.clipboard.writeText(codeElement.textContent.trim());
    }

    function openCreateUserModal() {
        const modal = document.getElementById('createUserModal');
        if (!modal) return;
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
    }

    function closeCreateUserModal() {
        const modal = document.getElementById('createUserModal');
        if (!modal) return;
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    }

    function openSimpleModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
    }

    function closeSimpleModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    }

    function openRemoveMemberModal(actionUrl, memberName) {
        const modal = document.getElementById('removeMemberModal');
        const form = document.getElementById('removeMemberForm');
        const name = document.getElementById('removeMemberName');
        if (!modal || !form || !name) return;
        form.action = actionUrl;
        name.textContent = memberName;
        openSimpleModal('removeMemberModal');
    }

    document.getElementById('createUserModal')?.addEventListener('click', function (event) {
        if (event.target.id === 'createUserModal') {
            closeCreateUserModal();
        }
    });

    ['generateCodeModal', 'leaveOrgModal', 'deleteOrgModal', 'removeMemberModal'].forEach(function (id) {
        document.getElementById(id)?.addEventListener('click', function (event) {
            if (event.target.id === id) {
                closeSimpleModal(id);
            }
        });
    });