from datetime import datetime, timedelta
from decimal import Decimal
import json

from .user import db

class PlanoVaaS(db.Model):
    """Planos de assinatura VaaS disponíveis"""
    __tablename__ = 'planos_vaas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco_mensal = db.Column(db.Numeric(10, 2), nullable=False)
    max_veterinarios = db.Column(db.Integer, nullable=False)
    max_consultas_mes = db.Column(db.Integer)
    max_procedimentos_mes = db.Column(db.Integer)
    recursos_inclusos = db.Column(db.Text)  # JSON com recursos
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco_mensal': float(self.preco_mensal),
            'max_veterinarios': self.max_veterinarios,
            'max_consultas_mes': self.max_consultas_mes,
            'max_procedimentos_mes': self.max_procedimentos_mes,
            'recursos_inclusos': json.loads(self.recursos_inclusos) if self.recursos_inclusos else [],
            'ativo': self.ativo
        }

class AssinaturaVaaS(db.Model):
    """Assinaturas VaaS dos proprietários"""
    __tablename__ = 'assinaturas_vaas'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(50), nullable=False)
    proprietario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    plano_id = db.Column(db.Integer, db.ForeignKey('planos_vaas.id'), nullable=False)
    
    # Datas da assinatura
    data_inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    data_cancelamento = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(50), nullable=False, default='ativa')  # ativa, cancelada, suspensa, expirada
    
    # Configurações personalizadas
    veterinarios_contratados = db.Column(db.Integer, default=0)
    limite_personalizado_consultas = db.Column(db.Integer)
    limite_personalizado_procedimentos = db.Column(db.Integer)
    
    # Relacionamentos
    plano = db.relationship('PlanoVaaS', backref='assinaturas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'proprietario_id': self.proprietario_id,
            'plano': self.plano.to_dict() if self.plano else None,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'data_cancelamento': self.data_cancelamento.isoformat() if self.data_cancelamento else None,
            'status': self.status,
            'veterinarios_contratados': self.veterinarios_contratados,
            'limite_personalizado_consultas': self.limite_personalizado_consultas,
            'limite_personalizado_procedimentos': self.limite_personalizado_procedimentos
        }
    
    def is_ativa(self):
        """Verifica se a assinatura está ativa"""
        if self.status != 'ativa':
            return False
        
        if self.data_fim and datetime.utcnow() > self.data_fim:
            return False
        
        return True
    
    def dias_restantes(self):
        """Retorna quantos dias restam na assinatura"""
        if not self.data_fim:
            return None
        
        delta = self.data_fim - datetime.utcnow()
        return max(0, delta.days)
    
    def get_limite_consultas(self):
        """Retorna o limite de consultas (personalizado ou do plano)"""
        return self.limite_personalizado_consultas or self.plano.max_consultas_mes
    
    def get_limite_procedimentos(self):
        """Retorna o limite de procedimentos (personalizado ou do plano)"""
        return self.limite_personalizado_procedimentos or self.plano.max_procedimentos_mes

class ContratoVeterinario(db.Model):
    """Contratos de veterinários com proprietários"""
    __tablename__ = 'contratos_veterinario'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(50), nullable=False)
    proprietario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    assinatura_id = db.Column(db.Integer, db.ForeignKey('assinaturas_vaas.id'), nullable=False)
    
    # Dados do contrato
    data_inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False, default='ativo')  # ativo, suspenso, finalizado
    
    # Precificação
    valor_hora = db.Column(db.Numeric(10, 2))
    valor_consulta = db.Column(db.Numeric(10, 2))
    valor_procedimento = db.Column(db.Numeric(10, 2))
    
    # Configurações de acesso
    permissoes_especiais = db.Column(db.Text)  # JSON com permissões específicas
    horarios_disponibilidade = db.Column(db.Text)  # JSON com horários
    
    # Relacionamentos
    assinatura = db.relationship('AssinaturaVaaS', backref='contratos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'proprietario_id': self.proprietario_id,
            'veterinario_id': self.veterinario_id,
            'assinatura_id': self.assinatura_id,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'status': self.status,
            'valor_hora': float(self.valor_hora) if self.valor_hora else None,
            'valor_consulta': float(self.valor_consulta) if self.valor_consulta else None,
            'valor_procedimento': float(self.valor_procedimento) if self.valor_procedimento else None,
            'permissoes_especiais': json.loads(self.permissoes_especiais) if self.permissoes_especiais else {},
            'horarios_disponibilidade': json.loads(self.horarios_disponibilidade) if self.horarios_disponibilidade else {}
        }

class AtendimentoVaaS(db.Model):
    """Registro de atendimentos realizados via VaaS"""
    __tablename__ = 'atendimentos_vaas'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(50), nullable=False)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contratos_veterinario.id'), nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    animal_id = db.Column(db.Integer)  # Referência ao animal atendido
    
    # Dados do atendimento
    data_atendimento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tipo_atendimento = db.Column(db.String(100), nullable=False)  # consulta, procedimento, emergencia
    duracao_minutos = db.Column(db.Integer)
    descricao = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    
    # Precificação
    valor_cobrado = db.Column(db.Numeric(10, 2), nullable=False)
    forma_cobranca = db.Column(db.String(50))  # hora, consulta, procedimento, fixo
    
    # Status
    status = db.Column(db.String(50), default='realizado')  # agendado, realizado, cancelado, faturado
    data_faturamento = db.Column(db.DateTime)
    
    # Relacionamentos
    contrato = db.relationship('ContratoVeterinario', backref='atendimentos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'contrato_id': self.contrato_id,
            'veterinario_id': self.veterinario_id,
            'animal_id': self.animal_id,
            'data_atendimento': self.data_atendimento.isoformat() if self.data_atendimento else None,
            'tipo_atendimento': self.tipo_atendimento,
            'duracao_minutos': self.duracao_minutos,
            'descricao': self.descricao,
            'observacoes': self.observacoes,
            'valor_cobrado': float(self.valor_cobrado),
            'forma_cobranca': self.forma_cobranca,
            'status': self.status,
            'data_faturamento': self.data_faturamento.isoformat() if self.data_faturamento else None
        }

class FaturaVaaS(db.Model):
    """Faturas mensais do serviço VaaS"""
    __tablename__ = 'faturas_vaas'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(50), nullable=False)
    assinatura_id = db.Column(db.Integer, db.ForeignKey('assinaturas_vaas.id'), nullable=False)
    
    # Período da fatura
    mes_referencia = db.Column(db.Integer, nullable=False)  # 1-12
    ano_referencia = db.Column(db.Integer, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    
    # Valores
    valor_plano = db.Column(db.Numeric(10, 2), nullable=False)
    valor_atendimentos = db.Column(db.Numeric(10, 2), default=0)
    valor_adicional = db.Column(db.Numeric(10, 2), default=0)
    desconto = db.Column(db.Numeric(10, 2), default=0)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Status
    status = db.Column(db.String(50), default='pendente')  # pendente, paga, vencida, cancelada
    data_pagamento = db.Column(db.DateTime)
    metodo_pagamento = db.Column(db.String(50))
    
    # Detalhes
    detalhes_cobranca = db.Column(db.Text)  # JSON com detalhes dos atendimentos
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    assinatura = db.relationship('AssinaturaVaaS', backref='faturas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'assinatura_id': self.assinatura_id,
            'mes_referencia': self.mes_referencia,
            'ano_referencia': self.ano_referencia,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'valor_plano': float(self.valor_plano),
            'valor_atendimentos': float(self.valor_atendimentos),
            'valor_adicional': float(self.valor_adicional),
            'desconto': float(self.desconto),
            'valor_total': float(self.valor_total),
            'status': self.status,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'metodo_pagamento': self.metodo_pagamento,
            'detalhes_cobranca': json.loads(self.detalhes_cobranca) if self.detalhes_cobranca else {},
            'observacoes': self.observacoes
        }

class MetricaVaaS(db.Model):
    """Métricas e analytics do serviço VaaS"""
    __tablename__ = 'metricas_vaas'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(50), nullable=False)
    data_metrica = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    
    # Métricas de uso
    total_atendimentos = db.Column(db.Integer, default=0)
    total_consultas = db.Column(db.Integer, default=0)
    total_procedimentos = db.Column(db.Integer, default=0)
    tempo_total_atendimento = db.Column(db.Integer, default=0)  # em minutos
    
    # Métricas financeiras
    receita_dia = db.Column(db.Numeric(10, 2), default=0)
    custo_veterinarios = db.Column(db.Numeric(10, 2), default=0)
    economia_gerada = db.Column(db.Numeric(10, 2), default=0)
    
    # Métricas de satisfação
    nota_satisfacao_media = db.Column(db.Numeric(3, 2))
    veterinarios_ativos = db.Column(db.Integer, default=0)
    taxa_utilizacao = db.Column(db.Numeric(5, 2), default=0)  # % de uso do plano
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'data_metrica': self.data_metrica.isoformat() if self.data_metrica else None,
            'total_atendimentos': self.total_atendimentos,
            'total_consultas': self.total_consultas,
            'total_procedimentos': self.total_procedimentos,
            'tempo_total_atendimento': self.tempo_total_atendimento,
            'receita_dia': float(self.receita_dia),
            'custo_veterinarios': float(self.custo_veterinarios),
            'economia_gerada': float(self.economia_gerada),
            'nota_satisfacao_media': float(self.nota_satisfacao_media) if self.nota_satisfacao_media else None,
            'veterinarios_ativos': self.veterinarios_ativos,
            'taxa_utilizacao': float(self.taxa_utilizacao)
        }
