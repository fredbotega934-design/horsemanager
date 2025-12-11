"""
Rotas da API para Analytics, Matching e Predições IA
Endpoints para funcionalidades avançadas do sistema de haras
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.algorithms.matching import (
    MatchingEngine, PerfilDoadora, PerfilReceptora, 
    StatusReproductivo, FaseEstral, ProtocoloSincronizacao
)
from src.algorithms.predictions import (
    SistemaPredictivo, TipoPredicao
)
from src.models.user import db
from src.models.models import Egual, ProcedimentoOPU, TransferenciaEmbriao, Gestacao

analytics_bp = Blueprint("analytics", __name__)

# Instâncias dos sistemas
matching_engine = MatchingEngine()
sistema_predictivo = SistemaPredictivo()

@analytics_bp.route("/matching/sugerir-receptoras", methods=["POST"])
def sugerir_receptoras():
    """
    Sugere as melhores receptoras para uma doadora específica
    """
    try:
        data = request.get_json()
        doadora_id = data.get('doadora_id')
        limite = data.get('limite', 5)
        
        if not doadora_id:
            return jsonify({"error": "ID da doadora é obrigatório"}), 400
        
        # Buscar dados da doadora no banco
        doadora_db = Egual.query.get(doadora_id)
        if not doadora_db:
            return jsonify({"error": "Doadora não encontrada"}), 404
        
        # Criar perfil da doadora
        perfil_doadora = _criar_perfil_doadora(doadora_db)
        
        # Buscar receptoras disponíveis
        receptoras_db = Egual.query.filter(
            Egual.classificacao == 'receptora',
            Egual.status_reprodutivo == 'ativa'
        ).all()
        
        # Criar perfis das receptoras
        perfis_receptoras = [_criar_perfil_receptora(r) for r in receptoras_db]
        
        # Executar matching
        melhores_receptoras = matching_engine.encontrar_melhores_receptoras(
            perfil_doadora, perfis_receptoras, limite
        )
        
        # Gerar relatório
        relatorio = matching_engine.gerar_relatorio_matching(
            perfil_doadora, melhores_receptoras
        )
        
        return jsonify(relatorio)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/matching/protocolo-sincronizacao", methods=["POST"])
def sugerir_protocolo_sincronizacao():
    """
    Sugere protocolo de sincronização para uma receptora
    """
    try:
        data = request.get_json()
        receptora_id = data.get('receptora_id')
        
        if not receptora_id:
            return jsonify({"error": "ID da receptora é obrigatório"}), 400
        
        # Buscar receptora no banco
        receptora_db = Egual.query.get(receptora_id)
        if not receptora_db:
            return jsonify({"error": "Receptora não encontrada"}), 404
        
        # Criar perfil da receptora
        perfil_receptora = _criar_perfil_receptora(receptora_db)
        
        # Sugerir protocolo
        protocolo = ProtocoloSincronizacao.sugerir_protocolo(perfil_receptora)
        
        return jsonify({
            "receptora": {
                "id": receptora_db.id,
                "nome": receptora_db.nome,
                "status_reprodutivo": perfil_receptora.status_reprodutivo.value,
                "fase_estral": perfil_receptora.fase_estral.value
            },
            "protocolo_sugerido": protocolo
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/predictions/taxa-prenhez", methods=["POST"])
def predizer_taxa_prenhez():
    """
    Prediz taxa de prenhez para uma transferência específica
    """
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['doadora_id', 'receptora_id', 'qualidade_embriao']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo {field} é obrigatório"}), 400
        
        # Buscar dados no banco
        doadora = Egual.query.get(data['doadora_id'])
        receptora = Egual.query.get(data['receptora_id'])
        
        if not doadora or not receptora:
            return jsonify({"error": "Doadora ou receptora não encontrada"}), 404
        
        # Preparar dados para predição
        dados_predicao = {
            'idade_doadora': doadora.idade,
            'idade_receptora': receptora.idade,
            'condicao_corporal_receptora': receptora.condicao_corporal,
            'qualidade_embriao': data['qualidade_embriao'],
            'experiencia_veterinario': data.get('experiencia_veterinario', 5),
            'mes': datetime.now().month,
            'tentativas_anteriores': data.get('tentativas_anteriores', 0),
            'intervalo_pos_parto': data.get('intervalo_pos_parto', 90),
            'sincronizacao_qualidade': data.get('sincronizacao_qualidade', 0.8),
            'historico_sucesso_receptora': _calcular_historico_sucesso_receptora(receptora.id)
        }
        
        # Fazer predição
        resultado = sistema_predictivo.fazer_predicao(
            TipoPredicao.TAXA_PRENHEZ, dados_predicao
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/predictions/qualidade-embrioes", methods=["POST"])
def predizer_qualidade_embrioes():
    """
    Prediz distribuição de qualidade de embriões para uma doadora
    """
    try:
        data = request.get_json()
        doadora_id = data.get('doadora_id')
        
        if not doadora_id:
            return jsonify({"error": "ID da doadora é obrigatório"}), 400
        
        # Buscar doadora no banco
        doadora = Egual.query.get(doadora_id)
        if not doadora:
            return jsonify({"error": "Doadora não encontrada"}), 404
        
        # Preparar dados para predição
        dados_predicao = {
            'idade_doadora': doadora.idade,
            'condicao_corporal_doadora': doadora.condicao_corporal,
            'numero_coletas_anteriores': _contar_coletas_anteriores(doadora_id),
            'intervalo_dias_ultima_coleta': _calcular_intervalo_ultima_coleta(doadora_id),
            'nutricao_score': data.get('nutricao_score', 8),
            'ccos_esperados': data.get('ccos_esperados', 10)
        }
        
        # Fazer predição
        resultado = sistema_predictivo.fazer_predicao(
            TipoPredicao.QUALIDADE_EMBRIAO, dados_predicao
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/predictions/recuperacao-ccos", methods=["POST"])
def predizer_recuperacao_ccos():
    """
    Prediz número de CCOs que serão recuperados
    """
    try:
        data = request.get_json()
        doadora_id = data.get('doadora_id')
        
        if not doadora_id:
            return jsonify({"error": "ID da doadora é obrigatório"}), 400
        
        # Buscar doadora no banco
        doadora = Egual.query.get(doadora_id)
        if not doadora:
            return jsonify({"error": "Doadora não encontrada"}), 404
        
        # Preparar dados para predição
        dados_predicao = {
            'idade_doadora': doadora.idade,
            'peso_doadora': doadora.peso,
            'condicao_corporal_doadora': doadora.condicao_corporal,
            'historico_medio_ccos': _calcular_media_ccos_historica(doadora_id),
            'dias_protocolo_superovulacao': data.get('dias_protocolo', 10),
            'experiencia_veterinario': data.get('experiencia_veterinario', 5)
        }
        
        # Fazer predição
        resultado = sistema_predictivo.fazer_predicao(
            TipoPredicao.RECUPERACAO_CCOS, dados_predicao
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/predictions/analise-completa-doadora", methods=["POST"])
def analise_completa_doadora():
    """
    Faz análise completa de uma doadora com múltiplas predições
    """
    try:
        data = request.get_json()
        doadora_id = data.get('doadora_id')
        
        if not doadora_id:
            return jsonify({"error": "ID da doadora é obrigatório"}), 400
        
        # Buscar doadora no banco
        doadora = Egual.query.get(doadora_id)
        if not doadora:
            return jsonify({"error": "Doadora não encontrada"}), 404
        
        # Preparar dados completos
        dados_doadora = {
            'idade_doadora': doadora.idade,
            'peso_doadora': doadora.peso,
            'condicao_corporal_doadora': doadora.condicao_corporal,
            'historico_medio_ccos': _calcular_media_ccos_historica(doadora_id),
            'numero_coletas_anteriores': _contar_coletas_anteriores(doadora_id),
            'intervalo_dias_ultima_coleta': _calcular_intervalo_ultima_coleta(doadora_id),
            'nutricao_score': data.get('nutricao_score', 8),
            'dias_protocolo_superovulacao': data.get('dias_protocolo', 10),
            'experiencia_veterinario': data.get('experiencia_veterinario', 5),
            'valor_potro_estimado': data.get('valor_potro_estimado', 15000.0)
        }
        
        # Fazer análise completa
        resultado = sistema_predictivo.analise_completa_doadora(dados_doadora)
        
        # Adicionar informações da doadora
        resultado['doadora_info'] = {
            'id': doadora.id,
            'nome': doadora.nome,
            'idade': doadora.idade,
            'raca': doadora.raca,
            'peso': doadora.peso,
            'condicao_corporal': doadora.condicao_corporal
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/predictions/analise-transferencia", methods=["POST"])
def analise_transferencia_embriao():
    """
    Análise completa para transferência de embrião
    """
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['doadora_id', 'receptora_id', 'qualidade_embriao']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo {field} é obrigatório"}), 400
        
        # Buscar dados no banco
        doadora = Egual.query.get(data['doadora_id'])
        receptora = Egual.query.get(data['receptora_id'])
        
        if not doadora or not receptora:
            return jsonify({"error": "Doadora ou receptora não encontrada"}), 404
        
        # Preparar dados
        dados_doadora = {
            'idade_doadora': doadora.idade,
            'condicao_corporal_doadora': doadora.condicao_corporal
        }
        
        dados_receptora = {
            'idade_receptora': receptora.idade,
            'condicao_corporal_receptora': receptora.condicao_corporal,
            'historico_sucesso_receptora': _calcular_historico_sucesso_receptora(receptora.id),
            'historico_perdas_receptora': _calcular_historico_perdas_receptora(receptora.id)
        }
        
        dados_embriao = {
            'qualidade_embriao': data['qualidade_embriao'],
            'experiencia_veterinario': data.get('experiencia_veterinario', 5),
            'tentativas_anteriores': data.get('tentativas_anteriores', 0),
            'intervalo_pos_parto': data.get('intervalo_pos_parto', 90),
            'sincronizacao_qualidade': data.get('sincronizacao_qualidade', 0.8)
        }
        
        # Fazer análise
        resultado = sistema_predictivo.analise_transferencia_embriao(
            dados_doadora, dados_receptora, dados_embriao
        )
        
        # Adicionar informações dos animais
        resultado['animais_info'] = {
            'doadora': {
                'id': doadora.id,
                'nome': doadora.nome,
                'idade': doadora.idade
            },
            'receptora': {
                'id': receptora.id,
                'nome': receptora.nome,
                'idade': receptora.idade
            }
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/dashboard/kpis", methods=["GET"])
def obter_kpis_dashboard():
    """
    Retorna KPIs principais para o dashboard
    """
    try:
        # Período de análise (últimos 12 meses)
        data_inicio = datetime.now() - timedelta(days=365)
        
        # KPIs básicos
        total_eguas = Egual.query.count()
        eguas_ativas = Egual.query.filter(Egual.status_reprodutivo == 'ativa').count()
        
        # Procedimentos no período
        procedimentos_periodo = ProcedimentoOPU.query.filter(
            ProcedimentoOPU.data_procedimento >= data_inicio
        ).count()
        
        # Taxa de prenhez (últimos 6 meses)
        data_prenhez = datetime.now() - timedelta(days=180)
        transferencias = TransferenciaEmbriao.query.filter(
            TransferenciaEmbriao.data_transferencia >= data_prenhez
        ).count()
        
        gestacoes_confirmadas = Gestacao.query.filter(
            Gestacao.data_diagnostico >= data_prenhez.strftime('%Y-%m-%d'),
            Gestacao.status_gestacao == 'confirmada'
        ).count()
        
        taxa_prenhez = (gestacoes_confirmadas / max(transferencias, 1)) * 100
        
        # Análise mensal (últimos 6 meses)
        dados_mensais = []
        for i in range(6):
            mes_inicio = datetime.now() - timedelta(days=30 * (i + 1))
            mes_fim = datetime.now() - timedelta(days=30 * i)
            
            proc_mes = ProcedimentoOPU.query.filter(
                ProcedimentoOPU.data_procedimento >= mes_inicio,
                ProcedimentoOPU.data_procedimento < mes_fim
            ).count()
            
            dados_mensais.append({
                'mes': mes_inicio.strftime('%Y-%m'),
                'procedimentos': proc_mes
            })
        
        dados_mensais.reverse()  # Ordem cronológica
        
        return jsonify({
            'kpis_principais': {
                'total_eguas': total_eguas,
                'eguas_ativas': eguas_ativas,
                'procedimentos_ano': procedimentos_periodo,
                'taxa_prenhez_percentual': round(taxa_prenhez, 1)
            },
            'tendencias_mensais': dados_mensais,
            'ultima_atualizacao': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Funções auxiliares
def _criar_perfil_doadora(doadora_db) -> PerfilDoadora:
    """Cria perfil de doadora a partir dos dados do banco"""
    return PerfilDoadora(
        id=doadora_db.id,
        nome=doadora_db.nome_egua,
        idade=doadora_db.idade,
        qualidade_genetica=8.0,  # Valor padrão, pode ser calculado
        taxa_recuperacao_ccos=_calcular_media_ccos_historica(doadora_db.id),
        qualidade_embrioes=75.0,  # Valor padrão
        ciclos_anteriores=_contar_coletas_anteriores(doadora_db.id),
        data_ultimo_procedimento=_obter_data_ultimo_procedimento(doadora_db.id)
    )

def _criar_perfil_receptora(receptora_db) -> PerfilReceptora:
    """Cria perfil de receptora a partir dos dados do banco"""
    return PerfilReceptora(
        id=receptora_db.id,
        nome=receptora_db.nome_egua,
        idade=receptora_db.idade,
        peso=receptora_db.peso,
        altura=receptora_db.altura,
        condicao_corporal=receptora_db.condicao_corporal,
        status_reprodutivo=StatusReproductivo.VAZIA,  # Simplificado
        fase_estral=FaseEstral.DIESTRO,  # Simplificado
        data_ultimo_cio=None,  # Seria obtido de outra tabela
        historico_gestacoes=_contar_gestacoes_anteriores(receptora_db.id),
        taxa_sucesso_historica=_calcular_historico_sucesso_receptora(receptora_db.id),
        dias_pos_parto=None,  # Seria calculado
        protocolos_anteriores=[],
        disponivel=receptora_db.status_reprodutivo == 'ativa',
        custo_manutencao=150.0
    )

def _calcular_historico_sucesso_receptora(receptora_id: int) -> float:
    """Calcula taxa de sucesso histórica da receptora"""
    try:
        transferencias = TransferenciaEmbriao.query.filter(
            TransferenciaEmbriao.receptora_id == receptora_id
        ).count()
        
        gestacoes = Gestacao.query.join(TransferenciaEmbriao).filter(
            TransferenciaEmbriao.receptora_id == receptora_id,
            Gestacao.status_gestacao == 'confirmada'
        ).count()
        
        return gestacoes / max(transferencias, 1)
    except:
        return 0.7  # Valor padrão

def _calcular_historico_perdas_receptora(receptora_id: int) -> float:
    """Calcula taxa de perdas embrionárias da receptora"""
    try:
        gestacoes_confirmadas = Gestacao.query.join(TransferenciaEmbriao).filter(
            TransferenciaEmbriao.receptora_id == receptora_id,
            Gestacao.status_gestacao == 'confirmada'
        ).count()
        
        perdas = Gestacao.query.join(TransferenciaEmbriao).filter(
            TransferenciaEmbriao.receptora_id == receptora_id,
            Gestacao.status_gestacao == 'perda_embrionaria'
        ).count()
        
        return perdas / max(gestacoes_confirmadas + perdas, 1)
    except:
        return 0.15  # Valor padrão

def _calcular_media_ccos_historica(doadora_id: int) -> float:
    """Calcula média histórica de CCOs recuperados"""
    try:
        procedimentos = ProcedimentoOPU.query.filter(
            ProcedimentoOPU.doadora_id == doadora_id
        ).all()
        
        if not procedimentos:
            return 10.0  # Valor padrão
        
        total_ccos = sum(p.ccos_recuperados for p in procedimentos if p.ccos_recuperados)
        return total_ccos / len(procedimentos)
    except:
        return 10.0

def _contar_coletas_anteriores(doadora_id: int) -> int:
    """Conta número de coletas anteriores"""
    try:
        return ProcedimentoOPU.query.filter(
            ProcedimentoOPU.doadora_id == doadora_id
        ).count()
    except:
        return 0

def _calcular_intervalo_ultima_coleta(doadora_id: int) -> int:
    """Calcula dias desde última coleta"""
    try:
        ultimo_proc = ProcedimentoOPU.query.filter(
            ProcedimentoOPU.doadora_id == doadora_id
        ).order_by(ProcedimentoOPU.data_procedimento.desc()).first()
        
        if ultimo_proc:
            return (datetime.now().date() - ultimo_proc.data_procedimento).days
        return 30  # Valor padrão
    except:
        return 30

def _obter_data_ultimo_procedimento(doadora_id: int):
    """Obtém data do último procedimento"""
    try:
        ultimo_proc = ProcedimentoOPU.query.filter(
            ProcedimentoOPU.doadora_id == doadora_id
        ).order_by(ProcedimentoOPU.data_procedimento.desc()).first()
        
        return ultimo_proc.data_procedimento if ultimo_proc else None
    except:
        return None

def _contar_gestacoes_anteriores(receptora_id: int) -> int:
    """Conta gestações anteriores da receptora"""
    try:
        return Gestacao.query.join(TransferenciaEmbriao).filter(
            TransferenciaEmbriao.receptora_id == receptora_id
        ).count()
    except:
        return 0
