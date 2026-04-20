function openDeleteClientModal(actionUrl, name) {
    const modal = document.getElementById('deleteClientModal');
    const nameSpan = document.getElementById('deleteClientName');
    const form = document.getElementById('deleteClientForm');
    if (!modal || !nameSpan || !form) return;

    nameSpan.innerText = name;
    form.action = actionUrl;
    modal.classList.add('active');
}

function closeDeleteClientModal() {
    document.getElementById('deleteClientModal')?.classList.remove('active');
}

document.addEventListener('DOMContentLoaded', function() {
    // Make globally available
    window.openDeleteClientModal = openDeleteClientModal;
    window.closeDeleteClientModal = closeDeleteClientModal;

    document.getElementById('deleteClientClose')?.addEventListener('click', closeDeleteClientModal);
    document.getElementById('deleteClientCancel')?.addEventListener('click', closeDeleteClientModal);

    // Fechar ao clicar no overlay
    document.getElementById('deleteClientModal')?.addEventListener('click', function(e) {
        if (e.target === this) closeDeleteClientModal();
    });

    // Adicionar fechamento de modal de imagem por ID específico se necessário
    document.getElementById('indexImageModalClose')?.addEventListener('click', function() {
        document.getElementById('imageModal')?.classList.remove('active');
    });
    document.getElementById('indexImageModalClose')?.addEventListener('click', closeImageModal);
    if (imageModal) {
        imageModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeImageModal();
            }
        });
    }

    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeImageModal();
        }
    });

    // Search and filter functionality
    const searchInput = document.getElementById('searchInput');
    const categoryChips = document.querySelectorAll('.category-chips .chip');
    const clientCards = document.querySelectorAll('.client-card');
    const dashboardCards = document.querySelectorAll('.dashboards-section .dashboard-card');
    const emptyState = document.querySelector('.empty-state');
    
    let selectedCategory = '';

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterContent();
        });
    }

    document.querySelector('.dashboards-section')?.addEventListener('click', function(e) {
        const t = e.target.closest('.js-open-dash-preview');
        if (!t) return;
        e.preventDefault();
        openImageModal(t.dataset.previewSrc, t.dataset.previewTitle);
    });

    // Category filter functionality
    categoryChips.forEach(chip => {
        chip.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active state
            categoryChips.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            
            // Set selected category
            selectedCategory = this.getAttribute('data-category');
            filterContent();
        });
    });

    function filterContent() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        let visibleClientsCount = 0;
        let visibleDashboardsCount = 0;

        // Filter clients
        clientCards.forEach(card => {
            const clientName = card.querySelector('.client-name').textContent.toLowerCase();
            const clientDescription = card.querySelector('.client-description')?.textContent.toLowerCase() || '';
            
            const matchesSearch = clientName.includes(searchTerm) || clientDescription.includes(searchTerm);
            
            if (matchesSearch) {
                card.style.display = '';
                visibleClientsCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Filter dashboards
        dashboardCards.forEach(card => {
            const dashboardTitle = card.querySelector('h4').textContent.toLowerCase();
            const dashboardClient = card.querySelector('.dashboard-client').textContent.toLowerCase();
            const dashboardCategories = card.getAttribute('data-categories') || '';
            
            const matchesSearch = dashboardTitle.includes(searchTerm) || 
                                dashboardClient.includes(searchTerm) || 
                                dashboardCategories.includes(searchTerm);
            
            const matchesCategory = !selectedCategory || 
                                  dashboardCategories.split(',').includes(selectedCategory.toLowerCase());
            
            if (matchesSearch && matchesCategory) {
                card.style.display = '';
                visibleDashboardsCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Show/hide empty state
        if (emptyState && visibleClientsCount === 0 && visibleDashboardsCount === 0) {
            emptyState.style.display = 'block';
        } else if (emptyState && visibleClientsCount === 0 && clientCards.length > 0) {
            const dashboardsSection = document.querySelector('.dashboards-section');
            if (dashboardsSection) {
                dashboardsSection.style.display = visibleDashboardsCount > 0 ? 'block' : 'none';
            }
        }

        // Update client count
        const clientCount = document.querySelector('.client-count');
        if (clientCount) {
            clientCount.textContent = visibleClientsCount + ' cliente' + (visibleClientsCount !== 1 ? 's' : '');
        }
    }
});

function openImageModal(imageUrl, dashboardName) {
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    
    modalImage.src = imageUrl;
    modalTitle.textContent = dashboardName;
    imageModal.classList.add('active');
}

function closeImageModal() {
    const imageModal = document.getElementById('imageModal');
    imageModal.classList.remove('active');
}