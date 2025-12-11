from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.models import Embriao

embrioes_bp = Blueprint("embrioes", __name__)

@embrioes_bp.route("/", methods=["GET"])
def get_embrioes():
    embrioes = Embriao.query.all()
    return jsonify([
        {
            "id": e.id,
            "doadora_id": e.doadora_id,
            "garanhao_id": e.garanhao_id,
            "data_coleta": e.data_coleta,
            "metodo_coleta": e.metodo_coleta,
            "qualidade": e.qualidade,
            "grau_desenvolvimento": e.grau_desenvolvimento,
            "diametro": e.diametro,
            "status": e.status,
            "data_congelamento": e.data_congelamento,
            "metodo_congelamento": e.metodo_congelamento,
            "recipiente_armazenamento": e.recipiente_armazenamento,
            "posicao_tanque": e.posicao_tanque,
            "observacoes": e.observacoes,
            "custo_producao": e.custo_producao,
        }
        for e in embrioes
    ])

@embrioes_bp.route("/<int:embriao_id>", methods=["GET"])
def get_embriao(embriao_id):
    embriao = Embriao.query.get_or_404(embriao_id)
    return jsonify({
        "id": embriao.id,
        "doadora_id": embriao.doadora_id,
        "garanhao_id": embriao.garanhao_id,
        "data_coleta": embriao.data_coleta,
        "metodo_coleta": embriao.metodo_coleta,
        "qualidade": embriao.qualidade,
        "grau_desenvolvimento": embriao.grau_desenvolvimento,
        "diametro": embriao.diametro,
        "status": embriao.status,
        "data_congelamento": embriao.data_congelamento,
        "metodo_congelamento": embriao.metodo_congelamento,
        "recipiente_armazenamento": embriao.recipiente_armazenamento,
        "posicao_tanque": embriao.posicao_tanque,
        "observacoes": embriao.observacoes,
        "custo_producao": embriao.custo_producao,
    })

@embrioes_bp.route("/", methods=["POST"])
def add_embriao():
    data = request.get_json()
    new_embriao = Embriao(
        doadora_id=data["doadora_id"],
        garanhao_id=data["garanhao_id"],
        data_coleta=data.get("data_coleta"),
        metodo_coleta=data.get("metodo_coleta"),
        qualidade=data.get("qualidade"),
        grau_desenvolvimento=data.get("grau_desenvolvimento"),
        diametro=data.get("diametro"),
        status=data.get("status"),
        data_congelamento=data.get("data_congelamento"),
        metodo_congelamento=data.get("metodo_congelamento"),
        recipiente_armazenamento=data.get("recipiente_armazenamento"),
        posicao_tanque=data.get("posicao_tanque"),
        observacoes=data.get("observacoes"),
        custo_producao=data.get("custo_producao"),
    )
    db.session.add(new_embriao)
    db.session.commit()
    return jsonify({"message": "Embrião adicionado com sucesso!", "id": new_embriao.id}), 201

@embrioes_bp.route("/<int:embriao_id>", methods=["PUT"])
def update_embriao(embriao_id):
    embriao = Embriao.query.get_or_404(embriao_id)
    data = request.get_json()
    embriao.doadora_id = data.get("doadora_id", embriao.doadora_id)
    embriao.garanhao_id = data.get("garanhao_id", embriao.garanhao_id)
    embriao.data_coleta = data.get("data_coleta", embriao.data_coleta)
    embriao.metodo_coleta = data.get("metodo_coleta", embriao.metodo_coleta)
    embriao.qualidade = data.get("qualidade", embriao.qualidade)
    embriao.grau_desenvolvimento = data.get("grau_desenvolvimento", embriao.grau_desenvolvimento)
    embriao.diametro = data.get("diametro", embriao.diametro)
    embriao.status = data.get("status", embriao.status)
    embriao.data_congelamento = data.get("data_congelamento", embriao.data_congelamento)
    embriao.metodo_congelamento = data.get("metodo_congelamento", embriao.metodo_congelamento)
    embriao.recipiente_armazenamento = data.get("recipiente_armazenamento", embriao.recipiente_armazenamento)
    embriao.posicao_tanque = data.get("posicao_tanque", embriao.posicao_tanque)
    embriao.observacoes = data.get("observacoes", embriao.observacoes)
    embriao.custo_producao = data.get("custo_producao", embriao.custo_producao)
    db.session.commit()
    return jsonify({"message": "Embrião atualizado com sucesso!"})

@embrioes_bp.route("/<int:embriao_id>", methods=["DELETE"])
def delete_embriao(embriao_id):
    embriao = Embriao.query.get_or_404(embriao_id)
    db.session.delete(embriao)
    db.session.commit()
    return jsonify({"message": "Embrião deletado com sucesso!"})

