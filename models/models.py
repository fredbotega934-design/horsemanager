# Importar modelos do arquivo user.py
from .user import db, Usuario, Egua, Garanhao, Embriao, TransferenciaEmbriao, Gestacao, Parto

# Modelos adicionais específicos do sistema legado
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    localizacao = db.Column(db.String(100))
    endereco_completo = db.Column(db.String(255))
    cep = db.Column(db.String(10))
    cnpj_cpf = db.Column(db.String(20), unique=True)
    responsavel_tecnico = db.Column(db.String(100))
    crmv_responsavel = db.Column(db.String(50))
    tipo_cliente = db.Column(db.String(50)) # haras, central, particular
    observacoes = db.Column(db.Text)
    data_cadastro = db.Column(db.String(10))
    status = db.Column(db.String(50)) # ativo, inativo, suspenso
    contrato_vigente = db.Column(db.Boolean)
    data_inicio_contrato = db.Column(db.String(10))
    data_fim_contrato = db.Column(db.String(10))

class ProcedimentoOPU(db.Model):
    __tablename__ = 'procedimentos_opu'
    id = db.Column(db.Integer, primary_key=True)
    egua_id = db.Column(db.Integer, db.ForeignKey('eguas.id'), nullable=False)
    tipo_procedimento = db.Column(db.String(50))
    data_procedimento = db.Column(db.String(10))
    foliculos_aspirados = db.Column(db.Integer)
    ccos_recuperados = db.Column(db.Integer)
    taxa_recuperacao = db.Column(db.Float)
    ciclo_estral = db.Column(db.String(50))
    dia_ciclo = db.Column(db.Integer)
    medicacao_utilizada = db.Column(db.String(255))
    protocolo_hormonal = db.Column(db.String(255))
    veterinario_responsavel = db.Column(db.String(100))
    crmv_veterinario = db.Column(db.String(50))
    tecnico_responsavel = db.Column(db.String(100))
    equipamento_utilizado = db.Column(db.String(100))
    complicacoes = db.Column(db.Text)
    pressao_aspiracao = db.Column(db.String(50))
    rotacao_agulha = db.Column(db.String(50))
    metodo_lavagem = db.Column(db.String(50))
    numero_lavagens_foliculo = db.Column(db.Integer)
    medicacao_pos_opu = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    proxima_opu = db.Column(db.String(10))
    tamanhos_foliculos = db.Column(db.String(255)) # JSON string or similar
    qualidade_ccos = db.Column(db.String(255)) # JSON string or similar
    tempo_procedimento = db.Column(db.Integer)
    custo_procedimento = db.Column(db.Float)
    status = db.Column(db.String(50))

class AnaliseLaboratorial(db.Model):
    __tablename__ = 'analises_laboratoriais'
    id = db.Column(db.Integer, primary_key=True)
    egua_id = db.Column(db.Integer, db.ForeignKey('eguas.id'), nullable=False)
    embriao_uid = db.Column(db.String(255), db.ForeignKey('embrioes_transferidos.embriao_uid'), nullable=True)
    tipo_analise = db.Column(db.String(50))
    material_coletado = db.Column(db.String(50))
    data_coleta = db.Column(db.String(10))
    parametros_analisados = db.Column(db.Text) # JSON string or similar
    taxa_maturacao = db.Column(db.Float)
    taxa_clivagem = db.Column(db.Float)
    taxa_blastocisto = db.Column(db.Float)
    laboratorio = db.Column(db.String(100))
    veterinario_solicitante = db.Column(db.String(100))
    resultado_geral = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    custo_analise = db.Column(db.Float)

class Financeiro(db.Model):
    __tablename__ = 'financeiro'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    tipo_transacao = db.Column(db.String(50))
    categoria = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    valor = db.Column(db.Float)
    data_transacao = db.Column(db.String(10))
    data_vencimento = db.Column(db.String(10))
    status_pagamento = db.Column(db.String(50))
    forma_pagamento = db.Column(db.String(50))
    observacoes = db.Column(db.Text)
