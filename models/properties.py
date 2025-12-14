from sqlalchemy import Column, Integer, String
from models.database import Base

class Propriedade(Base):
    __tablename__ = 'propriedades'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    nome = Column(String(100), nullable=False)
    registro_mapa = Column(String(50)) # Opcional
