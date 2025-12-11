from flask import Blueprint, request, jsonify
from models.custo_prenhez import ItemCusto, ProcedimentoCusto, ItemNoProcedimento
from models.database import db_session
from auth.middleware import token_required, role_required

custo_bp = Blueprint("custo_prenhez", __name__)

# --- 1. GERENCIAR ITENS (Medicamentos, Insumos) ---
@custo_bp.route("/itens", methods=["POST"])
@token_required
def add_item(current_user):
    data = request.get_json()
    try:
        # Calcula custo unitario (ex: R$ 100 frasco / 50ml = R$ 2/ml)
        valor_total = float(data['valor_total'])
        qtd_total = float(data['qtd_total'])
        custo_unit = valor_total / qtd_total if qtd_total > 0 else 0

        novo_item = ItemCusto(
            tenant_id=current_user.tenant_id,
            nome=data['nome'],
            categoria=data['categoria'],
            valor_total_frasco=valor_total,
            quantidade_total_frasco=qtd_total,
            unidade_medida=data['unidade'],
            custo_por_unidade=custo_unit
        )
        db_session.add(novo_item)
        db_session.commit()
        return jsonify({"message": "Item cadastrado", "custo_unitario": f"R$ {custo_unit:.2f}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@custo_bp.route("/itens", methods=["GET"])
@token_required
def list_itens(current_user):
    itens = db_session.query(ItemCusto).filter_by(tenant_id=current_user.tenant_id).all()
    res = []
    for i in itens:
        res.append({
            "id": i.id,
            "nome": i.nome,
            "categoria": i.categoria,
            "custo_unitario": f"R$ {i.custo_por_unidade:.2f} / {i.unidade_medida}"
        })
    return jsonify(res), 200

# --- 2. CALCULADORA DE PRENHEZ SIMPLIFICADA ---
# Para essa versao inicial, vamos fazer um endpoint que recebe os custos e calcula na hora
@custo_bp.route("/calcular", methods=["POST"])
@token_required
def calcular_prenhez(current_user):
    # Payload esperado: 
    # { "itens": [{"id": 1, "dose": 2}, {"id": 5, "dose": 1}], "ciclos": 3 }
    data = request.get_json()
    
    itens_selecionados = data.get('itens', [])
    num_ciclos = float(data.get('ciclos', 1))
    
    custo_por_ciclo = 0
    detalhes = []

    for req in itens_selecionados:
        item_db = db_session.query(ItemCusto).get(req['id'])
        if item_db:
            dose = float(req['dose'])
            custo_dose = item_db.custo_por_unidade * dose
            custo_por_ciclo += custo_dose
            detalhes.append({
                "item": item_db.nome,
                "dose": f"{dose} {item_db.unidade_medida}",
                "custo": f"R$ {custo_dose:.2f}"
            })
    
    custo_total_prenhez = custo_por_ciclo * num_ciclos

    return jsonify({
        "custo_medio_ciclo": f"R$ {custo_por_ciclo:.2f}",
        "custo_total_estimado": f"R$ {custo_total_prenhez:.2f}",
        "detalhes_ciclo": detalhes,
        "ciclos_considerados": num_ciclos
    }), 200
