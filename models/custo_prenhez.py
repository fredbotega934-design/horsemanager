from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime

# Tabelas de Associação
procedimento_itens = Table('procedimento_itens', Base.metadata,
    Column('procedimento_id', Integer, ForeignKey('procedimentos.id')),
    Column('item_id', Integer, ForeignKey('itens_custo.id'))
)

calculo_procedimentos = Table('calculo_procedimentos', Base.metadata,
    Column('calculo_id', Integer, ForeignKey('calculos_prenhez.id')),
    Column('procedimento_id', Integer, ForeignKey('procedimentos.id'))
)

class ItemCusto(Base):
    __tablename__ = 'itens_custo'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100), nullable=False)
    categoria = Column(String(50))
    valor_total = Column(Float)
    quantidade_total = Column(Float)
    unidade_medida = Column(String(20))
    dose_usada = Column(Float)
    custo_da_dose = Column(Float)
    observacoes = Column(String(255)) # Adicionado conforme seu HTML

class Procedimento(Base):
    __tablename__ = 'procedimentos'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100))
    tipo = Column(String(100))
    custo_total = Column(Float)
    observacoes = Column(String(255))
    itens_usados = relationship("ItemCusto", secondary=procedimento_itens, backref="procedimentos")

class CalculoPrenhez(Base):
    __tablename__ = 'calculos_prenhez'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100))
    num_ciclos = Column(Integer)
    num_tentativas = Column(Integer)
    custo_medio_ciclo = Column(Float)
    custo_total_prenhez = Column(Float)
    data_criacao = Column(String(50), default=str(datetime.now())) # Simplificado para string para evitar erros de data
    procedimentos_usados = relationship("Procedimento", secondary=calculo_procedimentos, backref="calculos")
