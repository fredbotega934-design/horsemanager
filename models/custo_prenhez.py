from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.database import Base

class ItemCusto(Base):
    __tablename__ = 'itens_custo'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100), nullable=False)
    categoria = Column(String(50)) # Hormonio, Insumo, Mao de Obra, etc.
    valor_total_frasco = Column(Float)
    quantidade_total_frasco = Column(Float) # Em ml ou unidades
    unidade_medida = Column(String(20)) # ml, un, dose
    
    # Propriedade calculada virtualmente no frontend/rota, mas podemos guardar cache
    custo_por_unidade = Column(Float) 

class ProcedimentoCusto(Base):
    __tablename__ = 'procedimentos_custo'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100)) # Ex: Inseminacao Sêmen Fresco
    custo_total_calculado = Column(Float)
    descricao = Column(Text)

# Tabela de ligação: Quais itens compõem um procedimento?
class ItemNoProcedimento(Base):
    __tablename__ = 'itens_procedimento'
    
    id = Column(Integer, primary_key=True)
    procedimento_id = Column(Integer, ForeignKey('procedimentos_custo.id'))
    item_id = Column(Integer, ForeignKey('itens_custo.id'))
    dose_usada = Column(Float)
    custo_calculado_dose = Column(Float)
    
    item = relationship("ItemCusto")
    procedimento = relationship("ProcedimentoCusto", backref="itens")
