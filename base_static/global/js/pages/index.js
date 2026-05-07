// ==========================================
// 1. FUNÇÕES GLOBAIS
// ==========================================

function openDeleteClientModal(actionUrl, name) {
  const modal = document.getElementById("deleteClientModal");
  const nameSpan = document.getElementById("deleteClientName");
  const form = document.getElementById("deleteClientForm");
  if (!modal || !nameSpan || !form) return;

  nameSpan.innerText = name;
  form.action = actionUrl;
  modal.classList.add("active");
}

function closeDeleteClientModal() {
  document.getElementById("deleteClientModal")?.classList.remove("active");
}

function openImageModal(imageUrl, dashboardName) {
  const imageModal = document.getElementById("imageModal");
  const modalImage = document.getElementById("modalImage");
  const modalTitle = document.getElementById("modalTitle");

  modalImage.src = imageUrl;
  modalTitle.textContent = dashboardName;
  imageModal.classList.add("active");
}

function closeImageModal() {
  const imageModal = document.getElementById("imageModal");
  imageModal?.classList.remove("active");
}

function getSelectedClientIds() {
  const checkboxes = document.querySelectorAll('.client-select:checked');
  return Array.from(checkboxes).map(cb => cb.getAttribute('data-client-id'));
}

function updateClientBulkBar() {
  const ids = getSelectedClientIds();
  const bar = document.getElementById('clientBulkActionsBar');
  const countSpan = document.getElementById('selectedClientCount');
  
  if (!bar || !countSpan) return;

  if (ids.length > 0) {
      countSpan.textContent = ids.length;
      bar.style.display = 'flex';
      bar.classList.add('is-visible');
  } else {
      bar.style.display = 'none';
      bar.classList.remove('is-visible');
  }
}

window.clearClientSelection = function() {
  document.querySelectorAll('.client-select').forEach(cb => {
      cb.checked = false;
      cb.closest('.client-card')?.classList.remove('selected');
  });
  updateClientBulkBar();
};

window.confirmClientBulk = function(actionType) {
  const ids = getSelectedClientIds();
  if (ids.length === 0) return;

  const config = document.getElementById('index-bulk-config');
  let url = '';
  
  if (actionType === 'duplicate') url = config.dataset.bulkDuplicateUrl;
  if (actionType === 'favorite') url = config.dataset.bulkFavoriteUrl;

  const form = document.createElement('form');
  form.method = 'POST';
  form.action = url;
  
  const csrf = document.createElement('input');
  csrf.type = 'hidden';
  csrf.name = 'csrfmiddlewaretoken';
  csrf.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  const idsInput = document.createElement('input');
  idsInput.type = 'hidden';
  idsInput.name = 'client_ids';
  idsInput.value = ids.join(',');
  
  form.appendChild(csrf);
  form.appendChild(idsInput);
  document.body.appendChild(form);
  form.submit();
};

window.openClientMoveModal = function() {
  const ids = getSelectedClientIds();
  if (ids.length === 0) return;
  document.getElementById('moveClientIdsInput').value = ids.join(',');
  document.getElementById('moveClientBulkModal').classList.add('active');
};

window.closeClientMoveModal = function() {
  document.getElementById('moveClientBulkModal').classList.remove('active');
};

window.openClientBulkDeleteModal = function() {
  const ids = getSelectedClientIds();
  if (ids.length === 0) return;
  document.getElementById('deleteClientIdsInput').value = ids.join(',');
  document.getElementById('bulkClientDeleteCount').textContent = ids.length;
  document.getElementById('deleteClientBulkModal').classList.add('active');
};

window.closeClientBulkDeleteModal = function() {
  document.getElementById('deleteClientBulkModal').classList.remove('active');
};

// Deixando globalmente disponível para chamadas antigas se existirem
window.openDeleteClientModal = openDeleteClientModal;
window.closeDeleteClientModal = closeDeleteClientModal;


// ==========================================
// 2. LISTENERS E EVENTOS TELA
// ==========================================
document.addEventListener("DOMContentLoaded", function () {

  // --- OUVINTE DOS CHECKBOXES DE CLIENTES ---
  document.body.addEventListener('change', function(e) {
      if (e.target.classList.contains('client-select')) {
          const card = e.target.closest('.client-card');
          if (e.target.checked) {
              card.classList.add('selected');
          } else {
              card.classList.remove('selected');
          }
          updateClientBulkBar();
      }
  });

  // --- FECHAMENTO DE MODAIS ---
  document.getElementById("deleteClientClose")?.addEventListener("click", closeDeleteClientModal);
  document.getElementById("deleteClientCancel")?.addEventListener("click", closeDeleteClientModal);

  document.getElementById("indexImageModalClose")?.addEventListener("click", closeImageModal);

  const imageModal = document.getElementById("imageModal");
  if (imageModal) {
    imageModal.addEventListener("click", function (e) {
      if (e.target === this) closeImageModal();
    });
  }

  // Fechar modais genéricos ao clicar no fundo escuro
  const modals = document.querySelectorAll('.image-modal');
  modals.forEach(modal => {
      modal.addEventListener('click', function(e) {
          if (e.target === this) {
              this.classList.remove('active');
          }
      });
  });

  // Close modal on Escape key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeImageModal();
      document.querySelectorAll('.image-modal.active').forEach(m => {
          m.classList.remove('active');
      });
    }
  });

  // --- FUNCIONALIDADE DE BUSCA E FILTROS ---
  const searchInput = document.getElementById("searchInput");
  const categoryChips = document.querySelectorAll(".category-chips .chip");
  const clientCards = document.querySelectorAll(".client-card");
  const dashboardCards = document.querySelectorAll(".dashboards-section .dashboard-card");
  const emptyState = document.querySelector(".empty-state");

  let selectedCategory = "";

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      filterContent();
    });
  }

  document.querySelector(".dashboards-section")?.addEventListener("click", function (e) {
    const t = e.target.closest(".js-open-dash-preview");
    if (!t) return;
    e.preventDefault();
    openImageModal(t.dataset.previewSrc, t.dataset.previewTitle);
  });

  categoryChips.forEach((chip) => {
    chip.addEventListener("click", function (e) {
      e.preventDefault();
      categoryChips.forEach((c) => c.classList.remove("active"));
      this.classList.add("active");
      selectedCategory = this.getAttribute("data-category");
      filterContent();
    });
  });

  function filterContent() {
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : "";
    let visibleClientsCount = 0;
    let visibleDashboardsCount = 0;

    clientCards.forEach((card) => {
      const clientName = card.querySelector(".client-name").textContent.toLowerCase();
      const clientDescription = card.querySelector(".client-description")?.textContent.toLowerCase() || "";
      const matchesSearch = clientName.includes(searchTerm) || clientDescription.includes(searchTerm);

      if (matchesSearch) {
        card.style.display = "";
        visibleClientsCount++;
      } else {
        card.style.display = "none";
      }
    });

    dashboardCards.forEach((card) => {
      const dashboardTitle = card.querySelector("h4").textContent.toLowerCase();
      const dashboardClient = card.querySelector(".dashboard-client").textContent.toLowerCase();
      const dashboardCategories = card.getAttribute("data-categories") || "";

      const matchesSearch = dashboardTitle.includes(searchTerm) || dashboardClient.includes(searchTerm) || dashboardCategories.includes(searchTerm);
      const matchesCategory = !selectedCategory || dashboardCategories.split(",").includes(selectedCategory.toLowerCase());

      if (matchesSearch && matchesCategory) {
        card.style.display = "";
        visibleDashboardsCount++;
      } else {
        card.style.display = "none";
      }
    });

    if (emptyState && visibleClientsCount === 0 && visibleDashboardsCount === 0) {
      emptyState.style.display = "block";
    } else if (emptyState && visibleClientsCount === 0 && clientCards.length > 0) {
      const dashboardsSection = document.querySelector(".dashboards-section");
      if (dashboardsSection) {
        dashboardsSection.style.display = visibleDashboardsCount > 0 ? "block" : "none";
      }
    }

    const clientCount = document.querySelector(".client-count");
    if (clientCount) {
      clientCount.textContent = visibleClientsCount + " cliente" + (visibleClientsCount !== 1 ? "s" : "");
    }
  }

  // --- FUNCIONALIDADE DE FAVORITAR INDIVIDUALMENTE ---
  const favoriteClientBtns = document.querySelectorAll(".btn-client-favorite");

  favoriteClientBtns.forEach((btn) => {
    btn.addEventListener("click", async function (e) {
      e.preventDefault();

      const url = this.getAttribute("data-url");
      const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
          },
        });

        const data = await response.json();

        if (data.success) {
          window.location.reload();
        } else {
          console.error("Erro ao favoritar:", data.error);
        }
      } catch (error) {
        console.error("Erro na requisição:", error);
      }
    });
  });

});

// ==========================================
// BUSCA INTELIGENTE DE FAQS (DROPDOWN)
// ==========================================
function setupFaqLiveSearch(inputId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById('faqDropdown');
    const list = document.getElementById('faqDropdownList');
    
    // Se os elementos não existirem na tela, não faz nada
    if (!input || !dropdown || !list) return;

    const url = input.dataset.url;
    let timer = null;
    let activeIndex = -1;

    function highlight(text, term) {
        if (!term) return text;
        const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp(`(${escaped})`, 'gi'), '<mark>$1</mark>');
    }

    function renderResults(results, term) {
        list.innerHTML = '';
        activeIndex = -1;

        if (!results.length) {
            // Se quiser, pode comentar essa linha para não mostrar "Nenhum resultado" 
            // e focar apenas nos resultados locais da tela.
            list.innerHTML = '<div class="faq-dropdown-empty" style="padding: 1rem; color: var(--app-muted); font-size: 0.9rem;">Nenhuma FAQ encontrada.</div>';
            dropdown.classList.add('open');
            return;
        }

        results.forEach((r, i) => {
            const item = document.createElement('a');
            item.href = r.url;
            item.className = 'faq-dropdown-item';
            item.dataset.index = i;
            
            // Layout dos itens do seu amigo
            item.innerHTML = `
                <div class="fqi-main" style="margin-bottom: 0.2rem;">
                    <i class="fa-solid fa-book-open" style="color: #3b82f6; margin-right: 0.5rem; font-size: 0.85rem;"></i>
                    <span class="fqi-title" style="font-weight: 600; color: var(--app-text);">${highlight(r.title, term)}</span>
                </div>
                ${r.match_field !== 'Título' ? `
                <div class="fqi-snippet" style="font-size: 0.8rem; color: var(--app-muted);">
                    <span class="fqi-field" style="background: var(--app-border); padding: 0.1rem 0.4rem; border-radius: 4px; margin-right: 0.4rem;">${r.match_field}</span>
                    <span class="fqi-text">${highlight(r.snippet, term)}</span>
                </div>` : ''}
            `;
            list.appendChild(item);
        });

        dropdown.classList.add('open');
    }

    function closeDropdown() {
        dropdown.classList.remove('open');
        activeIndex = -1;
    }

    function navigateItems(dir) {
        const items = list.querySelectorAll('.faq-dropdown-item');
        if (!items.length) return;
        items[activeIndex]?.classList.remove('active');
        activeIndex = (activeIndex + dir + items.length) % items.length;
        items[activeIndex].classList.add('active');
        items[activeIndex].scrollIntoView({ block: 'nearest' });
    }

    // Ouve a digitação
    input.addEventListener('input', () => {
        clearTimeout(timer);
        const q = input.value.trim();
        if (q.length < 2) { closeDropdown(); return; }
        
        // Dispara a busca no servidor após 300ms que o usuário parar de digitar
        timer = setTimeout(() => {
            fetch(`${url}?q=${encodeURIComponent(q)}`)
                .then(r => r.json())
                .then(data => renderResults(data.results, q));
        }, 300);
    });

    // Navegação pelo teclado
    input.addEventListener('keydown', (e) => {
        if (!dropdown.classList.contains('open')) return;
        if (e.key === 'ArrowDown') { e.preventDefault(); navigateItems(1); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); navigateItems(-1); }
        else if (e.key === 'Enter') {
            const active = list.querySelector('.faq-dropdown-item.active');
            // Se tiver uma FAQ selecionada, navega para ela (não dá preventDefault no submit geral caso seja outra coisa)
            if (active) {
                e.preventDefault();
                window.location.href = active.href;
            }
        } else if (e.key === 'Escape') { 
            closeDropdown(); 
        }
    });

    // Fechar ao clicar fora
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.faq-search-wrapper')) closeDropdown();
    });

    // Reabrir ao focar se já tiver pesquisa
    input.addEventListener('focus', () => {
        if (input.value.trim().length >= 2 && list.children.length) {
            dropdown.classList.add('open');
        }
    });
}

// ==========================================
// BUSCA OMNISEARCH (CLIENTES, DASHS E FAQS)
// ==========================================
function setupOmniSearch(inputId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById('faqDropdown');
    const list = document.getElementById('faqDropdownList');
    
    if (!input || !dropdown || !list) return;

    const url = input.dataset.url; // Puxa a rota do data-url="{% url 'buscar_faq_ajax' %}"
    let timer = null;

    // Função de grifar a palavra pesquisada
    function highlight(text, term) {
        if (!term) return text;
        const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp(`(${escaped})`, 'gi'), '<mark style="background: rgba(250, 204, 21, 0.4); color: inherit;">$1</mark>');
    }

    // Renderiza tudo misturado
    function renderOmniResults(faqResults, term) {
        list.innerHTML = '';
        let hasResults = false;

        // ----------------------------------------------------
        // 1. EXTRAIR CLIENTES DA TELA (Até 4 para não lotar)
        // ----------------------------------------------------
        const clients = Array.from(document.querySelectorAll('.client-card'))
                             .filter(c => c.style.display !== 'none').slice(0, 4);
        
        clients.forEach(card => {
            hasResults = true;
            const name = card.querySelector('.client-name')?.textContent || 'Cliente';
            const link = card.querySelector('a[title="Ver dashboards"]')?.href || '#';

            const item = document.createElement('a');
            item.href = link;
            item.className = 'faq-dropdown-item';
            item.style.textDecoration = 'none';
            item.innerHTML = `
                <div class="fqi-main" style="display: flex; align-items: center; padding: 0.5rem;">
                    <i class="fa-solid fa-building" style="color: #8b5cf6; margin-right: 0.5rem; width: 16px; text-align: center;"></i>
                    <span style="font-size: 0.65rem; background: #ede9fe; color: #6d28d9; padding: 0.1rem 0.4rem; border-radius: 4px; margin-right: 0.5rem; font-weight: bold;">CLIENTE</span>
                    <span class="fqi-title" style="font-weight: 600; color: var(--app-text);">${highlight(name, term)}</span>
                </div>
            `;
            list.appendChild(item);
        });

        // ----------------------------------------------------
        // 2. EXTRAIR DASHBOARDS DA TELA (Até 4 para não lotar)
        // ----------------------------------------------------
        const dashboards = Array.from(document.querySelectorAll('.dashboard-card'))
                                .filter(c => c.style.display !== 'none').slice(0, 4);
        
        dashboards.forEach(card => {
            hasResults = true;
            const title = card.querySelector('h4, h3')?.textContent || 'Dashboard';
            const clientName = card.querySelector('.dashboard-client')?.textContent || '';
            
            // Pega os links dos botões originais do card
            const viewBtn = card.querySelector('.js-open-dash-preview');
            const src = viewBtn ? viewBtn.getAttribute('data-preview-src') : '';
            const pTitle = viewBtn ? viewBtn.getAttribute('data-preview-title') : title;
            
            const downloadBtn = card.querySelector('.btn-download-dash');
            const downloadUrl = downloadBtn && downloadBtn.tagName === 'A' ? downloadBtn.href : '#';

            const item = document.createElement('div');
            item.className = 'faq-dropdown-item';
            item.style.cursor = 'default'; // Não clicável no fundo, só nos botões
            item.style.padding = '0.5rem';
            item.innerHTML = `
                <div class="fqi-main" style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div style="display: flex; align-items: center; flex: 1; overflow: hidden; padding-right: 10px;">
                        <i class="fa-solid fa-chart-pie" style="color: #10b981; margin-right: 0.5rem; width: 16px; text-align: center;"></i>
                        <span style="font-size: 0.65rem; background: #d1fae5; color: #047857; padding: 0.1rem 0.4rem; border-radius: 4px; margin-right: 0.5rem; font-weight: bold;">DASH</span>
                        <span class="fqi-title" style="font-weight: 600; color: var(--app-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${highlight(title, term)} <small style="color: var(--app-muted); font-weight: normal; margin-left: 4px;">(${highlight(clientName, term)})</small></span>
                    </div>
                    <div style="display: flex; gap: 0.4rem;">
                        ${src ? `<button type="button" class="btn-primary js-drop-preview" data-src="${src}" data-title="${pTitle}" style="padding: 0.3rem 0.6rem; font-size: 0.75rem;"><i class="fa-solid fa-eye"></i> Ver</button>` : ''}
                        ${downloadUrl !== '#' ? `<a href="${downloadUrl}" class="btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.75rem; text-decoration: none;"><i class="fa-solid fa-download"></i> Baixar</a>` : ''}
                    </div>
                </div>
            `;
            list.appendChild(item);
        });

        // ----------------------------------------------------
        // 3. RENDERIZAR AS FAQS DO BACKEND
        // ----------------------------------------------------
        if (faqResults && faqResults.length > 0) {
            hasResults = true;
            faqResults.forEach(r => {
                const item = document.createElement('a');
                item.href = r.url;
                item.className = 'faq-dropdown-item';
                item.style.textDecoration = 'none';
                item.style.padding = '0.5rem';
                item.innerHTML = `
                    <div class="fqi-main" style="display: flex; align-items: center; margin-bottom: 0.2rem;">
                        <i class="fa-solid fa-book-open" style="color: #3b82f6; margin-right: 0.5rem; width: 16px; text-align: center;"></i>
                        <span style="font-size: 0.65rem; background: #dbeafe; color: #1d4ed8; padding: 0.1rem 0.4rem; border-radius: 4px; margin-right: 0.5rem; font-weight: bold;">FAQ</span>
                        <span class="fqi-title" style="font-weight: 600; color: var(--app-text);">${highlight(r.title, term)}</span>
                    </div>
                    ${r.match_field !== 'Título' ? `
                    <div class="fqi-snippet" style="font-size: 0.75rem; color: var(--app-muted); margin-left: 2.2rem; margin-top: 0.3rem;">
                        <span style="background: var(--app-border); padding: 0.1rem 0.3rem; border-radius: 4px; margin-right: 0.3rem;">${r.match_field}</span>
                        <span>${highlight(r.snippet, term)}</span>
                    </div>` : ''}
                `;
                list.appendChild(item);
            });
        }

        // Se não tiver nada na tela nem no banco:
        if (!hasResults) {
            list.innerHTML = '<div class="faq-dropdown-empty" style="padding: 1.5rem; color: var(--app-muted); font-size: 0.9rem; text-align: center;"><i class="fa-solid fa-ghost fa-2x" style="margin-bottom: 0.5rem; opacity: 0.5;"></i><br>Nenhum resultado encontrado.</div>';
        }

        dropdown.classList.add('open');

        // Adiciona o evento de clique para o botão "Ver" dos Dashboards funcionarem
        list.querySelectorAll('.js-drop-preview').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                closeDropdown();
                if(typeof openImageModal === 'function') {
                    openImageModal(btn.getAttribute('data-src'), btn.getAttribute('data-title'));
                }
            });
        });
    }

    function closeDropdown() {
        dropdown.classList.remove('open');
    }

    // Quando o usuário digita
    input.addEventListener('input', () => {
        clearTimeout(timer);
        const q = input.value.trim();
        if (q.length < 2) { closeDropdown(); return; }
        
        // Colocamos 300ms de delay para dar tempo das suas funções filterContent() ou filterDashboards() 
        // esconderem e mostrarem os cards da tela antes de nós lermos eles!
        timer = setTimeout(() => {
            fetch(`${url}?q=${encodeURIComponent(q)}`)
                .then(r => r.json())
                .then(data => renderOmniResults(data.results, q));
        }, 300); 
    });

    // Fechar ao apertar ESC ou clicar fora do input
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') { closeDropdown(); input.blur(); }
    });
    
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.faq-search-wrapper')) closeDropdown();
    });
    
    // Reabrir se clicar no input de novo
    input.addEventListener('focus', () => {
        if (input.value.trim().length >= 2 && list.children.length) {
            dropdown.classList.add('open');
        }
    });
}

setupOmniSearch('searchInput');