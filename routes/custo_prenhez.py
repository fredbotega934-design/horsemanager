from flask import Blueprint, request, jsonify
from models.custo_prenhez import ItemCusto, Procedimento, CalculoPrenhez
from models.database import db_session
from auth.middleware import token_required
from datetime import datetime

custo_bp = Blueprint("custo_prenhez", __name__)

# --- ITENS ---
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
        # CONVERSÃO PARA FLOAT (Permite centavos)
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
        return jsonify({"message": "Item salvo com sucesso!"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

# --- PROCEDIMENTOS ---
@custo_bp.route("/procedimentos", methods=["GET"])
@token_required
def get_procs(current_user):
    l = db_session.query(Procedimento).filter_by(tenant_id=current_user.tenant_id).all()
    return jsonify([{"id":p.id,"nome":p.nome,"custo_total":p.custo_total} for p in l]), 200

@custo_bp.route("/procedimentos", methods=["POST"])
@token_required
def add_proc(current_user):
    data = request.get_json()
    try:
        ids = [int(x) for x in data.get('itens_ids', [])]
        itens = db_session.query(ItemCusto).filter(ItemCusto.id.in_(ids)).all()
        custo_total = sum(i.custo_da_dose for i in itens)
        
        novo = Procedimento(
            tenant_id=current_user.tenant_id,
            nome=data.get('nome'), 
            tipo=data.get('tipo'), 
            custo_total=custo_total
        )
        for i in itens: novo.itens_usados.append(i)
        
        db_session.add(novo)
        db_session.commit()
        return jsonify({"msg": "Procedimento salvo!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- PRENHEZ ---
@custo_bp.route("/prenhez", methods=["GET"])
@token_required
def get_calcs(current_user):
    l = db_session.query(CalculoPrenhez).filter_by(tenant_id=current_user.tenant_id).all()
    return jsonify([{"id":c.id,"nome":c.nome,"total":c.custo_total_prenhez, "data":c.data_criacao} for c in l]), 200

@custo_bp.route("/prenhez", methods=["POST"])
@token_required
def add_calc(current_user):
    data = request.get_json()
    try:
        p_ids = [int(x) for x in data.get('procedimentos_ids', [])]
        procs = db_session.query(Procedimento).filter(Procedimento.id.in_(p_ids)).all()
        custo_ciclo = sum(p.custo_total for p in procs)
        
        ciclos = int(data.get('num_ciclos', 1))
        tentativas = int(data.get('num_tentativas', 1))
        
        novo = CalculoPrenhez(
            tenant_id=current_user.tenant_id,
            nome=data.get('nome'),
            num_ciclos=ciclos, num_tentativas=tentativas,
            custo_medio_ciclo=custo_ciclo,
            custo_total_prenhez=custo_ciclo * ciclos * tentativas,
            data_criacao=datetime.now().strftime("%d/%m/%Y")
        )
        for p in procs: novo.procedimentos_usados.append(p)
        db_session.add(novo)
        db_session.commit()
        return jsonify({"msg": "Cálculo salvo!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
