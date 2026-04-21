(function() {
    // Functions need to be global for onclick attributes in HTML
    window.copyInviteCode = function() {
        const codeElement = document.getElementById('inviteCode');
        if (!codeElement) return;
        navigator.clipboard.writeText(codeElement.textContent.trim());
    }

    window.openCreateUserModal = function() {
        const modal = document.getElementById('createUserModal');
        if (!modal) return;
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
    }

    window.closeCreateUserModal = function() {
        const modal = document.getElementById('createUserModal');
        if (!modal) return;
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    }

    window.openSimpleModal = function(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
    }

    window.closeSimpleModal = function(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    }

    window.openRemoveMemberModal = function(actionUrl, memberName) {
        const modal = document.getElementById('removeMemberModal');
        const form = document.getElementById('removeMemberForm');
        const name = document.getElementById('removeMemberName');
        if (!modal || !form || !name) return;
        form.action = actionUrl;
        name.textContent = memberName;
        window.openSimpleModal('removeMemberModal');
    }

    // Initialize event listeners after DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById('createUserModal')?.addEventListener('click', function (event) {
            if (event.target.id === 'createUserModal') {
                window.closeCreateUserModal();
            }
        });

        ['generateCodeModal', 'leaveOrgModal', 'deleteOrgModal', 'removeMemberModal', 'importCsvModal'].forEach(function (id) {
            document.getElementById(id)?.addEventListener('click', function (event) {
                if (event.target.id === id) {
                    window.closeSimpleModal(id);
                }
            });
        });

        // --- Import CSV Functionality ---
        const dropZone = document.getElementById('dropZone');
        const csvFileInput = document.getElementById('csvFileInput');
        const btnConfirmImport = document.getElementById('btnConfirmImport');
        const csvPreview = document.getElementById('csvPreview');
        const previewTableBody = document.querySelector('#previewTable tbody');
        const importErrors = document.getElementById('importErrors');
        const errorList = document.getElementById('errorList');
        const processProgress = document.getElementById('processProgress');
        const progressBar = document.getElementById('progressBar');
        const progressStatus = document.getElementById('progressStatus');

        let selectedFile = null;

        window.openImportCsvModal = function() {
            resetImportState();
            window.openSimpleModal('importCsvModal');
        }

        window.closeImportCsvModal = function() {
            window.closeSimpleModal('importCsvModal');
        }

        function resetImportState() {
            selectedFile = null;
            if (csvFileInput) csvFileInput.value = '';
            if (btnConfirmImport) btnConfirmImport.disabled = true;
            if (csvPreview) csvPreview.style.display = 'none';
            if (importErrors) importErrors.style.display = 'none';
            if (processProgress) processProgress.style.display = 'none';
            if (progressBar) progressBar.style.width = '0%';
            if (previewTableBody) previewTableBody.innerHTML = '';
            if (errorList) errorList.innerHTML = '';
        }

        // Drag and Drop
        dropZone?.addEventListener('click', (e) => {
    // Só dispara o clique programático se o alvo inicial não for o próprio input
    if (e.target !== csvFileInput) {
        csvFileInput?.click();
    }
});

        dropZone?.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone?.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone?.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        csvFileInput?.addEventListener('change', (e) => {
            if (e.target.files.length) {
                handleFileSelect(e.target.files[0]);
            }
        });

        function handleFileSelect(file) {
            if (!file.name.endsWith('.csv')) {
                alert('Por favor, selecione um arquivo CSV.');
                return;
            }
            selectedFile = file;
            previewCsv(file);
        }

        function previewCsv(file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const lines = e.target.result.split('\n');
                if (!previewTableBody) return;
                previewTableBody.innerHTML = '';
                
                let count = 0;
                const delimiter = ';';
                
                for (let i = 0; i < lines.length && count < 6; i++) {
                    const row = lines[i].split(delimiter);
                    if (row.length < 5 || (i === 0 && row[0].toLowerCase().includes('nome'))) continue;
                    
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${row[0] || ''}</td>
                        <td>${row[1] || ''}</td>
                        <td>${row[4] || ''}</td>
                    `;
                    previewTableBody.appendChild(tr);
                    count++;
                }
                
                if (csvPreview) csvPreview.style.display = 'block';
                if (btnConfirmImport) btnConfirmImport.disabled = false;
            };
            reader.readAsText(file);
        }

        btnConfirmImport?.addEventListener('click', async () => {
            if (!selectedFile) return;

            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

            btnConfirmImport.disabled = true;
            if (processProgress) processProgress.style.display = 'block';
            if (importErrors) importErrors.style.display = 'none';
            if (errorList) errorList.innerHTML = '';

            try {
                let progress = 0;
                const interval = setInterval(() => {
                    progress += 5;
                    if (progress <= 90) {
                        if (progressBar) progressBar.style.width = `${progress}%`;
                        if (progressStatus) progressStatus.innerText = `Processando... ${progress}%`;
                    }
                }, 100);

                const response = await fetch('/organization/importar-csv', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                clearInterval(interval);
                if (progressBar) progressBar.style.width = '100%';

                if (result.success) {
                    if (progressStatus) progressStatus.innerText = result.message;
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    if (processProgress) processProgress.style.display = 'none';
                    if (importErrors) importErrors.style.display = 'block';
                    result.errors?.forEach(err => {
                        const li = document.createElement('li');
                        li.innerText = err;
                        if (errorList) errorList.appendChild(li);
                    });
                    btnConfirmImport.disabled = false;
                }
            } catch (error) {
                alert('Erro ao processar a importação: ' + error);
                btnConfirmImport.disabled = false;
            }
        });
    });
})();