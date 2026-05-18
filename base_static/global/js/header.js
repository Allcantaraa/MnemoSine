function toggleOrgDropdown(event) {
        event.stopPropagation();

        const header = event.currentTarget;
        const orgSelector = header.closest('.org-selector-item');
        if (!orgSelector) {
            console.warn('org-selector-item não encontrado');
            return;
        }

        const dropdown = orgSelector.querySelector('.org-dropdown');

        if (!dropdown) {
            console.warn('org-dropdown não encontrado');
            return;
        }

        document.querySelectorAll('.org-dropdown.active').forEach(d => {
            if (d !== dropdown) {
                d.classList.remove('active');
                d.closest('.org-selector-item')?.querySelector('.org-selector-header')?.classList.remove('active');
            }
        });

        dropdown.classList.toggle('active');
        header.classList.toggle('active');
    }

    document.addEventListener('click', function(event) {
        const orgSelector = event.target.closest('.org-selector-item');
        if (!orgSelector) {
            document.querySelectorAll('.org-dropdown.active').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
            document.querySelectorAll('.org-selector-header.active').forEach(header => {
                header.classList.remove('active');
            });
        }
    });

    (function () {
        const key = 'mnemosine-theme';
        const toggleBtn = document.getElementById('globalThemeToggle');
        const toggleLabel = document.getElementById('globalThemeToggleLabel');
        const toggleIcon = toggleBtn?.querySelector('i');

        function syncToggleLabel() {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            if (toggleLabel) {
                toggleLabel.textContent = isDark ? 'Light mode' : 'Dark mode';
            }
            if (toggleIcon) {
                toggleIcon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
            }
        }

        toggleBtn?.addEventListener('click', function () {
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem(key, next);
            syncToggleLabel();
        });

        syncToggleLabel();
    })();