from database.mongodb import db
from datetime import datetime
from bson import ObjectId

class Chamada:
    """Modelo para gerenciar chamadas de vídeo"""
    
    @staticmethod
    def registrar_chamada(consulta_id, paciente_id, psico_id):
        """Registra uma chamada iniciada"""
        chamada = {
            "consulta_id": ObjectId(consulta_id),
            "paciente_id": ObjectId(paciente_id),
            "psico_id": ObjectId(psico_id),
            "status": "pendente",  # pendente, aceita, rejeitada, finalizada
            "data_inicio": datetime.now(),
            "data_aceite": None,
            "data_finalizacao": None
        }
        return db.chamadas.insert_one(chamada)

    @staticmethod
    def buscar_chamada(chamada_id):
        """Busca uma chamada pelo ID"""
        return db.chamadas.find_one({"_id": ObjectId(chamada_id)})

    @staticmethod
    def aceitar_chamada(chamada_id):
        """Marca a chamada como aceita"""
        return db.chamadas.update_one(
            {"_id": ObjectId(chamada_id)},
            {
                "$set": {
                    "status": "aceita",
                    "data_aceite": datetime.now()
                }
            }
        )

    @staticmethod
    def rejeitar_chamada(chamada_id, motivo=""):
        """Marca a chamada como rejeitada"""
        return db.chamadas.update_one(
            {"_id": ObjectId(chamada_id)},
            {
                "$set": {
                    "status": "rejeitada",
                    "motivo": motivo,
                    "data_finalizacao": datetime.now()
                }
            }
        )

    @staticmethod
    def finalizar_chamada(chamada_id, duracao=0):
        """Finaliza a chamada"""
        return db.chamadas.update_one(
            {"_id": ObjectId(chamada_id)},
            {
                "$set": {
                    "status": "finalizada",
                    "duracao_segundos": duracao,
                    "data_finalizacao": datetime.now()
                }
            }
        )

    @staticmethod
    def listar_chamadas_pendentes(psico_id):
        """Lista chamadas pendentes para um psicólogo"""
        return list(db.chamadas.find({
            "psico_id": ObjectId(psico_id),
            "status": "pendente"
        }).sort("data_inicio", -1))
