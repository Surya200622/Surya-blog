/* ═══════════════════════════════════════════════
   BlogCraft — Main JavaScript
   ═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initScrollAnimations();
    initMobileMenu();
    initToasts();
    initReadingProgress();
    initDashboardSidebar();
});

/* ── Dashboard Mobile Sidebar Toggle ── */
function initDashboardSidebar() {
    const toggleBtns = document.querySelectorAll('.sidebar-toggle');
    const sidebar = document.getElementById('dashboard-sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (!sidebar || toggleBtns.length === 0) return;

    function openSidebar() {
        sidebar.classList.add('open');
        if (overlay) overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    });

    // Close on overlay click
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // Close on sidebar link click (mobile)
    sidebar.querySelectorAll('.sidebar__link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 1024) {
                closeSidebar();
            }
        });
    });

    // Close on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });
}

/* ── Scroll Reveal Animations ── */
function initScrollAnimations() {
    const elements = document.querySelectorAll('.animate-on-scroll, .animate-left, .animate-right, .animate-scale');

    if (!elements.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    elements.forEach(el => observer.observe(el));
}

/* ── Mobile Menu Toggle ── */
function initMobileMenu() {
    const toggle = document.getElementById('navbar-toggle');
    const menu = document.getElementById('navbar-links');

    if (!toggle || !menu) return;

    toggle.addEventListener('click', () => {
        menu.classList.toggle('open');
        toggle.setAttribute('aria-expanded', menu.classList.contains('open'));
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!toggle.contains(e.target) && !menu.contains(e.target)) {
            menu.classList.remove('open');
        }
    });
}

/* ── Toast Notifications ── */
function initToasts() {
    const alerts = document.querySelectorAll('.messages .alert');
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            alert.style.animation = 'slideInRight 0.4s ease-out';
        }, index * 150);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            alert.style.transition = 'all 0.3s ease-out';
            setTimeout(() => alert.remove(), 300);
        }, 5000 + index * 150);
    });
}

/* ── Reading Progress Bar ── */
function initReadingProgress() {
    const progressBar = document.getElementById('reading-progress');
    if (!progressBar) return;

    window.addEventListener('scroll', () => {
        const scrollTop = document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const progress = (scrollTop / scrollHeight) * 100;
        progressBar.style.width = `${progress}%`;
    });
}

/* ── Like Toggle ── */
function toggleLike(slug) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                      getCookie('csrftoken');

    fetch(`/blog/${slug}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
    })
    .then(res => res.json())
    .then(data => {
        const btn = document.getElementById('like-btn');
        const count = document.getElementById('like-count');
        if (btn) {
            btn.classList.toggle('liked', data.liked);
            btn.innerHTML = data.liked ? '❤️' : '🤍';
        }
        if (count) count.textContent = data.count;
    })
    .catch(err => console.error('Like error:', err));
}

/* ── CSRF Cookie Helper ── */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

/* ── Counter Animation ── */
function animateCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    counters.forEach(counter => {
        const target = parseInt(counter.dataset.counter);
        const duration = 1500;
        const step = target / (duration / 16);
        let current = 0;

        const update = () => {
            current += step;
            if (current < target) {
                counter.textContent = Math.floor(current).toLocaleString();
                requestAnimationFrame(update);
            } else {
                counter.textContent = target.toLocaleString();
            }
        };
        update();
    });
}

// Trigger counters when visible
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounters();
            counterObserver.unobserve(entry.target);
        }
    });
});
const statsSection = document.querySelector('.stats-section');
if (statsSection) counterObserver.observe(statsSection);
