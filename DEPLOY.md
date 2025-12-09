# Guia de Implantação - Sistema de Haras

## 🚀 Opções de Implantação

### 1. Heroku (Recomendado para Iniciantes)

```bash
# 1. Instalar Heroku CLI
# 2. Fazer login
heroku login

# 3. Criar aplicação
heroku create nome-do-seu-haras

# 4. Configurar variáveis de ambiente
heroku config:set SECRET_KEY=sua-chave-secreta-aqui
heroku config:set JWT_SECRET_KEY=sua-jwt-chave-aqui
heroku config:set FLASK_ENV=production

# 5. Deploy
git add .
git commit -m "Deploy inicial"
git push heroku main

# 6. Abrir aplicação
heroku open
```

### 2. Railway (Mais Simples)

1. Acesse [railway.app](https://railway.app)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente:
   - `SECRET_KEY`: sua-chave-secreta
   - `JWT_SECRET_KEY`: sua-jwt-chave
   - `FLASK_ENV`: production
4. Deploy automático!

### 3. Render (Gratuito)

1. Acesse [render.com](https://render.com)
2. Conecte seu repositório
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd src && gunicorn app_simple:app --bind 0.0.0.0:$PORT`
4. Adicione variáveis de ambiente
5. Deploy!

### 4. Vercel (Frontend + Serverless)

```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Deploy
vercel

# 3. Configurar variáveis de ambiente no dashboard
```

### 5. DigitalOcean App Platform

1. Acesse DigitalOcean App Platform
2. Conecte seu repositório
3. Configure como Web Service
4. Adicione variáveis de ambiente
5. Deploy automático

### 6. Docker (Qualquer Provedor)

```bash
# 1. Build da imagem
docker build -t sistema-haras .

# 2. Executar localmente
docker run -p 5000:5000 -e SECRET_KEY=sua-chave sistema-haras

# 3. Deploy para Docker Hub
docker tag sistema-haras seu-usuario/sistema-haras
docker push seu-usuario/sistema-haras
```

### 7. Docker Compose (Produção Completa)

```bash
# 1. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# 2. Executar
docker-compose up -d

# 3. Verificar
curl http://localhost/health
```

## 🔧 Configurações Necessárias

### Variáveis de Ambiente Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta do Flask | `sua-chave-super-secreta-123` |
| `JWT_SECRET_KEY` | Chave secreta do JWT | `jwt-chave-super-secreta-456` |
| `FLASK_ENV` | Ambiente da aplicação | `production` |

### Variáveis Opcionais

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `PORT` | Porta da aplicação | `5000` |
| `DATABASE_URL` | URL do banco de dados | `sqlite:///haras_prod.db` |

## 📋 Checklist Pré-Deploy

- [ ] Configurar `SECRET_KEY` única e segura
- [ ] Configurar `JWT_SECRET_KEY` única e segura
- [ ] Definir `FLASK_ENV=production`
- [ ] Testar aplicação localmente
- [ ] Verificar se todas as dependências estão no `requirements.txt`
- [ ] Confirmar que o `Procfile` está correto

## 🧪 Testando o Deploy

Após o deploy, teste os seguintes endpoints:

```bash
# Health check
curl https://sua-app.herokuapp.com/health

# Status da API
curl https://sua-app.herokuapp.com/api/status

# Dashboard principal
curl https://sua-app.herokuapp.com/
```

## 🔒 Segurança em Produção

### Chaves Secretas
```bash
# Gerar chaves seguras
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### HTTPS
- Heroku: Automático
- Railway: Automático
- Render: Automático
- Outros: Configure SSL/TLS

### Banco de Dados
Para produção, considere usar PostgreSQL:

```bash
# Heroku
heroku addons:create heroku-postgresql:hobby-dev

# Railway
# Adicione PostgreSQL no dashboard

# Outros
# Configure DATABASE_URL com PostgreSQL
```

## 📊 Monitoramento

### Logs
```bash
# Heroku
heroku logs --tail

# Railway
# Veja logs no dashboard

# Docker
docker logs container-name
```

### Métricas
- Acesse `/health` para health check
- Acesse `/api/status` para status da API
- Configure alertas para downtime

## 🚨 Troubleshooting

### Erro: "Application Error"
- Verifique as variáveis de ambiente
- Veja os logs da aplicação
- Confirme se o `Procfile` está correto

### Erro: "Module not found"
- Verifique se todas as dependências estão no `requirements.txt`
- Confirme a estrutura de diretórios

### Erro: "Port already in use"
- Use a variável `PORT` fornecida pela plataforma
- Não hardcode a porta no código

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs da aplicação
2. Confirme as configurações de ambiente
3. Teste localmente primeiro
4. Consulte a documentação da plataforma escolhida

## 🎯 Próximos Passos

Após o deploy bem-sucedido:
1. Configure domínio personalizado
2. Configure backup do banco de dados
3. Implemente monitoramento avançado
4. Configure CI/CD para deploys automáticos
