from flask import Blueprint, request, jsonify
from models.custo_prenhez import ItemCusto, Procedimento, CalculoPrenhez, ProcedimentoCalculo
from models.database import db_session
from auth.middleware import token_required
from datetime import datetime

custo_bp = Blueprint("custo_prenhez", __name__)

# --- ITENS ---
@custo_bp.route("/custo_itens", methods=["GET"])
@token_required
def get_itens(current_user):
    itens = db_session.query(ItemCusto).filter_by(tenant_id=current_user.tenant_id).all()
    return jsonify([{
        "id": i.id, "nome": i.nome, "categoria": i.categoria,
        "dose_usada": i.dose_usada, "unidade_medida": i.unidade_medida,
        "custo_da_dose": i.custo_da_dose
    } for i in itens]), 200

@custo_bp.route("/custo_itens", methods=["POST"])
@token_required
def add_item(current_user):
    data = request.get_json()
    # Calculo do custo da dose: (Valor Total / Qtd Total) * Dose Usada
    custo_dose = (float(data['valor_total']) / float(data['quantidade_total'])) * float(data['dose_usada'])
    
    novo = ItemCusto(
        tenant_id=current_user.tenant_id,
        nome=data['nome'], categoria=data['categoria'],
        valor_total=data['valor_total'], quantidade_total=data['quantidade_total'],
        unidade_medida=data['unidade_medida'], dose_usada=data['dose_usada'],
        custo_da_dose=custo_dose
    )
    db_session.add(novo)
    db_session.commit()
    return jsonify({"message": "Item criado"}), 201

@custo_bp.route("/custo_itens/<int:id>", methods=["DELETE"])
@token_required
def delete_item(current_user, id):
    item = db_session.query(ItemCusto).get(id)
    if item:
        db_session.delete(item)
        db_session.commit()
        return jsonify({"message": "Deletado"}), 200
    return jsonify({"error": "Nao encontrado"}), 404

# --- PROCEDIMENTOS ---
@custo_bp.route("/procedimentos", methods=["GET"])
@token_required
def get_procedimentos(current_user):
    procs = db_session.query(Procedimento).filter_by(tenant_id=current_user.tenant_id).all()
    return jsonify([{
        "id": p.id, "nome": p.nome, "tipo": p.tipo, "custo_total": p.custo_total
    } for p in procs]), 200

@custo_bp.route("/procedimentos", methods=["POST"])
@token_required
def add_procedimento(current_user):
    data = request.get_json()
    # Soma o custo dos itens selecionados
    itens = db_session.query(ItemCusto).filter(ItemCusto.id.in_(data['itens_ids'])).all()
    custo_total = sum(i.custo_da_dose for i in itens)
    
    novo = Procedimento(
        tenant_id=current_user.tenant_id,
        nome=data['nome'], tipo=data['tipo'], custo_total=custo_total
    )
    # Aqui poderiamos salvar a relacao Many-to-Many se necessario
    db_session.add(novo)
    db_session.commit()
    return jsonify({"message": "Procedimento criado"}), 201

@custo_bp.route("/procedimentos/<int:id>", methods=["DELETE"])
@token_required
def delete_proc(current_user, id):
    proc = db_session.query(Procedimento).get(id)
    if proc:
        db_session.delete(proc)
        db_session.commit()
        return jsonify({"message": "Deletado"}), 200
    return jsonify({"error": "Nao encontrado"}), 404

# --- CALCULO PRENHEZ ---
@custo_bp.route("/prenhez", methods=["GET"])
@token_required
def get_calculos(current_user):
    calcs = db_session.query(CalculoPrenhez).filter_by(tenant_id=current_user.tenant_id).all()
    return jsonify([{
        "id": c.id, "nome": c.nome, 
        "custo_total_prenhez": c.custo_total_prenhez,
        "custo_medio_ciclo": c.custo_medio_ciclo,
        "data_criacao": c.data_criacao.strftime("%d/%m/%Y")
    } for c in calcs]), 200

@custo_bp.route("/prenhez", methods=["POST"])
@token_required
def add_calculo(current_user):
    data = request.get_json()
    procs = db_session.query(Procedimento).filter(Procedimento.id.in_(data['procedimentos_ids'])).all()
    
    custo_procs = sum(p.custo_total for p in procs)
    num_ciclos = int(data['num_ciclos'])
    num_tentativas = int(data['num_tentativas'])
    
    custo_medio_ciclo = custo_procs
    custo_total = custo_medio_ciclo * num_ciclos * num_tentativas
    
    novo = CalculoPrenhez(
        tenant_id=current_user.tenant_id,
        nome=data['nome'],
        num_ciclos=num_ciclos, num_tentativas=num_tentativas,
        custo_medio_ciclo=custo_medio_ciclo,
        custo_total_prenhez=custo_total,
        data_criacao=datetime.now()
    )
    db_session.add(novo)
    db_session.commit()
    return jsonify({"message": "Calculo salvo"}), 201

@custo_bp.route("/prenhez/<int:id>", methods=["DELETE"])
@token_required
def delete_calculo(current_user, id):
    c = db_session.query(CalculoPrenhez).get(id)
    if c:
        db_session.delete(c)
        db_session.commit()
        return jsonify({"message": "Deletado"}), 200
    return jsonify({"error": "Nao encontrado"}), 404
