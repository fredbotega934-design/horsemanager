from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime

class Embriao(Base):
    __tablename__ = 'embrioes'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    
    # Rastreabilidade (Origem)
    doadora_id = Column(Integer) # ID da Egua Doadora
    garanhao_nome = Column(String(100)) # Nome do Pai
    data_producao = Column(Date) # Data da OPU ou Inseminacao
    laboratorio_origem = Column(String(100))
    
    # Classificacao (Squires & Carnevale)
    grau_qualidade = Column(String(10)) # Grau 1, 2, 3, 4
    estagio_desenvolvimento = Column(String(50)) # Blastocisto, Blast. Expandido, Morula
    
    # Status Atual
    status = Column(String(50)) # Congelado, Fresco, Transferido, Descartado
    
    # Localizacao (Se congelado)
    botijao = Column(String(50))
    caneca = Column(String(50))
    palheta_cor = Column(String(50))
    
    # Destino (Se transferido)
    receptora_id = Column(Integer, ForeignKey('receptoras.id'), nullable=True)
    data_transferencia = Column(Date, nullable=True)
    
    # Relacionamento
    receptora_destino = relationship("Receptora", backref="embriao_recebido")
