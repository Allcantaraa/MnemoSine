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