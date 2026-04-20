(function () {
    const key = 'mnemosine-theme';
    const saved = localStorage.getItem(key);
    const preferredDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (preferredDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
})();
