import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# 1. Tenta pegar a URL do Banco do Render. Se nao tiver, usa sqlite local.
database_url = os.environ.get('DATABASE_URL', 'sqlite:///haras.db')

# 2. Correcao necessaria para o Render (ele fornece 'postgres://' mas o SQLAlchemy pede 'postgresql://')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# 3. Cria a conexao
engine = create_engine(database_url)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # Importar todos os modelos para criar as tabelas
    import models.user
    import models.receptora
    import models.financeiro
    import models.custo_prenhez
    import models.potro
    
    Base.metadata.create_all(bind=engine)
