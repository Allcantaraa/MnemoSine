document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('btnBulkMove')?.addEventListener('click', openMoveModal);
    document.getElementById('btnBulkDelete')?.addEventListener('click', confirmBulkDelete);
    document.getElementById('btnBulkCancel')?.addEventListener('click', clearSelection);
    document.getElementById('dashImageModalClose')?.addEventListener('click', closeImageModal);
    document.getElementById('dashMoveModalClose')?.addEventListener('click', closeMoveModal);
    document.getElementById('dashMoveModalCancel')?.addEventListener('click', closeMoveModal);

    // Modal functionality
    const viewButtons = document.querySelectorAll('.btn-view');
    viewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const imageUrl = this.getAttribute('data-image');
            const dashboardName = this.closest('.dashboard-card').querySelector('h3').textContent;
            openImageModal(imageUrl, dashboardName);
        });
    });

    const imageModal = document.getElementById('imageModal');
    imageModal?.addEventListener('click', function(e) {
        if (e.target === this) {
            closeImageModal();
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeImageModal();
            closeMoveModal();
        }
    });

    // Search and filter functionality
    const searchInput = document.getElementById('dashboardSearch');
    const categoryChips = document.querySelectorAll('.category-chips .chip');
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    const dashboardsGrid = document.querySelector('.dashboards-grid');
    const emptyState = document.querySelector('.empty-state');
    const dashboardSelects = document.querySelectorAll('.dashboard-select');
    
    let selectedCategory = '';

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterDashboards();
        });
    }

    // Category filter functionality
    categoryChips.forEach(chip => {
        chip.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active state
            categoryChips.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            
            // Set selected category
            selectedCategory = this.getAttribute('data-category');
            filterDashboards();
        });
    });

    // Checkbox selection functionality
    dashboardSelects.forEach(checkbox => {
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

        // Show/hide no results message
        let noResultsMsg = document.querySelector('.no-results-message');
        
        if (visibleCount === 0 && dashboardsGrid) {
            if (!noResultsMsg) {
                noResultsMsg = document.createElement('div');
                noResultsMsg.className = 'no-results-message';
                dashboardsGrid.parentNode.insertBefore(noResultsMsg, dashboardsGrid);
            }
            noResultsMsg.innerHTML = `
                <div class="no-results-inner">
                    <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
                    <p>Nenhum dashboard encontrado</p>
                </div>
            `;
            dashboardsGrid.style.display = 'none';
        } else if (dashboardsGrid) {
            dashboardsGrid.style.display = '';
            if (noResultsMsg) {
                noResultsMsg.remove();
            }
        }
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

    window.updateBulkActionsBar = updateBulkActionsBar;
});

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
    const imageModal = document.getElementById('imageModal');
    imageModal?.classList.remove('active');
}

function openMoveModal() {
    const selectedCheckboxes = document.querySelectorAll('.dashboard-select:checked');
    const dashboardIds = Array.from(selectedCheckboxes).map(cb => cb.getAttribute('data-dashboard-id'));
    
    if (dashboardIds.length === 0) {
        alert('Selecione ao menos um dashboard');
        return;
    }

    document.getElementById('selectedDashboardsInput').value = dashboardIds.join(',');
    const moveModal = document.getElementById('moveModal');
    moveModal.classList.add('active');
}

function closeMoveModal() {
    const moveModal = document.getElementById('moveModal');
    moveModal?.classList.remove('active');
}

function confirmBulkDelete() {
    const selectedCheckboxes = document.querySelectorAll('.dashboard-select:checked');
    
    if (selectedCheckboxes.length === 0) {
        alert('Selecione ao menos um dashboard');
        return;
    }

    const message = selectedCheckboxes.length === 1 
        ? 'Tem certeza que deseja deletar este dashboard?' 
        : `Tem certeza que deseja deletar ${selectedCheckboxes.length} dashboards?`;

    if (confirm(message)) {
        // Submeter form de delete
        const form = document.createElement('form');
        form.method = 'POST';
        const bulkUrl = document.getElementById('cliente-dashboards-config')?.dataset?.bulkDeleteUrl;
        if (!bulkUrl) return;
        form.action = bulkUrl;
        
        // Adicionar CSRF token
        const csrfTokenInput = document.createElement('input');
        csrfTokenInput.type = 'hidden';
        csrfTokenInput.name = 'csrfmiddlewaretoken';
        csrfTokenInput.value = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        form.appendChild(csrfTokenInput);
        
        // Adicionar dashboard IDs
        const dashboardIdsInput = document.createElement('input');
        dashboardIdsInput.type = 'hidden';
        dashboardIdsInput.name = 'dashboard_ids';
        dashboardIdsInput.value = Array.from(selectedCheckboxes).map(cb => cb.getAttribute('data-dashboard-id')).join(',');
        form.appendChild(dashboardIdsInput);
        
        document.body.appendChild(form);
        form.submit();
    }
}

function clearSelection() {
    document.querySelectorAll('.dashboard-select').forEach(checkbox => {
        checkbox.checked = false;
        checkbox.closest('.dashboard-card')?.classList.remove('selected');
    });
    document.getElementById('bulkActionsBar')?.classList.remove('is-visible');
}