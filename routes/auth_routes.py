from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from models.usuario import Usuario
from database.mongodb import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        user = Usuario.buscar_por_email(email)
        if user and Usuario.verificar_senha(user['senha'], senha):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['nome']
            session['user_type'] = user['tipo']
            return redirect(url_for('user.inicio'))
        
        flash('E-mail ou senha incorretos.', 'error')
    return render_template('login.html')

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        tipo = request.form.get('tipo', 'user').strip()
        
        # Validação básica
        if not nome or not email or not senha:
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('cadastro.html')
        
        if Usuario.buscar_por_email(email):
            flash('Este e-mail já está cadastrado.', 'error')
            return render_template('cadastro.html')
        
        try:
            # Criar o usuário
            usuario = Usuario.criar(nome, email, senha, tipo)
            user_id = str(usuario.inserted_id)
            
            # Se for psicólogo, atualizar campos adicionais
            if tipo == 'psico':
                crp = request.form.get('crp', '').strip()
                especialidade = request.form.get('especialidade', '').strip()
                descricao = request.form.get('descricao', '').strip()
                
                # Validar se os campos foram preenchidos
                if not crp or not especialidade or not descricao:
                    flash('Por favor, preencha todos os campos do psicólogo.', 'error')
                    # Deletar usuário criado se validação falhar
                    db.usuarios.delete_one({"_id": usuario.inserted_id})
                    return render_template('cadastro.html')
                
                dados_psico = {
                    'crp': crp,
                    'especialidade': especialidade,
                    'descricao': descricao
                }
                
                resultado = Usuario.atualizar_perfil(user_id, dados_psico)
                if not resultado or resultado.modified_count == 0:
                    flash('Erro ao salvar dados profissionais. Tente novamente.', 'error')
                    return render_template('cadastro.html')
            
            # Se for paciente, atualizar telefone se fornecido
            if tipo == 'user':
                telefone = request.form.get('telefone', '').strip()
                if telefone:
                    Usuario.atualizar_perfil(user_id, {'telefone': telefone})
            
            flash('✅ Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            flash(f'Erro ao criar conta: {str(e)}', 'error')
            return render_template('cadastro.html')
            
    return render_template('cadastro.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('splash'))
