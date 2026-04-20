// Global Modal Management Functions
function openCategoryModal() {
    const modal = document.getElementById('categoryModal');
    const title = document.getElementById('categoryModalTitle');
    const form = document.getElementById('categoryForm');
    const input = document.getElementById('id_category_name');
    const btn = document.getElementById('btnSaveCategory');
    if (!modal || !title || !form || !input || !btn) return;

    title.innerText = 'Nova Categoria';
    btn.innerText = 'Criar';
    input.value = '';
    
    const pathParts = window.location.pathname.split('/').filter(p => p !== '');
    // URL patterns: /clientes/SLUG/ ou /dashboard/clientes/SLUG/
    // Se parts: ["clientes", "slug"] -> index 1
    // Se parts: ["dashboard", "clientes", "slug"] -> index 2
    const clientSlug = pathParts[0] === 'dashboard' ? pathParts[2] : pathParts[1];
    
    if (!clientSlug) {
        console.error("Não foi possível identificar o slug do cliente a partir da URL:", window.location.pathname);
        return;
    }
    
    form.action = `/dashboard/categoria/${clientSlug}/criar/`;
    
    modal.classList.add('active');
}

function closeCategoryModal() {
    document.getElementById('categoryModal')?.classList.remove('active');
}

function openEditCategoryModal(slug, name) {
    const modal = document.getElementById('categoryModal');
    const title = document.getElementById('categoryModalTitle');
    const form = document.getElementById('categoryForm');
    const input = document.getElementById('id_category_name');
    const btn = document.getElementById('btnSaveCategory');
    if (!modal || !title || !form || !input || !btn) return;

    title.innerText = 'Editar Categoria';
    btn.innerText = 'Atualizar';
    input.value = name;
    
    const pathParts = window.location.pathname.split('/').filter(p => p !== '');
    const clientSlug = pathParts[0] === 'dashboard' ? pathParts[2] : pathParts[1];
    form.action = `/dashboard/categoria/${clientSlug}/atualizar/${slug}/`;
    
    modal.classList.add('active');
}

function openDeleteCategoryModal(slug, name) {
    const modal = document.getElementById('deleteCategoryModal');
    const nameSpan = document.getElementById('deleteCategoryName');
    const form = document.getElementById('deleteCategoryForm');
    if (!modal || !nameSpan || !form) return;

    nameSpan.innerText = name;
    const pathParts = window.location.pathname.split('/').filter(p => p !== '');
    const clientSlug = pathParts[0] === 'dashboard' ? pathParts[2] : pathParts[1];
    form.action = `/dashboard/categoria/${clientSlug}/deletar/${slug}/`;
    
    modal.classList.add('active');
}

function closeDeleteCategoryModal() {
    document.getElementById('deleteCategoryModal')?.classList.remove('active');
}

function openDeleteDashboardModal(actionUrl, title) {
    const modal = document.getElementById('deleteDashboardModal');
    const titleSpan = document.getElementById('deleteDashboardTitle');
    const form = document.getElementById('deleteDashboardForm');
    if (!modal || !titleSpan || !form) return;

    titleSpan.innerText = title;
    form.action = actionUrl;
    
    modal.classList.add('active');
}

function closeDeleteDashboardModal() {
    document.getElementById('deleteDashboardModal')?.classList.remove('active');
}

function openImageModal(imageUrl, dashboardName) {
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    if (!imageModal || !modalImage || !modalTitle) return;

    modalImage.src = imageUrl || '';
    modalTitle.textContent = dashboardName;
    imageModal.classList.add('active');
}

function closeImageModal() {
    document.getElementById('imageModal')?.classList.remove('active');
}

function openMoveModal() {
    const selectedCheckboxes = document.querySelectorAll('.dashboard-select:checked');
    const dashboardIds = Array.from(selectedCheckboxes).map(cb => cb.getAttribute('data-dashboard-id'));
    
    if (dashboardIds.length === 0) {
        alert('Selecione ao menos um dashboard');
        return;
    }

    const input = document.getElementById('selectedDashboardsInput');
    if (input) input.value = dashboardIds.join(',');
    
    document.getElementById('moveModal')?.classList.add('active');
}

function closeMoveModal() {
    document.getElementById('moveModal')?.classList.remove('active');
}

function updateBulkActionsBar() {
    const selectedCheckboxes = document.querySelectorAll('.dashboard-select:checked');
    const bulkActionsBar = document.getElementById('bulkActionsBar');
    const selectedCount = document.getElementById('selectedCount');
    if (!bulkActionsBar || !selectedCount) return;

    selectedCount.textContent = selectedCheckboxes.length;

    if (selectedCheckboxes.length > 0) {
        bulkActionsBar.classList.add('is-visible');
    } else {
        bulkActionsBar.classList.remove('is-visible');
    }
}

function clearSelection() {
    document.querySelectorAll('.dashboard-select').forEach(checkbox => {
        checkbox.checked = false;
        checkbox.closest('.dashboard-card')?.classList.remove('selected');
    });
    document.getElementById('bulkActionsBar')?.classList.remove('is-visible');
}

function confirmBulkDelete() {
    const selectedCheckboxes = document.querySelectorAll('.dashboard-select:checked');
    if (selectedCheckboxes.length === 0) {
        alert('Selecione ao menos um dashboard');
        return;
    }

    const modal = document.getElementById('bulkDeleteModal');
    const countSpan = document.getElementById('bulkDeleteCount');
    const input = document.getElementById('bulkDeleteDashboardsInput');
    
    if (!modal || !countSpan || !input) return;

    countSpan.innerText = selectedCheckboxes.length;
    input.value = Array.from(selectedCheckboxes).map(cb => cb.getAttribute('data-dashboard-id')).join(',');
    
    modal.classList.add('active');
}

function closeBulkDeleteModal() {
    document.getElementById('bulkDeleteModal')?.classList.remove('active');
}

// Event Listeners Initialization
document.addEventListener('DOMContentLoaded', function() {
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

    window.closeBulkDeleteModal = closeBulkDeleteModal;

    // Adicionando ouvintes específicos para os botões de fechar que podem ter IDs diferentes
    document.getElementById('dashImageModalClose')?.addEventListener('click', closeImageModal);
    document.getElementById('dashMoveModalClose')?.addEventListener('click', closeMoveModal);
    document.getElementById('dashMoveModalCancel')?.addEventListener('click', closeMoveModal);
    document.getElementById('bulkDeleteClose')?.addEventListener('click', closeBulkDeleteModal);
    document.getElementById('bulkDeleteCancel')?.addEventListener('click', closeBulkDeleteModal);

    const searchInput = document.getElementById('dashboardSearch');
    const categoryChips = document.querySelectorAll('.category-chips .chip');
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    const dashboardsGrid = document.querySelector('.dashboards-grid');
    const checkboxes = document.querySelectorAll('.dashboard-select');

    // Dashboard Search
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterDashboards();
        });
    }

    // Category Filter
    let selectedCategory = '';
    categoryChips.forEach(chip => {
        chip.addEventListener('click', function(e) {
            e.preventDefault();
            categoryChips.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            selectedCategory = this.getAttribute('data-category');
            filterDashboards();
        });
    });

    function filterDashboards() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        let visibleCount = 0;

        dashboardCards.forEach(card => {
            const dashboardTitle = card.querySelector('h3').textContent.toLowerCase();
            const dashboardCategories = card.getAttribute('data-categories') || '';
            const matchesSearch = dashboardTitle.includes(searchTerm) || dashboardCategories.includes(searchTerm);
            const matchesCategory = !selectedCategory || dashboardCategories.split(',').includes(selectedCategory.toLowerCase());
            
            if (matchesSearch && matchesCategory) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        let noResultsMsg = document.querySelector('.no-results-message');
        if (visibleCount === 0 && dashboardsGrid) {
            if (!noResultsMsg) {
                noResultsMsg = document.createElement('div');
                noResultsMsg.className = 'no-results-message';
                dashboardsGrid.parentNode.insertBefore(noResultsMsg, dashboardsGrid);
            }
            noResultsMsg.innerHTML = `
                <div class="no-results-inner" style="text-align: center; padding: 3rem; color: var(--app-muted);">
                    <i class="fa-solid fa-magnifying-glass" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>Nenhum dashboard encontrado</p>
                </div>
            `;
            dashboardsGrid.style.display = 'none';
        } else if (dashboardsGrid) {
            dashboardsGrid.style.display = '';
            if (noResultsMsg) noResultsMsg.remove();
        }
    }

    // Selection/Checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const card = this.closest('.dashboard-card');
            if (this.checked) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
            updateBulkActionsBar();
        });
    });

    // Image Preview Click
    const viewButtons = document.querySelectorAll('.btn-view');
    viewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const imageUrl = this.getAttribute('data-image');
            const dashboardName = this.closest('.dashboard-card').querySelector('h3').textContent;
            openImageModal(imageUrl, dashboardName);
        });
    });

    // Close Modals on Overlay Click
    const modals = document.querySelectorAll('.image-modal');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });

    // Bulk Actions buttons
    document.getElementById('btnBulkMove')?.addEventListener('click', openMoveModal);
    document.getElementById('btnBulkDelete')?.addEventListener('click', confirmBulkDelete);
    document.getElementById('btnBulkCancel')?.addEventListener('click', clearSelection);

    // Global Esc Key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.image-modal.active').forEach(m => m.classList.remove('active'));
        }
    });
});
