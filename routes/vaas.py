from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, date
from decimal import Decimal
import json
import calendar

from models.user import db, Usuario
from models.vaas import (
    PlanoVaaS, AssinaturaVaaS, ContratoVeterinario, 
    AtendimentoVaaS, FaturaVaaS, MetricaVaaS
)
from auth.middleware import role_required, tenant_access_required, financial_access_required

vaas_bp = Blueprint('vaas', __name__)

@vaas_bp.route('/planos', methods=['GET'])
@jwt_required()
def get_planos_vaas():
    """Listar planos VaaS disponíveis"""
    planos = PlanoVaaS.query.filter_by(ativo=True).all()
    return jsonify([plano.to_dict() for plano in planos])

@vaas_bp.route('/assinatura', methods=['GET'])
@jwt_required()
@tenant_access_required
def get_assinatura_atual(current_user, tenant_id):
    """Obter assinatura VaaS atual do tenant"""
    assinatura = AssinaturaVaaS.query.filter_by(
        tenant_id=tenant_id,
        status='ativa'
    ).first()
    
    if not assinatura:
        return jsonify({'message': 'Nenhuma assinatura ativa encontrada'}), 404
    
    return jsonify(assinatura.to_dict())

@vaas_bp.route('/assinatura', methods=['POST'])
@jwt_required()
@role_required(['proprietario'])
def criar_assinatura():
    """Criar nova assinatura VaaS"""
    data = request.get_json()
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(int(user_id))
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    plano_id = data.get('plano_id')
    if not plano_id:
        return jsonify({'error': 'ID do plano é obrigatório'}), 400
    
    plano = PlanoVaaS.query.get(plano_id)
    if not plano:
        return jsonify({'error': 'Plano não encontrado'}), 404
    
    # Verificar se já existe assinatura ativa
    assinatura_existente = AssinaturaVaaS.query.filter_by(
        tenant_id=usuario.tenant_id,
        status='ativa'
    ).first()
    
    if assinatura_existente:
        return jsonify({'error': 'Já existe uma assinatura ativa'}), 400
    
    # Criar nova assinatura
    assinatura = AssinaturaVaaS(
        tenant_id=usuario.tenant_id,
        proprietario_id=usuario.id,
        plano_id=plano_id,
        data_inicio=datetime.utcnow(),
        data_fim=datetime.utcnow() + timedelta(days=30),  # 30 dias iniciais
        status='ativa'
    )
    
    db.session.add(assinatura)
    db.session.commit()
    
    return jsonify({
        'message': 'Assinatura criada com sucesso',
        'assinatura': assinatura.to_dict()
    }), 201

@vaas_bp.route('/veterinarios', methods=['GET'])
@jwt_required()
@tenant_access_required
def get_veterinarios_contratados(current_user, tenant_id):
    """Listar veterinários contratados via VaaS"""
    contratos = ContratoVeterinario.query.filter_by(
        tenant_id=tenant_id,
        status='ativo'
    ).all()
    
    veterinarios = []
    for contrato in contratos:
        veterinario = Usuario.query.get(contrato.veterinario_id)
        if veterinario:
            vet_data = veterinario.to_dict()
            vet_data['contrato'] = contrato.to_dict()
            veterinarios.append(vet_data)
    
    return jsonify(veterinarios)

@vaas_bp.route('/veterinarios/contratar', methods=['POST'])
@jwt_required()
@role_required(['proprietario'])
def contratar_veterinario():
    """Contratar um veterinário via VaaS"""
    data = request.get_json()
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(int(user_id))
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    # Verificar assinatura ativa
    assinatura = AssinaturaVaaS.query.filter_by(
        tenant_id=usuario.tenant_id,
        status='ativa'
    ).first()
    
    if not assinatura or not assinatura.is_ativa():
        return jsonify({'error': 'Assinatura VaaS inativa ou inexistente'}), 400
    
    # Verificar limite de veterinários
    contratos_ativos = ContratoVeterinario.query.filter_by(
        tenant_id=usuario.tenant_id,
        status='ativo'
    ).count()
    
    if contratos_ativos >= assinatura.plano.max_veterinarios:
        return jsonify({'error': 'Limite de veterinários atingido para o plano atual'}), 400
    
    veterinario_id = data.get('veterinario_id')
    if not veterinario_id:
        return jsonify({'error': 'ID do veterinário é obrigatório'}), 400
    
    veterinario = Usuario.query.get(veterinario_id)
    if not veterinario or veterinario.role != 'veterinario':
        return jsonify({'error': 'Veterinário não encontrado'}), 404
    
    # Verificar se já existe contrato ativo
    contrato_existente = ContratoVeterinario.query.filter_by(
        tenant_id=usuario.tenant_id,
        veterinario_id=veterinario_id,
        status='ativo'
    ).first()
    
    if contrato_existente:
        return jsonify({'error': 'Veterinário já contratado'}), 400
    
    # Criar contrato
    contrato = ContratoVeterinario(
        tenant_id=usuario.tenant_id,
        proprietario_id=usuario.id,
        veterinario_id=veterinario_id,
        assinatura_id=assinatura.id,
        data_inicio=datetime.utcnow(),
        status='ativo',
        valor_hora=Decimal(data.get('valor_hora', '150.00')),
        valor_consulta=Decimal(data.get('valor_consulta', '200.00')),
        valor_procedimento=Decimal(data.get('valor_procedimento', '300.00'))
    )
    
    db.session.add(contrato)
    
    # Atualizar contador na assinatura
    assinatura.veterinarios_contratados = contratos_ativos + 1
    
    # Associar veterinário ao tenant
    veterinario.tenant_id = usuario.tenant_id
    
    db.session.commit()
    
    return jsonify({
        'message': 'Veterinário contratado com sucesso',
        'contrato': contrato.to_dict()
    }), 201

@vaas_bp.route('/atendimentos', methods=['GET'])
@jwt_required()
@tenant_access_required
def get_atendimentos(current_user, tenant_id):
    """Listar atendimentos VaaS"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    atendimentos = AtendimentoVaaS.query.filter_by(
        tenant_id=tenant_id
    ).order_by(AtendimentoVaaS.data_atendimento.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'atendimentos': [atendimento.to_dict() for atendimento in atendimentos.items],
        'total': atendimentos.total,
        'pages': atendimentos.pages,
        'current_page': page
    })

@vaas_bp.route('/atendimentos', methods=['POST'])
@jwt_required()
@role_required(['veterinario', 'proprietario'])
def registrar_atendimento():
    """Registrar novo atendimento VaaS"""
    data = request.get_json()
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(int(user_id))
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    # Se for veterinário, buscar contrato ativo
    if usuario.role == 'veterinario':
        contrato = ContratoVeterinario.query.filter_by(
            tenant_id=usuario.tenant_id,
            veterinario_id=usuario.id,
            status='ativo'
        ).first()
        
        if not contrato:
            return jsonify({'error': 'Contrato VaaS não encontrado'}), 404
    else:
        # Se for proprietário, buscar contrato pelo veterinário especificado
        veterinario_id = data.get('veterinario_id')
        if not veterinario_id:
            return jsonify({'error': 'ID do veterinário é obrigatório'}), 400
        
        contrato = ContratoVeterinario.query.filter_by(
            tenant_id=usuario.tenant_id,
            veterinario_id=veterinario_id,
            status='ativo'
        ).first()
        
        if not contrato:
            return jsonify({'error': 'Contrato VaaS não encontrado'}), 404
    
    # Calcular valor baseado no tipo de atendimento
    tipo_atendimento = data.get('tipo_atendimento', 'consulta')
    duracao_minutos = data.get('duracao_minutos', 60)
    
    if tipo_atendimento == 'consulta':
        valor_cobrado = contrato.valor_consulta
        forma_cobranca = 'consulta'
    elif tipo_atendimento == 'procedimento':
        valor_cobrado = contrato.valor_procedimento
        forma_cobranca = 'procedimento'
    else:
        # Cobrança por hora
        valor_cobrado = contrato.valor_hora * (Decimal(duracao_minutos) / 60)
        forma_cobranca = 'hora'
    
    # Criar atendimento
    atendimento = AtendimentoVaaS(
        tenant_id=usuario.tenant_id,
        contrato_id=contrato.id,
        veterinario_id=contrato.veterinario_id,
        animal_id=data.get('animal_id'),
        data_atendimento=datetime.utcnow(),
        tipo_atendimento=tipo_atendimento,
        duracao_minutos=duracao_minutos,
        descricao=data.get('descricao', ''),
        observacoes=data.get('observacoes', ''),
        valor_cobrado=valor_cobrado,
        forma_cobranca=forma_cobranca,
        status='realizado'
    )
    
    db.session.add(atendimento)
    db.session.commit()
    
    return jsonify({
        'message': 'Atendimento registrado com sucesso',
        'atendimento': atendimento.to_dict()
    }), 201

@vaas_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@tenant_access_required
def get_dashboard_vaas(current_user, tenant_id):
    """Dashboard com métricas VaaS"""
    # Buscar assinatura ativa
    assinatura = AssinaturaVaaS.query.filter_by(
        tenant_id=tenant_id,
        status='ativa'
    ).first()
    
    if not assinatura:
        return jsonify({'error': 'Assinatura VaaS não encontrada'}), 404
    
    # Métricas do mês atual
    hoje = date.today()
    inicio_mes = date(hoje.year, hoje.month, 1)
    
    # Atendimentos do mês
    atendimentos_mes = AtendimentoVaaS.query.filter(
        AtendimentoVaaS.tenant_id == tenant_id,
        AtendimentoVaaS.data_atendimento >= inicio_mes
    ).all()
    
    # Veterinários ativos
    veterinarios_ativos = ContratoVeterinario.query.filter_by(
        tenant_id=tenant_id,
        status='ativo'
    ).count()
    
    # Calcular métricas
    total_atendimentos = len(atendimentos_mes)
    total_consultas = len([a for a in atendimentos_mes if a.tipo_atendimento == 'consulta'])
    total_procedimentos = len([a for a in atendimentos_mes if a.tipo_atendimento == 'procedimento'])
    
    valor_total_mes = sum([float(a.valor_cobrado) for a in atendimentos_mes])
    tempo_total = sum([a.duracao_minutos or 0 for a in atendimentos_mes])
    
    # Taxa de utilização do plano
    limite_consultas = assinatura.get_limite_consultas()
    limite_procedimentos = assinatura.get_limite_procedimentos()
    
    taxa_utilizacao_consultas = (total_consultas / limite_consultas * 100) if limite_consultas else 0
    taxa_utilizacao_procedimentos = (total_procedimentos / limite_procedimentos * 100) if limite_procedimentos else 0
    
    # Economia estimada (comparado com contratação direta)
    custo_contratacao_direta = veterinarios_ativos * 8000  # R$ 8.000 por veterinário/mês
    custo_vaas = float(assinatura.plano.preco_mensal) + valor_total_mes
    economia_estimada = custo_contratacao_direta - custo_vaas
    
    return jsonify({
        'assinatura': assinatura.to_dict(),
        'metricas_mes': {
            'total_atendimentos': total_atendimentos,
            'total_consultas': total_consultas,
            'total_procedimentos': total_procedimentos,
            'valor_total_mes': valor_total_mes,
            'tempo_total_horas': round(tempo_total / 60, 1),
            'veterinarios_ativos': veterinarios_ativos,
            'taxa_utilizacao_consultas': round(taxa_utilizacao_consultas, 1),
            'taxa_utilizacao_procedimentos': round(taxa_utilizacao_procedimentos, 1),
            'economia_estimada': economia_estimada,
            'custo_vaas': custo_vaas,
            'custo_contratacao_direta': custo_contratacao_direta
        },
        'limites_plano': {
            'max_veterinarios': assinatura.plano.max_veterinarios,
            'max_consultas_mes': limite_consultas,
            'max_procedimentos_mes': limite_procedimentos,
            'veterinarios_utilizados': veterinarios_ativos,
            'consultas_utilizadas': total_consultas,
            'procedimentos_utilizados': total_procedimentos
        },
        'dias_restantes': assinatura.dias_restantes()
    })

@vaas_bp.route('/faturas', methods=['GET'])
@jwt_required()
@financial_access_required
def get_faturas_vaas(current_user, tenant_id):
    """Listar faturas VaaS"""
    faturas = FaturaVaaS.query.filter_by(
        tenant_id=tenant_id
    ).order_by(FaturaVaaS.ano_referencia.desc(), FaturaVaaS.mes_referencia.desc()).all()
    
    return jsonify([fatura.to_dict() for fatura in faturas])

@vaas_bp.route('/faturas/gerar', methods=['POST'])
@jwt_required()
@role_required(['proprietario', 'admin'])
def gerar_fatura_mes():
    """Gerar fatura do mês para assinatura VaaS"""
    data = request.get_json()
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(int(user_id))
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    mes = data.get('mes', date.today().month)
    ano = data.get('ano', date.today().year)
    
    # Buscar assinatura ativa
    assinatura = AssinaturaVaaS.query.filter_by(
        tenant_id=usuario.tenant_id,
        status='ativa'
    ).first()
    
    if not assinatura:
        return jsonify({'error': 'Assinatura VaaS não encontrada'}), 404
    
    # Verificar se já existe fatura para o período
    fatura_existente = FaturaVaaS.query.filter_by(
        tenant_id=usuario.tenant_id,
        mes_referencia=mes,
        ano_referencia=ano
    ).first()
    
    if fatura_existente:
        return jsonify({'error': 'Fatura já existe para este período'}), 400
    
    # Buscar atendimentos do período
    inicio_mes = date(ano, mes, 1)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    fim_mes = date(ano, mes, ultimo_dia)
    
    atendimentos = AtendimentoVaaS.query.filter(
        AtendimentoVaaS.tenant_id == usuario.tenant_id,
        AtendimentoVaaS.data_atendimento >= inicio_mes,
        AtendimentoVaaS.data_atendimento <= fim_mes,
        AtendimentoVaaS.status == 'realizado'
    ).all()
    
    # Calcular valores
    valor_plano = assinatura.plano.preco_mensal
    valor_atendimentos = sum([float(a.valor_cobrado) for a in atendimentos])
    valor_total = valor_plano + valor_atendimentos
    
    # Criar fatura
    fatura = FaturaVaaS(
        tenant_id=usuario.tenant_id,
        assinatura_id=assinatura.id,
        mes_referencia=mes,
        ano_referencia=ano,
        data_vencimento=date(ano, mes, 10),  # Vencimento dia 10
        valor_plano=valor_plano,
        valor_atendimentos=valor_atendimentos,
        valor_total=valor_total,
        status='pendente',
        detalhes_cobranca=json.dumps([a.to_dict() for a in atendimentos])
    )
    
    db.session.add(fatura)
    
    # Marcar atendimentos como faturados
    for atendimento in atendimentos:
        atendimento.status = 'faturado'
        atendimento.data_faturamento = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Fatura gerada com sucesso',
        'fatura': fatura.to_dict()
    }), 201

@vaas_bp.route('/analytics', methods=['GET'])
@jwt_required()
@tenant_access_required
def get_analytics_vaas(current_user, tenant_id):
    """Analytics e relatórios VaaS"""
    dias = request.args.get('dias', 30, type=int)
    data_inicio = date.today() - timedelta(days=dias)
    
    # Buscar métricas do período
    metricas = MetricaVaaS.query.filter(
        MetricaVaaS.tenant_id == tenant_id,
        MetricaVaaS.data_metrica >= data_inicio
    ).order_by(MetricaVaaS.data_metrica).all()
    
    # Buscar atendimentos do período para análise
    atendimentos = AtendimentoVaaS.query.filter(
        AtendimentoVaaS.tenant_id == tenant_id,
        AtendimentoVaaS.data_atendimento >= data_inicio
    ).all()
    
    # Agrupar por data
    atendimentos_por_dia = {}
    receita_por_dia = {}
    
    for atendimento in atendimentos:
        data_str = atendimento.data_atendimento.date().isoformat()
        
        if data_str not in atendimentos_por_dia:
            atendimentos_por_dia[data_str] = 0
            receita_por_dia[data_str] = 0
        
        atendimentos_por_dia[data_str] += 1
        receita_por_dia[data_str] += float(atendimento.valor_cobrado)
    
    # Veterinários mais ativos
    veterinarios_stats = {}
    for atendimento in atendimentos:
        vet_id = atendimento.veterinario_id
        if vet_id not in veterinarios_stats:
            veterinario = Usuario.query.get(vet_id)
            veterinarios_stats[vet_id] = {
                'nome': veterinario.nome if veterinario else 'Desconhecido',
                'atendimentos': 0,
                'receita': 0,
                'tempo_total': 0
            }
        
        veterinarios_stats[vet_id]['atendimentos'] += 1
        veterinarios_stats[vet_id]['receita'] += float(atendimento.valor_cobrado)
        veterinarios_stats[vet_id]['tempo_total'] += atendimento.duracao_minutos or 0
    
    return jsonify({
        'periodo': {
            'data_inicio': data_inicio.isoformat(),
            'data_fim': date.today().isoformat(),
            'dias': dias
        },
        'resumo': {
            'total_atendimentos': len(atendimentos),
            'receita_total': sum(receita_por_dia.values()),
            'tempo_total_horas': sum([a.duracao_minutos or 0 for a in atendimentos]) / 60,
            'veterinarios_ativos': len(veterinarios_stats)
        },
        'atendimentos_por_dia': atendimentos_por_dia,
        'receita_por_dia': receita_por_dia,
        'veterinarios_stats': list(veterinarios_stats.values()),
        'metricas_historicas': [metrica.to_dict() for metrica in metricas]
    })
