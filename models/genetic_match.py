"""
Módulo de Acasalamento Inteligente (Genetic Match Engine)
Modelos de dados para análise genética e recomendações de acasalamento.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json

Base = declarative_base()

class Animal(Base):
    """Modelo para dados completos dos animais com pedigree."""
    __tablename__ = 'animals'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), nullable=False)
    
    # Dados básicos
    nome = Column(String(100), nullable=False)
    registro = Column(String(50), unique=True)
    sexo = Column(String(1), nullable=False)  # M/F
    data_nascimento = Column(DateTime)
    raca = Column(String(50))
    
    # Pedigree (até 4 gerações)
    pai_id = Column(Integer, ForeignKey('animals.id'))
    mae_id = Column(Integer, ForeignKey('animals.id'))
    avo_paterno_id = Column(Integer, ForeignKey('animals.id'))
    avo_paterna_id = Column(Integer, ForeignKey('animals.id'))
    avo_materno_id = Column(Integer, ForeignKey('animals.id'))
    avo_materna_id = Column(Integer, ForeignKey('animals.id'))
    
    # Dados fenotípicos
    altura = Column(Float)  # em metros
    peso = Column(Float)    # em kg
    condicao_corporal = Column(Float)  # 1-9
    tipo_morfologico = Column(String(50))  # corrida, conformação, trabalho
    
    # Status e metadados
    ativo = Column(Boolean, default=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    observacoes = Column(Text)
    
    # Relacionamentos
    pai = relationship("Animal", remote_side=[id], foreign_keys=[pai_id])
    mae = relationship("Animal", remote_side=[id], foreign_keys=[mae_id])
    
    # Histórico reprodutivo
    historico_reprodutivo = relationship("HistoricoReprodutivo", back_populates="animal")
    
    # Performance da progênie
    performance_filhos = relationship("PerformanceProgenie", back_populates="animal")

class HistoricoReprodutivo(Base):
    """Histórico de prenhez e protocolos reprodutivos."""
    __tablename__ = 'repro_history'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), nullable=False)
    animal_id = Column(Integer, ForeignKey('animals.id'), nullable=False)
    
    # Dados do ciclo reprodutivo
    data_cobertura = Column(DateTime)
    tipo_cobertura = Column(String(20))  # natural, IA, TE
    garanhao_id = Column(Integer, ForeignKey('animals.id'))
    
    # Resultados
    prenhez_confirmada = Column(Boolean)
    data_confirmacao = Column(DateTime)
    qualidade_embriao = Column(String(20))  # excelente, boa, regular, ruim
    data_parto = Column(DateTime)
    resultado_parto = Column(String(50))  # normal, distócico, aborto
    
    # Custos associados
    custo_protocolo = Column(Float)
    custo_veterinario = Column(Float)
    custo_total = Column(Float)
    
    # Metadados
    data_registro = Column(DateTime, default=datetime.utcnow)
    observacoes = Column(Text)
    
    # Relacionamentos
    animal = relationship("Animal", back_populates="historico_reprodutivo")
    garanhao = relationship("Animal", foreign_keys=[garanhao_id])

class PerformanceProgenie(Base):
    """Performance esportiva e reprodutiva dos filhos."""
    __tablename__ = 'progeny_performance'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), nullable=False)
    animal_id = Column(Integer, ForeignKey('animals.id'), nullable=False)  # pai/mãe
    filho_id = Column(Integer, ForeignKey('animals.id'), nullable=False)   # filho
    
    # Performance esportiva
    modalidade = Column(String(50))  # corrida, salto, adestramento, etc.
    ranking_nacional = Column(Integer)
    premios_ganhos = Column(Float)
    tempo_melhor = Column(Float)  # para corridas
    altura_maxima = Column(Float)  # para salto
    
    # Performance reprodutiva (se aplicável)
    taxa_prenhez_filho = Column(Float)
    qualidade_media_embrioes = Column(Float)
    
    # Valor de mercado
    valor_estimado = Column(Float)
    valor_venda = Column(Float)
    data_venda = Column(DateTime)
    
    # Metadados
    data_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    animal = relationship("Animal", back_populates="performance_filhos", foreign_keys=[animal_id])
    filho = relationship("Animal", foreign_keys=[filho_id])

class DadosGenomicos(Base):
    """Dados genéticos e marcadores (opcional)."""
    __tablename__ = 'genomic_data'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), nullable=False)
    animal_id = Column(Integer, ForeignKey('animals.id'), nullable=False)
    
    # Marcadores genéticos
    marcadores_velocidade = Column(Text)  # JSON com marcadores
    marcadores_resistencia = Column(Text)
    marcadores_conformacao = Column(Text)
    
    # Scores genéticos
    score_velocidade = Column(Float)
    score_resistencia = Column(Float)
    score_conformacao = Column(Float)
    score_fertilidade = Column(Float)
    
    # Coeficientes
    coeficiente_consanguinidade = Column(Float)
    diversidade_genetica = Column(Float)
    
    # Metadados
    data_teste = Column(DateTime)
    laboratorio = Column(String(100))
    data_registro = Column(DateTime, default=datetime.utcnow)

class SolicitacaoMatch(Base):
    """Solicitações e resultados das recomendações de acasalamento."""
    __tablename__ = 'match_requests'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), nullable=False)
    usuario_id = Column(Integer, nullable=False)
    
    # Parâmetros da solicitação
    doadora_id = Column(Integer, ForeignKey('animals.id'), nullable=False)
    categoria_objetivo = Column(String(50))  # corrida, conformação, trabalho
    orcamento_maximo = Column(Float)
    prioridade_genetica = Column(Float)  # 0-1
    prioridade_financeira = Column(Float)  # 0-1
    
    # Resultados
    resultados_json = Column(Text)  # JSON com ranking de garanhões
    melhor_garanhao_id = Column(Integer, ForeignKey('animals.id'))
    taxa_prenhez_prevista = Column(Float)
    roi_estimado = Column(Float)
    score_genetico = Column(Float)
    
    # Metadados
    data_solicitacao = Column(DateTime, default=datetime.utcnow)
    data_processamento = Column(DateTime)
    tempo_processamento = Column(Float)  # em segundos
    versao_modelo = Column(String(20))
    
    # Relacionamentos
    doadora = relationship("Animal", foreign_keys=[doadora_id])
    melhor_garanhao = relationship("Animal", foreign_keys=[melhor_garanhao_id])

class ConfiguracaoMatch(Base):
    """Configurações do sistema de matching por tenant."""
    __tablename__ = 'match_config'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), unique=True, nullable=False)
    
    # Pesos dos fatores
    peso_genetica = Column(Float, default=0.4)
    peso_performance = Column(Float, default=0.3)
    peso_financeiro = Column(Float, default=0.3)
    
    # Limites
    consanguinidade_maxima = Column(Float, default=0.125)  # 12.5%
    idade_minima_garanhao = Column(Integer, default=3)
    idade_maxima_garanhao = Column(Integer, default=25)
    
    # Configurações de modelo
    modelo_ativo = Column(String(50), default='xgboost_v1')
    threshold_confianca = Column(Float, default=0.7)
    max_recomendacoes = Column(Integer, default=10)
    
    # Metadados
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow)

# Funções auxiliares para cálculos genéticos

def calcular_consanguinidade(animal_id, profundidade=4):
    """
    Calcula o coeficiente de consanguinidade de um animal.
    Implementação simplificada - em produção usar algoritmo de Wright.
    """
    # Implementação básica - expandir conforme necessário
    return 0.0

def calcular_parentesco(animal1_id, animal2_id):
    """
    Calcula o coeficiente de parentesco entre dois animais.
    """
    # Implementação básica - expandir conforme necessário
    return 0.0

def extrair_features_geneticas(doadora_id, garanhao_id):
    """
    Extrai features para o modelo de ML baseado nos dados dos animais.
    """
    features = {
        'idade_doadora': 0,
        'idade_garanhao': 0,
        'peso_doadora': 0,
        'peso_garanhao': 0,
        'altura_doadora': 0,
        'altura_garanhao': 0,
        'consanguinidade': 0,
        'parentesco': 0,
        'taxa_prenhez_doadora': 0,
        'taxa_prenhez_garanhao': 0,
        'performance_media_progenie': 0,
        'compatibilidade_raca': 1,
        'score_genetico_combinado': 0
    }
    
    return features
