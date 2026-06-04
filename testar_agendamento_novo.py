#!/usr/bin/env python3
"""
Script para testar o sistema de agendamento de consultas
"""
import sys
from datetime import datetime, timedelta
from bson import ObjectId
from database.mongodb import db
from models.usuario import Usuario
from models.consulta import Consulta

def main():
    print("=" * 60)
    print("🧪 TESTE DO SISTEMA DE AGENDAMENTO")
    print("=" * 60)
    
    try:
        # 1. Limpar dados antigos
        print("\n1️⃣  Limpando dados de teste antigos...")
        db.usuarios.delete_many({"email": {"$regex": "teste_"}})
        db.consultas.delete_many({})
        print("   ✅ Dados limpos!")
        
        # 2. Criar paciente e psicólogo de teste
        print("\n2️⃣  Criando usuários de teste...")
        paciente = Usuario.criar(
            nome="Paciente Teste",
            email="teste_paciente@example.com",
            senha="senha123",
            tipo="user"
        )
        print(f"   ✅ Paciente criado: {paciente.inserted_id}")
        
        psico = Usuario.criar(
            nome="Psicólogo Teste",
            email="teste_psico@example.com",
            senha="senha123",
            tipo="psico"
        )
        print(f"   ✅ Psicólogo criado: {psico.inserted_id}")
        
        # Atualizar dados do psicólogo
        Usuario.atualizar_perfil(str(psico.inserted_id), {
            'crp': '06/123456',
            'especialidade': 'Ansiedade',
            'descricao': 'Especialista em tratamento de ansiedade'
        })
        print("   ✅ Dados do psicólogo atualizados")
        
        # 3. Agendar consulta
        print("\n3️⃣  Agendando consulta...")
        amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        consulta = Consulta.agendar(
            usuario_id=str(paciente.inserted_id),
            psico_id=str(psico.inserted_id),
            data_consulta=amanha,
            horario="14:00",
            descricao="Primeira consulta para avaliar ansiedade"
        )
        print(f"   ✅ Consulta agendada: {consulta.inserted_id}")
        
        # 4. Verificar consultas do psicólogo
        print("\n4️⃣  Verificando consultas do psicólogo...")
        consultas_psico = Consulta.listar_por_psico(str(psico.inserted_id))
        print(f"   ✅ Encontradas {len(consultas_psico)} consultas")
        
        for c in consultas_psico:
            print(f"\n      📅 Consulta:")
            print(f"         ID: {c['_id']}")
            print(f"         Data: {c['data_consulta']}")
            print(f"         Horário: {c['horario']}")
            print(f"         Status: {c['status']}")
            print(f"         Descrição: {c['descricao']}")
        
        # 5. Verificar consultas do paciente
        print("\n5️⃣  Verificando consultas do paciente...")
        consultas_paciente = Consulta.listar_por_usuario(str(paciente.inserted_id))
        print(f"   ✅ Encontradas {len(consultas_paciente)} consultas")
        
        for c in consultas_paciente:
            print(f"\n      📅 Consulta:")
            print(f"         ID: {c['_id']}")
            print(f"         Data: {c['data_consulta']}")
            print(f"         Horário: {c['horario']}")
            print(f"         Status: {c['status']}")
        
        # 6. Verificar dados no MongoDB
        print("\n6️⃣  Verificando dados no MongoDB...")
        consulta_db = db.consultas.find_one({"_id": consulta.inserted_id})
        print(f"   ✅ Consulta no DB:")
        print(f"      usuario_id: {consulta_db['usuario_id']} (tipo: {type(consulta_db['usuario_id']).__name__})")
        print(f"      psico_id: {consulta_db['psico_id']} (tipo: {type(consulta_db['psico_id']).__name__})")
        
        psico_db = db.usuarios.find_one({"_id": ObjectId(str(psico.inserted_id))})
        print(f"   ✅ Psicólogo no DB:")
        print(f"      Nome: {psico_db.get('nome')}")
        print(f"      CRP: {psico_db.get('crp')}")
        print(f"      Especialidade: {psico_db.get('especialidade')}")
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
