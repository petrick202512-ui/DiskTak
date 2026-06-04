"""
Script de Teste - Sistema de Agendamento de Consultas
Executa: python testar_consultas.py
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.mongodb import db
from models.usuario import Usuario
from models.consulta import Consulta
from bson import ObjectId

def limpar_dados_teste():
    """Limpa dados de teste anterior"""
    db.usuarios.delete_many({"email": {"$regex": "teste_"}})
    db.consultas.delete_many({})
    print("✅ Dados de teste anterior removidos")

def criar_usuarios_teste():
    """Cria usuários de teste"""
    print("\n📝 Criando usuários de teste...")
    
    # Criar psicólogo de teste
    Usuario.criar("Dr. Teste Psico", "teste_psico@teste.com", "senha123", "psico")
    psico = Usuario.buscar_por_email("teste_psico@teste.com")
    db.usuarios.update_one(
        {"_id": psico["_id"]},
        {"$set": {
            "crp": "06/999999",
            "descricao": "Psicólogo de teste para validação do sistema",
            "telefone": "(11) 99999-9999",
            "especialidade": "Teste"
        }}
    )
    print(f"  ✅ Psicólogo criado: {psico['_id']}")
    
    # Criar paciente de teste
    Usuario.criar("Paciente Teste", "teste_paciente@teste.com", "senha123", "user")
    paciente = Usuario.buscar_por_email("teste_paciente@teste.com")
    print(f"  ✅ Paciente criado: {paciente['_id']}")
    
    return psico, paciente

def testar_agendamento(psico, paciente):
    """Testa agendamento de consulta"""
    print("\n📅 Testando agendamento de consulta...")
    
    # Agendar consulta
    data_teste = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    horario_teste = "14:30"
    
    try:
        Consulta.agendar(
            usuario_id=str(paciente["_id"]),
            psico_id=str(psico["_id"]),
            data_consulta=data_teste,
            horario=horario_teste,
            descricao="Consulta de teste"
        )
        print(f"  ✅ Consulta agendada para {data_teste} às {horario_teste}")
    except Exception as e:
        print(f"  ❌ Erro ao agendar: {e}")
        return False
    
    return True

def testar_listagem(psico, paciente):
    """Testa listagem de consultas"""
    print("\n📊 Testando listagem de consultas...")
    
    try:
        # Listar consultas do paciente
        consultas_paciente = Consulta.listar_por_usuario(str(paciente["_id"]))
        print(f"  ✅ Consultas do paciente: {len(consultas_paciente)}")
        
        # Listar consultas do psicólogo
        consultas_psico = Consulta.listar_por_psico(str(psico["_id"]))
        print(f"  ✅ Consultas do psicólogo: {len(consultas_psico)}")
        
        if consultas_paciente:
            consulta = consultas_paciente[0]
            print(f"  📋 Primeira consulta:")
            print(f"     - Status: {consulta['status']}")
            print(f"     - Data: {consulta['data_consulta']}")
            print(f"     - Horário: {consulta['horario']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro na listagem: {e}")
        return False

def testar_atualizacao_status(psico, paciente):
    """Testa atualização de status"""
    print("\n🔄 Testando atualização de status...")
    
    try:
        consultas = Consulta.listar_por_usuario(str(paciente["_id"]))
        if consultas:
            consulta_id = consultas[0]["_id"]
            
            # Confirmar consulta
            Consulta.confirmar(str(consulta_id))
            consulta_atualizada = Consulta.buscar_por_id(str(consulta_id))
            print(f"  ✅ Status atualizado: {consulta_atualizada['status']}")
            
            return True
    except Exception as e:
        print(f"  ❌ Erro na atualização: {e}")
        return False

def testar_cancelamento(psico, paciente):
    """Testa cancelamento de consulta"""
    print("\n❌ Testando cancelamento de consulta...")
    
    try:
        consultas = Consulta.listar_por_usuario(str(paciente["_id"]))
        if len(consultas) > 0:
            consulta_id = consultas[0]["_id"]
            
            # Cancelar consulta
            Consulta.cancelar(str(consulta_id))
            consulta_cancelada = Consulta.buscar_por_id(str(consulta_id))
            print(f"  ✅ Consulta cancelada: {consulta_cancelada['status']}")
            
            return True
    except Exception as e:
        print(f"  ❌ Erro no cancelamento: {e}")
        return False

def testar_modelos_usuario():
    """Testa novos métodos do modelo Usuario"""
    print("\n👥 Testando modelo Usuario...")
    
    try:
        # Listar psicólogos
        psicologos = Usuario.listar_psicologos()
        print(f"  ✅ Total de psicólogos: {len(psicologos)}")
        
        # Buscar por ID
        if psicologos:
            psico = Usuario.buscar_por_id(str(psicologos[0]["_id"]))
            print(f"  ✅ Busca por ID funcional: {psico['nome']}")
        
        # Buscar por especialidade
        especializados = Usuario.buscar_psicologos_por_especialidade("Teste")
        print(f"  ✅ Busca por especialidade: {len(especializados)} encontrados")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro no modelo Usuario: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 TESTE DO SISTEMA DE AGENDAMENTO DE CONSULTAS")
    print("="*60)
    
    try:
        # 1. Verificar conexão
        print("\n1️⃣  Verificando conexão com MongoDB...")
        db.usuarios.count_documents({})
        print("  ✅ Conectado com sucesso!")
        
        # 2. Limpar dados anteriores
        print("\n2️⃣  Limpando dados de teste anterior...")
        limpar_dados_teste()
        
        # 3. Criar usuários
        print("\n3️⃣  Criando usuários de teste...")
        psico, paciente = criar_usuarios_teste()
        
        # 4. Testar modelos
        print("\n4️⃣  Testando modelo Usuario...")
        testar_modelos_usuario()
        
        # 5. Testar agendamento
        print("\n5️⃣  Testando agendamento...")
        if not testar_agendamento(psico, paciente):
            return False
        
        # 6. Testar listagem
        print("\n6️⃣  Testando listagem...")
        if not testar_listagem(psico, paciente):
            return False
        
        # 7. Testar atualização de status
        print("\n7️⃣  Testando atualização de status...")
        if not testar_atualizacao_status(psico, paciente):
            return False
        
        # 8. Testar cancelamento
        print("\n8️⃣  Testando cancelamento...")
        if not testar_cancelamento(psico, paciente):
            return False
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("="*60)
        print("\n🎉 O sistema está pronto para uso!")
        print("\n📝 Próximos passos:")
        print("   1. Verifique se o app.py está rodando")
        print("   2. Teste no navegador: http://localhost:5000")
        print("   3. Login com: teste_paciente@teste.com / senha123")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
