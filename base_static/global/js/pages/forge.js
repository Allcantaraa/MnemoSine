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

// ── Content Editor ───────────────────────────────────────────────────────────
(function () {
    var typeSelect    = document.getElementById('codeTypeSelect');
    var contentEditor = document.getElementById('contentEditor');
    var fieldGroup    = document.getElementById('contentFieldGroup');
    if (!typeSelect || !contentEditor || !fieldGroup) return;

    var BLOCK_MAP = {
        html_graphics:   'block-html-graphics',
        html_text:       'block-html-text',
        business_text:   'block-business-text',
        business_charts: 'block-business-charts',
        canvas:          'block-json',
        dashboard_json:  'block-json',
        sql:             'block-json',
        javascript:      'block-json',
        css:             'block-json',
        svg:             'block-json',
    };

    var JSON_PLACEHOLDERS = {
        canvas:         '{"panels": [...]}',
        dashboard_json: '{ ...cole o JSON completo do dashboard Grafana... }',
        sql:            'SELECT ...\nFROM ...',
        javascript:     '// JavaScript code',
        css:            '.classe { color: white; }',
        svg:            '<svg xmlns="http://www.w3.org/2000/svg">...</svg>',
    };

    // Toggle Campos/JSON panels within a specific block
    function activateBlockMode(block, mode) {
        if (!block) return;
        block.querySelectorAll('.forge-mode-tab').forEach(function (tab) {
            tab.classList.toggle('active', tab.getAttribute('data-mode') === mode);
        });
        var fieldsPanel = block.querySelector('.forge-block-fields');
        var jsonPanel   = block.querySelector('.forge-block-json');
        if (fieldsPanel) fieldsPanel.style.display = mode === 'fields' ? 'block' : 'none';
        if (jsonPanel)   jsonPanel.style.display   = mode === 'json'   ? 'block' : 'none';
    }

    function getBlockMode(block) {
        if (!block) return 'fields';
        var active = block.querySelector('.forge-mode-tab.active');
        return active ? active.getAttribute('data-mode') : 'fields';
    }

    window.forgeContentEditor = {
        switchBlock: function (typeVal) {
            document.querySelectorAll('.forge-content-block').forEach(function (b) {
                b.style.display = 'none';
            });
            var blockId = BLOCK_MAP[typeVal];
            if (!blockId) { fieldGroup.style.display = 'none'; return; }

            fieldGroup.style.display = 'block';
            var block = document.getElementById(blockId);
            if (block) block.style.display = 'block';

            if (blockId === 'block-json') {
                var ph = JSON_PLACEHOLDERS[typeVal];
                var jsonEditor = document.getElementById('jsonEditor');
                if (jsonEditor && ph && !jsonEditor.value.trim()) {
                    jsonEditor.placeholder = ph;
                }
            }
        },

        assemble: function (typeVal) {
            var blockId = BLOCK_MAP[typeVal];
            if (!blockId) return null;

            // Plain JSON-only block (canvas, dashboard_json, sql, etc.)
            if (blockId === 'block-json') {
                var raw = (document.getElementById('jsonEditor') || {}).value;
                if (!raw || !raw.trim()) return null;
                try { return JSON.parse(raw.trim()); } catch (e) { return '__invalid__'; }
            }

            var block = document.getElementById(blockId);
            var mode  = getBlockMode(block);

            // JSON mode: parse the block's raw JSON textarea
            if (mode === 'json') {
                var ta = block && block.querySelector('.forge-block-json textarea');
                var raw = ta ? ta.value.trim() : '';
                if (!raw) return null;
                try { return JSON.parse(raw); } catch (e) { return '__invalid__'; }
            }

            // Fields mode: assemble from structured inputs
            if (typeVal === 'html_text') {
                return { html: document.getElementById('htHtml').value };
            }
            if (typeVal === 'business_charts') {
                return { code: document.getElementById('bcCode').value };
            }
            if (typeVal === 'business_text') {
                return {
                    content:            document.getElementById('btContent').value,
                    afterContentReady:  document.getElementById('btAfter').value,
                    beforeContentReady: document.getElementById('btBefore').value,
                    defaultContent:     document.getElementById('btDefault').value,
                };
            }
            if (typeVal === 'html_graphics') {
                return {
                    html:     document.getElementById('hgHtml').value,
                    css:      document.getElementById('hgCss').value,
                    rootCss:  document.getElementById('hgRootCss').value,
                    onRender: document.getElementById('hgOnRender').value,
                    onInit:   document.getElementById('hgOnInit').value,
                };
            }
            return null;
        },

        populate: function (typeVal, contentObj) {
            if (!contentObj) return;
            this.switchBlock(typeVal);

            var blockId = BLOCK_MAP[typeVal];
            var block   = blockId ? document.getElementById(blockId) : null;

            if (blockId === 'block-json') {
                var el = document.getElementById('jsonEditor');
                if (el) el.value = JSON.stringify(contentObj, null, 2);
                return;
            }

            var putJson = function () {
                var ta = block && block.querySelector('.forge-block-json textarea');
                if (ta) ta.value = JSON.stringify(contentObj, null, 2);
                activateBlockMode(block, 'json');
            };

            if (typeVal === 'html_text') {
                if (contentObj.html !== undefined) {
                    document.getElementById('htHtml').value = contentObj.html || '';
                    activateBlockMode(block, 'fields');
                } else { putJson(); }
                return;
            }
            if (typeVal === 'business_charts') {
                if (contentObj.code !== undefined) {
                    document.getElementById('bcCode').value = contentObj.code || '';
                    activateBlockMode(block, 'fields');
                } else { putJson(); }
                return;
            }
            if (typeVal === 'business_text') {
                if (contentObj.content !== undefined || contentObj.afterContentReady !== undefined) {
                    var set = function (id, key) {
                        var el = document.getElementById(id);
                        if (el) el.value = contentObj[key] || '';
                    };
                    set('btContent', 'content');
                    set('btAfter',   'afterContentReady');
                    set('btBefore',  'beforeContentReady');
                    set('btDefault', 'defaultContent');
                    activateBlockMode(block, 'fields');
                } else { putJson(); }
                return;
            }
            if (typeVal === 'html_graphics') {
                var hasFields = contentObj.html !== undefined
                    || contentObj.css !== undefined
                    || contentObj.onRender !== undefined;
                if (hasFields) {
                    var set = function (id, key) {
                        var el = document.getElementById(id);
                        if (el) el.value = contentObj[key] || '';
                    };
                    set('hgHtml',     'html');
                    set('hgCss',      'css');
                    set('hgRootCss',  'rootCss');
                    set('hgOnRender', 'onRender');
                    set('hgOnInit',   'onInit');
                    activateBlockMode(block, 'fields');
                } else { putJson(); }
                return;
            }
        },
    };

    // Tab click — any block
    document.addEventListener('click', function (e) {
        var tab = e.target.closest('.forge-content-block .forge-mode-tab');
        if (!tab) return;
        var block = tab.closest('.forge-content-block');
        activateBlockMode(block, tab.getAttribute('data-mode'));
    });

    // Type select → show the right block
    typeSelect.addEventListener('change', function () {
        window.forgeContentEditor.switchBlock(this.value);
    });

    // Initialize on load
    window.forgeContentEditor.switchBlock(typeSelect.value);

    // Form submit — assemble into hidden field
    var form = contentEditor.closest('form');
    if (form) {
        form.addEventListener('submit', function (e) {
            var typeVal = typeSelect.value;
            var result  = window.forgeContentEditor.assemble(typeVal);
            if (result === '__invalid__') {
                e.preventDefault();
                alert('JSON inválido. Verifique o conteúdo digitado.');
                return;
            }
            if (result === null) {
                e.preventDefault();
                alert('Preencha o conteúdo antes de salvar.');
                return;
            }
            contentEditor.value = JSON.stringify(result);
        });
    }
})();
