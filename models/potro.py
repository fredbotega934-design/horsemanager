from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from models.database import Base

class Potro(Base):
    __tablename__ = 'potros'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100))
    identificacao = Column(String(50))
    data_nascimento = Column(Date)
    sexo = Column(String(20))
    raca = Column(String(50))
    peso_nascimento = Column(Float)
    valor_venda = Column(Float, default=0.0)
