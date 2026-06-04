from database.mongodb import db
from datetime import datetime
from bson import ObjectId

class Avaliacao:
    @staticmethod
    def criar(usuario_id, psico_id, consulta_id, nota, comentario=""):
        """Cria uma avaliação de consulta"""
        avaliacao = {
            "usuario_id": ObjectId(usuario_id),
            "psico_id": ObjectId(psico_id),
            "consulta_id": ObjectId(consulta_id),
            "nota": nota,  # 1 a 5
            "comentario": comentario,
            "data_criacao": datetime.now()
        }
        result = db.avaliacoes.insert_one(avaliacao)
        
        # Atualizar nota média do psicólogo
        Avaliacao.atualizar_nota_media_psicologo(psico_id)
        
        return result

    @staticmethod
    def buscar_por_id(avaliacao_id):
        """Busca uma avaliação pelo ID"""
        try:
            return db.avaliacoes.find_one({"_id": ObjectId(avaliacao_id)})
        except:
            return None

    @staticmethod
    def listar_por_psico(psico_id):
        """Lista todas as avaliações de um psicólogo"""
        try:
            return list(db.avaliacoes.find({"psico_id": ObjectId(psico_id)}).sort("data_criacao", -1))
        except:
            return []

    @staticmethod
    def atualizar_nota_media_psicologo(psico_id):
        """Atualiza a nota média de um psicólogo"""
        try:
            avaliacoes = list(db.avaliacoes.find({"psico_id": ObjectId(psico_id)}))
            if avaliacoes:
                nota_media = sum([a["nota"] for a in avaliacoes]) / len(avaliacoes)
                total_avaliacoes = len(avaliacoes)
                
                db.usuarios.update_one(
                    {"_id": ObjectId(psico_id)},
                    {"$set": {
                        "nota_media": round(nota_media, 1),
                        "total_avaliacoes": total_avaliacoes
                    }}
                )
        except Exception as e:
            print(f"Erro ao atualizar nota média: {str(e)}")

    @staticmethod
    def buscar_por_usuario_e_psico(usuario_id, psico_id):
        """Busca avaliação de um usuário para um psicólogo"""
        try:
            return db.avaliacoes.find_one({
                "usuario_id": ObjectId(usuario_id),
                "psico_id": ObjectId(psico_id)
            })
        except:
            return None
