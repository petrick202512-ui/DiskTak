# 🧠 DISCK TALK - Plataforma de Psicologia Voluntária

> **Você não precisa estar bem para pedir ajuda.** | Aqui você será ouvido.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green?logo=mongodb)
![Socket.IO](https://img.shields.io/badge/Socket.IO-4.7-blue)
![License](https://img.shields.io/badge/License-MIT-red)

---

## 📖 Sobre o Projeto

**Disck Talk** é uma plataforma inovadora de saúde mental que conecta pacientes com psicólogos voluntários. 

### Missão
Democratizar o acesso à saúde mental, permitindo que qualquer pessoa possa conversar com um psicólogo profissional, totalmente de forma voluntária.

### Valores
- 💚 **Empatia**: Escuta ativa e acolhedora
- 🤝 **Voluntariedade**: Psicólogos trabalham por vontade própria
- 🔒 **Privacidade**: Conversa 100% confidencial
- 🌱 **Acessibilidade**: Gratuito para todos
- ♿ **Inclusão**: Acesso fácil para todos

---

## 🌟 Recursos Principais

### Para Pacientes 👤
- ✨ Conversa em tempo real com psicólogos
- 📅 Agendamento de consultas
- 🎥 Chamadas de vídeo
- 📝 Desabafos anônimos
- ⭐ Avaliar psicólogos
- 💬 Histórico de conversas

### Para Psicólogos 🧑‍⚕️
- 📊 Dashboard com estatísticas
- 👥 Gerenciar pacientes
- 📋 Consultas agendadas
- 💌 Responder desabafos
- 📈 Ver feedback dos pacientes
- 🎯 Acompanhar atendimentos

---

## 🏗️ Arquitetura

```
Disck Talk/
├── app.py                      # Aplicação principal
├── requirements.txt            # Dependências Python
├── setup.py                    # Setup inicial
│
├── database/
│   └── mongodb.py             # Conexão MongoDB
│
├── models/                      # Modelos de dados
│   ├── usuario.py
│   ├── consulta.py
│   ├── conversa.py
│   ├── desabafo.py
│   ├── avaliacao.py
│   └── chamada.py
│
├── routes/                      # Rotas Flask
│   ├── auth_routes.py
│   ├── user_routes.py
│   └── chat_routes.py
│
├── static/                      # Arquivos estáticos
│   ├── css/
│   │   ├── style.css           # Estilos principais
│   │   └── responsivo.css      # Media queries
│   ├── js/
│   │   ├── app.js              # Lógica principal
│   │   └── animacoes.js        # Animações
│   └── img/                    # Imagens
│
├── templates/                   # Templates HTML
│   ├── base.html               # Base layout
│   ├── index.html              # Splash
│   ├── login.html, cadastro.html
│   ├── inicio.html, psicologos.html
│   ├── perfil*.html
│   ├── consultas*.html
│   ├── chat.html, conversas.html
│   ├── desabafo*.html
│   └── admin.html
│
└── utils/
    ├── helpers.py              # Funções auxiliares
    └── seed_db.py              # Popular banco
```

---

## 🚀 Quick Start

### Pré-requisitos
```bash
- Python 3.8+
- MongoDB 4.4+
- pip
```

### Instalação (3 passos)
```bash
# 1. Clonar/baixar projeto
cd "c:\Users\Arthur\Desktop\Disck Talk"

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar
python setup.py
python app.py
```

**Acesso**: http://localhost:5000

---

## 🔑 Dados de Teste

### Login Padrão (Psicólogo)
```
Email: ana@exemplo.com
Senha: 123456
```

### Psicólogos Disponíveis
1. Dra. Ana Paula - Psicologia Clínica
2. Dr. Marcos Silva - Acolhimento e Luto
3. Dra. Júlia Costa - Ansiedade e Stress
4. Dr. Felipe Oliveira - Relacionamentos
5. Dra. Carla Santos - Saúde Mental

---

## 💻 Stack Técnico

### Backend
- **Framework**: Flask 3.0
- **Real-time**: Socket.IO 4.7
- **Database**: MongoDB 4.4
- **Auth**: Flask-Login + Werkzeug
- **Python**: 3.8+

### Frontend
- **Template Engine**: Jinja2
- **CSS**: Vanilla CSS com Glassmorphism
- **JavaScript**: Vanilla JS + Socket.IO
- **Icons**: FontAwesome 6.4

### DevOps
- **Database**: MongoDB Cloud Atlas (recomendado)
- **Deploy**: Heroku / AWS / DigitalOcean
- **Version Control**: Git

---

## 📊 Funcionalidades (85% Completo)

| Feature | Status | Prioridade |
|---------|--------|-----------|
| Autenticação | ✅ 100% | Alta |
| Chat em Tempo Real | ✅ 80% | Alta |
| Agendamento | ✅ 95% | Alta |
| Desabafos | ✅ 100% | Alta |
| Avaliações | ✅ 100% | Média |
| Chamadas Vídeo | ⏳ 20% | Média |
| Responsividade | ✅ 100% | Alta |
| Segurança | ✅ 80% | Alta |

---

## 🎨 Design & UI/UX

### Paleta de Cores
```
Primary Dark:  #0B1520
Teal:          #2A6B6B
Soft Green:    #6DBAAB
Light Green:   #A8D5C2
Cream:         #F6F4E9
```

### Design System
- Glassmorphism moderno
- Animações suaves
- Mobile-first responsive
- Acessibilidade considerada
- Feedback visual claro

---

## 📱 Responsividade

✅ **100% Responsivo**
- 📱 Mobile (<480px)
- 📱 Smartphone (480-768px)
- 📱 Tablet (768-1024px)
- 💻 Desktop (>1024px)

---

## 🔒 Segurança

### Implementado
- ✅ Autenticação com hash
- ✅ Proteção CSRF
- ✅ CORS configurado
- ✅ Sanitização de inputs
- ✅ Validação de dados
- ✅ Tratamento de exceções

### Planned
- 🔄 Two-factor auth
- 🔄 Rate limiting
- 🔄 SSL/TLS (produção)

---

## 📚 Documentação

- 📖 [Setup Guide](./SETUP_GUIDE.md) - Instalação completa
- 📖 [API Routes](./API_ROUTES.md) - Documentação de rotas
- 📖 [Resumo Análise](./RESUMO_ANALISE.md) - Análise do projeto
- 📖 [Checklist](./CHECKLIST.md) - Funcionalidades

---

## 🤝 Como Contribuir

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 🐛 Reportar Bugs

Se encontrou um bug:
1. Verifique se já foi reportado
2. Descreva o comportamento esperado e o atual
3. Forneça passos para reproduzir
4. Adicione screenshots se possível

---

## 📝 Licença

Distribuído sob a licença MIT. Ver `LICENSE` para mais informações.

---

## 🙏 Agradecimentos

- Comunidade Python
- Flask e Socket.IO
- MongoDB
- Todos os voluntários psicólogos

---

## 📞 Contato

- 📧 Email: contato@discktalk.com.br
- 🌐 Website: www.discktalk.com.br
- 💬 Discord: [Link do Servidor]

---

## 🎯 Roadmap

### v1.1 (Próximas Semanas)
- [ ] WebRTC para vídeo real
- [ ] Notificações por email
- [ ] Melhorias de performance

### v1.5 (Próximos Meses)
- [ ] App mobile (React Native)
- [ ] Pagamentos integrados
- [ ] Suporte multilíngue

### v2.0 (Futuro)
- [ ] Terapia em grupo
- [ ] Testes psicológicos
- [ ] Recursos educacionais

---

## 📊 Stats

![Python](https://img.shields.io/badge/Total%20Lines-2500+-blue)
![Commits](https://img.shields.io/badge/Commits-50%2B-green)
![Contributors](https://img.shields.io/badge/Contributors-1-orange)
![Last Update](https://img.shields.io/badge/Last%20Update-Junho%202024-blue)

---

## ⭐ Show Your Support

Se este projeto te ajudou, deixe uma ⭐!

---

<div align="center">

**Desenvolvido com ❤️ para a Saúde Mental**

*Você não precisa estar bem para pedir ajuda.*

Made with 🧠 | [Disck Talk](https://discktalk.com.br)

</div>

---

**Status**: 🟢 Produção Parcial | **v1.0.0** | Junho 2024
