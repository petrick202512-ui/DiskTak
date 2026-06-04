// ==================== INTERSECTION OBSERVER ====================

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    // Observar elementos com fade-in
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Efeito de feedback visual nos botões e cards
    setupButtonFeedback();
    
    // Inicializar partículas se houver
    initHeroParticles();
    
    // Efeito parallax suave
    setupParallaxEffect();
});

// ==================== BUTTON FEEDBACK ====================

function setupButtonFeedback() {
    const interactive = document.querySelectorAll('button, .btn-primary, .btn-secondary, a.glass-card');
    
    interactive.forEach(element => {
        element.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                element.style.transform = 'scale(0.95)';
                element.style.transition = 'transform 0.1s ease';
            }
        });
        
        element.addEventListener('touchend', (e) => {
            element.style.transform = 'scale(1)';
        });
        
        element.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.97)';
        });
        
        element.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// ==================== HERO PARTICLES ====================

function initHeroParticles() {
    const container = document.getElementById('particles');
    if (!container) return;

    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        const size = Math.random() * 4 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + 'vw';
        particle.style.bottom = Math.random() * 100 + 'vh';
        particle.style.opacity = Math.random() * 0.5 + 0.2;
        particle.style.animationDelay = Math.random() * 10 + 's';
        container.appendChild(particle);
    }
}

// ==================== PARALLAX EFFECT ====================

function setupParallaxEffect() {
    if (!window.matchMedia('(max-width: 768px)').matches) {
        window.addEventListener('scroll', () => {
            const scrollPos = window.scrollY;
            const parallaxElements = document.querySelectorAll('[data-parallax]');
            
            parallaxElements.forEach(element => {
                const speed = element.getAttribute('data-parallax') || 0.5;
                element.style.transform = `translateY(${scrollPos * speed}px)`;
            });
        });
    }
}

// ==================== RIPPLE EFFECT ====================

function createRipple(event) {
    const element = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    element.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// ==================== SMOOTH SCROLL ====================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== LAZY LOADING ====================

const lazyImages = document.querySelectorAll('img[data-src]');

if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
} else {
    lazyImages.forEach(img => {
        img.src = img.dataset.src;
    });
}

// ==================== SCROLL TO TOP ====================

const scrollTopButton = document.getElementById('scrollTopBtn');

if (scrollTopButton) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollTopButton.style.display = 'block';
        } else {
            scrollTopButton.style.display = 'none';
        }
    });
    
    scrollTopButton.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}
