from sqlalchemy import Column, Integer, String, Date, Float
from models.database import Base
from datetime import datetime

class Egua(Base):
    __tablename__ = 'eguas'
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100))
    registro = Column(String(50))
    status = Column(String(50))
    historico = Column(String(500))
    data_cadastro = Column(Date, default=datetime.utcnow)

class Receptora(Base):
    __tablename__ = 'receptoras_new'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100))
    lote = Column(String(50))
    status = Column(String(50))
    obs = Column(String(255))
