from database.mongodb import db
from datetime import datetime
from bson import ObjectId

class Consulta:
    @staticmethod
    def agendar(usuario_id, psico_id, data_consulta, horario, descricao=""):
        """Agenda uma nova consulta"""
        try:
            # Validar que os dados obrigatórios estão presentes
            if not usuario_id or not psico_id or not data_consulta or not horario:
                raise ValueError("Faltam dados obrigatórios para agendamento")
            
            # Validar tipos de dados
            try:
                usuario_oid = ObjectId(usuario_id) if isinstance(usuario_id, str) else usuario_id
                psico_oid = ObjectId(psico_id) if isinstance(psico_id, str) else psico_id
            except Exception as e:
                raise ValueError(f"IDs de usuário ou psicólogo inválidos: {str(e)}")
            
            consulta = {
                "usuario_id": usuario_oid,
                "psico_id": psico_oid,
                "data_consulta": data_consulta,
                "horario": horario,
                "descricao": descricao or "",
                "status": "agendada",
                "data_agendamento": datetime.now(),
                "notas": "",
                "avaliacao": None,
                "duracao_minutos": 0
            }
            
            resultado = db.consultas.insert_one(consulta)
            print(f"[DEBUG] Consulta inserida com ID: {resultado.inserted_id}")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Erro em Consulta.agendar(): {str(e)}")
            raise

    @staticmethod
    def buscar_por_id(consulta_id):
        """Busca uma consulta pelo ID"""
        try:
            return db.consultas.find_one({"_id": ObjectId(consulta_id)})
        except:
            return None

    @staticmethod
    def listar_por_usuario(usuario_id):
        """Lista todas as consultas de um usuário"""
        try:
            return list(db.consultas.find({"usuario_id": ObjectId(usuario_id)}).sort("data_consulta", -1))
        except:
            return []

    @staticmethod
    def listar_por_psico(psico_id):
        """Lista todas as consultas de um psicólogo"""
        try:
            return list(db.consultas.find({"psico_id": ObjectId(psico_id)}).sort("data_consulta", -1))
        except:
            return []

    @staticmethod
    def listar_proximas(usuario_id, tipo='user'):
        """Lista próximas consultas"""
        try:
            if tipo == 'user':
                return list(db.consultas.find({
                    "usuario_id": ObjectId(usuario_id),
                    "status": {"$in": ["agendada", "confirmada"]}
                }).sort("data_consulta", 1))
            else:
                return list(db.consultas.find({
                    "psico_id": ObjectId(usuario_id),
                    "status": {"$in": ["agendada", "confirmada"]}
                }).sort("data_consulta", 1))
        except:
            return []

    @staticmethod
    def cancelar(consulta_id):
        """Cancela uma consulta"""
        try:
            return db.consultas.update_one(
                {"_id": ObjectId(consulta_id)},
                {"$set": {"status": "cancelada"}}
            )
        except Exception as e:
            print(f"Erro ao cancelar: {str(e)}")
            return None

    @staticmethod
    def confirmar(consulta_id):
        """Confirma uma consulta"""
        try:
            return db.consultas.update_one(
                {"_id": ObjectId(consulta_id)},
                {"$set": {"status": "confirmada"}}
            )
        except Exception as e:
            print(f"Erro ao confirmar: {str(e)}")
            return None
    
    @staticmethod
    def marcar_realizada(consulta_id, duracao_minutos=0):
        """Marca uma consulta como realizada"""
        try:
            return db.consultas.update_one(
                {"_id": ObjectId(consulta_id)},
                {"$set": {"status": "realizada", "duracao_minutos": duracao_minutos}}
            )
        except Exception as e:
            print(f"Erro ao marcar realizada: {str(e)}")
            return None
