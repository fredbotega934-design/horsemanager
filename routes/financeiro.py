from flask import Blueprint, request, jsonify
from models.financeiro import TransacaoFinanceira
from models.database import db_session
from auth.middleware import token_required, role_required
from datetime import datetime

financeiro_bp = Blueprint("financeiro", __name__)

# Listar Transacoes e Saldo
@financeiro_bp.route("", methods=["GET"])
@token_required
@role_required(["proprietario", "veterinario"])
def get_financeiro(current_user):
    tenant_id = current_user.tenant_id
    transacoes = db_session.query(TransacaoFinanceira).filter_by(tenant_id=tenant_id).order_by(TransacaoFinanceira.data_transacao.desc()).all()
    
    lista = []
    total_receitas = 0.0
    total_despesas = 0.0

    for t in transacoes:
        if t.tipo == 'Receita':
            total_receitas += t.valor
        else:
            total_despesas += t.valor
            
        lista.append({
            "id": t.id,
            "descricao": t.descricao,
            "tipo": t.tipo,
            "valor": f"R$ {t.valor:.2f}",
            "categoria": t.categoria,
            "data": t.data_transacao.strftime('%d/%m/%Y')
        })
    
    saldo = total_receitas - total_despesas

    return jsonify({
        "extrato": lista,
        "resumo": {
            "receitas": f"R$ {total_receitas:.2f}",
            "despesas": f"R$ {total_despesas:.2f}",
            "saldo": f"R$ {saldo:.2f}"
        }
    }), 200

# Adicionar Transacao
@financeiro_bp.route("", methods=["POST"])
@token_required
@role_required(["proprietario"])
def add_transacao(current_user):
    data = request.get_json()
    try:
        nova_transacao = TransacaoFinanceira(
            tenant_id=current_user.tenant_id,
            descricao=data['descricao'],
            tipo=data['tipo'], # Receita ou Despesa
            valor=float(data['valor']),
            categoria=data.get('categoria', 'Geral'),
            data_transacao=datetime.strptime(data['data'], '%Y-%m-%d').date() if data.get('data') else datetime.now().date()
        )
        db_session.add(nova_transacao)
        db_session.commit()
        return jsonify({"message": "Lançamento realizado com sucesso!"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"message": str(e)}), 400
