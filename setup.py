"""
Script de Setup Inicial do Disck Talk
Executa: python setup.py
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.mongodb import db
from utils.seed_db import popular_banco
from models.usuario import Usuario

def verificar_conexao():
    """Verifica se consegue conectar ao MongoDB"""
    try:
        # Tentar fazer uma operação simples
        db.usuarios.count_documents({})
        print("✅ Conexão com MongoDB estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com MongoDB: {str(e)}")
        print("Certifique-se de que o MongoDB está rodando e MONGO_URI está configurada no .env")
        return False

def criar_indices():
    """Cria índices no banco para melhorar performance"""
    try:
        db.usuarios.create_index([("email", 1)], unique=True)
        db.consultas.create_index([("usuario_id", 1)])
        db.consultas.create_index([("psico_id", 1)])
        db.consultas.create_index([("data_consulta", 1)])
        db.avaliacoes.create_index([("psico_id", 1)])
        print("✅ Índices criados com sucesso!")
        return True
    except Exception as e:
        print(f"⚠️ Aviso ao criar índices: {str(e)}")
        return True

def main():
    print("\n" + "="*60)
    print("🚀 SETUP INICIAL - DISCK TALK")
    print("="*60 + "\n")
    
    # 1. Verificar conexão
    print("1️⃣  Verificando conexão com MongoDB...")
    if not verificar_conexao():
        sys.exit(1)
    
    # 2. Criar índices
    print("\n2️⃣  Criando índices no banco de dados...")
    criar_indices()
    
    # 3. Popular banco com dados iniciais
    print("\n3️⃣  Populando banco com psicólogos iniciais...")
    popular_banco()
    
    # 4. Verificar usuários
    print("\n4️⃣  Verificando dados no banco...")
    total_usuarios = db.usuarios.count_documents({})
    total_psicos = db.usuarios.count_documents({"tipo": "psico"})
    print(f"   📊 Total de usuários: {total_usuarios}")
    print(f"   👨‍⚕️  Total de psicólogos: {total_psicos}")
    
    print("\n" + "="*60)
    print("✅ SETUP CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print("\n🎯 Próximos passos:")
    print("   1. Instale as dependências: pip install -r requirements.txt")
    print("   2. Execute o app: python app.py")
    print("   3. Acesse: http://localhost:5000")
    print("\n💡 Dados de teste:")
    print("   - Email: ana@exemplo.com")
    print("   - Senha: 123456")
    print("   - Tipo: Psicólogo")
    print("\n")

if __name__ == "__main__":
    main()
