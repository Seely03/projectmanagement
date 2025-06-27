// Theme management functionality
class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.themeIcon = document.getElementById('themeIcon');
        this.html = document.documentElement;
        this.init();
    }

    init() {
        // Get saved theme from localStorage or default to 'light'
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        this.updateThemeIcon(savedTheme);
        
        // Add event listener for theme toggle
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Check system preference on first load
        if (!localStorage.getItem('theme')) {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const defaultTheme = prefersDark ? 'dark' : 'light';
            this.setTheme(defaultTheme);
            this.updateThemeIcon(defaultTheme);
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                const newTheme = e.matches ? 'dark' : 'light';
                this.setTheme(newTheme);
                this.updateThemeIcon(newTheme);
            }
        });
    }

    setTheme(theme) {
        this.html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }

    toggleTheme() {
        const currentTheme = this.html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        this.setTheme(newTheme);
        this.updateThemeIcon(newTheme);
    }

    updateThemeIcon(theme) {
        if (!this.themeIcon) return;
        
        if (theme === 'dark') {
            this.themeIcon.className = 'fas fa-sun';
            this.themeToggle.title = 'Switch to Light Mode';
        } else {
            this.themeIcon.className = 'fas fa-moon';
            this.themeToggle.title = 'Switch to Dark Mode';
        }
    }

    getCurrentTheme() {
        return this.html.getAttribute('data-theme') || 'light';
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
} 