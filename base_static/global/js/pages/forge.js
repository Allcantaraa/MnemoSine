(function () {
    // ── Search autocomplete ──────────────────────────────────────────
    var searchInput = document.getElementById('forgeSearchInput');
    var searchDropdown = document.getElementById('forgeSearchDropdown');
    var searchResults = document.getElementById('forgeSearchResults');
    var searchTimer;

    if (searchInput) {
        var searchUrl = searchInput.getAttribute('data-url');

        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimer);
            var q = this.value.trim();
            if (q.length < 2) {
                searchDropdown.classList.remove('open');
                return;
            }
            searchTimer = setTimeout(function () {
                fetch(searchUrl + '?q=' + encodeURIComponent(q))
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (!data.results.length) {
                            searchResults.innerHTML = '<div class="forge-search-empty">Nenhum resultado encontrado</div>';
                        } else {
                            searchResults.innerHTML = data.results.map(function (r) {
                                var meta = [r.type, r.category].filter(Boolean).join(' · ');
                                return '<a href="' + r.url + '" class="forge-search-result-item">'
                                    + '<div class="forge-search-result-initial">' + r.initial + '</div>'
                                    + '<div class="forge-search-result-info">'
                                    + '<span class="forge-search-result-name">' + r.name + '</span>'
                                    + (meta ? '<span class="forge-search-result-meta">' + meta + '</span>' : '')
                                    + '</div></a>';
                            }).join('');
                        }
                        searchDropdown.classList.add('open');
                    });
            }, 250);
        });

        document.addEventListener('click', function (e) {
            if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
                searchDropdown.classList.remove('open');
            }
        });

        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') searchDropdown.classList.remove('open');
        });
    }

    // ── Nova Categoria (modal) ───────────────────────────────────────
    var btnNovaCat  = document.getElementById('btnNovaCategoria');
    var modal       = document.getElementById('novaCatModal');
    var novaCatInput = document.getElementById('novaCatInput');
    var btnSalvar   = document.getElementById('btnSalvarCategoria');
    var btnCancelar = document.getElementById('btnCancelarCategoria');
    var btnFechar   = document.getElementById('btnFecharModal');

    function abrirModal() {
        if (!modal) return;
        modal.classList.add('open');
        novaCatInput.focus();
    }

    function fecharModal() {
        if (!modal) return;
        modal.classList.remove('open');
        novaCatInput.value = '';
    }

    if (btnNovaCat) {
        var createCatUrl = btnNovaCat.getAttribute('data-url');

        btnNovaCat.addEventListener('click', abrirModal);
        if (btnFechar)   btnFechar.addEventListener('click', fecharModal);
        if (btnCancelar) btnCancelar.addEventListener('click', fecharModal);

        modal.addEventListener('click', function (e) {
            if (e.target === modal) fecharModal();
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && modal.classList.contains('open')) fecharModal();
        });

        function salvarCategoria() {
            var name = novaCatInput.value.trim();
            if (!name) { novaCatInput.focus(); return; }
            var csrf = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
            fetch(createCatUrl, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'name=' + encodeURIComponent(name)
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) { alert(data.error || 'Erro'); return; }
                var select = document.getElementById('categorySelect');
                if (select) {
                    var exists = Array.from(select.options).some(function (o) { return o.value === data.name; });
                    if (!exists) {
                        var opt = document.createElement('option');
                        opt.value = data.name;
                        opt.textContent = data.name;
                        select.appendChild(opt);
                    }
                    select.value = data.name;
                }
                fecharModal();
            });
        }

        btnSalvar.addEventListener('click', salvarCategoria);
        novaCatInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') { e.preventDefault(); salvarCategoria(); }
        });
    }

    // ── Bulk selection ───────────────────────────────────────────────
    function getSelectedIds() {
        return Array.from(document.querySelectorAll('.client-select:checked'))
            .map(cb => cb.getAttribute('data-code-id'));
    }

    function updateBulkBar() {
        var ids = getSelectedIds();
        var bar = document.getElementById('forgeBulkBar');
        var count = document.getElementById('forgeSelectedCount');
        if (!bar || !count) return;

        if (ids.length > 0) {
            count.textContent = ids.length;
            bar.style.display = 'flex';
            requestAnimationFrame(function () { bar.classList.add('is-visible'); });
        } else {
            bar.classList.remove('is-visible');
            setTimeout(function () { bar.style.display = 'none'; }, 300);
        }
    }

    window.clearForgeSelection = function () {
        document.querySelectorAll('.client-select').forEach(function (cb) {
            cb.checked = false;
            var card = cb.closest('.forge-client-card, .client-card');
            if (card) card.classList.remove('selected');
        });
        updateBulkBar();
    };

    window.forgeBulkAction = function (action) {
        var ids = getSelectedIds();
        if (!ids.length) return;

        var csrf = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
        var body = new URLSearchParams({ action: action });
        ids.forEach(function (id) { body.append('ids[]', id); });

        fetch(window.FORGE_BULK_URL, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
            body: body.toString()
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success) { location.reload(); }
            else { alert(data.error || 'Erro ao executar ação'); }
        })
        .catch(function () { alert('Erro de conexão'); });
    };

    document.addEventListener('change', function (e) {
        if (e.target.classList.contains('client-select')) {
            var card = e.target.closest('.forge-client-card, .client-card');
            if (card) card.classList.toggle('selected', e.target.checked);
            updateBulkBar();
        }
    });

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.btn-client-favorite[data-toggle-url]');
        if (!btn) return;
        var csrf = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
        fetch(btn.getAttribute('data-toggle-url'), {
            method: 'POST',
            headers: { 'X-CSRFToken': csrf }
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) return;
            location.reload();
        });
    });
})();
