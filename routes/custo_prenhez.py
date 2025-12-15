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
    except Exception as e:
        print(f"Erro GET itens: {e}")
        return jsonify([]), 200

@custo_bp.route("/custo_itens", methods=["POST"])
@token_required
def add_item(current_user):
    data = request.get_json()
    try:
        # Conversão segura de tipos
        val_total = float(data.get('valor_total', 0))
        qtd_total = float(data.get('quantidade_total', 1))
        dose_usada = float(data.get('dose_usada', 0))
        
        # Evita divisão por zero
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
            observacoes=data.get('observacoes', '')
        )
        db_session.add(novo)
        db_session.commit()
        return jsonify({"message": "Item criado com sucesso!"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"message": f"Erro ao salvar: {str(e)}"}), 500

@custo_bp.route("/custo_itens/<int:id>", methods=["DELETE"])
@token_required
def delete_item(current_user, id):
    try:
        item = db_session.query(ItemCusto).get(id)
        if item:
            db_session.delete(item)
            db_session.commit()
            return jsonify({"message": "Deletado"}), 200
        return jsonify({"error": "Nao encontrado"}), 404
    except:
        return jsonify({"error": "Erro ao deletar"}), 500

# --- PROCEDIMENTOS ---
@custo_bp.route("/procedimentos", methods=["GET"])
@token_required
def get_procedimentos(current_user):
    try:
        procs = db_session.query(Procedimento).filter_by(tenant_id=current_user.tenant_id).all()
        return jsonify([{
            "id": p.id, "nome": p.nome, "tipo": p.tipo, "custo_total": p.custo_total
        } for p in procs]), 200
    except: return jsonify([]), 200

@custo_bp.route("/procedimentos", methods=["POST"])
@token_required
def add_procedimento(current_user):
    data = request.get_json()
    try:
        ids = data.get('itens_ids', [])
        # Garante que ids sejam inteiros
        ids = [int(x) for x in ids]
        
        itens = db_session.query(ItemCusto).filter(ItemCusto.id.in_(ids)).all()
        custo_total = sum(i.custo_da_dose for i in itens)
        
        novo = Procedimento(
            tenant_id=current_user.tenant_id,
            nome=data.get('nome'), 
            tipo=data.get('tipo'), 
            custo_total=custo_total, 
            observacoes=data.get('observacoes', '')
        )
        for item in itens:
            novo.itens_usados.append(item)
            
        db_session.add(novo)
        db_session.commit()
        return jsonify({"message": "Procedimento criado"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"message": f"Erro proc: {str(e)}"}), 500

@custo_bp.route("/procedimentos/<int:id>", methods=["DELETE"])
@token_required
def delete_proc(current_user, id):
    try:
        proc = db_session.query(Procedimento).get(id)
        if proc:
            db_session.delete(proc)
            db_session.commit()
            return jsonify({"message": "Deletado"}), 200
        return jsonify({"error": "Nao encontrado"}), 404
    except: return jsonify({"error": "Erro"}), 500

# --- CALCULO PRENHEZ ---
@custo_bp.route("/prenhez", methods=["GET"])
@token_required
def get_calculos(current_user):
    try:
        calcs = db_session.query(CalculoPrenhez).filter_by(tenant_id=current_user.tenant_id).all()
        return jsonify([{
            "id": c.id, "nome": c.nome, 
            "custo_total_prenhez": c.custo_total_prenhez,
            "custo_medio_ciclo": c.custo_medio_ciclo,
            "data_criacao": c.data_criacao
        } for c in calcs]), 200
    except: return jsonify([]), 200

@custo_bp.route("/prenhez", methods=["POST"])
@token_required
def add_calculo(current_user):
    data = request.get_json()
    try:
        p_ids = [int(x) for x in data.get('procedimentos_ids', [])]
        procs = db_session.query(Procedimento).filter(Procedimento.id.in_(p_ids)).all()
        
        custo_procs = sum(p.custo_total for p in procs)
        num_ciclos = int(data.get('num_ciclos', 1))
        num_tentativas = int(data.get('num_tentativas', 1))
        
        custo_medio_ciclo = custo_procs
        custo_total = custo_medio_ciclo * num_ciclos * num_tentativas
        
        novo = CalculoPrenhez(
            tenant_id=current_user.tenant_id,
            nome=data.get('nome'),
            num_ciclos=num_ciclos, num_tentativas=num_tentativas,
            custo_medio_ciclo=custo_medio_ciclo,
            custo_total_prenhez=custo_total,
            data_criacao=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        for p in procs:
            novo.procedimentos_usados.append(p)
            
        db_session.add(novo)
        db_session.commit()
        return jsonify({"message": "Calculo salvo"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"message": f"Erro calculo: {str(e)}"}), 500

@custo_bp.route("/prenhez/<int:id>", methods=["DELETE"])
@token_required
def delete_calculo(current_user, id):
    try:
        c = db_session.query(CalculoPrenhez).get(id)
        if c:
            db_session.delete(c)
            db_session.commit()
            return jsonify({"message": "Deletado"}), 200
        return jsonify({"error": "Nao encontrado"}), 404
    except: return jsonify({"error": "Erro"}), 500
