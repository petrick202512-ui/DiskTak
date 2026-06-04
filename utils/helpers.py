from datetime import datetime, timedelta
import re
from bson import ObjectId

# ==================== FORMATAÇÃO ====================

def formatar_data(data):
    """Formata datas para exibição amigável no chat."""
    if not data:
        return ""
    
    if isinstance(data, str):
        return data
    
    agora = datetime.now()
    
    if data.date() == agora.date():
        return data.strftime("%H:%M")
    elif data.date() == (agora - timedelta(days=1)).date():
        return "Ontem às " + data.strftime("%H:%M")
    else:
        return data.strftime("%d/%m/%Y")

def formatar_data_completa(data):
    """Formata data completa."""
    if not data:
        return ""
    
    if isinstance(data, str):
        return data
    
    meses = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    dia = data.day
    mes = meses.get(data.month, '')
    ano = data.year
    
    return f"{dia} de {mes} de {ano}"

def extrair_primeiro_nome(nome_completo):
    """Retorna apenas o primeiro nome para saudações."""
    return nome_completo.split()[0] if nome_completo else "Amigo(a)"

def formatar_telefone(telefone):
    """Formata número de telefone."""
    if not telefone:
        return ""
    
    telefone = re.sub(r'\D', '', telefone)
    
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    else:
        return telefone

# ==================== VALIDAÇÃO ====================

def validar_email(email):
    """Valida formato de email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_senha(senha):
    """Valida força da senha."""
    if len(senha) < 6:
        return False, "Senha deve ter no mínimo 6 caracteres"
    
    if not any(c.isupper() for c in senha):
        return False, "Senha deve conter pelo menos uma letra maiúscula"
    
    return True, "Senha válida"

def sanitizar_texto(texto):
    """Remove caracteres perigosos do texto."""
    if not texto:
        return ""
    
    # Remove tags HTML
    texto = re.sub(r'<[^>]+>', '', texto)
    
    # Remove caracteres especiais perigosos
    texto = texto.replace('<', '').replace('>', '')
    
    return texto.strip()

# ==================== CONVERSÃO ====================

def object_id_para_string(obj_id):
    """Converte ObjectId para string."""
    if isinstance(obj_id, ObjectId):
        return str(obj_id)
    return obj_id

def string_para_object_id(string_id):
    """Converte string para ObjectId."""
    try:
        return ObjectId(string_id)
    except:
        return None

# ==================== PAGINAÇÃO ====================

def calcular_paginacao(total, por_pagina, pagina_atual):
    """Calcula informações de paginação."""
    total_paginas = (total + por_pagina - 1) // por_pagina
    offset = (pagina_atual - 1) * por_pagina
    
    return {
        'total': total,
        'por_pagina': por_pagina,
        'pagina_atual': pagina_atual,
        'total_paginas': total_paginas,
        'offset': offset,
        'proxima_pagina': pagina_atual + 1 if pagina_atual < total_paginas else None,
        'pagina_anterior': pagina_atual - 1 if pagina_atual > 1 else None
    }

# ==================== UTILIDADES ====================

def gerar_avatar_url(email):
    """Gera URL de avatar baseado no email."""
    return f"https://i.pravatar.cc/150?u={email}"

def calcular_tempo_restante(data_fim):
    """Calcula tempo restante até uma data."""
    if not data_fim:
        return "Indefinido"
    
    agora = datetime.now()
    diferenca = data_fim - agora
    
    if diferenca.total_seconds() < 0:
        return "Expirado"
    
    horas = diferenca.seconds // 3600
    minutos = (diferenca.seconds % 3600) // 60
    
    if horas > 0:
        return f"{horas}h {minutos}m"
    else:
        return f"{minutos}m"

def obter_status_consulta_emoji(status):
    """Retorna emoji baseado no status da consulta."""
    emojis = {
        'agendada': '📅',
        'confirmada': '✅',
        'realizada': '✔️',
        'cancelada': '❌'
    }
    return emojis.get(status, '❓')

def calcular_media_avaliacoes(avaliacoes):
    """Calcula média de avaliações."""
    if not avaliacoes:
        return 0
    
    notas = [a.get('nota', 0) for a in avaliacoes if 'nota' in a]
    
    if not notas:
        return 0
    
    return round(sum(notas) / len(notas), 1)
