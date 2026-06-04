// ==================== APP INITIALIZATION ====================

const app = {
    init() {
        console.log('🚀 Disck Talk inicializado...');
        this.setupEventListeners();
        this.setupToast();
        this.setupNavigationActive();
        this.setupFormValidation();
        this.setupWebSocket();
    },

    // ==================== TOAST NOTIFICATIONS ====================

    setupToast() {
        window.showToast = (message, type = 'info', duration = 3000) => {
            const toast = document.createElement('div');
            toast.className = `glass-card fade-in toast-notification`;
            toast.setAttribute('role', 'alert');
            
            const bgColor = type === 'success' ? 'rgba(46, 204, 113, 0.2)' : 
                           type === 'error' ? 'rgba(231, 76, 60, 0.2)' : 
                           'rgba(52, 152, 219, 0.2)';
            
            const textColor = type === 'success' ? '#2ecc71' : 
                             type === 'error' ? '#e74c3c' : '#3498db';
            
            toast.style.cssText = `
                position: fixed;
                bottom: 100px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 2000;
                padding: 14px 24px;
                background: ${bgColor};
                color: ${textColor};
                font-weight: bold;
                border-radius: 12px;
                border: 1px solid ${textColor}33;
                max-width: 80vw;
                text-align: center;
            `;
            
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        };
    },

    // ==================== NAVIGATION ====================

    setupNavigationActive() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && currentPath.includes(href.replace(/^\//, '').split('/')[0])) {
                item.classList.add('active');
            }
        });
    },

    // ==================== FORM VALIDATION ====================

    setupFormValidation() {
        const forms = document.querySelectorAll('form:not(#chat-form)');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    showToast('Por favor, preencha todos os campos obrigatórios.', 'error');
                }
            });
        });
    },

    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.style.borderColor = '#e74c3c';
                isValid = false;
                
                setTimeout(() => {
                    input.style.borderColor = '';
                }, 2000);
            }
        });
        
        return isValid;
    },

    // ==================== WEBSOCKET ====================

    setupWebSocket() {
        if (typeof io !== 'undefined') {
            const socket = io();
            
            socket.on('connect', () => {
                console.log('✅ Conectado ao servidor');
            });
            
            socket.on('disconnect', () => {
                console.log('❌ Desconectado do servidor');
            });
            
            socket.on('message', (data) => {
                console.log('Mensagem recebida:', data);
            });
            
            window.socket = socket;
        }
    },

    // ==================== EVENT LISTENERS ====================

    setupEventListeners() {
        // Logout
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-logout')) {
                if (confirm('Tem certeza que deseja sair?')) {
                    window.location.href = '/logout';
                }
            }
        });
        
        // Rating Stars
        document.addEventListener('click', (e) => {
            if (e.target.closest('.star-rating i')) {
                const star = e.target;
                const rating = star.dataset.rating;
                const container = star.closest('.star-rating');
                
                if (rating && container) {
                    const stars = container.querySelectorAll('i');
                    stars.forEach((s, index) => {
                        if (index < rating) {
                            s.classList.add('filled');
                        } else {
                            s.classList.remove('filled');
                        }
                    });
                    
                    const input = container.nextElementSibling;
                    if (input && input.type === 'hidden') {
                        input.value = rating;
                    }
                }
            }
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => app.init());
