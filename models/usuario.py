from database.mongodb import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId

class Usuario:
    @staticmethod
    def criar(nome, email, senha, tipo='user'):
        senha_hash = generate_password_hash(senha)
        usuario = {
            "nome": nome,
            "email": email,
            "senha": senha_hash,
            "tipo": tipo,
            "status": "online",
            "avatar": f"https://i.pravatar.cc/150?u={email}",
            "data_cadastro": datetime.now(),
            "telefone": "",
            "bio": "",
            "ultima_atividade": datetime.now()
        }
        
        # Campos adicionais para psicólogos
        if tipo == 'psico':
            usuario.update({
                "especialidade": "",
                "crp": "",
                "descricao": "",
                "nota_media": 5.0,
                "total_avaliacoes": 0,
                "total_atendimentos": 0,
                "disponivel": True
            })
        
        return db.usuarios.insert_one(usuario)

    @staticmethod
    def buscar_por_email(email):
        return db.usuarios.find_one({"email": email})

    @staticmethod
    def buscar_por_id(usuario_id):
        try:
            return db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        except:
            return None

    @staticmethod
    def verificar_senha(senha_hash, senha_plana):
        return check_password_hash(senha_hash, senha_plana)

    @staticmethod
    def atualizar_perfil(usuario_id, dados):
        """Atualiza o perfil de um usuário"""
        try:
            dados['ultima_atividade'] = datetime.now()
            return db.usuarios.update_one(
                {"_id": ObjectId(usuario_id)},
                {"$set": dados}
            )
        except Exception as e:
            print(f"Erro ao atualizar perfil: {str(e)}")
            return None

    @staticmethod
    def atualizar_status(usuario_id, status):
        """Atualiza o status do usuário (online/offline)"""
        try:
            return db.usuarios.update_one(
                {"_id": ObjectId(usuario_id)},
                {"$set": {"status": status, "ultima_atividade": datetime.now()}}
            )
        except Exception as e:
            print(f"Erro ao atualizar status: {str(e)}")
            return None

    @staticmethod
    def listar_psicologos():
        """Lista todos os psicólogos cadastrados"""
        return list(db.usuarios.find({"tipo": "psico"}).sort("nota_media", -1))

    @staticmethod
    def buscar_psicologos_por_especialidade(especialidade):
        """Busca psicólogos por especialidade"""
        return list(db.usuarios.find({
            "tipo": "psico",
            "especialidade": {"$regex": especialidade, "$options": "i"}
        }).sort("nota_media", -1))
    
    @staticmethod
    def buscar_psicologos_disponiveis():
        """Busca psicólogos disponíveis online"""
        return list(db.usuarios.find({
            "tipo": "psico",
            "disponivel": True,
            "status": "online"
        }).sort("nota_media", -1))
