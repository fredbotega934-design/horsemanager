from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
import json

from models.user import db, Usuario
from models.models import Egua, Garanhao, TransferenciaEmbriao
from auth.middleware import role_required, tenant_access_required
from ai.ml_engine import MLEngine, TipoPrevisao

ai_predictions_bp = Blueprint('ai_predictions', __name__)

# Instância global do engine de ML
ml_engine = MLEngine()

@ai_predictions_bp.route('/previsao-prenhez', methods=['GET'])
@jwt_required()
@tenant_access_required
def prever_taxa_prenhez(current_user, tenant_id):
    """Prevê taxa de prenhez baseada em dados históricos"""
    
    # Buscar dados históricos de transferências
    transferencias = TransferenciaEmbriao.query.filter_by(tenant_id=tenant_id).all()
    
    # Processar dados para o modelo
    dados_historicos = []
    if transferencias:
        # Agrupar por mês e calcular taxa de prenhez
        dados_por_mes = {}
        for t in transferencias:
            mes = t.data_transferencia.month if t.data_transferencia else datetime.now().month
            if mes not in dados_por_mes:
                dados_por_mes[mes] = {'total': 0, 'sucessos': 0}
            
            dados_por_mes[mes]['total'] += 1
            if t.resultado == 'prenhez_confirmada':
                dados_por_mes[mes]['sucessos'] += 1
        
        for mes, dados in dados_por_mes.items():
            taxa = (dados['sucessos'] / dados['total'] * 100) if dados['total'] > 0 else 0
            dados_historicos.append({
                'mes': mes,
                'taxa': taxa,
                'temperatura': 28,  # Dados simulados
                'umidade': 70
            })
    
    # Fatores ambientais (podem vir de sensores IoT no futuro)
    fatores_ambientais = {
        'temperatura': request.args.get('temperatura', 28, type=float),
        'umidade': request.args.get('umidade', 70, type=float)
    }
    
    # Gerar previsão
    previsao = ml_engine.prever_taxa_prenhez(dados_historicos, fatores_ambientais)
    
    return jsonify({
        'previsao': {
            'taxa_prenhez_prevista': previsao.valor_previsto,
            'confianca': previsao.confianca,
            'periodo': previsao.periodo,
            'fatores_influencia': previsao.fatores_influencia,
            'recomendacoes': previsao.recomendacoes
        },
        'dados_historicos_utilizados': len(dados_historicos),
        'data_previsao': previsao.data_previsao.isoformat()
    })

@ai_predictions_bp.route('/previsao-receita', methods=['GET'])
@jwt_required()
@tenant_access_required
def prever_receita_mensal(current_user, tenant_id):
    """Prevê receita mensal baseada em histórico financeiro"""
    
    # Dados simulados para demonstração (em produção, viria do módulo financeiro)
    dados_financeiros = [
        {'mes': 1, 'receita': 42000, 'vendas_animais': 25000, 'servicos': 17000},
        {'mes': 2, 'receita': 38000, 'vendas_animais': 22000, 'servicos': 16000},
        {'mes': 3, 'receita': 45000, 'vendas_animais': 28000, 'servicos': 17000},
        {'mes': 4, 'receita': 52000, 'vendas_animais': 32000, 'servicos': 20000},
        {'mes': 5, 'receita': 48000, 'vendas_animais': 30000, 'servicos': 18000},
        {'mes': 6, 'receita': 44000, 'vendas_animais': 26000, 'servicos': 18000}
    ]
    
    # Tendências de mercado (podem vir de APIs externas)
    tendencias_mercado = {
        'crescimento_setor': request.args.get('crescimento_setor', 5.2, type=float),
        'demanda_regional': request.args.get('demanda_regional', 1.1, type=float)
    }
    
    # Gerar previsão
    previsao = ml_engine.prever_receita_mensal(dados_financeiros, tendencias_mercado)
    
    return jsonify({
        'previsao': {
            'receita_prevista': previsao.valor_previsto,
            'confianca': previsao.confianca,
            'periodo': previsao.periodo,
            'fatores_influencia': previsao.fatores_influencia,
            'recomendacoes': previsao.recomendacoes
        },
        'tendencias_mercado': tendencias_mercado,
        'data_previsao': previsao.data_previsao.isoformat()
    })

@ai_predictions_bp.route('/previsao-demanda-vaas', methods=['GET'])
@jwt_required()
@tenant_access_required
def prever_demanda_vaas(current_user, tenant_id):
    """Prevê demanda por serviços VaaS"""
    
    # Dados simulados de utilização VaaS
    dados_utilizacao = [
        {'mes': 1, 'atendimentos': 18, 'veterinarios_ativos': 2, 'satisfacao': 4.5},
        {'mes': 2, 'atendimentos': 22, 'veterinarios_ativos': 2, 'satisfacao': 4.6},
        {'mes': 3, 'atendimentos': 24, 'veterinarios_ativos': 2, 'satisfacao': 4.7},
        {'mes': 4, 'atendimentos': 28, 'veterinarios_ativos': 3, 'satisfacao': 4.8},
        {'mes': 5, 'atendimentos': 26, 'veterinarios_ativos': 2, 'satisfacao': 4.6},
        {'mes': 6, 'atendimentos': 24, 'veterinarios_ativos': 2, 'satisfacao': 4.7}
    ]
    
    # Gerar previsão
    previsao = ml_engine.prever_demanda_vaas(dados_utilizacao)
    
    return jsonify({
        'previsao': {
            'demanda_prevista': previsao.valor_prevista,
            'confianca': previsao.confianca,
            'periodo': previsao.periodo,
            'fatores_influencia': previsao.fatores_influencia,
            'recomendacoes': previsao.recomendacoes
        },
        'utilizacao_atual': dados_utilizacao[-1] if dados_utilizacao else None,
        'data_previsao': previsao.data_previsao.isoformat()
    })

@ai_predictions_bp.route('/recomendacoes-acasalamento', methods=['GET'])
@jwt_required()
@tenant_access_required
def recomendar_acasalamentos(current_user, tenant_id):
    """Recomenda acasalamentos otimizados"""
    
    # Buscar éguas e garanhões disponíveis
    eguas = Egua.query.filter_by(tenant_id=tenant_id).all()
    garanhoes = Garanhao.query.filter_by(tenant_id=tenant_id).all()
    
    # Converter para formato do ML
    eguas_disponiveis = []
    for egua in eguas:
        eguas_disponiveis.append({
            'id': egua.id,
            'nome': egua.nome,
            'idade': egua.idade or 8,
            'linhagem': egua.raca or 'Mangalarga',
            'taxa_prenhez_historica': 80,  # Dados simulados
            'qualidade_genetica': 8.5
        })
    
    garanhoes_disponiveis = []
    for garanhao in garanhoes:
        garanhoes_disponiveis.append({
            'id': garanhao.id,
            'nome': garanhao.nome,
            'idade': garanhao.idade or 10,
            'linhagem': garanhao.raca or 'Mangalarga',
            'taxa_fertilidade': 88,  # Dados simulados
            'qualidade_genetica': 9.0
        })
    
    # Gerar recomendações
    recomendacoes = ml_engine.recomendar_acasalamentos(eguas_disponiveis, garanhoes_disponiveis)
    
    return jsonify({
        'recomendacoes': recomendacoes,
        'total_combinacoes_analisadas': len(eguas_disponiveis) * len(garanhoes_disponiveis),
        'criterios_utilizados': [
            'Compatibilidade genética',
            'Qualidade genética média',
            'Taxa de sucesso histórica',
            'Fator idade'
        ],
        'data_analise': datetime.now().isoformat()
    })

@ai_predictions_bp.route('/otimizacao-alimentacao', methods=['GET'])
@jwt_required()
@tenant_access_required
def otimizar_alimentacao(current_user, tenant_id):
    """Otimiza plano alimentar baseado em IA"""
    
    # Buscar animais do tenant
    eguas = Egua.query.filter_by(tenant_id=tenant_id).all()
    garanhoes = Garanhao.query.filter_by(tenant_id=tenant_id).all()
    
    # Converter para formato do ML
    animais = []
    
    for egua in eguas:
        tipo_animal = 'egua_prenha' if egua.status_reprodutivo == 'prenha' else 'egua_lactante' if egua.status_reprodutivo == 'lactante' else 'egua'
        animais.append({
            'id': egua.id,
            'tipo': tipo_animal,
            'peso': egua.peso or 450,
            'idade': egua.idade or 8,
            'atividade': 'reproducao'
        })
    
    for garanhao in garanhoes:
        animais.append({
            'id': garanhao.id,
            'tipo': 'garanhao',
            'peso': garanhao.peso or 520,
            'idade': garanhao.idade or 10,
            'atividade': 'reproducao'
        })
    
    # Custos de rações (podem vir de API de fornecedores)
    custos_racoes = {
        'feno_premium': 2.50,
        'feno_standard': 1.80,
        'concentrado_reproducao': 3.20,
        'concentrado_manutencao': 2.40,
        'suplemento_mineral': 4.50
    }
    
    # Gerar otimização
    plano_otimizado = ml_engine.otimizar_alimentacao(animais, custos_racoes)
    
    return jsonify({
        'plano_otimizado': plano_otimizado,
        'total_animais': len(animais),
        'economia_percentual': round((plano_otimizado['economia_estimada'] / (plano_otimizado['custo_total_mensal'] + plano_otimizado['economia_estimada'])) * 100, 1),
        'data_otimizacao': datetime.now().isoformat()
    })

@ai_predictions_bp.route('/insights-dashboard', methods=['GET'])
@jwt_required()
@tenant_access_required
def get_insights_dashboard(current_user, tenant_id):
    """Retorna insights consolidados para o dashboard de IA"""
    
    # Gerar múltiplas previsões
    previsao_prenhez = ml_engine.prever_taxa_prenhez([])
    previsao_receita = ml_engine.prever_receita_mensal([])
    previsao_vaas = ml_engine.prever_demanda_vaas([])
    
    # Insights consolidados
    insights = {
        'resumo_previsoes': {
            'taxa_prenhez': {
                'valor': previsao_prenhez.valor_previsto,
                'confianca': previsao_prenhez.confianca,
                'tendencia': 'alta' if previsao_prenhez.valor_previsto > 80 else 'media' if previsao_prenhez.valor_previsto > 70 else 'baixa'
            },
            'receita_mensal': {
                'valor': previsao_receita.valor_previsto,
                'confianca': previsao_receita.confianca,
                'variacao_percentual': 8.5  # Simulado
            },
            'demanda_vaas': {
                'valor': previsao_vaas.valor_previsto,
                'confianca': previsao_vaas.confianca,
                'crescimento_esperado': 12.3  # Simulado
            }
        },
        'alertas_inteligentes': [
            {
                'tipo': 'oportunidade',
                'titulo': 'Pico Reprodutivo Detectado',
                'descricao': 'Condições ideais para transferência de embriões nos próximos 15 dias',
                'prioridade': 'alta',
                'acao_recomendada': 'Agendar transferências prioritárias'
            },
            {
                'tipo': 'otimizacao',
                'titulo': 'Economia em Alimentação',
                'descricao': 'Plano otimizado pode reduzir custos em 18% mantendo qualidade nutricional',
                'prioridade': 'media',
                'acao_recomendada': 'Revisar fornecedores de ração'
            },
            {
                'tipo': 'financeiro',
                'titulo': 'Crescimento de Receita',
                'descricao': 'Tendência de crescimento de 8.5% na receita mensal detectada',
                'prioridade': 'baixa',
                'acao_recomendada': 'Considerar expansão de serviços'
            }
        ],
        'recomendacoes_estrategicas': [
            'Focar em acasalamentos de alta compatibilidade genética para maximizar taxa de prenhez',
            'Implementar plano alimentar otimizado para reduzir custos operacionais',
            'Expandir serviços VaaS devido ao crescimento da demanda prevista',
            'Monitorar condições ambientais para otimizar período reprodutivo'
        ],
        'metricas_ia': {
            'modelos_ativos': 4,
            'previsoes_geradas_mes': 156,
            'acuracia_media': 87.3,
            'economia_gerada': 15420.50
        }
    }
    
    return jsonify(insights)

@ai_predictions_bp.route('/historico-previsoes', methods=['GET'])
@jwt_required()
@tenant_access_required
def get_historico_previsoes(current_user, tenant_id):
    """Retorna histórico de previsões e sua acurácia"""
    
    # Dados simulados de histórico
    historico = [
        {
            'data': '2025-09-01',
            'tipo': 'taxa_prenhez',
            'valor_previsto': 82.5,
            'valor_real': 84.2,
            'acuracia': 97.9,
            'confianca': 0.89
        },
        {
            'data': '2025-09-01',
            'tipo': 'receita_mensal',
            'valor_previsto': 47500.00,
            'valor_real': 45800.00,
            'acuracia': 96.4,
            'confianca': 0.85
        },
        {
            'data': '2025-08-01',
            'tipo': 'taxa_prenhez',
            'valor_previsto': 78.3,
            'valor_real': 76.8,
            'acuracia': 98.1,
            'confianca': 0.87
        },
        {
            'data': '2025-08-01',
            'tipo': 'receita_mensal',
            'valor_previsto': 44200.00,
            'valor_real': 46100.00,
            'acuracia': 95.9,
            'confianca': 0.82
        }
    ]
    
    # Calcular estatísticas
    acuracia_media = sum([h['acuracia'] for h in historico]) / len(historico)
    confianca_media = sum([h['confianca'] for h in historico]) / len(historico)
    
    return jsonify({
        'historico': historico,
        'estatisticas': {
            'total_previsoes': len(historico),
            'acuracia_media': round(acuracia_media, 1),
            'confianca_media': round(confianca_media, 2),
            'tipos_previsao': list(set([h['tipo'] for h in historico]))
        }
    })
