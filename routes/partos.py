from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.models import Parto

partos_bp = Blueprint("partos", __name__)

@partos_bp.route("/", methods=["GET"])
def get_partos():
    partos = Parto.query.all()
    return jsonify([
        {
            "id": p.id,
            "gestacao_id": p.gestacao_id,
            "egua_id": p.egua_id,
            "data_parto": p.data_parto,
            "tipo_parto": p.tipo_parto,
            "duracao_parto": p.duracao_parto,
            "veterinario_responsavel": p.veterinario_responsavel,
            "peso_potro": p.peso_potro,
            "sexo_potro": p.sexo_potro,
            "nome_potro": p.nome_potro,
            "registro_potro": p.registro_potro,
            "condicoes_nascimento": p.condicoes_nascimento,
            "complicacoes": p.complicacoes,
            "observacoes": p.observacoes,
            "custo_parto": p.custo_parto,
        }
        for p in partos
    ])

@partos_bp.route("/<int:parto_id>", methods=["GET"])
def get_parto(parto_id):
    parto = Parto.query.get_or_404(parto_id)
    return jsonify({
        "id": parto.id,
        "gestacao_id": parto.gestacao_id,
        "egua_id": parto.egua_id,
        "data_parto": parto.data_parto,
        "tipo_parto": parto.tipo_parto,
        "duracao_parto": parto.duracao_parto,
        "veterinario_responsavel": parto.veterinario_responsavel,
        "peso_potro": parto.peso_potro,
        "sexo_potro": parto.sexo_potro,
        "nome_potro": parto.nome_potro,
        "registro_potro": parto.registro_potro,
        "condicoes_nascimento": parto.condicoes_nascimento,
        "complicacoes": parto.complicacoes,
        "observacoes": parto.observacoes,
        "custo_parto": parto.custo_parto,
    })

@partos_bp.route("/", methods=["POST"])
def add_parto():
    data = request.get_json()
    new_parto = Parto(
        gestacao_id=data["gestacao_id"],
        egua_id=data["egua_id"],
        data_parto=data.get("data_parto"),
        tipo_parto=data.get("tipo_parto"),
        duracao_parto=data.get("duracao_parto"),
        veterinario_responsavel=data.get("veterinario_responsavel"),
        peso_potro=data.get("peso_potro"),
        sexo_potro=data.get("sexo_potro"),
        nome_potro=data.get("nome_potro"),
        registro_potro=data.get("registro_potro"),
        condicoes_nascimento=data.get("condicoes_nascimento"),
        complicacoes=data.get("complicacoes"),
        observacoes=data.get("observacoes"),
        custo_parto=data.get("custo_parto"),
    )
    db.session.add(new_parto)
    db.session.commit()
    return jsonify({"message": "Parto adicionado com sucesso!", "id": new_parto.id}), 201

@partos_bp.route("/<int:parto_id>", methods=["PUT"])
def update_parto(parto_id):
    parto = Parto.query.get_or_404(parto_id)
    data = request.get_json()
    parto.gestacao_id = data.get("gestacao_id", parto.gestacao_id)
    parto.egua_id = data.get("egua_id", parto.egua_id)
    parto.data_parto = data.get("data_parto", parto.data_parto)
    parto.tipo_parto = data.get("tipo_parto", parto.tipo_parto)
    parto.duracao_parto = data.get("duracao_parto", parto.duracao_parto)
    parto.veterinario_responsavel = data.get("veterinario_responsavel", parto.veterinario_responsavel)
    parto.peso_potro = data.get("peso_potro", parto.peso_potro)
    parto.sexo_potro = data.get("sexo_potro", parto.sexo_potro)
    parto.nome_potro = data.get("nome_potro", parto.nome_potro)
    parto.registro_potro = data.get("registro_potro", parto.registro_potro)
    parto.condicoes_nascimento = data.get("condicoes_nascimento", parto.condicoes_nascimento)
    parto.complicacoes = data.get("complicacoes", parto.complicacoes)
    parto.observacoes = data.get("observacoes", parto.observacoes)
    parto.custo_parto = data.get("custo_parto", parto.custo_parto)
    db.session.commit()
    return jsonify({"message": "Parto atualizado com sucesso!"})

@partos_bp.route("/<int:parto_id>", methods=["DELETE"])
def delete_parto(parto_id):
    parto = Parto.query.get_or_404(parto_id)
    db.session.delete(parto)
    db.session.commit()
    return jsonify({"message": "Parto deletado com sucesso!"})

