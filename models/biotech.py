from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime

class SessaoOPU(Base):
    __tablename__ = 'sessoes_opu'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50))
    receptora_id = Column(Integer, ForeignKey('receptoras.id')) # Aqui atuando como Doadora
    data_procedimento = Column(DateTime, default=datetime.utcnow)
    veterinario_responsavel = Column(String(100))
    
    # --- METRICAS DE EFICIENCIA (O Funil) ---
    foliculos_visualizados = Column(Integer)
    foliculos_aspirados = Column(Integer)
    oocitos_recuperados = Column(Integer)
    taxa_recuperacao = Column(Float) # Calculado: oocitos / aspirados
    
    # --- TECNICA ---
    pressao_vacuo = Column(String(50)) # Ex: 80mmHg
    tecnica_flushing = Column(String(50)) # Ex: Continuo, 5x
    
    # --- POS-OPERATORIO & SEGURANCA ---
    antibiotico_profilatico = Column(Boolean, default=False)
    tipo_antibiotico = Column(String(100))
    complicacoes_intra = Column(Text) # Ex: Sangramento retal leve
    
    # --- MONITORAMENTO POS (24h/48h) ---
    temp_pos_24h = Column(Float)
    freq_cardiaca_pos_24h = Column(Integer)
    sinais_colica = Column(Boolean, default=False)
    
    # --- DADOS DO LAB (ICSI) ---
    laboratorio_destino = Column(String(100))
    oocitos_maturados = Column(Integer) # MII
    embrioes_blastocisto = Column(Integer) # Resultado Final
    
    # Relacionamento
    animal = relationship("Receptora", backref="opus")
