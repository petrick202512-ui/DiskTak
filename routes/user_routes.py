from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from database.mongodb import db
from datetime import datetime
from bson import ObjectId
from models.consulta import Consulta
from models.desabafo import Desabafo
from models.avaliacao import Avaliacao
from models.usuario import Usuario
from utils.helpers import calcular_media_avaliacoes

user_bp = Blueprint('user', __name__)

# ==================== DASHBOARD ====================

@user_bp.route('/inicio')
def inicio():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    nome = session.get('user_name', 'Amigo(a)')
    
    if session.get('user_type') == 'psico':
        # Para psicólogos: mostrar consultas confirmadas
        proximas_consultas = Consulta.listar_proximas(session['user_id'], 'psico')
        
        for consulta in proximas_consultas:
            try:
                paciente = db.usuarios.find_one({"_id": ObjectId(consulta['usuario_id'])})
                consulta['paciente'] = paciente
            except:
                consulta['paciente'] = None
        
        return render_template('inicio.html', nome=nome, consultas=proximas_consultas, tipo='psico')
    
    return render_template('inicio.html', nome=nome)

# ==================== PSICÓLOGOS ====================

@user_bp.route('/psicologos')
def psicologos():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    psicologos_lista = Usuario.listar_psicologos()
    return render_template('psicologos.html', psicologos=psicologos_lista)

@user_bp.route('/perfil-psicologo/<psico_id>')
def perfil_psicologo(psico_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        psico = db.usuarios.find_one({"_id": ObjectId(psico_id), "tipo": "psico"})
        if not psico:
            flash('Psicólogo não encontrado.', 'error')
            return redirect(url_for('user.psicologos'))
        
        # Buscar avaliações do psicólogo
        avaliacoes = Avaliacao.listar_por_psico(psico_id)
        
        # Calcular média de avaliações
        media_avaliacoes = calcular_media_avaliacoes(avaliacoes) if avaliacoes else 0
        
        return render_template('perfil_psicologo.html', psico=psico, avaliacoes=avaliacoes, media_avaliacoes=media_avaliacoes)
    except Exception as e:
        flash(f'Erro ao carregar perfil: {str(e)}', 'error')
        return redirect(url_for('user.psicologos'))

# ==================== PERFIL ====================

@user_bp.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = db.usuarios.find_one({"_id": ObjectId(user_id)})
    
    if request.method == 'POST':
        try:
            dados_atualizacao = {
                'nome': request.form.get('nome', user['nome']),
                'telefone': request.form.get('telefone', ''),
                'bio': request.form.get('bio', '')
            }
            
            # Se for psicólogo, atualizar dados adicionais
            if session.get('user_type') == 'psico':
                dados_atualizacao.update({
                    'especialidade': request.form.get('especialidade', ''),
                    'crp': request.form.get('crp', ''),
                    'descricao': request.form.get('descricao', '')
                })
            
            Usuario.atualizar_perfil(user_id, dados_atualizacao)
            session['user_name'] = dados_atualizacao['nome']
            
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('user.perfil'))
        except Exception as e:
            flash(f'Erro ao atualizar perfil: {str(e)}', 'error')
    
    user = db.usuarios.find_one({"_id": ObjectId(user_id)})
    return render_template('perfil.html', user=user)

# ==================== CONSULTAS ====================

@user_bp.route('/agendar-consulta/<psico_id>', methods=['GET', 'POST'])
def agendar_consulta(psico_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            data_consulta = request.form.get('data_consulta', '').strip()
            horario = request.form.get('horario', '').strip()
            descricao = request.form.get('descricao', '').strip()
            
            print(f"\n[DEBUG AGENDAR] Iniciando agendamento:")
            print(f"  Usuario: {session['user_id']}")
            print(f"  Psico: {psico_id}")
            print(f"  Data: {data_consulta}")
            print(f"  Horario: {horario}")
            print(f"  Descrição: {descricao}")
            
            # Validar campos obrigatórios
            if not data_consulta:
                flash('❌ Data da consulta é obrigatória.', 'error')
                return redirect(url_for('user.perfil_psicologo', psico_id=psico_id))
            
            if not horario:
                flash('❌ Horário da consulta é obrigatório.', 'error')
                return redirect(url_for('user.perfil_psicologo', psico_id=psico_id))
            
            # Tentar agendar
            try:
                resultado = Consulta.agendar(
                    usuario_id=session['user_id'],
                    psico_id=psico_id,
                    data_consulta=data_consulta,
                    horario=horario,
                    descricao=descricao
                )
                
                print(f"[DEBUG] ✅ Consulta agendada com sucesso! ID: {resultado.inserted_id}")
                flash('✅ Consulta agendada com sucesso!', 'success')
                return redirect(url_for('user.minhas_consultas'))
                
            except ValueError as ve:
                print(f"[ERROR] Erro de validação: {str(ve)}")
                flash(f'❌ Erro na validação: {str(ve)}', 'error')
                return redirect(url_for('user.perfil_psicologo', psico_id=psico_id))
            except Exception as ae:
                print(f"[ERROR] Erro ao inserir consulta: {str(ae)}")
                flash(f'❌ Erro ao agendar consulta: {str(ae)}', 'error')
                return redirect(url_for('user.perfil_psicologo', psico_id=psico_id))
        
        except Exception as e:
            print(f"[ERROR] Erro geral em agendar_consulta: {str(e)}")
            flash(f'❌ Erro inesperado: {str(e)}', 'error')
            return redirect(url_for('user.perfil_psicologo', psico_id=psico_id))
    
    return redirect(url_for('user.perfil_psicologo', psico_id=psico_id))

@user_bp.route('/minhas-consultas')
def minhas_consultas():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    consultas = Consulta.listar_por_usuario(session['user_id'])
    
    # Enriquecer dados com informações do psicólogo
    for consulta in consultas:
        try:
            psico = db.usuarios.find_one({"_id": ObjectId(consulta['psico_id'])})
            consulta['psico'] = psico
        except:
            consulta['psico'] = None
    
    return render_template('minhas_consultas.html', consultas=consultas)

@user_bp.route('/consultas-agendadas')
def consultas_agendadas():
    """Dashboard do psicólogo com suas consultas agendadas"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_type') != 'psico':
        flash('Acesso restrito a psicólogos.', 'error')
        return redirect(url_for('user.inicio'))
    
    consultas = Consulta.listar_por_psico(session['user_id'])
    
    # Enriquecer dados com informações do paciente
    for consulta in consultas:
        try:
            paciente = db.usuarios.find_one({"_id": ObjectId(consulta['usuario_id'])})
            consulta['paciente'] = paciente
        except:
            consulta['paciente'] = None
    
    return render_template('consultas_agendadas.html', consultas=consultas)

@user_bp.route('/cancelar-consulta/<consulta_id>', methods=['POST'])
def cancelar_consulta(consulta_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        Consulta.cancelar(consulta_id)
        flash('Consulta cancelada com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao cancelar: {str(e)}', 'error')
    
    return redirect(url_for('user.minhas_consultas'))

@user_bp.route('/confirmar-consulta/<consulta_id>', methods=['POST'])
def confirmar_consulta(consulta_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        Consulta.confirmar(consulta_id)
        flash('Consulta confirmada.', 'success')
    except Exception as e:
        flash(f'Erro ao confirmar: {str(e)}', 'error')
    
    return redirect(url_for('user.consultas_agendadas'))

# ==================== CHAMADAS DE VÍDEO ====================

@user_bp.route('/chamada-video/<consulta_id>')
def chamada_video(consulta_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        consulta = Consulta.buscar_por_id(consulta_id)
        if not consulta:
            flash('Consulta não encontrada.', 'error')
            return redirect(url_for('user.recursos'))
        
        usuario_tipo = session.get('user_type', 'user')
        
        if usuario_tipo == 'psico':
            paciente = db.usuarios.find_one({"_id": ObjectId(consulta['usuario_id'])})
            return render_template('chamada_video.html', consulta=consulta, psico=paciente, usuario_tipo=usuario_tipo)
        else:
            psico = db.usuarios.find_one({"_id": ObjectId(consulta['psico_id'])})
            return render_template('chamada_video.html', consulta=consulta, psico=psico, usuario_tipo=usuario_tipo)
    except Exception as e:
        flash(f'Erro ao carregar chamada: {str(e)}', 'error')
        return redirect(url_for('user.inicio'))

# ==================== DESABAFOS ====================

@user_bp.route('/desabafar', methods=['GET', 'POST'])
def desabafar():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        texto = request.form.get('texto')
        
        if texto and len(texto) > 0:
            try:
                Desabafo.criar(session['user_id'], texto)
                flash('Seu desabafo foi enviado com sucesso!', 'success')
                return redirect(url_for('user.inicio'))
            except Exception as e:
                flash(f'Erro ao enviar: {str(e)}', 'error')
        else:
            flash('Por favor, escreva algo.', 'error')
    
    return render_template('desabafar.html')

@user_bp.route('/meus-desabafos')
def meus_desabafos():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    desabafos = Desabafo.listar_por_usuario(session['user_id'])
    
    return render_template('meus_desabafos.html', desabafos=desabafos)

# ==================== ADMIN (PSICÓLOGOS) ====================

@user_bp.route('/admin')
def admin():
    if 'user_id' not in session or session.get('user_type') != 'psico':
        flash('Acesso restrito.', 'error')
        return redirect(url_for('user.inicio'))
    
    # Estatísticas
    total_usuarios = db.usuarios.count_documents({"tipo": "user"})
    total_psicos = db.usuarios.count_documents({"tipo": "psico"})
    total_desabafos = db.desabafos.count_documents({})
    
    # Desabafos não respondidos
    desabafos_nao_respondidos = Desabafo.listar_nao_respondidos()
    
    # Próximas consultas
    proximas_consultas = Consulta.listar_proximas(session['user_id'], 'psico')
    
    return render_template('admin.html', 
                           total_users=total_usuarios, 
                           total_psicos=total_psicos, 
                           total_desabafos=total_desabafos,
                           desabafos_nao_respondidos=desabafos_nao_respondidos,
                           proximas_consultas=proximas_consultas)

@user_bp.route('/responder-desabafo/<desabafo_id>', methods=['POST'])
def responder_desabafo(desabafo_id):
    if 'user_id' not in session or session.get('user_type') != 'psico':
        return jsonify({'erro': 'Acesso negado'}), 403
    
    resposta = request.form.get('resposta', '').strip()
    
    if not resposta:
        return jsonify({'erro': 'Resposta vazia'}), 400
    
    try:
        Desabafo.responder(desabafo_id, session['user_id'], resposta)
        return jsonify({'sucesso': True})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ==================== AVALIAÇÕES ====================

@user_bp.route('/avaliar-consulta/<consulta_id>', methods=['POST'])
def avaliar_consulta(consulta_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        consulta = Consulta.buscar_por_id(consulta_id)
        if not consulta or str(consulta['usuario_id']) != session['user_id']:
            flash('Consulta não encontrada.', 'error')
            return redirect(url_for('user.minhas_consultas'))
        
        nota = int(request.form.get('nota', 5))
        comentario = request.form.get('comentario', '')
        
        if nota < 1 or nota > 5:
            nota = 5
        
        Avaliacao.criar(
            usuario_id=session['user_id'],
            psico_id=consulta['psico_id'],
            consulta_id=ObjectId(consulta_id),
            nota=nota,
            comentario=comentario
        )
        
        flash('Obrigado pela avaliação!', 'success')
    except Exception as e:
        flash(f'Erro ao avaliar: {str(e)}', 'error')
    
    return redirect(url_for('user.minhas_consultas'))

# ==================== RECURSOS ====================

@user_bp.route('/recursos')
def recursos():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_type = session.get('user_type', 'user')
    
    # Se for psicólogo, redirecionar para consultas agendadas
    if user_type == 'psico':
        return redirect(url_for('user.consultas_agendadas'))
    
    # Próximas consultas do paciente
    proximas_consultas = Consulta.listar_proximas(session['user_id'], user_type)
    
    for consulta in proximas_consultas:
        try:
            psico = db.usuarios.find_one({"_id": ObjectId(consulta['psico_id'])})
            consulta['psico'] = psico
        except:
            consulta['psico'] = None
    
    return render_template('recursos.html', consultas=proximas_consultas)

@user_bp.route('/exercicio-respiracao')
def exercicio_respiracao():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('exercicio_respiracao.html')

# ==================== MENSAGENS DE USUÁRIOS (PSICÓLOGO) ====================

@user_bp.route('/mensagens-usuarios')
def mensagens_usuarios():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Apenas psicólogos podem acessar
    if session.get('user_type') != 'psico':
        flash('Acesso restrito a psicólogos', 'error')
        return redirect(url_for('user.recursos'))
    
    return render_template('mensagens_usuarios.html')

@user_bp.route('/api/mensagens-usuarios', methods=['GET'])
def api_mensagens_usuarios():
    if 'user_id' not in session or session.get('user_type') != 'psico':
        return jsonify({'erro': 'Acesso negado'}), 403
    
    try:
        # Buscar todos os desabafos
        desabafos = Desabafo.listar_todos()
        
        mensagens = []
        for desabafo in desabafos:
            try:
                usuario = db.usuarios.find_one({"_id": ObjectId(desabafo['usuario_id'])})
                mensagens.append({
                    '_id': str(desabafo['_id']),
                    'usuario_id': str(desabafo['usuario_id']),
                    'usuario_nome': usuario['nome'] if usuario else 'Anônimo',
                    'usuario_email': usuario['email'] if usuario else 'N/A',
                    'texto': desabafo['texto'],
                    'data_criacao': desabafo['data_criacao'].isoformat() if desabafo.get('data_criacao') else '',
                    'status': desabafo.get('status', 'nao_lido'),
                    'resposta': desabafo.get('resposta', '')
                })
            except:
                pass
        
        return jsonify({'mensagens': mensagens})
    
    except Exception as e:
        print(f"Erro ao listar mensagens: {str(e)}")
        return jsonify({'erro': str(e)}), 500

@user_bp.route('/api/responder-mensagem', methods=['POST'])
def api_responder_mensagem():
    if 'user_id' not in session or session.get('user_type') != 'psico':
        return jsonify({'erro': 'Acesso negado'}), 403
    
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        resposta = data.get('resposta', '')
        
        if not message_id or not resposta:
            return jsonify({'erro': 'Dados incompletos'}), 400
        
        # Atualizar o desabafo com a resposta
        Desabafo.responder(message_id, session['user_id'], resposta)
        
        # Marcar como lido
        Desabafo.marcar_como_lido(message_id)
        
        return jsonify({'sucesso': True, 'mensagem': 'Resposta enviada com sucesso'})
    
    except Exception as e:
        print(f"Erro ao responder: {str(e)}")
        return jsonify({'erro': str(e)}), 500

# ==================== AÇÕES DE CONSULTAS ====================

@user_bp.route('/api/confirmar-consulta/<consulta_id>', methods=['POST'])
def api_confirmar_consulta(consulta_id):
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401
    
    try:
        consulta = Consulta.buscar_por_id(consulta_id)
        
        if not consulta:
            return jsonify({'erro': 'Consulta não encontrada'}), 404
        
        # Verificar se o usuário é o dono da consulta
        if str(consulta['usuario_id']) != session['user_id']:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        # Confirmar consulta
        Consulta.confirmar(consulta_id)
        
        return jsonify({'sucesso': True, 'mensagem': 'Consulta confirmada com sucesso'})
    
    except Exception as e:
        print(f"Erro ao confirmar: {str(e)}")
        return jsonify({'erro': str(e)}), 500

@user_bp.route('/api/cancelar-consulta/<consulta_id>', methods=['POST'])
def api_cancelar_consulta(consulta_id):
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401
    
    try:
        consulta = Consulta.buscar_por_id(consulta_id)
        
        if not consulta:
            return jsonify({'erro': 'Consulta não encontrada'}), 404
        
        # Verificar se o usuário é o dono da consulta
        if str(consulta['usuario_id']) != session['user_id']:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        # Cancelar consulta
        Consulta.cancelar(consulta_id)
        
        return jsonify({'sucesso': True, 'mensagem': 'Consulta cancelada'})
    
    except Exception as e:
        print(f"Erro ao cancelar: {str(e)}")
        return jsonify({'erro': str(e)}), 500

# ==================== AVALIAÇÕES ====================

@user_bp.route('/api/avaliar-psico/<psico_id>', methods=['POST'])
def api_avaliar_psico(psico_id):
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        nota = data.get('nota')
        comentario = data.get('comentario', '')
        
        # Validar nota
        if not nota or nota < 1 or nota > 5:
            return jsonify({'erro': 'Nota deve ser entre 1 e 5'}), 400
        
        # Verificar se psicólogo existe
        psico = db.usuarios.find_one({"_id": ObjectId(psico_id), "tipo": "psico"})
        if not psico:
            return jsonify({'erro': 'Psicólogo não encontrado'}), 404
        
        # Verificar se já existe avaliação do mesmo usuário
        avaliacao_existente = db.avaliacoes.find_one({
            "usuario_id": ObjectId(session['user_id']),
            "psico_id": ObjectId(psico_id)
        })
        
        if avaliacao_existente:
            # Atualizar avaliação existente
            db.avaliacoes.update_one(
                {"_id": avaliacao_existente["_id"]},
                {"$set": {
                    "nota": nota,
                    "comentario": comentario,
                    "data_criacao": datetime.now()
                }}
            )
            print(f"[DEBUG] Avaliação atualizada: {avaliacao_existente['_id']}")
        else:
            # Criar nova avaliação
            avaliacao = {
                "usuario_id": ObjectId(session['user_id']),
                "psico_id": ObjectId(psico_id),
                "nota": nota,
                "comentario": comentario,
                "data_criacao": datetime.now()
            }
            resultado = db.avaliacoes.insert_one(avaliacao)
            print(f"[DEBUG] Avaliação criada: {resultado.inserted_id}")
        
        # Atualizar nota média do psicólogo
        Avaliacao.atualizar_nota_media_psicologo(psico_id)
        
        return jsonify({'sucesso': True, 'mensagem': 'Avaliação salva com sucesso'})
    
    except Exception as e:
        print(f"[ERROR] Erro ao avaliar: {str(e)}")
        return jsonify({'erro': str(e)}), 500
