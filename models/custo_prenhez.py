from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime

# Tabela de associação (Muitos-para-Muitos) entre Procedimento e Item
procedimento_itens = Table('procedimento_itens', Base.metadata,
    Column('procedimento_id', Integer, ForeignKey('procedimentos.id')),
    Column('item_id', Integer, ForeignKey('itens_custo.id'))
)

# Tabela de associação entre Calculo e Procedimento
calculo_procedimentos = Table('calculo_procedimentos', Base.metadata,
    Column('calculo_id', Integer, ForeignKey('calculos_prenhez.id')),
    Column('procedimento_id', Integer, ForeignKey('procedimentos.id'))
)

class ItemCusto(Base):
    __tablename__ = 'itens_custo'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100), nullable=False)
    categoria = Column(String(50)) # Hormonio, Material, etc
    valor_total = Column(Float)
    quantidade_total = Column(Float)
    unidade_medida = Column(String(20)) # ml, frasco, un
    dose_usada = Column(Float)
    custo_da_dose = Column(Float)

class Procedimento(Base):
    __tablename__ = 'procedimentos'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100)) # Ex: Inseminacao
    tipo = Column(String(50))
    custo_total = Column(Float)
    
    # Relacionamento com itens
    itens_usados = relationship("ItemCusto", secondary=procedimento_itens, backref="procedimentos")

class CalculoPrenhez(Base):
    __tablename__ = 'calculos_prenhez'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100)) # Ex: Protocolo Doadora X
    num_ciclos = Column(Integer, default=1)
    num_tentativas = Column(Integer, default=1)
    
    custo_medio_ciclo = Column(Float)
    custo_total_prenhez = Column(Float)
    
    data_criacao = Column(Date, default=datetime.utcnow)
    
    # Relacionamento com procedimentos
    procedimentos_usados = relationship("Procedimento", secondary=calculo_procedimentos, backref="calculos")

# Classe auxiliar para compatibilidade (se necessario no futuro)
class ProcedimentoCalculo(Base):
    __tablename__ = 'procedimento_calculo_link'
    id = Column(Integer, primary_key=True)
    dummy = Column(Integer)
