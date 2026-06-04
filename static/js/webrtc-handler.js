/**
 * Handler de WebRTC para Chamadas de Vídeo
 * Sistema real de P2P com fallback para áudio
 */

class WebRTCHandler {
    constructor(options = {}) {
        this.peerConnections = new Map();
        this.localStream = null;
        this.remoteStreams = new Map();
        this.socket = null;
        this.consultaId = options.consultaId || null;
        this.userId = options.userId || null;
        this.isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        this.config = {
            iceServers: [
                { urls: ['stun:stun.l.google.com:19302'] },
                { urls: ['stun:stun1.l.google.com:19302'] }
            ],
            ...options
        };
        
        // Constraints adaptados para mobile e desktop
        this.constraints = this.getMediaConstraints();
    }

    /**
     * Obter constraints otimizadas baseado no dispositivo
     */
    getMediaConstraints() {
        if (this.isMobile) {
            // Constraints otimizadas para celular
            return {
                video: {
                    width: { max: 640 },
                    height: { max: 480 },
                    facingMode: 'user'
                },
                audio: {
                    echoCancellation: { ideal: true },
                    noiseSuppression: { ideal: true },
                    autoGainControl: { ideal: true }
                }
            };
        } else {
            // Constraints para desktop
            return {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                },
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            };
        }
    }

    /**
     * Inicializar conexão Socket.IO
     */
    initSocket(socket) {
        this.socket = socket;
        this.setupSocketListeners();
    }

    /**
     * Configurar listeners do Socket.IO
     */
    setupSocketListeners() {
        if (!this.socket) return;

        this.socket.on('offer', (data) => this.handleOffer(data));
        this.socket.on('answer', (data) => this.handleAnswer(data));
        this.socket.on('ice-candidate', (data) => this.handleIceCandidate(data));
        this.socket.on('stream-end', (data) => this.handleStreamEnd(data));
        this.socket.on('call-rejected', (data) => this.handleCallRejected(data));
    }

    /**
     * Inicializar mídia local
     */
    async initializeMedia(constraints = null) {
        try {
            // Verificar suporte a getUserMedia
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Navegador não suporta getUserMedia');
            }

            console.log('🎥 Solicitando acesso a câmera e microfone...');
            
            const mediaConstraints = constraints || this.constraints;
            console.log('📹 Constraints:', mediaConstraints);
            
            this.localStream = await navigator.mediaDevices.getUserMedia(mediaConstraints);
            
            console.log('✅ Mídia local (vídeo + áudio) inicializada');
            return this.localStream;
            
        } catch (error) {
            console.error('❌ Erro ao acessar mídia:', error.name, error.message);
            
            // Fallback 1: Constraints flexíveis
            try {
                console.warn('⚠️ FALLBACK 1: Tentando com constraints genéricas...');
                this.localStream = await navigator.mediaDevices.getUserMedia({
                    video: true,
                    audio: true
                });
                console.log('✅ FALLBACK 1 funcionou');
                return this.localStream;
            } catch (fallback1) {
                console.error('❌ FALLBACK 1 falhou');
            }
            
            // Fallback 2: Apenas vídeo
            try {
                console.warn('⚠️ FALLBACK 2: Tentando apenas vídeo...');
                this.localStream = await navigator.mediaDevices.getUserMedia({
                    video: true
                });
                console.log('✅ FALLBACK 2 funcionou (vídeo apenas)');
                return this.localStream;
            } catch (fallback2) {
                console.error('❌ FALLBACK 2 falhou');
            }
            
            // Fallback 3: Apenas áudio
            try {
                console.warn('⚠️ FALLBACK 3: Tentando apenas áudio...');
                this.localStream = await navigator.mediaDevices.getUserMedia({
                    audio: true
                });
                console.log('✅ FALLBACK 3 funcionou (áudio apenas)');
                return this.localStream;
            } catch (fallback3) {
                console.error('❌ FALLBACK 3 falhou');
                throw new Error(`Sem acesso a câmera ou microfone: ${error.message}`);
            }
        }
    }

    /**
     * Criar conexão peer
     */
    async createPeerConnection(peerId) {
        try {
            console.log(`🔗 ========== CRIAR PEER CONNECTION ==========`);
            console.log(`🔗 Peer ID: ${peerId}`);
            
            // Verificar ICE servers
            console.log(`🔗 ICE Servers: ${this.config.iceServers.length} configurados`);
            this.config.iceServers.forEach((server, i) => {
                console.log(`   ${i+1}. ${JSON.stringify(server)}`);
            });
            
            // Criar RTCPeerConnection
            console.log('🔗 Criando nova RTCPeerConnection...');
            const peerConnection = new RTCPeerConnection({
                iceServers: this.config.iceServers
            });
            console.log('✅ RTCPeerConnection criada com sucesso');

            // Adicionar tracks do stream local
            if (this.localStream) {
                console.log(`🔗 Adicionando ${this.localStream.getTracks().length} tracks...`);
                this.localStream.getTracks().forEach((track, index) => {
                    console.log(`   ${index+1}. ${track.kind.toUpperCase()} - ${track.label}`);
                    peerConnection.addTrack(track, this.localStream);
                });
                console.log('✅ Todos os tracks adicionados');
            } else {
                console.warn('⚠️ Nenhum stream local disponível');
            }

            // Listener para streams remotos
            peerConnection.ontrack = (event) => {
                console.log('📹 [EVENTO] Stream remoto recebido');
                console.log(`   └─ Tracks: ${event.streams[0].getTracks().length}`);
                this.remoteStreams.set(peerId, event.streams[0]);
                this.onRemoteStream?.(peerId, event.streams[0]);
            };

            // Listener para ICE candidates
            peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    console.log('❄️ [EVENTO] ICE candidate gerado');
                    this.socket?.emit('ice-candidate', {
                        consulta_id: this.consultaId,
                        candidate: event.candidate
                    });
                } else {
                    console.log('❄️ [EVENTO] Coleta de ICE candidates concluída');
                }
            };

            // Listener para ICE connection state
            peerConnection.oniceconnectionstatechange = () => {
                console.log(`❄️ [EVENTO] ICE Connection State: ${peerConnection.iceConnectionState}`);
            };

            // Listener para ICE gathering state
            peerConnection.onicegatheringstatechange = () => {
                console.log(`❄️ [EVENTO] ICE Gathering State: ${peerConnection.iceGatheringState}`);
            };

            // Listener para mudanças de conexão
            peerConnection.onconnectionstatechange = () => {
                console.log(`📊 [EVENTO] Connection State: ${peerConnection.connectionState}`);
                
                if (peerConnection.connectionState === 'failed') {
                    console.warn('⚠️ Conexão falhou, tentando reconectar...');
                    peerConnection.restartIce?.();
                }
                
                if (peerConnection.connectionState === 'closed' || 
                    peerConnection.connectionState === 'disconnected') {
                    this.handleStreamEnd({ from: peerId });
                }
            };

            // Listener para signaling state
            peerConnection.onsignalingstatechange = () => {
                console.log(`🔗 [EVENTO] Signaling State: ${peerConnection.signalingState}`);
            };

            this.peerConnections.set(peerId, peerConnection);
            console.log(`🔗 ========== PEER CONNECTION CRIADA COM SUCESSO ==========`);
            return peerConnection;
            
        } catch (error) {
            console.error('❌ ========== ERRO AO CRIAR PEER CONNECTION ==========');
            console.error('❌ Erro:', error.name, '-', error.message);
            console.error('❌ Stack:', error.stack);
            throw error;
        }
    }

    /**
     * Fazer uma chamada
     */
    async initiateCall(peerId) {
        try {
            console.log(`📞 ========== INICIAR CHAMADA P2P ==========`);
            console.log(`📞 Peer ID destino: ${peerId}`);
            console.log(`📞 Sala de consulta: ${this.consultaId}`);
            
            // Verificar mídia
            console.log(`📞 1️⃣ Verificando mídia local...`);
            if (!this.localStream) {
                console.log(`📞    └─ Sem stream, inicializando...`);
                await this.initializeMedia();
                console.log(`📞    └─ ✅ Stream inicializado`);
            } else {
                console.log(`📞    ✅ Stream já existe (${this.localStream.getTracks().length} tracks)`);
            }

            // Criar peer connection
            console.log(`📞 2️⃣ Criando peer connection...`);
            const peerConnection = await this.createPeerConnection(peerId);
            console.log(`📞    ✅ Peer connection criada`);

            // Criar offer
            console.log(`📞 3️⃣ Criando offer SDP...`);
            console.log(`📞    └─ offerToReceiveAudio: true`);
            console.log(`📞    └─ offerToReceiveVideo: true`);
            
            let offer;
            try {
                offer = await peerConnection.createOffer({
                    offerToReceiveAudio: true,
                    offerToReceiveVideo: true
                });
                console.log(`📞    ✅ Offer criado com sucesso`);
                console.log(`📞    └─ Tipo: ${offer.type}`);
                console.log(`📞    └─ SDI Length: ${offer.sdp.length} caracteres`);
            } catch (offerError) {
                console.error('❌ Erro ao criar offer:', offerError.name, '-', offerError.message);
                throw offerError;
            }

            // Definir local description
            console.log(`📞 4️⃣ Definindo local description...`);
            try {
                await peerConnection.setLocalDescription(offer);
                console.log(`📞    ✅ Local description definida`);
                console.log(`📞    └─ Signaling State: ${peerConnection.signalingState}`);
            } catch (descError) {
                console.error('❌ Erro ao definir local description:', descError.name, '-', descError.message);
                throw descError;
            }

            // Enviar offer via Socket.IO
            console.log(`📞 5️⃣ Enviando offer via Socket.IO...`);
            if (!this.socket) {
                console.error('❌ Socket não disponível!');
                throw new Error('Socket não conectado');
            }
            
            this.socket.emit('offer', {
                consulta_id: this.consultaId,
                offer: offer
            });
            console.log(`📞    ✅ Offer enviado para sala ${this.consultaId}`);

            console.log(`📞 ========== CHAMADA P2P INICIADA COM SUCESSO ==========`);
            
        } catch (error) {
            console.error(`📞 ========== ERRO AO INICIAR CHAMADA P2P ==========`);
            console.error('❌ Tipo de erro:', error.name);
            console.error('❌ Mensagem:', error.message);
            console.error('❌ Stack:', error.stack);
            console.error('❌ Contexto:', {
                peerId: peerId,
                consultaId: this.consultaId,
                socketConnected: !!this.socket,
                localStreamExists: !!this.localStream
            });
            throw error;
        }
    }

    /**
     * Lidar com offer recebido
     */
    async handleOffer(data) {
        try {
            const { consulta_id, from, offer } = data;
            
            // Ignorar ofertas do próprio usuário
            if (from === this.userId) {
                console.log('ℹ️ Ignorando offer do próprio usuário');
                return;
            }
            
            console.log(`📨 Offer recebido de ${from}`);

            // Guardar consulta_id se não tiver
            if (consulta_id) {
                this.consultaId = consulta_id;
            }

            // Inicializar mídia se não estiver pronta
            if (!this.localStream) {
                await this.initializeMedia();
            }

            // Criar peer connection se não existir
            let peerConnection = this.peerConnections.get(from);
            if (!peerConnection) {
                peerConnection = await this.createPeerConnection(from);
            }

            // Definir remote description
            await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));

            // Criar answer
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);

            // Enviar answer via Socket.IO
            this.socket?.emit('answer', {
                consulta_id: this.consultaId,
                answer: answer
            });

            console.log('✅ Answer enviado para sala', this.consultaId);
            
        } catch (error) {
            console.error('❌ Erro ao lidar com offer:', error);
        }
    }

    /**
     * Lidar com answer recebido
     */
    async handleAnswer(data) {
        try {
            const { from, answer } = data;
            
            // Ignorar answers do próprio usuário
            if (from === this.userId) {
                console.log('ℹ️ Ignorando answer do próprio usuário');
                return;
            }
            
            console.log(`📨 Answer recebido de ${from}`);

            const peerConnection = this.peerConnections.get(from);
            if (!peerConnection) {
                console.error('Peer connection não encontrada');
                return;
            }

            await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
            console.log('✅ Remote description definida');
            
        } catch (error) {
            console.error('❌ Erro ao lidar com answer:', error);
        }
    }

    /**
     * Lidar com ICE candidate
     */
    async handleIceCandidate(data) {
        try {
            const { from, candidate } = data;
            
            // Ignorar ICE candidates do próprio usuário
            if (from === this.userId) {
                return;
            }
            
            const peerConnection = this.peerConnections.get(from);
            if (!peerConnection) {
                console.error('Peer connection não encontrada');
                return;
            }

            if (candidate) {
                await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
            }
            
        } catch (error) {
            console.error('❌ Erro ao adicionar ICE candidate:', error);
        }
    }

    /**
     * Lidar com fim de stream
     */
    handleStreamEnd(data) {
        const { from } = data;
        console.log(`🔌 Stream encerrado de ${from}`);
        
        this.remoteStreams.delete(from);
        const peerConnection = this.peerConnections.get(from);
        if (peerConnection) {
            peerConnection.close();
            this.peerConnections.delete(from);
        }
        
        this.onStreamEnd?.(from);
    }

    /**
     * Lidar com chamada rejeitada
     */
    handleCallRejected(data) {
        console.log('❌ Chamada rejeitada:', data.reason);
        this.onCallRejected?.(data.reason);
    }

    /**
     * Encerrar chamada
     */
    endCall() {
        console.log('📴 Encerrando chamada...');
        
        // Parar todas as tracks do stream local
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }

        // Fechar todas as peer connections
        this.peerConnections.forEach((peerConnection, peerId) => {
            peerConnection.close();
        });
        this.peerConnections.clear();
        this.remoteStreams.clear();

        // Notificar via Socket.IO
        this.socket?.emit('stream-end', {});
        
        console.log('✅ Chamada encerrada');
    }

    /**
     * Obter stream local
     */
    getLocalStream() {
        return this.localStream;
    }

    /**
     * Obter stream remoto
     */
    getRemoteStream(peerId) {
        return this.remoteStreams.get(peerId);
    }

    /**
     * Togglear vídeo
     */
    toggleVideo(enabled) {
        if (this.localStream) {
            this.localStream.getVideoTracks().forEach(track => {
                track.enabled = enabled;
            });
        }
    }

    /**
     * Togglear áudio
     */
    toggleAudio(enabled) {
        if (this.localStream) {
            this.localStream.getAudioTracks().forEach(track => {
                track.enabled = enabled;
            });
        }
    }
}

// Exportar para uso global
window.WebRTCHandler = WebRTCHandler;
