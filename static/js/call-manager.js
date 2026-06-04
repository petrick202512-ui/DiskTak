/**
 * Gerenciador de Chamadas de Vídeo
 * Integra WebRTC com Socket.IO
 */

class CallManager {
    constructor() {
        this.rtcHandler = null;
        this.socket = null;
        this.callStartTime = null;
        this.callTimerInterval = null;
        this.cameraEnabled = true;
        this.microphoneEnabled = true;
        
        this.localVideo = document.getElementById('localVideo');
        this.cameraBtn = document.getElementById('cameraBtn');
        this.microphoneBtn = document.getElementById('microphoneBtn');
        this.hangupBtn = document.getElementById('hangupBtn');
        this.callTimer = document.getElementById('callTimer');
        this.psycoAvatar = document.getElementById('psycoAvatar');
    }

    async initialize() {
        console.log('🎥 Inicializando sistema de chamada...');
        
        try {
            // Pegar IDs da consulta
            const container = document.querySelector('.video-call-container');
            const consultaId = container?.dataset.consultaId || '';
            const psicoId = container?.dataset.psicoId || '';
            const userType = container?.dataset.userType || 'user';
            const userId = container?.dataset.userId || '';
            
            // Criar handler WebRTC com consultaId e userId
            this.rtcHandler = new WebRTCHandler({ consultaId, userId });
            this.setupRTCCallbacks();
            
            // Inicializar mídia (com fallback automático para áudio)
            try {
                const mediaStream = await this.rtcHandler.initializeMedia();
                if (this.localVideo && mediaStream) {
                    this.localVideo.srcObject = mediaStream;
                }
            } catch (mediaError) {
                console.warn('⚠️ Câmera indisponível, continuando com áudio');
            }
            
            // Inicializar Socket.IO
            this.initializeSocket(consultaId, psicoId, userType);
            
            // Setup controles
            this.setupControls();
            
            // ATIVAR MODO DEMO SE NECESSÁRIO
            // Para ativar: adicione ?demo na URL ou execute: localStorage.setItem('call_demo_mode', 'true')
            this.setupDemoMode();
            
        } catch (error) {
            console.error('❌ Erro crítico ao inicializar:', error);
            showToast('❌ Erro: ' + error.message, 'error');
        }
    }

    setupRTCCallbacks() {
        this.rtcHandler.onRemoteStream = (peerId, stream) => {
            console.log('📹 Stream remoto recebido');
            this.displayRemoteStream(stream);
            
            if (this.psycoAvatar) {
                this.psycoAvatar.innerHTML = '<div style="color: var(--soft-green); font-size: 1.2rem; font-weight: 600;">✅ Conectado</div>';
            }
            
            showToast('✅ Conectado com sucesso!', 'success');
            this.startCallTimer();
        };
        
        this.rtcHandler.onStreamEnd = (peerId) => {
            console.log('❌ Stream encerrado');
            if (this.psycoAvatar) {
                this.psycoAvatar.innerHTML = '<div style="color: #e74c3c; font-size: 1.2rem; font-weight: 600;">📴 Desconectado</div>';
            }
        };
        
        this.rtcHandler.onCallRejected = (reason) => {
            showToast('❌ Chamada rejeitada: ' + reason, 'error');
            setTimeout(() => this.endCall(), 2000);
        };
    }

    /**
     * Simular modo demo/teste - aceita automaticamente após timeout
     */
    setupDemoMode() {
        const urlParams = new URLSearchParams(window.location.search);
        const isDemoMode = urlParams.has('demo') || localStorage.getItem('call_demo_mode');
        
        if (!isDemoMode) return;
        
        console.log('🎮 MODO DEMO ATIVADO - Simulando outro usuário');
        
        // Após 3 segundos, simular aceitação da chamada
        setTimeout(() => {
            console.log('🎮 Simulando resposta do outro usuário...');
            
            if (this.psycoAvatar) {
                this.psycoAvatar.innerHTML = '<div style="color: var(--soft-green); font-size: 1.2rem; font-weight: 600;">✅ Conectado</div>';
            }
            
            // Simular o recebimento de um stream remoto
            this.simulateRemoteStream();
            
            showToast('✅ Conectado com sucesso (MODO TESTE)!', 'success');
            this.startCallTimer();
        }, 3000);
    }

    /**
     * Simular stream remoto para testes
     */
    simulateRemoteStream() {
        try {
            // Criar canvas com conteúdo fake
            const canvas = document.createElement('canvas');
            canvas.width = 640;
            canvas.height = 480;
            const ctx = canvas.getContext('2d');
            
            // Desenhar um gradiente
            const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
            gradient.addColorStop(0, '#8EE4AF');
            gradient.addColorStop(1, '#2a6b6b');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Adicionar texto
            ctx.fillStyle = '#F5EFE0';
            ctx.font = 'bold 40px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('MODO TESTE', canvas.width / 2, canvas.height / 2 - 40);
            ctx.font = '20px Arial';
            ctx.fillText('Stream simulado para teste', canvas.width / 2, canvas.height / 2 + 40);
            
            // Pegar stream do canvas
            const canvasStream = canvas.captureStream(30);
            this.displayRemoteStream(canvasStream);
            
            console.log('✅ Stream remoto simulado para testes');
        } catch (error) {
            console.error('❌ Erro ao simular stream remoto:', error);
        }
    }

    displayRemoteStream(stream) {
        const remoteVideo = document.createElement('video');
        remoteVideo.srcObject = stream;
        remoteVideo.autoplay = true;
        remoteVideo.playsinline = true;
        remoteVideo.style.cssText = 'width: 100%; height: 100%; object-fit: cover;';
        remoteVideo.id = 'remoteVideo';
        
        const oldRemoteVideo = document.getElementById('remoteVideo');
        if (oldRemoteVideo) oldRemoteVideo.remove();
        
        const remoteContainer = document.querySelector('.remote-video-container');
        if (remoteContainer) {
            remoteContainer.innerHTML = '';
            remoteContainer.appendChild(remoteVideo);
        }
    }

    initializeSocket(consultaId, psicoId, userType) {
        const checkSocket = setInterval(() => {
            if (typeof io !== 'undefined') {
                clearInterval(checkSocket);
                this.socket = io();
                this.rtcHandler.initSocket(this.socket);
                
                this.socket.on('connect', () => {
                    console.log('✅ Socket conectado');
                    
                    this.socket.emit('entrar_sala_video', {
                        consulta_id: consultaId
                    });
                    
                    // Se for paciente, iniciar chamada
                    if (userType === 'user') {
                        setTimeout(() => {
                            console.log('📞 Iniciando chamada P2P...');
                            this.rtcHandler.initiateCall(psicoId).catch(err => {
                                console.error('Erro ao iniciar chamada:', err.message);
                                showToast('❌ Erro ao iniciar chamada', 'error');
                            });
                        }, 500);
                    } else {
                        console.log('⏳ Aguardando chamada do paciente...');
                    }
                });
            }
        }, 100);
    }

    setupControls() {
        this.cameraBtn?.addEventListener('click', () => this.toggleCamera());
        this.microphoneBtn?.addEventListener('click', () => this.toggleMicrophone());
        this.hangupBtn?.addEventListener('click', () => this.confirmEndCall());
    }

    toggleCamera() {
        this.cameraEnabled = !this.cameraEnabled;
        this.rtcHandler?.toggleVideo(this.cameraEnabled);
        
        this.cameraBtn.classList.toggle('disabled', !this.cameraEnabled);
        this.cameraBtn.innerHTML = this.cameraEnabled 
            ? '<i class="fa-solid fa-video"></i>'
            : '<i class="fa-solid fa-video-slash"></i>';
        
        showToast(this.cameraEnabled ? '📹 Câmera ativada' : '📹 Câmera desativada', 'info');
    }

    toggleMicrophone() {
        this.microphoneEnabled = !this.microphoneEnabled;
        this.rtcHandler?.toggleAudio(this.microphoneEnabled);
        
        this.microphoneBtn.classList.toggle('disabled', !this.microphoneEnabled);
        this.microphoneBtn.innerHTML = this.microphoneEnabled
            ? '<i class="fa-solid fa-microphone"></i>'
            : '<i class="fa-solid fa-microphone-slash"></i>';
        
        showToast(this.microphoneEnabled ? '🎤 Microfone ativado' : '🎤 Microfone desativado', 'info');
    }

    confirmEndCall() {
        if (confirm('Tem certeza que deseja encerrar a chamada?')) {
            this.endCall();
        }
    }

    startCallTimer() {
        if (this.callStartTime) return;
        
        this.callStartTime = Date.now();
        this.callTimerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.callStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            
            if (this.callTimer) {
                this.callTimer.textContent = 
                    String(minutes).padStart(2, '0') + ':' + 
                    String(seconds).padStart(2, '0');
            }
        }, 1000);
    }

    stopCallTimer() {
        if (this.callTimerInterval) {
            clearInterval(this.callTimerInterval);
            this.callTimerInterval = null;
        }
    }

    endCall() {
        console.log('📴 Encerrando chamada...');
        this.stopCallTimer();
        this.rtcHandler?.endCall();
        
        setTimeout(() => {
            window.location.href = '/recursos';
        }, 500);
    }
}

// Fallback para showToast
if (typeof showToast === 'undefined') {
    window.showToast = (message, type = 'info', duration = 3000) => {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%);
            z-index: 2000; padding: 14px 24px; border-radius: 12px;
            background: ${type === 'success' ? 'rgba(46, 204, 113, 0.2)' : type === 'error' ? 'rgba(231, 76, 60, 0.2)' : 'rgba(52, 152, 219, 0.2)'};
            color: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
            border: 1px solid ${type === 'success' ? '#2ecc7133' : type === 'error' ? '#e74c3c33' : '#3498db33'};
            font-weight: bold; text-align: center; max-width: 80vw;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    };
}

// Inicializar quando página carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new CallManager().initialize();
    });
} else {
    new CallManager().initialize();
}

// Encerrar ao fechar aba
window.addEventListener('beforeunload', () => {
    if (window.callManager) {
        window.callManager.rtcHandler?.endCall();
    }
});

// ESC para sair
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && window.callManager) {
        window.callManager.confirmEndCall();
    }
});
