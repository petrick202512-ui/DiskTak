from database.mongodb import db
from datetime import datetime

class Conversa:
    @staticmethod
    def iniciar(usuario_id, psico_id):
        conversa = {
            "usuario_id": usuario_id,
            "psico_id": psico_id,
            "data_inicio": datetime.now(),
            "status": "ativa",
            "ultima_mensagem": ""
        }
        return db.conversas.insert_one(conversa)

    @staticmethod
    def salvar_mensagem(conversa_id, remetente_id, texto):
        mensagem = {
            "conversa_id": conversa_id,
            "remetente_id": remetente_id,
            "texto": texto,
            "data": datetime.now()
        }
        # Atualiza a última mensagem na conversa pai
        db.conversas.update_one(
            {"_id": conversa_id},
            {"$set": {"ultima_mensagem": texto}}
        )
        return db.mensagens.insert_one(mensagem)
