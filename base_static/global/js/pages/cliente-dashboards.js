function openCategoryModal(actionUrl) {
  const modal = document.getElementById("categoryModal");
  const title = document.getElementById("categoryModalTitle");
  const form = document.getElementById("categoryForm");
  const input = document.getElementById("id_category_name");
  const btn = document.getElementById("btnSaveCategory");
  if (!modal || !title || !form || !input || !btn) return;

  title.innerText = "Nova Categoria";
  btn.innerText = "Criar";
  input.value = "";

  // Recebe a rota correta direto do Django
  form.action = actionUrl;

  modal.classList.add("active");
}

function closeCategoryModal() {
  document.getElementById("categoryModal")?.classList.remove("active");
}

function openEditCategoryModal(actionUrl, name) {
  const modal = document.getElementById("categoryModal");
  const title = document.getElementById("categoryModalTitle");
  const form = document.getElementById("categoryForm");
  const input = document.getElementById("id_category_name");
  const btn = document.getElementById("btnSaveCategory");
  if (!modal || !title || !form || !input || !btn) return;

  title.innerText = "Editar Categoria";
  btn.innerText = "Atualizar";
  input.value = name;

  form.action = actionUrl;

  modal.classList.add("active");
}

function openDeleteCategoryModal(actionUrl, name) {
  const modal = document.getElementById("deleteCategoryModal");
  const nameSpan = document.getElementById("deleteCategoryName");
  const form = document.getElementById("deleteCategoryForm");
  if (!modal || !nameSpan || !form) return;

  nameSpan.innerText = name;
  form.action = actionUrl;

  modal.classList.add("active");
}

function closeDeleteCategoryModal() {
  document.getElementById("deleteCategoryModal")?.classList.remove("active");
}

function openDeleteDashboardModal(actionUrl, title) {
  const modal = document.getElementById("deleteDashboardModal");
  const titleSpan = document.getElementById("deleteDashboardTitle");
  const form = document.getElementById("deleteDashboardForm");
  if (!modal || !titleSpan || !form) return;

  titleSpan.innerText = title;
  form.action = actionUrl;

  modal.classList.add("active");
}

function closeDeleteDashboardModal() {
  document.getElementById("deleteDashboardModal")?.classList.remove("active");
}

function openImageModal(imageUrl, dashboardName) {
  const imageModal = document.getElementById("imageModal");
  const modalImage = document.getElementById("modalImage");
  const modalTitle = document.getElementById("modalTitle");
  if (!imageModal || !modalImage || !modalTitle) return;

  modalImage.src = imageUrl || "";
  modalTitle.textContent = dashboardName;
  imageModal.classList.add("active");
}

function closeImageModal() {
  document.getElementById("imageModal")?.classList.remove("active");
}

function openMoveModal() {
  const selectedCheckboxes = document.querySelectorAll(
    ".dashboard-select:checked",
  );
  const dashboardIds = Array.from(selectedCheckboxes).map((cb) =>
    cb.getAttribute("data-dashboard-id"),
  );

  if (dashboardIds.length === 0) {
    alert("Selecione ao menos um dashboard");
    return;
  }

  const input = document.getElementById("selectedDashboardsInput");
  if (input) input.value = dashboardIds.join(",");

  document.getElementById("moveModal")?.classList.add("active");
}

function closeMoveModal() {
  document.getElementById("moveModal")?.classList.remove("active");
}

function updateBulkActionsBar() {
  const selectedCheckboxes = document.querySelectorAll(
    ".dashboard-select:checked",
  );
  const bulkActionsBar = document.getElementById("bulkActionsBar");
  const selectedCount = document.getElementById("selectedCount");
  if (!bulkActionsBar || !selectedCount) return;

  selectedCount.textContent = selectedCheckboxes.length;

  if (selectedCheckboxes.length > 0) {
    bulkActionsBar.classList.add("is-visible");
  } else {
    bulkActionsBar.classList.remove("is-visible");
  }
}

function clearSelection() {
  document.querySelectorAll(".dashboard-select").forEach((checkbox) => {
    checkbox.checked = false;
    checkbox.closest(".dashboard-card")?.classList.remove("selected");
  });
  document.getElementById("bulkActionsBar")?.classList.remove("is-visible");
}

function confirmBulkDelete() {
  const selectedCheckboxes = document.querySelectorAll(
    ".dashboard-select:checked",
  );
  if (selectedCheckboxes.length === 0) {
    alert("Selecione ao menos um dashboard");
    return;
  }

  const modal = document.getElementById("bulkDeleteModal");
  const countSpan = document.getElementById("bulkDeleteCount");
  const input = document.getElementById("bulkDeleteDashboardsInput");

  if (!modal || !countSpan || !input) return;

  countSpan.innerText = selectedCheckboxes.length;
  input.value = Array.from(selectedCheckboxes)
    .map((cb) => cb.getAttribute("data-dashboard-id"))
    .join(",");

  modal.classList.add("active");
}

function closeBulkDeleteModal() {
  document.getElementById("bulkDeleteModal")?.classList.remove("active");
}

// Event Listeners Initialization
document.addEventListener("DOMContentLoaded", function () {
  // Make functions globally available
  window.openCategoryModal = openCategoryModal;
  window.closeCategoryModal = closeCategoryModal;
  window.openEditCategoryModal = openEditCategoryModal;
  window.openDeleteCategoryModal = openDeleteCategoryModal;
  window.closeDeleteCategoryModal = closeDeleteCategoryModal;
  window.openDeleteDashboardModal = openDeleteDashboardModal;
  window.closeDeleteDashboardModal = closeDeleteDashboardModal;
  window.openImageModal = openImageModal;
  window.closeImageModal = closeImageModal;
  window.openMoveModal = openMoveModal;
  window.closeMoveModal = closeMoveModal;
  window.updateBulkActionsBar = updateBulkActionsBar;
  window.clearSelection = clearSelection;
  window.confirmBulkDelete = confirmBulkDelete;
  window.confirmBulkDuplicate = confirmBulkDuplicate;
  window.closeBulkDeleteModal = closeBulkDeleteModal;
  window.confirmBulkFavorite = confirmBulkFavorite;

  // Adicionando ouvintes específicos para os botões de fechar que podem ter IDs diferentes
  document
    .getElementById("dashImageModalClose")
    ?.addEventListener("click", closeImageModal);
  document
    .getElementById("dashMoveModalClose")
    ?.addEventListener("click", closeMoveModal);
  document
    .getElementById("dashMoveModalCancel")
    ?.addEventListener("click", closeMoveModal);
  document
    .getElementById("bulkDeleteClose")
    ?.addEventListener("click", closeBulkDeleteModal);
  document
    .getElementById("bulkDeleteCancel")
    ?.addEventListener("click", closeBulkDeleteModal);
  document
    .getElementById("btnBulkDuplicate")
    ?.addEventListener("click", confirmBulkDuplicate);
  document
    .getElementById("btnBulkFavorite")
    ?.addEventListener("click", confirmBulkFavorite);

  const searchInput = document.getElementById("dashboardSearch");
  const categoryChips = document.querySelectorAll(".category-chips .chip");
  const dashboardCards = document.querySelectorAll(".dashboard-card");
  const dashboardsGrid = document.querySelector(".dashboards-grid");
  const checkboxes = document.querySelectorAll(".dashboard-select");

  // Dashboard Search
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      filterDashboards();
    });
  }

  // Category Filter
  let selectedCategory = "";
  categoryChips.forEach((chip) => {
    chip.addEventListener("click", function (e) {
      e.preventDefault();
      categoryChips.forEach((c) => c.classList.remove("active"));
      this.classList.add("active");
      selectedCategory = this.getAttribute("data-category");
      filterDashboards();
    });
  });

  function filterDashboards() {
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : "";
    let visibleCount = 0;

    dashboardCards.forEach((card) => {
      const dashboardTitle = card.querySelector("h3").textContent.toLowerCase();
      const dashboardCategories = card.getAttribute("data-categories") || "";
      const matchesSearch =
        dashboardTitle.includes(searchTerm) ||
        dashboardCategories.includes(searchTerm);
      const matchesCategory =
        !selectedCategory ||
        dashboardCategories.split(",").includes(selectedCategory.toLowerCase());

      if (matchesSearch && matchesCategory) {
        card.style.display = "";
        visibleCount++;
      } else {
        card.style.display = "none";
      }
    });

    let noResultsMsg = document.querySelector(".no-results-message");
    if (visibleCount === 0 && dashboardsGrid) {
      if (!noResultsMsg) {
        noResultsMsg = document.createElement("div");
        noResultsMsg.className = "no-results-message";
        dashboardsGrid.parentNode.insertBefore(noResultsMsg, dashboardsGrid);
      }
      noResultsMsg.innerHTML = `
                <div class="no-results-inner" style="text-align: center; padding: 3rem; color: var(--app-muted);">
                    <i class="fa-solid fa-magnifying-glass" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>Nenhum dashboard encontrado</p>
                </div>
            `;
      dashboardsGrid.style.display = "none";
    } else if (dashboardsGrid) {
      dashboardsGrid.style.display = "";
      if (noResultsMsg) noResultsMsg.remove();
    }

    const termForRecs = searchTerm || selectedCategory;

    // Mapeia os IDs que JÁ ESTÃO visíveis na tela principal
    const visibleIds = [];
    dashboardCards.forEach((card) => {
      if (card.style.display !== "none") {
        visibleIds.push(card.getAttribute("data-dashboard-id"));
      }
    });

    // Dispara a busca inteligente
    if (termForRecs) {
      buscarRecomendacoes(termForRecs, visibleIds);
    } else {
      // Se limpou os filtros, esconde as recomendações
      const recSection = document.getElementById("recommendationsSection");
      if (recSection) recSection.style.display = "none";
    }
  }

  // Selection/Checkboxes
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const card = this.closest(".dashboard-card");
      if (this.checked) {
        card.classList.add("selected");
      } else {
        card.classList.remove("selected");
      }
      updateBulkActionsBar();
    });
  });

  // Image Preview Click
  const viewButtons = document.querySelectorAll(".btn-view");
  viewButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      const imageUrl = this.getAttribute("data-image");
      const dashboardName =
        this.closest(".dashboard-card").querySelector("h3").textContent;
      openImageModal(imageUrl, dashboardName);
    });
  });

  // Close Modals on Overlay Click
  const modals = document.querySelectorAll(".image-modal");
  modals.forEach((modal) => {
    modal.addEventListener("click", function (e) {
      if (e.target === this) {
        this.classList.remove("active");
      }
    });
  });

  // Bulk Actions buttons
  document
    .getElementById("btnBulkMove")
    ?.addEventListener("click", openMoveModal);
  document
    .getElementById("btnBulkDelete")
    ?.addEventListener("click", confirmBulkDelete);
  document
    .getElementById("btnBulkCancel")
    ?.addEventListener("click", clearSelection);

  // Global Esc Key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      document
        .querySelectorAll(".image-modal.active")
        .forEach((m) => m.classList.remove("active"));
    }
  });

  // Toggle de Favorito Individual no Card
  const favoriteButtons = document.querySelectorAll(".dashboard-favorite");

  favoriteButtons.forEach((btn) => {
    btn.addEventListener("click", async function (e) {
      e.preventDefault();

      const url = this.getAttribute("data-url");
      const icon = this.querySelector("i");
      const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]",
      )?.value;

      // Feedback visual imediato (Optimistic UI)
      this.classList.toggle("active");
      if (this.classList.contains("active")) {
        icon.classList.remove("fa-regular");
        icon.classList.add("fa-solid");
      } else {
        icon.classList.remove("fa-solid");
        icon.classList.add("fa-regular");
      }

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
          },
        });

        const data = await response.json();

        // Se o servidor retornar erro, revertemos a animação
        if (!data.success) {
          console.error("Erro ao favoritar:", data.error);
          this.classList.toggle("active");
          icon.classList.toggle("fa-solid");
          icon.classList.toggle("fa-regular");
        }
      } catch (error) {
        console.error("Erro na requisição:", error);
        // Reverte em caso de falha de rede
        this.classList.toggle("active");
        icon.classList.toggle("fa-solid");
        icon.classList.toggle("fa-regular");
      }
    });
  });
});

function confirmBulkDuplicate() {
  const selectedCheckboxes = document.querySelectorAll(
    ".dashboard-select:checked",
  );
  if (selectedCheckboxes.length === 0) {
    alert("Selecione ao menos um dashboard para duplicar.");
    return;
  }

  const message =
    selectedCheckboxes.length === 1
      ? "Tem certeza que deseja duplicar este dashboard?"
      : `Tem certeza que deseja duplicar ${selectedCheckboxes.length} dashboards?`;

  if (confirm(message)) {
    const form = document.createElement("form");
    form.method = "POST";

    // Pega a URL do config que atualizamos no HTML
    const config = document.getElementById("cliente-dashboards-config");
    const bulkDuplicateUrl = config?.dataset?.bulkDuplicateUrl;
    if (!bulkDuplicateUrl) return;

    form.action = bulkDuplicateUrl;

    const csrfTokenInput = document.createElement("input");
    csrfTokenInput.type = "hidden";
    csrfTokenInput.name = "csrfmiddlewaretoken";
    csrfTokenInput.value =
      document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    form.appendChild(csrfTokenInput);

    const dashboardIdsInput = document.createElement("input");
    dashboardIdsInput.type = "hidden";
    dashboardIdsInput.name = "dashboard_ids";
    dashboardIdsInput.value = Array.from(selectedCheckboxes)
      .map((cb) => cb.getAttribute("data-dashboard-id"))
      .join(",");
    form.appendChild(dashboardIdsInput);

    document.body.appendChild(form);
    form.submit();
  }
}

function confirmBulkFavorite() {
  const selectedCheckboxes = document.querySelectorAll(
    ".dashboard-select:checked",
  );
  if (selectedCheckboxes.length === 0) {
    alert("Selecione ao menos um dashboard para favoritar.");
    return;
  }

  // Não precisa de confirm() para favoritar, pois é uma ação inofensiva.
  // Basta submeter o form direto.
  const form = document.createElement("form");
  form.method = "POST";

  const config = document.getElementById("cliente-dashboards-config");
  const bulkFavoriteUrl = config?.dataset?.bulkFavoriteUrl;
  if (!bulkFavoriteUrl) return;

  form.action = bulkFavoriteUrl;

  const csrfTokenInput = document.createElement("input");
  csrfTokenInput.type = "hidden";
  csrfTokenInput.name = "csrfmiddlewaretoken";
  csrfTokenInput.value =
    document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
  form.appendChild(csrfTokenInput);

  const dashboardIdsInput = document.createElement("input");
  dashboardIdsInput.type = "hidden";
  dashboardIdsInput.name = "dashboard_ids";
  dashboardIdsInput.value = Array.from(selectedCheckboxes)
    .map((cb) => cb.getAttribute("data-dashboard-id"))
    .join(",");
  form.appendChild(dashboardIdsInput);

  document.body.appendChild(form);
  form.submit();
}


async function buscarRecomendacoes(term, visibleIds) {
    const config = document.getElementById('cliente-dashboards-config');
    const apiUrl = config?.dataset?.apiRecsUrl;
    if (!apiUrl) return;

    try {
        const response = await fetch(`${apiUrl}?q=${encodeURIComponent(term)}`);
        const data = await response.json();

        const recSection = document.getElementById('recommendationsSection');
        const recGrid = document.getElementById('recommendationsGrid');
        
        if (!recSection || !recGrid) return;

        // O Segredo: Filtra para remover qualquer dashboard que já está na tela!
        const recommendations = data.dashboards.filter(d => !visibleIds.includes(String(d.id)));

        if (recommendations.length > 0) {
            recGrid.innerHTML = ''; // Limpa as recomendações antigas

            recommendations.forEach(dash => {
                const card = document.createElement('div');
                card.className = 'dashboard-card';
                card.innerHTML = `
                    <div class="dashboard-image">
                        ${dash.image_url ? `<img src="${dash.image_url}" alt="${dash.title}">` : `<div class="no-image">Sem imagem</div>`}
                    </div>
                    <div class="dashboard-content">
                        <div class="client-badge">
                            <i class="fa-solid fa-building"></i> ${dash.client_name}
                        </div>
                        <h3>${dash.title}</h3>
                        
                        <div class="dashboard-actions" style="justify-content: flex-start; margin-top: 1rem; border-top: 1px solid var(--app-border, #e2e8f0); padding-top: 1rem;">
                            <a href="javascript:void(0)" class="btn-view" data-image="${dash.image_url}" title="Ver imagem do dashboard">
                                <i class="fa-solid fa-eye"></i>
                            </a>
                            <a href="${dash.download_url}" class="btn-download" title="Download JSON">
                                <i class="fa-solid fa-download"></i>
                            </a>
                        </div>
                    </div>
                `;
                recGrid.appendChild(card);
            });

        const newViewButtons = recGrid.querySelectorAll('.btn-view');
            newViewButtons.forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const imageUrl = this.getAttribute('data-image');
                    const dashboardName = this.closest('.dashboard-content').querySelector('h3').textContent;
                    
                    // Usa a função global que criamos anteriormente
                    if (typeof window.openImageModal === 'function') {
                        window.openImageModal(imageUrl, dashboardName);
                    }
                });
            });

            recSection.style.display = 'block';
        } else {
            recSection.style.display = 'none';
        }
    } catch (error) {
        console.error('Erro ao buscar recomendações:', error);
    }
}

// --- CRIAÇÃO EM MASSA (SMART MATCHING) ---

let bulkDashboardPairs = []; // Vai guardar o estado atual da pré-visualização

window.openBulkCreateModal = function() {
    document.getElementById('bulkCreateModal').classList.add('active');
    resetBulkCreateState();
};

window.closeBulkCreateModal = function() {
    document.getElementById('bulkCreateModal').classList.remove('active');
    resetBulkCreateState();
};

function resetBulkCreateState() {
    bulkDashboardPairs = [];
    document.getElementById('bulkFileInput').value = '';
    document.getElementById('bulkPreviewSection').style.display = 'none';
    document.getElementById('bulkPairsGrid').innerHTML = '';
    document.getElementById('btnConfirmBulkCreate').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('bulkDropZone');
    const fileInput = document.getElementById('bulkFileInput');
    const confirmBtn = document.getElementById('btnConfirmBulkCreate');

    if (dropZone) {
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            processFiles(e.dataTransfer.files);
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => processFiles(e.target.files));
    }

    if (confirmBtn) {
        confirmBtn.addEventListener('click', submitBulkDashboards);
    }
});

// A Mágica de Pareamento
async function processFiles(fileList) {
    const files = Array.from(fileList);
    const jsons = files.filter(f => f.name.toLowerCase().endsWith('.json'));
    const images = files.filter(f => f.name.toLowerCase().match(/\.(jpg|jpeg|png)$/));

    if (jsons.length === 0) {
        alert("Por favor, envie ao menos um arquivo JSON.");
        return;
    }

    document.getElementById('bulkPreviewSection').style.display = 'block';
    document.getElementById('btnConfirmBulkCreate').style.display = 'block';
    
    const grid = document.getElementById('bulkPairsGrid');
    
    // Processa os JSONs assincronamente para ler a chave "title"
    for (const jsonFile of jsons) {
        // Pega o nome do arquivo sem a extensão para buscar a imagem
        const baseName = jsonFile.name.substring(0, jsonFile.name.lastIndexOf('.')) || jsonFile.name;
        
        // Tenta achar uma imagem correspondente
        let matchedImage = images.find(img => {
            const imgBase = img.name.substring(0, img.name.lastIndexOf('.'));
            return imgBase === baseName;
        }) || null;

        // Lê o conteúdo do JSON para pegar o Título
        const title = await extractTitleFromJson(jsonFile);

        // Cria o objeto na memória
        const pairId = Date.now() + Math.random().toString(36).substr(2, 9);
        bulkDashboardPairs.push({
            id: pairId,
            jsonFile: jsonFile,
            imageFile: matchedImage,
            title: title || baseName // fallback pro nome do arquivo se não achar titulo
        });
    }

    renderBulkPreview();
}

function extractTitleFromJson(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                resolve(data.title || null);
            } catch (err) {
                resolve(null);
            }
        };
        reader.readAsText(file);
    });
}

function renderBulkPreview() {
    const grid = document.getElementById('bulkPairsGrid');
    document.getElementById('bulkPairCount').textContent = `${bulkDashboardPairs.length} Dashboard(s)`;
    grid.innerHTML = '';

    bulkDashboardPairs.forEach((pair, index) => {
        const imageUrl = pair.imageFile ? URL.createObjectURL(pair.imageFile) : null;
        
        const card = document.createElement('div');
        card.className = 'bulk-pair-card';
        card.innerHTML = `
            <div class="bulk-pair-image-area" onclick="triggerManualImageSelect('${pair.id}')">
                ${imageUrl ? `<img src="${imageUrl}">` : `<i class="fa-regular fa-image fa-2x" style="color: #cbd5e1;"></i>`}
                <div class="bulk-pair-image-overlay">
                    <i class="fa-solid fa-pen"></i>
                    <span>Alterar Imagem</span>
                </div>
                <input type="file" id="img-input-${pair.id}" accept=".png,.jpg,.jpeg" style="display: none;" onchange="handleManualImageChange(event, '${pair.id}')">
            </div>
            
            <div class="bulk-pair-info">
                <div class="bulk-pair-title" title="${pair.title}">${pair.title}</div>
                <div class="bulk-pair-filename">
                    <i class="fa-solid fa-code" style="color: #10b981;"></i> ${pair.jsonFile.name}
                </div>
                ${pair.imageFile ? 
                  `<div class="bulk-pair-filename" style="margin-top: 4px;">
                     <i class="fa-regular fa-image" style="color: #3b82f6;"></i> ${pair.imageFile.name}
                   </div>` 
                  : 
                  `<div class="bulk-pair-filename" style="margin-top: 4px; color: #ef4444;">
                     <i class="fa-solid fa-triangle-exclamation"></i> Sem imagem
                   </div>`
                }
            </div>
        `;
        grid.appendChild(card);
    });
}

// Funções para correção manual do usuário no card
window.triggerManualImageSelect = function(pairId) {
    document.getElementById(`img-input-${pairId}`).click();
};

window.handleManualImageChange = function(event, pairId) {
    const file = event.target.files[0];
    if (file) {
        const pairIndex = bulkDashboardPairs.findIndex(p => p.id === pairId);
        if (pairIndex > -1) {
            bulkDashboardPairs[pairIndex].imageFile = file;
            renderBulkPreview(); // Re-renderiza para atualizar a foto
        }
    }
};

// Envio para o Backend
async function submitBulkDashboards() {
    const confirmBtn = document.getElementById('btnConfirmBulkCreate');
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Salvando...';

    const config = document.getElementById('cliente-dashboards-config');
    const bulkCreateUrl = config?.dataset?.bulkCreateUrl;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    const formData = new FormData();
    formData.append('dashboards_count', bulkDashboardPairs.length);

    bulkDashboardPairs.forEach((pair, i) => {
        formData.append(`title_${i}`, pair.title);
        formData.append(`json_${i}`, pair.jsonFile);
        if (pair.imageFile) {
            formData.append(`image_${i}`, pair.imageFile);
        }
    });

    try {
        const response = await fetch(bulkCreateUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            body: formData
        });

        const data = await response.json();
        
        if (data.success) {
            window.location.reload(); // Recarrega para ver os novos dashboards
        } else {
            alert('Erro ao salvar dashboards: ' + data.error);
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = 'Confirmar e Salvar Dashboards';
        }
    } catch (error) {
        console.error("Erro na requisição:", error);
        alert('Erro crítico ao conectar com o servidor.');
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = 'Confirmar e Salvar Dashboards';
    }
}

window.openCategoryBulkModal = function() {
    const selectedCheckboxes = document.querySelectorAll('.dashboard-select:checked');
    const dashboardIds = Array.from(selectedCheckboxes).map(cb => cb.getAttribute('data-dashboard-id'));
    
    if (dashboardIds.length === 0) {
        alert('Selecione ao menos um dashboard.');
        return;
    }

    const input = document.getElementById('categoryBulkIdsInput');
    if (input) input.value = dashboardIds.join(',');
    
    // Reseta os checkboxes do modal sempre que abrir
    document.querySelectorAll('input[name="categorias"]').forEach(cb => cb.checked = false);

    document.getElementById('categoryBulkModal')?.classList.add('active');
};

window.closeCategoryBulkModal = function() {
    document.getElementById('categoryBulkModal')?.classList.remove('active');
};