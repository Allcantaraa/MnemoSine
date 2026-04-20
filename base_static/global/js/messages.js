document.addEventListener('click', function (e) {
    const btn = e.target.closest('.message-close');
    if (!btn) return;
    const row = btn.closest('.message');
    if (row) row.style.display = 'none';
});
