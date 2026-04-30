const AUTO_DISMISS_MS = 5000;

function dismissMessage(msg) {
    msg.style.animation = 'slideOut 0.35s ease-in forwards';
    msg.addEventListener('animationend', () => msg.remove(), { once: true });
}

document.addEventListener('DOMContentLoaded', () => {
    const messages = document.querySelectorAll('.message');
    messages.forEach((msg) => {
        msg.style.display = 'flex';
        const timer = setTimeout(() => dismissMessage(msg), AUTO_DISMISS_MS);
        msg.querySelector('.message-close')?.addEventListener('click', () => {
            clearTimeout(timer);
            dismissMessage(msg);
        });
    });
});