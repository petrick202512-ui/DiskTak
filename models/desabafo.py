from database.mongodb import db
from datetime import datetime
from bson import ObjectId

class Desabafo:
    @staticmethod
    def criar(usuario_id, texto):
        """Cria um novo desabafo"""
        desabafo = {
            "usuario_id": ObjectId(usuario_id),
            "texto": texto,
            "data_criacao": datetime.now(),
            "status": "nao_lido",  # nao_lido, lido, respondido
            "resposta": "",
            "psico_id": None,
            "curtidas": []
        }
        return db.desabafos.insert_one(desabafo)

    @staticmethod
    def buscar_por_id(desabafo_id):
        """Busca um desabafo pelo ID"""
        try:
            return db.desabafos.find_one({"_id": ObjectId(desabafo_id)})
        except:
            return None

    @staticmethod
    def listar_todos():
        """Lista todos os desabafos"""
        try:
            return list(db.desabafos.find().sort("data_criacao", -1))
        except:
            return []

    @staticmethod
    def listar_por_usuario(usuario_id):
        """Lista desabafos de um usuário"""
        try:
            return list(db.desabafos.find({"usuario_id": ObjectId(usuario_id)}).sort("data_criacao", -1))
        except:
            return []

    @staticmethod
    def listar_nao_respondidos():
        """Lista desabafos que não foram respondidos"""
        try:
            return list(db.desabafos.find({"status": {"$in": ["nao_lido", "lido"]}}).sort("data_criacao", 1))
        except:
            return []

    @staticmethod
    def responder(desabafo_id, psico_id, resposta):
        """Adiciona uma resposta a um desabafo"""
        try:
            return db.desabafos.update_one(
                {"_id": ObjectId(desabafo_id)},
                {"$set": {"resposta": resposta, "psico_id": ObjectId(psico_id), "status": "respondido"}}
            )
        except Exception as e:
            print(f"Erro ao responder: {str(e)}")
            return None

    @staticmethod
    def marcar_como_lido(desabafo_id):
        """Marca um desabafo como lido"""
        try:
            return db.desabafos.update_one(
                {"_id": ObjectId(desabafo_id)},
                {"$set": {"status": "lido"}}
            )
        except Exception as e:
            print(f"Erro ao marcar como lido: {str(e)}")
            return None
