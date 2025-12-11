from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from models.database import Base
from datetime import datetime

class TransacaoFinanceira(Base):
    __tablename__ = 'transacoes_financeiras'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    descricao = Column(String(200), nullable=False)
    tipo = Column(String(20)) # 'Receita' ou 'Despesa'
    valor = Column(Float, nullable=False)
    categoria = Column(String(100)) # Ex: 'Racao', 'Veterinario'
    data_transacao = Column(Date, default=datetime.utcnow)
    observacoes = Column(String(500))
    animal_id = Column(Integer, nullable=True) 
