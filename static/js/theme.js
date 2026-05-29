/* ═══════════════════════════════════════════════
   BlogCraft — Theme Toggle (Dark/Light)
   ═══════════════════════════════════════════════ */

(function() {
    const STORAGE_KEY = 'blogcraft-theme';

    function getPreferredTheme() {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) return stored;
        return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(STORAGE_KEY, theme);
        
        // Update icon if it exists
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
            if (window.lucide) {
                window.lucide.createIcons();
            }
        }
    }

    // Apply theme immediately (before DOM loads to prevent flash)
    setTheme(getPreferredTheme());

    // Toggle handler
    document.addEventListener('DOMContentLoaded', () => {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        toggleBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            setTheme(next);
        });
    });

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
        if (!localStorage.getItem(STORAGE_KEY)) {
            setTheme(e.matches ? 'light' : 'dark');
        }
    });
})();
