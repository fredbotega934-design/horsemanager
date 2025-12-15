from flask import Blueprint, request, jsonify
from models.database import db_session
from models.user import Usuario
from models.extras import Lancamento, AtendimentoVaas
from auth.middleware import token_required
from datetime import datetime

integracao_bp = Blueprint("integracao", __name__)

# --- ROTA DE USUÁRIOS (Para o painel de gerenciamento) ---
@integracao_bp.route("/users", methods=["GET"])
@token_required
def list_users(current_user):
    # Apenas admin ou proprietario veem todos
    if current_user.role not in ['admin', 'proprietario']:
        return jsonify({"msg": "Acesso negado"}), 403
        
    users = db_session.query(Usuario).filter_by(tenant_id=current_user.tenant_id).all()
    return jsonify([{
        "id": u.id, "nome": u.nome, "email": u.email, 
        "role": u.role, "ativo": True, 
        "ultimo_login": "2025-12-14" # Simulado para visual
    } for u in users]), 200

# --- ROTA FINANCEIRO ---
@integracao_bp.route("/financeiro/lancamentos", methods=["GET"])
@token_required
def list_financas(current_user):
    lancamentos = db_session.query(Lancamento).filter_by(tenant_id=current_user.tenant_id).all()
    receita = sum(l.valor for l in lancamentos if l.tipo == 'Receita')
    despesa = sum(l.valor for l in lancamentos if l.tipo == 'Despesa')
    
    return jsonify({
        "resumo": {"receita": receita, "despesa": despesa, "saldo": receita - despesa},
        "lancamentos": [{"id":l.id, "desc":l.descricao, "valor":l.valor, "tipo":l.tipo} for l in lancamentos]
    }), 200

# --- ROTA IA / DASHBOARD (Mock para não quebrar o frontend) ---
@integracao_bp.route("/ai/predictions", methods=["GET"])
@token_required
def ai_predictions(current_user):
    # Retorna dados simulados para o gráfico do dashboard funcionar
    return jsonify({
        "taxa_prenhez": 82.5,
        "previsao_receita": 45000.00,
        "alertas": ["Pico de fertilidade detectado", "Estoque de hormônio baixo"]
    }), 200
