

from sqlalchemy.orm import relationship

class Egua(Base):
    # ... (existing columns)
    embrioes_doados = relationship("EmbriaoTransferido", back_populates="doadora")

