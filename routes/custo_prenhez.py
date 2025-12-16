from flask import Blueprint, request, jsonify
from models.custo_prenhez import ItemCusto, Procedimento, CalculoPrenhez
from models.database import db_session
from auth.middleware import token_required
from datetime import datetime

custo_bp = Blueprint("custo_prenhez", __name__)

@custo_bp.route("/custo_itens", methods=["GET"])
@token_required
def get_itens(current_user):
    try:
        itens = db_session.query(ItemCusto).filter_by(tenant_id=current_user.tenant_id).all()
        return jsonify([{
            "id": i.id, "nome": i.nome, "categoria": i.categoria,
            "dose_usada": i.dose_usada, "unidade_medida": i.unidade_medida,
            "custo_da_dose": i.custo_da_dose
        } for i in itens]), 200
    except: return jsonify([]), 200

@custo_bp.route("/custo_itens", methods=["POST"])
@token_required
def add_item(current_user):
    data = request.get_json()
    try:
        # Conversão FORÇADA para Float (aceita 0.5, 1.5, etc)
        val_total = float(data.get('valor_total', 0))
        qtd_total = float(data.get('quantidade_total', 1))
        dose_usada = float(data.get('dose_usada', 0))
        
        if qtd_total == 0: qtd_total = 1
        custo_dose = (val_total / qtd_total) * dose_usada
        
        novo = ItemCusto(
            tenant_id=current_user.tenant_id,
            nome=data.get('nome', 'Sem Nome'), 
            categoria=data.get('categoria', 'Geral'),
            valor_total=val_total, 
            quantidade_total=qtd_total,
            unidade_medida=data.get('unidade_medida', 'un'), 
            dose_usada=dose_usada,
            custo_da_dose=custo_dose,
            observacoes=str(data.get('observacoes', ''))
        )
        db_session.add(novo)
        db_session.commit()
        return jsonify({"message": "Item salvo"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"message": str(e)}), 500

# (Mantendo as outras rotas simplificadas para economizar espaço, mas funcionais)
@custo_bp.route("/custo_itens/<int:id>", methods=["DELETE"])
@token_required
def delete_item(current_user, id):
    i = db_session.query(ItemCusto).get(id)
    if i: 
        db_session.delete(i)
        db_session.commit()
    return jsonify({"msg":"OK"}), 200

@custo_bp.route("/procedimentos", methods=["GET"])
@token_required
def get_procs(current_user):
    l = db_session.query(Procedimento).filter_by(tenant_id=current_user.tenant_id).all()
    return jsonify([{"id":p.id,"nome":p.nome,"custo_total":p.custo_total} for p in l]), 200

@custo_bp.route("/prenhez", methods=["GET"])
@token_required
def get_calcs(current_user):
    l = db_session.query(CalculoPrenhez).filter_by(tenant_id=current_user.tenant_id).all()
    return jsonify([{"id":c.id,"nome":c.nome,"total":c.custo_total_prenhez} for c in l]), 200
