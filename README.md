# Sistema de Gestão de Haras e Centro de Reprodução Equina

Sistema completo para gestão de haras com funcionalidades avançadas de RBAC, VaaS (Veterinarian as a Service), IA e arquitetura multi-tenant.

## 🚀 Funcionalidades Principais

- **Dashboard Integrado** com KPIs em tempo real
- **RBAC (Role-Based Access Control)** com 3 níveis de acesso
- **VaaS (Veterinarian as a Service)** para contratação sob demanda
- **Rastreamento Financeiro** com análises de ROI
- **IA para Previsões** e recomendações inteligentes
- **Arquitetura Multi-tenant** para múltiplos haras
- **APIs RESTful** completas

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.11, Flask, SQLAlchemy, JWT
- **Frontend**: HTML5, JavaScript, Tailwind CSS, Chart.js
- **Banco de Dados**: SQLite (desenvolvimento), PostgreSQL (produção)
- **IA**: Scikit-learn, NumPy, Pandas

## 📦 Instalação Local

### Pré-requisitos
- Python 3.11+
- pip

### Passos

1. **Clone o repositório**
```bash
git clone <repository-url>
cd sistema-haras-producao
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Execute a aplicação**
```bash
cd src
python app_production.py
```

A aplicação estará disponível em `http://localhost:5000`

## 🌐 Implantação em Produção

### Heroku

1. **Instale o Heroku CLI**
2. **Faça login no Heroku**
```bash
heroku login
```

3. **Crie uma nova aplicação**
```bash
heroku create nome-da-sua-app
```

4. **Configure as variáveis de ambiente**
```bash
heroku config:set SECRET_KEY=sua-chave-secreta
heroku config:set JWT_SECRET_KEY=sua-jwt-chave
heroku config:set FLASK_ENV=production
```

5. **Faça o deploy**
```bash
git add .
git commit -m "Deploy inicial"
git push heroku main
```

### Railway

1. **Conecte seu repositório ao Railway**
2. **Configure as variáveis de ambiente no painel**
3. **O deploy será automático**

### Render

1. **Conecte seu repositório ao Render**
2. **Configure o comando de build**: `pip install -r requirements.txt`
3. **Configure o comando de start**: `cd src && gunicorn app_production:app --bind 0.0.0.0:$PORT`

### DigitalOcean App Platform

1. **Conecte seu repositório**
2. **Configure o tipo de aplicação como Web Service**
3. **Configure as variáveis de ambiente**

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `FLASK_ENV` | Ambiente da aplicação | `production` |
| `SECRET_KEY` | Chave secreta do Flask | - |
| `JWT_SECRET_KEY` | Chave secreta do JWT | - |
| `DATABASE_URL` | URL do banco de dados | `sqlite:///haras_prod.db` |
| `PORT` | Porta da aplicação | `5000` |

### Banco de Dados

Para produção, recomenda-se usar PostgreSQL:

```bash
# Instalar psycopg2 para PostgreSQL
pip install psycopg2-binary

# Configurar DATABASE_URL
export DATABASE_URL=postgresql://user:password@host:port/database
```

## 📱 Uso da API

### Autenticação

```bash
# Login
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@haras.com", "senha": "123456"}'
```

### Endpoints Principais

- `GET /` - Dashboard principal
- `GET /health` - Health check
- `POST /api/users/login` - Login
- `GET /api/users/dashboard` - KPIs do dashboard
- `GET /api/vaas/dashboard` - Dashboard VaaS
- `GET /api/financeiro/dashboard` - Dashboard financeiro
- `GET /api/ai/predictions` - Previsões de IA
- `GET /api/tenants/` - Lista de tenants

## 🧪 Testes

```bash
# Executar testes
python -m pytest tests/

# Com cobertura
python -m pytest tests/ --cov=src
```

## 📊 Monitoramento

### Health Check

A aplicação expõe um endpoint de health check em `/health`:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

### Logs

Configure o nível de log através da variável `LOG_LEVEL`:

```bash
export LOG_LEVEL=INFO
```

## 🔒 Segurança

- **JWT** para autenticação
- **RBAC** para controle de acesso
- **CORS** configurado
- **Isolamento multi-tenant**
- **Validação de entrada**

## 📈 Performance

- **Gunicorn** com múltiplos workers
- **Índices otimizados** no banco de dados
- **Cache** por tenant
- **Queries otimizadas** com SQLAlchemy

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte técnico, entre em contato através de:
- Email: suporte@sistemaharas.com
- Issues: GitHub Issues
- Documentação: [Link para documentação completa]

## 🎯 Roadmap

- [ ] Integração com APIs de pagamento
- [ ] Aplicativo mobile
- [ ] Relatórios avançados em PDF
- [ ] Integração com IoT para monitoramento
- [ ] Dashboard em tempo real com WebSockets
