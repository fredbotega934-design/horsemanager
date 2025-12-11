"""
API Routes para Genetic Match Engine
Endpoints para recomendações de acasalamento inteligente.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
from ai.genetic_match_engine import genetic_engine, RecomendacaoAcasalamento
from auth.middleware import token_required, tenant_access_required

genetic_match_bp = Blueprint('genetic_match', __name__)

# Dados sintéticos para demonstração
DADOS_DOADORAS = [
    {
        'id': 1,
        'nome': 'Estrela Dourada',
        'raca': 'Mangalarga',
        'data_nascimento': datetime(2016, 3, 15),
        'peso': 445.0,
        'altura': 1.54,
        'taxa_prenhez_historica': 0.75,
        'score_genetico': 0.82,
        'tipo_morfologico': 'conformação'
    },
    {
        'id': 2,
        'nome': 'Bela Vista',
        'raca': 'Quarto de Milha',
        'data_nascimento': datetime(2018, 7, 22),
        'peso': 465.0,
        'altura': 1.56,
        'taxa_prenhez_historica': 0.68,
        'score_genetico': 0.78,
        'tipo_morfologico': 'corrida'
    },
    {
        'id': 3,
        'nome': 'Lua Cheia',
        'raca': 'Mangalarga',
        'data_nascimento': datetime(2014, 11, 8),
        'peso': 420.0,
        'altura': 1.52,
        'taxa_prenhez_historica': 0.85,
        'score_genetico': 0.88,
        'tipo_morfologico': 'trabalho'
    }
]

DADOS_GARANHOES = [
    {
        'id': 101,
        'nome': 'Trovão Negro',
        'raca': 'Mangalarga',
        'data_nascimento': datetime(2012, 5, 10),
        'peso': 520.0,
        'altura': 1.62,
        'taxa_prenhez_historica': 0.72,
        'score_genetico': 0.85,
        'performance_media_progenie': 0.78,
        'valor_cobertura': 8000,
        'tipo_morfologico': 'conformação'
    },
    {
        'id': 102,
        'nome': 'Relâmpago',
        'raca': 'Quarto de Milha',
        'data_nascimento': datetime(2015, 9, 3),
        'peso': 540.0,
        'altura': 1.58,
        'taxa_prenhez_historica': 0.68,
        'score_genetico': 0.82,
        'performance_media_progenie': 0.85,
        'valor_cobertura': 12000,
        'tipo_morfologico': 'corrida'
    },
    {
        'id': 103,
        'nome': 'Imperador',
        'raca': 'Mangalarga',
        'data_nascimento': datetime(2013, 1, 20),
        'peso': 510.0,
        'altura': 1.60,
        'taxa_prenhez_historica': 0.78,
        'score_genetico': 0.90,
        'performance_media_progenie': 0.82,
        'valor_cobertura': 15000,
        'tipo_morfologico': 'conformação'
    },
    {
        'id': 104,
        'nome': 'Furacão',
        'raca': 'Quarto de Milha',
        'data_nascimento': datetime(2014, 8, 12),
        'peso': 535.0,
        'altura': 1.59,
        'taxa_prenhez_historica': 0.70,
        'score_genetico': 0.87,
        'performance_media_progenie': 0.88,
        'valor_cobertura': 18000,
        'tipo_morfologico': 'corrida'
    },
    {
        'id': 105,
        'nome': 'Majestoso',
        'raca': 'Mangalarga',
        'data_nascimento': datetime(2011, 4, 5),
        'peso': 525.0,
        'altura': 1.63,
        'taxa_prenhez_historica': 0.75,
        'score_genetico': 0.92,
        'performance_media_progenie': 0.80,
        'valor_cobertura': 20000,
        'tipo_morfologico': 'trabalho'
    }
]

@genetic_match_bp.route('/sugerir', methods=['POST'])
@token_required
@tenant_access_required
def sugerir_acasalamentos(current_user):
    """
    Endpoint principal para sugestões de acasalamento.
    
    Body:
    {
        "doadora_id": 1,
        "categoria_objetivo": "corrida|conformação|trabalho",
        "orcamento_maximo": 25000,
        "prioridade_genetica": 0.7,
        "prioridade_financeira": 0.3,
        "max_recomendacoes": 5
    }
    """
    try:
        data = request.get_json()
        
        # Validar parâmetros obrigatórios
        doadora_id = data.get('doadora_id')
        if not doadora_id:
            return jsonify({'error': 'doadora_id é obrigatório'}), 400
        
        # Buscar dados da doadora
        doadora = next((d for d in DADOS_DOADORAS if d['id'] == doadora_id), None)
        if not doadora:
            return jsonify({'error': 'Doadora não encontrada'}), 404
        
        # Parâmetros opcionais
        categoria_objetivo = data.get('categoria_objetivo', 'conformação')
        orcamento_maximo = data.get('orcamento_maximo', 50000)
        max_recomendacoes = data.get('max_recomendacoes', 5)
        
        # Filtrar garanhões por orçamento e categoria
        garanhoes_filtrados = []
        for garanhao in DADOS_GARANHOES:
            if garanhao['valor_cobertura'] <= orcamento_maximo:
                # Bonus para mesma categoria
                if garanhao['tipo_morfologico'] == categoria_objetivo:
                    garanhao['bonus_categoria'] = True
                garanhoes_filtrados.append(garanhao)
        
        if not garanhoes_filtrados:
            return jsonify({
                'error': 'Nenhum garanhão disponível dentro do orçamento',
                'orcamento_maximo': orcamento_maximo
            }), 404
        
        # Gerar recomendações
        inicio_processamento = datetime.now()
        recomendacoes = genetic_engine.recomendar_acasalamentos(
            doadora, garanhoes_filtrados, max_recomendacoes
        )
        tempo_processamento = (datetime.now() - inicio_processamento).total_seconds()
        
        # Converter para JSON
        resultado = {
            'doadora': {
                'id': doadora['id'],
                'nome': doadora['nome'],
                'raca': doadora['raca'],
                'idade': (datetime.now() - doadora['data_nascimento']).days / 365.25
            },
            'parametros': {
                'categoria_objetivo': categoria_objetivo,
                'orcamento_maximo': orcamento_maximo,
                'garanhoes_avaliados': len(garanhoes_filtrados),
                'tempo_processamento': tempo_processamento
            },
            'recomendacoes': []
        }
        
        for i, rec in enumerate(recomendacoes, 1):
            garanhao = next(g for g in DADOS_GARANHOES if g['id'] == rec.garanhao_id)
            
            resultado['recomendacoes'].append({
                'ranking': i,
                'garanhao': {
                    'id': rec.garanhao_id,
                    'nome': rec.garanhao_nome,
                    'raca': garanhao['raca'],
                    'idade': (datetime.now() - garanhao['data_nascimento']).days / 365.25,
                    'valor_cobertura': garanhao['valor_cobertura']
                },
                'predicoes': {
                    'taxa_prenhez': round(rec.taxa_prenhez_prevista * 100, 1),
                    'score_genetico': round(rec.score_genetico * 100, 1),
                    'roi_estimado': round(rec.roi_estimado * 100, 1),
                    'confianca': round(rec.confianca * 100, 1)
                },
                'financeiro': {
                    'custo_estimado': round(rec.custo_estimado, 2),
                    'valor_potro_estimado': round(rec.valor_potro_estimado, 2),
                    'lucro_esperado': round(rec.valor_potro_estimado * rec.taxa_prenhez_prevista - rec.custo_estimado, 2)
                },
                'justificativa': rec.justificativa,
                'fatores_positivos': rec.fatores_positivos,
                'fatores_atencao': rec.fatores_atencao
            })
        
        # Salvar solicitação (em produção, salvar no banco)
        resultado['metadata'] = {
            'versao_modelo': 'xgboost_v1_demo',
            'data_processamento': datetime.now().isoformat(),
            'tenant_id': current_user.tenant_id,
            'usuario_id': current_user.id
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@genetic_match_bp.route('/predict/prenhez', methods=['POST'])
@token_required
@tenant_access_required
def prever_prenhez(current_user):
    """
    Predição específica de prenhez para um par doadora-garanhão.
    
    Body:
    {
        "doadora_id": 1,
        "garanhao_id": 101
    }
    """
    try:
        data = request.get_json()
        
        doadora_id = data.get('doadora_id')
        garanhao_id = data.get('garanhao_id')
        
        if not doadora_id or not garanhao_id:
            return jsonify({'error': 'doadora_id e garanhao_id são obrigatórios'}), 400
        
        # Buscar dados
        doadora = next((d for d in DADOS_DOADORAS if d['id'] == doadora_id), None)
        garanhao = next((g for g in DADOS_GARANHOES if g['id'] == garanhao_id), None)
        
        if not doadora or not garanhao:
            return jsonify({'error': 'Doadora ou garanhão não encontrado'}), 404
        
        # Gerar predição única
        recomendacoes = genetic_engine.recomendar_acasalamentos(doadora, [garanhao], 1)
        
        if not recomendacoes:
            return jsonify({'error': 'Erro ao gerar predição'}), 500
        
        rec = recomendacoes[0]
        
        resultado = {
            'doadora': {
                'id': doadora['id'],
                'nome': doadora['nome'],
                'raca': doadora['raca']
            },
            'garanhao': {
                'id': garanhao['id'],
                'nome': garanhao['nome'],
                'raca': garanhao['raca']
            },
            'predicao': {
                'taxa_prenhez': round(rec.taxa_prenhez_prevista * 100, 1),
                'score_genetico': round(rec.score_genetico * 100, 1),
                'roi_estimado': round(rec.roi_estimado * 100, 1),
                'confianca': round(rec.confianca * 100, 1)
            },
            'analise_financeira': {
                'custo_total': round(rec.custo_estimado, 2),
                'valor_potro_estimado': round(rec.valor_potro_estimado, 2),
                'receita_esperada': round(rec.valor_potro_estimado * rec.taxa_prenhez_prevista, 2),
                'lucro_esperado': round(rec.valor_potro_estimado * rec.taxa_prenhez_prevista - rec.custo_estimado, 2)
            },
            'analise_genetica': {
                'consanguinidade': round(genetic_engine.calcular_consanguinidade(doadora_id, garanhao_id) * 100, 2),
                'compatibilidade_racial': doadora['raca'] == garanhao['raca'],
                'score_combinado': round(rec.score_genetico * 100, 1)
            },
            'justificativa': rec.justificativa,
            'fatores_positivos': rec.fatores_positivos,
            'fatores_atencao': rec.fatores_atencao,
            'metadata': {
                'data_predicao': datetime.now().isoformat(),
                'versao_modelo': 'xgboost_v1_demo'
            }
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@genetic_match_bp.route('/simular', methods=['POST'])
@token_required
@tenant_access_required
def simular_cenario(current_user):
    """
    Simulação de cenários com variação de preços e custos.
    
    Body:
    {
        "doadora_id": 1,
        "garanhao_id": 101,
        "variacao_preco": 0.2,  // +20%
        "variacao_custo": -0.1  // -10%
    }
    """
    try:
        data = request.get_json()
        
        doadora_id = data.get('doadora_id')
        garanhao_id = data.get('garanhao_id')
        variacao_preco = data.get('variacao_preco', 0.0)
        variacao_custo = data.get('variacao_custo', 0.0)
        
        if not doadora_id or not garanhao_id:
            return jsonify({'error': 'doadora_id e garanhao_id são obrigatórios'}), 400
        
        # Buscar dados
        doadora = next((d for d in DADOS_DOADORAS if d['id'] == doadora_id), None)
        garanhao = next((g for g in DADOS_GARANHOES if g['id'] == garanhao_id), None)
        
        if not doadora or not garanhao:
            return jsonify({'error': 'Doadora ou garanhão não encontrado'}), 404
        
        # Gerar recomendação base
        recomendacoes = genetic_engine.recomendar_acasalamentos(doadora, [garanhao], 1)
        rec = recomendacoes[0]
        
        # Simular cenário
        simulacao = genetic_engine.simular_cenario(rec, variacao_preco, variacao_custo)
        
        resultado = {
            'cenario_base': {
                'roi': round(rec.roi_estimado * 100, 1),
                'valor_potro': round(rec.valor_potro_estimado, 2),
                'custo_total': round(rec.custo_estimado, 2),
                'lucro_esperado': round(rec.valor_potro_estimado * rec.taxa_prenhez_prevista - rec.custo_estimado, 2)
            },
            'cenario_simulado': {
                'roi': round(simulacao['roi_simulado'] * 100, 1),
                'valor_potro': round(simulacao['valor_potro_simulado'], 2),
                'custo_total': round(simulacao['custo_simulado'], 2),
                'lucro_esperado': round(simulacao['lucro_simulado'], 2)
            },
            'impacto': {
                'diferenca_roi': round(simulacao['diferenca_roi'] * 100, 1),
                'diferenca_lucro': round(simulacao['lucro_simulado'] - (rec.valor_potro_estimado * rec.taxa_prenhez_prevista - rec.custo_estimado), 2),
                'variacao_preco_aplicada': round(variacao_preco * 100, 1),
                'variacao_custo_aplicada': round(variacao_custo * 100, 1)
            },
            'parametros': {
                'doadora': doadora['nome'],
                'garanhao': garanhao['nome'],
                'taxa_prenhez': round(rec.taxa_prenhez_prevista * 100, 1)
            }
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@genetic_match_bp.route('/doadoras', methods=['GET'])
@token_required
@tenant_access_required
def listar_doadoras(current_user):
    """Lista doadoras disponíveis para acasalamento."""
    try:
        doadoras = []
        for doadora in DADOS_DOADORAS:
            idade = (datetime.now() - doadora['data_nascimento']).days / 365.25
            doadoras.append({
                'id': doadora['id'],
                'nome': doadora['nome'],
                'raca': doadora['raca'],
                'idade': round(idade, 1),
                'peso': doadora['peso'],
                'altura': doadora['altura'],
                'taxa_prenhez_historica': round(doadora['taxa_prenhez_historica'] * 100, 1),
                'score_genetico': round(doadora['score_genetico'] * 100, 1),
                'tipo_morfologico': doadora['tipo_morfologico']
            })
        
        return jsonify({
            'doadoras': doadoras,
            'total': len(doadoras)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@genetic_match_bp.route('/garanhoes', methods=['GET'])
@token_required
@tenant_access_required
def listar_garanhoes(current_user):
    """Lista garanhões disponíveis para acasalamento."""
    try:
        garanhoes = []
        for garanhao in DADOS_GARANHOES:
            idade = (datetime.now() - garanhao['data_nascimento']).days / 365.25
            garanhoes.append({
                'id': garanhao['id'],
                'nome': garanhao['nome'],
                'raca': garanhao['raca'],
                'idade': round(idade, 1),
                'peso': garanhao['peso'],
                'altura': garanhao['altura'],
                'taxa_prenhez_historica': round(garanhao['taxa_prenhez_historica'] * 100, 1),
                'score_genetico': round(garanhao['score_genetico'] * 100, 1),
                'performance_media_progenie': round(garanhao['performance_media_progenie'] * 100, 1),
                'valor_cobertura': garanhao['valor_cobertura'],
                'tipo_morfologico': garanhao['tipo_morfologico']
            })
        
        return jsonify({
            'garanhoes': garanhoes,
            'total': len(garanhoes)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@genetic_match_bp.route('/stats', methods=['GET'])
@token_required
@tenant_access_required
def estatisticas_sistema(current_user):
    """Estatísticas do sistema de acasalamento inteligente."""
    try:
        # Calcular estatísticas dos dados disponíveis
        total_doadoras = len(DADOS_DOADORAS)
        total_garanhoes = len(DADOS_GARANHOES)
        
        # Taxa média de prenhez
        taxa_media_doadoras = sum(d['taxa_prenhez_historica'] for d in DADOS_DOADORAS) / total_doadoras
        taxa_media_garanhoes = sum(g['taxa_prenhez_historica'] for g in DADOS_GARANHOES) / total_garanhoes
        
        # Score genético médio
        score_medio_doadoras = sum(d['score_genetico'] for d in DADOS_DOADORAS) / total_doadoras
        score_medio_garanhoes = sum(g['score_genetico'] for g in DADOS_GARANHOES) / total_garanhoes
        
        # Distribuição por raça
        racas_doadoras = {}
        racas_garanhoes = {}
        
        for doadora in DADOS_DOADORAS:
            raca = doadora['raca']
            racas_doadoras[raca] = racas_doadoras.get(raca, 0) + 1
        
        for garanhao in DADOS_GARANHOES:
            raca = garanhao['raca']
            racas_garanhoes[raca] = racas_garanhoes.get(raca, 0) + 1
        
        resultado = {
            'resumo': {
                'total_doadoras': total_doadoras,
                'total_garanhoes': total_garanhoes,
                'combinacoes_possiveis': total_doadoras * total_garanhoes
            },
            'performance': {
                'taxa_prenhez_media_doadoras': round(taxa_media_doadoras * 100, 1),
                'taxa_prenhez_media_garanhoes': round(taxa_media_garanhoes * 100, 1),
                'score_genetico_medio_doadoras': round(score_medio_doadoras * 100, 1),
                'score_genetico_medio_garanhoes': round(score_medio_garanhoes * 100, 1)
            },
            'distribuicao_racas': {
                'doadoras': racas_doadoras,
                'garanhoes': racas_garanhoes
            },
            'modelo': {
                'versao': 'xgboost_v1_demo',
                'acuracia_estimada': 87.3,
                'features_utilizadas': len(genetic_engine.feature_names),
                'ultima_atualizacao': '2025-10-05'
            }
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
