from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from models.database import Base
from datetime import datetime

# --- FINANCEIRO ---
class Lancamento(Base):
    __tablename__ = 'financeiro_lancamentos'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    tipo = Column(String(20)) # Receita / Despesa
    categoria = Column(String(50))
    valor = Column(Float)
    descricao = Column(String(200))
    data_vencimento = Column(Date)
    pago = Column(Boolean, default=False)
    data_criacao = Column(Date, default=datetime.utcnow)

# --- VaaS (Veterinarios) ---
class AtendimentoVaas(Base):
    __tablename__ = 'vaas_atendimentos'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    veterinario_nome = Column(String(100))
    animal_nome = Column(String(100))
    tipo_servico = Column(String(100))
    data_agendada = Column(Date)
    status = Column(String(50)) # Agendado, Realizado
    custo = Column(Float)
