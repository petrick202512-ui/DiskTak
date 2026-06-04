from models.usuario import Usuario
from database.mongodb import db
from datetime import datetime

def popular_banco():
    if db.usuarios.count_documents({"tipo": "psico"}) == 0:
        print("Populando banco com psicólogos iniciais...")
        psicologos = [
            {
                "nome": "Dra. Ana Paula",
                "email": "ana@exemplo.com",
                "especialidade": "Psicologia Clínica",
                "senha": "123456",
                "crp": "06/123456",
                "descricao": "Especialista em Psicologia Clínica com 10 anos de experiência. Atendo pacientes com ansiedade, depressão e traumas. Acredito na abordagem humanizada e no acolhimento genuíno.",
                "telefone": "(11) 99999-0001"
            },
            {
                "nome": "Dr. Marcos Silva",
                "email": "marcos@exemplo.com",
                "especialidade": "Acolhimento e Luto",
                "senha": "123456",
                "crp": "06/234567",
                "descricao": "Psicólogo especializado em processos de luto, separação e perdas. Oferço espaço seguro para processar emoções difíceis e encontrar novos significados.",
                "telefone": "(11) 99999-0002"
            },
            {
                "nome": "Dra. Júlia Costa",
                "email": "julia@exemplo.com",
                "especialidade": "Ansiedade e Stress",
                "senha": "123456",
                "crp": "06/345678",
                "descricao": "Especialista em Transtornos de Ansiedade e Manejo de Stress. Trabalho com técnicas cognitivo-comportamentais e práticas de mindfulness.",
                "telefone": "(11) 99999-0003"
            },
            {
                "nome": "Dr. Felipe Oliveira",
                "email": "felipe@exemplo.com",
                "especialidade": "Relacionamentos e Autoestima",
                "senha": "123456",
                "crp": "06/456789",
                "descricao": "Acompanho pacientes em questões de relacionamentos, autoestima e identidade. Meu foco é ajudar você a construir relacionamentos saudáveis.",
                "telefone": "(11) 99999-0004"
            },
            {
                "nome": "Dra. Carla Santos",
                "email": "carla@exemplo.com",
                "especialidade": "Saúde Mental e Bem-estar",
                "senha": "123456",
                "crp": "06/567890",
                "descricao": "Psicóloga holística focada em bem-estar integral. Integro práticas de psicologia com atenção plena e desenvolvimento pessoal.",
                "telefone": "(11) 99999-0005"
            }
        ]
        
        for psico in psicologos:
            Usuario.criar(psico["nome"], psico["email"], psico["senha"], "psico")
            
            # Atualizar com informações adicionais
            db.usuarios.update_one(
                {"email": psico["email"]},
                {
                    "$set": {
                        "especialidade": psico["especialidade"],
                        "crp": psico["crp"],
                        "descricao": psico["descricao"],
                        "telefone": psico["telefone"],
                        "data_cadastro": datetime.now(),
                        "status": "online",
                        "nota": 4.8 + (hash(psico["email"]) % 2) * 0.1,
                        "conversoes": 5 + (hash(psico["email"]) % 10)
                    }
                }
            )
            print(f"✅ Psicólogo(a) {psico['nome']} criado(a) com sucesso!")
        
        print("\n✅ Banco populado com sucesso!")
    else:
        print("Psicólogos já existem no banco!")

if __name__ == "__main__":
    popular_banco()
