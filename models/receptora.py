from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime

class Receptora(Base):
    __tablename__ = 'receptoras'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    
    propriedade = Column(String(100))
    categoria = Column(String(50))
    
    nome = Column(String(100))
    identificacao = Column(String(50))
    raca = Column(String(50))
    
    status_saude = Column(String(100)) # Vazia, Prenhe
    
    # --- O NOVO CAMPO CRITICO ---
    data_ovulacao = Column(Date, nullable=True) # A data base para calcular D4, D5, D6...
    
    exames = relationship("ExameGinecologico", backref="receptora", order_by="desc(ExameGinecologico.data_exame)")

class ExameGinecologico(Base):
    __tablename__ = 'exames_ginecologicos'

    id = Column(Integer, primary_key=True)
    receptora_id = Column(Integer, ForeignKey('receptoras.id'))
    data_exame = Column(Date, default=datetime.utcnow)
    ovario_esq = Column(String(50))
    ovario_dir = Column(String(50))
    utero_edema = Column(String(10))
    utero_tonus = Column(String(10))
    diagnostico = Column(String(200))
