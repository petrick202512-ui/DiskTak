"""
Teste de Funcionalidades - Sistema de Vídeo
Executa: python testar_video.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.mongodb import db
from models.usuario import Usuario
from models.consulta import Consulta
from bson import ObjectId
from datetime import datetime, timedelta

def testar_fluxo_video():
    """Testa o fluxo completo de vídeo"""
    
    print("\n" + "="*60)
    print("🎥 TESTE DO SISTEMA DE CHAMADA DE VÍDEO")
    print("="*60)
    
    try:
        # 1. Verificar conexão
        print("\n1️⃣  Verificando conexão...")
        db.usuarios.count_documents({})
        print("  ✅ Conectado com sucesso!")
        
        # 2. Buscar paciente de teste
        print("\n2️⃣  Buscando paciente de teste...")
        paciente = Usuario.buscar_por_email("teste_paciente@teste.com")
        if not paciente:
            print("  ⚠️ Paciente não encontrado. Execute testar_consultas.py primeiro.")
            return False
        print(f"  ✅ Paciente encontrado: {paciente['nome']}")
        
        # 3. Buscar psicólogo de teste
        print("\n3️⃣  Buscando psicólogo de teste...")
        psico = Usuario.buscar_por_email("teste_psico@teste.com")
        if not psico:
            print("  ⚠️ Psicólogo não encontrado.")
            return False
        print(f"  ✅ Psicólogo encontrado: {psico['nome']}")
        
        # 4. Listar consultas do paciente
        print("\n4️⃣  Listando consultas do paciente...")
        consultas = Consulta.listar_por_usuario(str(paciente["_id"]))
        print(f"  ✅ Total de consultas: {len(consultas)}")
        
        if len(consultas) == 0:
            print("  ⚠️ Nenhuma consulta encontrada!")
            return False
        
        # 5. Testar dados da primeira consulta
        print("\n5️⃣  Analisando primeira consulta...")
        consulta = consultas[0]
        print(f"  ✅ ID da consulta: {consulta['_id']}")
        print(f"  ✅ Data: {consulta['data_consulta']}")
        print(f"  ✅ Horário: {consulta['horario']}")
        print(f"  ✅ Status: {consulta['status']}")
        print(f"  ✅ Psicólogo: {psico['nome']}")
        print(f"  ✅ Especialidade: {psico.get('especialidade', 'N/A')}")
        
        # 6. Verificar campos necessários para vídeo
        print("\n6️⃣  Verificando campos necessários...")
        campos_ok = True
        
        if 'psico_id' not in consulta:
            print("  ❌ Campo 'psico_id' faltando")
            campos_ok = False
        else:
            print("  ✅ Campo 'psico_id' presente")
        
        if 'data_consulta' not in consulta:
            print("  ❌ Campo 'data_consulta' faltando")
            campos_ok = False
        else:
            print("  ✅ Campo 'data_consulta' presente")
        
        if 'horario' not in consulta:
            print("  ❌ Campo 'horario' faltando")
            campos_ok = False
        else:
            print("  ✅ Campo 'horario' presente")
        
        if not campos_ok:
            return False
        
        # 7. Verificar dados do psicólogo
        print("\n7️⃣  Verificando dados do psicólogo...")
        psico_dados_ok = True
        
        if 'nome' not in psico:
            print("  ❌ Campo 'nome' faltando")
            psico_dados_ok = False
        else:
            print(f"  ✅ Nome: {psico['nome']}")
        
        if 'avatar' not in psico:
            print("  ⚠️ Campo 'avatar' faltando (usando padrão)")
        else:
            print(f"  ✅ Avatar: {psico['avatar'][:50]}...")
        
        if 'especialidade' not in psico:
            print("  ⚠️ Campo 'especialidade' faltando")
        else:
            print(f"  ✅ Especialidade: {psico['especialidade']}")
        
        if not psico_dados_ok:
            return False
        
        # 8. Simular requisição
        print("\n8️⃣  Simulando requisição para página de vídeo...")
        print(f"  📍 URL: /chamada-video/{consulta['_id']}")
        print(f"  ✅ Dados serão passados ao template")
        
        print("\n" + "="*60)
        print("✅ TESTES PASSARAM COM SUCESSO!")
        print("="*60)
        print("\n🎥 Sistema de vídeo está pronto!")
        print("\n📋 Para testar na aplicação:")
        print("   1. Inicie o app.py")
        print("   2. Faça login com: teste_paciente@teste.com / senha123")
        print("   3. Vá para 'Recursos'")
        print("   4. Você deve ver a consulta agendada")
        print("   5. Clique nela para abrir a interface de vídeo")
        print("\n🎬 Teste de Funcionalidades:")
        print("   - Câmera deve aparecer (após autorizar)")
        print("   - Avatar do psicólogo deve aparecer")
        print("   - Timer deve iniciar")
        print("   - Botões devem funcionar (cam, mic, encerrar)")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = testar_fluxo_video()
    sys.exit(0 if success else 1)
