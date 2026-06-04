from flask import Blueprint, render_template, session, request, redirect, url_for
from database.mongodb import db
from bson import ObjectId

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/conversas')
def conversas():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('auth.login'))
    
    # Busca conversas onde o usuário participa
    conversas_lista = list(db.conversas.find({
        "$or": [{"usuario_id": user_id}, {"psico_id": user_id}]
    }).sort("data_inicio", -1))
    
    # Enriquece com dados do outro participante
    for conv in conversas_lista:
        outro_id = conv['psico_id'] if conv['usuario_id'] == user_id else conv['usuario_id']
        conv['outro'] = db.usuarios.find_one({"_id": ObjectId(outro_id)})
        
    return render_template('conversas.html', conversas=conversas_lista)

@chat_bp.route('/chat/<id>')
def chat(id):
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    if not user_id: return redirect(url_for('auth.login'))
    
    # Se eu sou user, o 'id' é do psicólogo. Se eu sou psico, o 'id' é do usuário.
    if user_type == 'user':
        u_id, p_id = user_id, id
    else:
        u_id, p_id = id, user_id

    outro_participante = db.usuarios.find_one({"_id": ObjectId(id)})
    if not outro_participante: return redirect(url_for('user.inicio'))
    
    # Busca ou cria conversa
    conversa = db.conversas.find_one({"usuario_id": u_id, "psico_id": p_id})
    
    if not conversa:
        from models.conversa import Conversa
        result = Conversa.iniciar(u_id, p_id)
        conversa_id = str(result.inserted_id)
    else:
        conversa_id = str(conversa['_id'])
        
    # Busca mensagens anteriores
    mensagens = list(db.mensagens.find({"conversa_id": conversa_id}).sort("data", 1))
    
    return render_template('chat.html', 
                           psico=outro_participante, 
                           mensagens=mensagens, 
                           conversa_id=conversa_id, 
                           user_id=user_id)
