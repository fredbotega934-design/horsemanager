from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
import calendar
from sqlalchemy import func, extract, and_, or_

from models.user import db, Usuario
from models.financeiro import (
    CategoriaFinanceira, TransacaoFinanceira, OrcamentoAnual,
    CentroCusto, AnaliseROI, RelatorioFinanceiro, FluxoCaixa
)
from auth.middleware import role_required, tenant_access_required, financial_access_required

financeiro_avancado_bp = Blueprint('financeiro_avancado', __name__)

@financeiro_avancado_bp.route('/categorias', methods=['GET'])
@jwt_required()
@tenant_access_required
def get_categorias(current_user, tenant_id):
    """Listar categorias financeiras"""
    categorias = CategoriaFinanceira.query.filter_by(
        tenant_id=tenant_id,
        ativa=True
    ).all()
    
    return jsonify([categoria.to_dict() for categoria in categorias])

@financeiro_avancado_bp.route('/categorias', methods=['POST'])
@jwt_required()
@financial_access_required
def criar_categoria(current_user, tenant_id):
    """Criar nova categoria financeira"""
    data = request.get_json()
    
    categoria = CategoriaFinanceira(
        tenant_id=tenant_id,
        nome=data.get('nome'),
        tipo=data.get('tipo'),
        descricao=data.get('descricao', ''),
        cor=data.get('cor', '#3B82F6')
    )
    
    db.session.add(categoria)
    db.session.commit()
    
    return jsonify({
        'message': 'Categoria criada com sucesso',
        'categoria': categoria.to_dict()
    }), 201

@financeiro_avancado_bp.route('/transacoes', methods=['GET'])
@jwt_required()
@financial_access_required
def get_transacoes(current_user, tenant_id):
    """Listar transações financeiras com filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    tipo = request.args.get('tipo')  # receita, despesa
    categoria_id = request.args.get('categoria_id', type=int)
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    status = request.args.get('status')
    
    query = TransacaoFinanceira.query.filter_by(tenant_id=tenant_id)
    
    # Aplicar filtros
    if tipo:
        query = query.filter(TransacaoFinanceira.tipo == tipo)
    
    if categoria_id:
        query = query.filter(TransacaoFinanceira.categoria_id == categoria_id)
    
    if data_inicio:
        query = query.filter(TransacaoFinanceira.data_transacao >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
    
    if data_fim:
        query = query.filter(TransacaoFinanceira.data_transacao <= datetime.strptime(data_fim, '%Y-%m-%d').date())
    
    if status:
        query = query.filter(TransacaoFinanceira.status == status)
    
    transacoes = query.order_by(TransacaoFinanceira.data_transacao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'transacoes': [transacao.to_dict() for transacao in transacoes.items],
        'total': transacoes.total,
        'pages': transacoes.pages,
        'current_page': page
    })

@financeiro_avancado_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@financial_access_required
def get_dashboard_financeiro(current_user, tenant_id):
    """Dashboard financeiro com KPIs principais"""
    # Período padrão: mês atual
    hoje = date.today()
    inicio_mes = date(hoje.year, hoje.month, 1)
    fim_mes = date(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])
    
    # Dados simulados para demonstração
    dados_simulados = {
        'receitas_mes': 45000.00,
        'despesas_mes': 28000.00,
        'lucro_mes': 17000.00,
        'margem_lucro': 37.8,
        'contas_receber': 12500.00,
        'contas_pagar': 8300.00,
        'fluxo_projetado': 25000.00,
        'receitas_categoria': [
            {'categoria': 'Venda de Animais', 'valor': 25000.00},
            {'categoria': 'Serviços Reprodutivos', 'valor': 15000.00},
            {'categoria': 'Aluguel de Pasto', 'valor': 5000.00}
        ],
        'despesas_categoria': [
            {'categoria': 'Alimentação', 'valor': 12000.00},
            {'categoria': 'Veterinário', 'valor': 8000.00},
            {'categoria': 'Manutenção', 'valor': 5000.00},
            {'categoria': 'Funcionários', 'valor': 3000.00}
        ]
    }
    
    return jsonify({
        'periodo': {
            'inicio': inicio_mes.isoformat(),
            'fim': fim_mes.isoformat()
        },
        'kpis': dados_simulados
    })

@financeiro_avancado_bp.route('/relatorios/fluxo-caixa', methods=['GET'])
@jwt_required()
@financial_access_required
def relatorio_fluxo_caixa(current_user, tenant_id):
    """Relatório de fluxo de caixa"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    if not data_inicio or not data_fim:
        # Padrão: últimos 30 dias
        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=30)
    else:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    
    # Dados simulados para demonstração
    fluxo_dados = []
    data_atual = data_inicio
    saldo_acumulado = 15000.00  # Saldo inicial simulado
    
    while data_atual <= data_fim:
        # Simular entradas e saídas variáveis
        dia_mes = data_atual.day
        entradas = 1500 + (dia_mes * 50) + ((dia_mes % 7) * 200)
        saidas = 1200 + (dia_mes * 30) + ((dia_mes % 5) * 150)
        
        saldo_final = saldo_acumulado + entradas - saidas
        
        fluxo_dados.append({
            'data_referencia': data_atual.isoformat(),
            'saldo_inicial': round(saldo_acumulado, 2),
            'entradas': round(entradas, 2),
            'saidas': round(saidas, 2),
            'saldo_final': round(saldo_final, 2)
        })
        
        saldo_acumulado = saldo_final
        data_atual += timedelta(days=1)
    
    # Calcular resumo
    total_entradas = sum([f['entradas'] for f in fluxo_dados])
    total_saidas = sum([f['saidas'] for f in fluxo_dados])
    saldo_inicial = fluxo_dados[0]['saldo_inicial'] if fluxo_dados else 0
    saldo_final = fluxo_dados[-1]['saldo_final'] if fluxo_dados else 0
    
    return jsonify({
        'periodo': {
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat()
        },
        'resumo': {
            'saldo_inicial': saldo_inicial,
            'total_entradas': round(total_entradas, 2),
            'total_saidas': round(total_saidas, 2),
            'saldo_final': round(saldo_final, 2),
            'variacao': round(saldo_final - saldo_inicial, 2)
        },
        'dados_diarios': fluxo_dados
    })

@financeiro_avancado_bp.route('/relatorios/dre', methods=['GET'])
@jwt_required()
@financial_access_required
def relatorio_dre(current_user, tenant_id):
    """Demonstrativo de Resultado do Exercício (DRE)"""
    ano = request.args.get('ano', date.today().year, type=int)
    mes = request.args.get('mes', type=int)
    
    # Definir período
    if mes:
        data_inicio = date(ano, mes, 1)
        data_fim = date(ano, mes, calendar.monthrange(ano, mes)[1])
    else:
        data_inicio = date(ano, 1, 1)
        data_fim = date(ano, 12, 31)
    
    # Dados simulados para demonstração
    receitas = [
        {'categoria': 'Venda de Animais', 'valor': 180000.00},
        {'categoria': 'Serviços Reprodutivos', 'valor': 95000.00},
        {'categoria': 'Aluguel de Pasto', 'valor': 36000.00},
        {'categoria': 'Consultoria', 'valor': 24000.00}
    ]
    
    despesas = [
        {'categoria': 'Alimentação', 'valor': 85000.00},
        {'categoria': 'Veterinário', 'valor': 45000.00},
        {'categoria': 'Funcionários', 'valor': 72000.00},
        {'categoria': 'Manutenção', 'valor': 28000.00},
        {'categoria': 'Impostos', 'valor': 15000.00},
        {'categoria': 'Energia e Água', 'valor': 12000.00}
    ]
    
    # Calcular totais
    total_receitas = sum([r['valor'] for r in receitas])
    total_despesas = sum([d['valor'] for d in despesas])
    lucro_bruto = total_receitas - total_despesas
    margem_lucro = (lucro_bruto / total_receitas * 100) if total_receitas > 0 else 0
    
    return jsonify({
        'periodo': {
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat(),
            'ano': ano,
            'mes': mes
        },
        'receitas': receitas,
        'despesas': despesas,
        'resumo': {
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'lucro_bruto': lucro_bruto,
            'margem_lucro': round(margem_lucro, 2)
        }
    })

@financeiro_avancado_bp.route('/analises-roi', methods=['GET'])
@jwt_required()
@financial_access_required
def get_analises_roi(current_user, tenant_id):
    """Listar análises de ROI"""
    # Dados simulados para demonstração
    analises_simuladas = [
        {
            'id': 1,
            'nome': 'Aquisição Garanhão Premium',
            'descricao': 'Investimento em garanhão de linhagem superior para melhorar genética do plantel',
            'investimento_inicial': 250000.00,
            'custos_operacionais': 45000.00,
            'receitas_geradas': 180000.00,
            'roi_percentual': 72.0,
            'payback_meses': 18,
            'tipo_investimento': 'reproducao',
            'status': 'ativo'
        },
        {
            'id': 2,
            'nome': 'Modernização Estábulo',
            'descricao': 'Reforma e modernização das instalações para melhor conforto animal',
            'investimento_inicial': 120000.00,
            'custos_operacionais': 15000.00,
            'receitas_geradas': 85000.00,
            'roi_percentual': 41.7,
            'payback_meses': 24,
            'tipo_investimento': 'infraestrutura',
            'status': 'ativo'
        },
        {
            'id': 3,
            'nome': 'Sistema de Irrigação',
            'descricao': 'Instalação de sistema automatizado de irrigação para pastagens',
            'investimento_inicial': 80000.00,
            'custos_operacionais': 12000.00,
            'receitas_geradas': 45000.00,
            'roi_percentual': 28.1,
            'payback_meses': 30,
            'tipo_investimento': 'infraestrutura',
            'status': 'ativo'
        }
    ]
    
    return jsonify(analises_simuladas)

@financeiro_avancado_bp.route('/relatorios/comparativo-mensal', methods=['GET'])
@jwt_required()
@financial_access_required
def relatorio_comparativo_mensal(current_user, tenant_id):
    """Relatório comparativo mensal dos últimos 12 meses"""
    hoje = date.today()
    
    dados_mensais = []
    
    # Dados simulados para demonstração
    base_receita = 40000
    base_despesa = 25000
    
    for i in range(12):
        # Calcular mês e ano
        mes_atual = hoje.month - i
        ano_atual = hoje.year
        
        if mes_atual <= 0:
            mes_atual += 12
            ano_atual -= 1
        
        # Simular variação sazonal
        fator_sazonal = 1.0 + (0.2 * (mes_atual % 4 - 2) / 2)  # Variação de ±20%
        variacao_aleatoria = 1.0 + ((i % 7 - 3) * 0.05)  # Variação de ±15%
        
        receitas = base_receita * fator_sazonal * variacao_aleatoria
        despesas = base_despesa * (1.0 + ((i % 5 - 2) * 0.03))  # Variação menor nas despesas
        lucro = receitas - despesas
        
        dados_mensais.append({
            'mes': mes_atual,
            'ano': ano_atual,
            'mes_nome': calendar.month_name[mes_atual],
            'receitas': round(receitas, 2),
            'despesas': round(despesas, 2),
            'lucro': round(lucro, 2),
            'margem_lucro': round((lucro / receitas * 100) if receitas > 0 else 0, 2)
        })
    
    # Inverter para ordem cronológica
    dados_mensais.reverse()
    
    # Calcular médias
    media_receitas = sum([d['receitas'] for d in dados_mensais]) / 12
    media_despesas = sum([d['despesas'] for d in dados_mensais]) / 12
    media_lucro = sum([d['lucro'] for d in dados_mensais]) / 12
    
    return jsonify({
        'dados_mensais': dados_mensais,
        'medias': {
            'receitas': round(media_receitas, 2),
            'despesas': round(media_despesas, 2),
            'lucro': round(media_lucro, 2),
            'margem_lucro': round((media_lucro / media_receitas * 100) if media_receitas > 0 else 0, 2)
        }
    })

@financeiro_avancado_bp.route('/relatorios/performance-categorias', methods=['GET'])
@jwt_required()
@financial_access_required
def relatorio_performance_categorias(current_user, tenant_id):
    """Relatório de performance por categorias"""
    periodo = request.args.get('periodo', '12')  # meses
    
    # Dados simulados para demonstração
    categorias_receita = [
        {
            'categoria': 'Venda de Animais',
            'valor_atual': 180000.00,
            'valor_anterior': 165000.00,
            'crescimento': 9.1,
            'participacao': 53.7
        },
        {
            'categoria': 'Serviços Reprodutivos',
            'valor_atual': 95000.00,
            'valor_anterior': 88000.00,
            'crescimento': 8.0,
            'participacao': 28.4
        },
        {
            'categoria': 'Aluguel de Pasto',
            'valor_atual': 36000.00,
            'valor_anterior': 34000.00,
            'crescimento': 5.9,
            'participacao': 10.7
        },
        {
            'categoria': 'Consultoria',
            'valor_atual': 24000.00,
            'valor_anterior': 18000.00,
            'crescimento': 33.3,
            'participacao': 7.2
        }
    ]
    
    categorias_despesa = [
        {
            'categoria': 'Alimentação',
            'valor_atual': 85000.00,
            'valor_anterior': 82000.00,
            'crescimento': 3.7,
            'participacao': 33.1
        },
        {
            'categoria': 'Funcionários',
            'valor_atual': 72000.00,
            'valor_anterior': 68000.00,
            'crescimento': 5.9,
            'participacao': 28.0
        },
        {
            'categoria': 'Veterinário',
            'valor_atual': 45000.00,
            'valor_anterior': 52000.00,
            'crescimento': -13.5,
            'participacao': 17.5
        },
        {
            'categoria': 'Manutenção',
            'valor_atual': 28000.00,
            'valor_anterior': 25000.00,
            'crescimento': 12.0,
            'participacao': 10.9
        }
    ]
    
    return jsonify({
        'periodo_meses': int(periodo),
        'receitas': {
            'categorias': categorias_receita,
            'total_atual': sum([c['valor_atual'] for c in categorias_receita]),
            'total_anterior': sum([c['valor_anterior'] for c in categorias_receita]),
            'crescimento_total': 10.2
        },
        'despesas': {
            'categorias': categorias_despesa,
            'total_atual': sum([c['valor_atual'] for c in categorias_despesa]),
            'total_anterior': sum([c['valor_anterior'] for c in categorias_despesa]),
            'crescimento_total': 2.1
        }
    })
