from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from models.database import Base

# Tabela de Associação (Muitos-para-Muitos)
procedimento_itens = Table('procedimento_itens', Base.metadata,
    Column('procedimento_id', Integer, ForeignKey('procedimentos.id')),
    Column('item_id', Integer, ForeignKey('itens_custo.id')),
    extend_existing=True
)

calculo_procedimentos = Table('calculo_procedimentos', Base.metadata,
    Column('calculo_id', Integer, ForeignKey('calculos_prenhez.id')),
    Column('procedimento_id', Integer, ForeignKey('procedimentos.id')),
    extend_existing=True
)

class ItemCusto(Base):
    __tablename__ = 'itens_custo'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100))
    categoria = Column(String(50))
    valor_total = Column(Float)
    quantidade_total = Column(Float)
    unidade_medida = Column(String(20))
    dose_usada = Column(Float)
    custo_da_dose = Column(Float)
    observacoes = Column(String(255))

class Procedimento(Base):
    __tablename__ = 'procedimentos'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100))
    tipo = Column(String(50))
    custo_total = Column(Float)
    observacoes = Column(String(255))
    itens_usados = relationship("ItemCusto", secondary=procedimento_itens)

class CalculoPrenhez(Base):
    __tablename__ = 'calculos_prenhez'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100))
    num_ciclos = Column(Integer)
    num_tentativas = Column(Integer)
    custo_medio_ciclo = Column(Float)
    custo_total_prenhez = Column(Float)
    data_criacao = Column(String(20))
    procedimentos_usados = relationship("Procedimento", secondary=calculo_procedimentos)
