from flask import Flask, render_template, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Blueprints
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.chat_routes import chat_bp
          
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "disck_tallk_secret_key_2024")

# Configurar CORS
CORS(app)

# Configurar SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)
# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(chat_bp)

# ==================== ROTAS GERAIS ====================

@app.route('/')
def splash():
    if 'user_id' in session:
        return redirect(url_for('user.inicio'))
    return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('join')
def on_join(data):
    """Usuário entra em uma sala"""
    room = data.get('conversa_id')
    if room:
        join_room(room)
        emit('user_joined', {'user_id': session.get('user_id')}, to=room)

@socketio.on('leave')
def on_leave(data):
    """Usuário sai de uma sala"""
    room = data.get('conversa_id')
    if room:
        leave_room(room)
        emit('user_left', {'user_id': session.get('user_id')}, to=room)

@socketio.on('message')
def handle_message(data):
    """Mensagem de chat"""
    from models.conversa import Conversa
    
    conversa_id = data.get('conversa_id')
    remetente_id = session.get('user_id')
    texto = data.get('texto')
    
    if conversa_id and remetente_id and texto:
        # Salvar mensagem no banco
        Conversa.salvar_mensagem(conversa_id, remetente_id, texto)
        
        # Emitir para a sala
        emit('message', {
            'texto': texto,
            'remetente_id': remetente_id,
            'conversa_id': conversa_id,
            'data': str(data.get('data', ''))
        }, to=conversa_id)

@socketio.on('typing')
def handle_typing(data):
    """Usuário está digitando"""
    room = data.get('conversa_id')
    emit('user_typing', {
        'user_id': session.get('user_id')
    }, to=room, skip_sid=True)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Usuário parou de digitar"""
    room = data.get('conversa_id')
    emit('user_stop_typing', {
        'user_id': session.get('user_id')
    }, to=room, skip_sid=True)

# ==================== VIDEO CALL EVENTS ====================

@socketio.on('iniciar_chamada')
def iniciar_chamada(data):
    """Psicólogo recebe notificação de chamada"""
    from flask import session as flask_session
    
    consulta_id = data.get('consulta_id')
    psico_id = data.get('psico_id')
    paciente_id = flask_session.get('user_id')
    
    room = f"psico_{psico_id}"
    
    emit('chamada_recebida', {
        'consulta_id': consulta_id,
        'paciente_id': paciente_id,
        'timestamp': data.get('timestamp')
    }, to=room)

@socketio.on('aceitar_chamada')
def aceitar_chamada(data):
    """Notifica paciente que psicólogo aceitou"""
    consulta_id = data.get('consulta_id')
    room = f"consulta_{consulta_id}"
    
    emit('chamada_aceita', {
        'consulta_id': consulta_id,
        'timestamp': data.get('timestamp')
    }, to=room)

@socketio.on('rejeitar_chamada')
def rejeitar_chamada(data):
    """Notifica paciente que psicólogo rejeitou"""
    consulta_id = data.get('consulta_id')
    room = f"consulta_{consulta_id}"
    
    emit('chamada_rejeitada', {
        'consulta_id': consulta_id,
        'motivo': data.get('motivo', 'O psicólogo não pode atender no momento')
    }, to=room)

@socketio.on('entrar_sala_video')
def entrar_sala_video(data):
    """Entra na sala de vídeo"""
    consulta_id = data.get('consulta_id')
    room = f"consulta_{consulta_id}"
    join_room(room)
    
    print(f"[VIDEO] Usuário {session.get('user_id')} entrou na sala {room}")
    
    emit('usuario_entrou_sala', {
        'user_id': session.get('user_id')
    }, to=room, skip_sid=True)

# ==================== WEBRTC SIGNALING ====================

@socketio.on('offer')
def handle_offer(data):
    """WebRTC Offer recebido"""
    consulta_id = data.get('consulta_id')
    offer = data.get('offer')
    from_user = session.get('user_id')
    
    room = f"consulta_{consulta_id}"
    print(f"[WEBRTC] Offer de {from_user} para sala {room}")
    
    # Enviar para TODOS EXCETO o remetente
    emit('offer', {
        'consulta_id': consulta_id,
        'from': from_user,
        'offer': offer
    }, to=room, skip_sid=True)

@socketio.on('answer')
def handle_answer(data):
    """WebRTC Answer recebido"""
    consulta_id = data.get('consulta_id')
    answer = data.get('answer')
    from_user = session.get('user_id')
    
    room = f"consulta_{consulta_id}"
    print(f"[WEBRTC] Answer de {from_user} para sala {room}")
    
    emit('answer', {
        'consulta_id': consulta_id,
        'from': from_user,
        'answer': answer
    }, to=room, skip_sid=True)

@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    """ICE Candidate recebido"""
    consulta_id = data.get('consulta_id')
    candidate = data.get('candidate')
    from_user = session.get('user_id')
    
    room = f"consulta_{consulta_id}"
    print(f"[WEBRTC] ICE candidate de {from_user} para sala {room}")
    
    emit('ice-candidate', {
        'consulta_id': consulta_id,
        'from': from_user,
        'candidate': candidate
    }, to=room, skip_sid=True)

@socketio.on('stream-end')
def handle_stream_end(data):
    """Stream encerrado"""
    print(f"[WEBRTC] Stream encerrado por {session.get('user_id')}")
    emit('stream-end', {
        'from': session.get('user_id')
    }, skip_sid=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
