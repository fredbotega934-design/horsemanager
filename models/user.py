from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
# O SEGREDO ESTA NESTE IMPORT: Usar a Base do database.py
from models.database import Base

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255))
    role = Column(String(50), default='user')
    tenant_id = Column(String(50))
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    ultimo_login = Column(DateTime)
    
    # Campos extras para evitar erros futuros
    crmv = Column(String(20))
    especialidade = Column(String(100))
    telefone = Column(String(20))
    permissoes = Column(String(500)) # Armazenado como string ou JSON simples
    proprietario_id = Column(Integer, nullable=True)

class Egua(Base):
    __tablename__ = 'eguas'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100))
    registro = Column(String(100))
    data_nascimento = Column(DateTime)
    raca = Column(String(50))
    # Adicione outros campos se necessario no futuro
