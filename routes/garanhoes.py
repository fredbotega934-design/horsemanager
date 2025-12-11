from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.models import Garanhao

garanhoes_bp = Blueprint("garanhoes", __name__)

@garanhoes_bp.route("/", methods=["GET"])
def get_garanhoes():
    garanhoes = Garanhao.query.all()
    return jsonify([
        {
            "id": g.id,
            "nome_garanhao": g.nome_garanhao,
            "proprietario_id": g.proprietario_id,
            "idade": g.idade,
            "raca": g.raca,
            "registro": g.registro,
            "data_nascimento": g.data_nascimento,
            "pelagem": g.pelagem,
            "altura": g.altura,
            "peso": g.peso,
            "microchip": g.microchip,
            "pai": g.pai,
            "mae": g.mae,
            "status_reprodutivo": g.status_reprodutivo,
            "tipo_cobertura": g.tipo_cobertura,
            "valor_cobertura": g.valor_cobertura,
            "historico_coberturas": g.historico_coberturas,
            "taxa_prenhez": g.taxa_prenhez,
            "qualidade_semen": g.qualidade_semen,
            "observacoes": g.observacoes,
            "data_cadastro": g.data_cadastro,
        }
        for g in garanhoes
    ])

@garanhoes_bp.route("/<int:garanhao_id>", methods=["GET"])
def get_garanhao(garanhao_id):
    garanhao = Garanhao.query.get_or_404(garanhao_id)
    return jsonify({
        "id": garanhao.id,
        "nome_garanhao": garanhao.nome_garanhao,
        "proprietario_id": garanhao.proprietario_id,
        "idade": garanhao.idade,
        "raca": garanhao.raca,
        "registro": garanhao.registro,
        "data_nascimento": garanhao.data_nascimento,
        "pelagem": garanhao.pelagem,
        "altura": garanhao.altura,
        "peso": garanhao.peso,
        "microchip": garanhao.microchip,
        "pai": garanhao.pai,
        "mae": garanhao.mae,
        "status_reprodutivo": garanhao.status_reprodutivo,
        "tipo_cobertura": garanhao.tipo_cobertura,
        "valor_cobertura": garanhao.valor_cobertura,
        "historico_coberturas": garanhao.historico_coberturas,
        "taxa_prenhez": garanhao.taxa_prenhez,
        "qualidade_semen": garanhao.qualidade_semen,
        "observacoes": garanhao.observacoes,
        "data_cadastro": garanhao.data_cadastro,
    })

@garanhoes_bp.route("/", methods=["POST"])
def add_garanhao():
    data = request.get_json()
    new_garanhao = Garanhao(
        nome_garanhao=data["nome_garanhao"],
        proprietario_id=data["proprietario_id"],
        idade=data.get("idade"),
        raca=data.get("raca"),
        registro=data.get("registro"),
        data_nascimento=data.get("data_nascimento"),
        pelagem=data.get("pelagem"),
        altura=data.get("altura"),
        peso=data.get("peso"),
        microchip=data.get("microchip"),
        pai=data.get("pai"),
        mae=data.get("mae"),
        status_reprodutivo=data.get("status_reprodutivo"),
        tipo_cobertura=data.get("tipo_cobertura"),
        valor_cobertura=data.get("valor_cobertura"),
        historico_coberturas=data.get("historico_coberturas"),
        taxa_prenhez=data.get("taxa_prenhez"),
        qualidade_semen=data.get("qualidade_semen"),
        observacoes=data.get("observacoes"),
        data_cadastro=data.get("data_cadastro"),
    )
    db.session.add(new_garanhao)
    db.session.commit()
    return jsonify({"message": "Garanhão adicionado com sucesso!", "id": new_garanhao.id}), 201

@garanhoes_bp.route("/<int:garanhao_id>", methods=["PUT"])
def update_garanhao(garanhao_id):
    garanhao = Garanhao.query.get_or_404(garanhao_id)
    data = request.get_json()
    garanhao.nome_garanhao = data.get("nome_garanhao", garanhao.nome_garanhao)
    garanhao.proprietario_id = data.get("proprietario_id", garanhao.proprietario_id)
    garanhao.idade = data.get("idade", garanhao.idade)
    garanhao.raca = data.get("raca", garanhao.raca)
    garanhao.registro = data.get("registro", garanhao.registro)
    garanhao.data_nascimento = data.get("data_nascimento", garanhao.data_nascimento)
    garanhao.pelagem = data.get("pelagem", garanhao.pelagem)
    garanhao.altura = data.get("altura", garanhao.altura)
    garanhao.peso = data.get("peso", garanhao.peso)
    garanhao.microchip = data.get("microchip", garanhao.microchip)
    garanhao.pai = data.get("pai", garanhao.pai)
    garanhao.mae = data.get("mae", garanhao.mae)
    garanhao.status_reprodutivo = data.get("status_reprodutivo", garanhao.status_reprodutivo)
    garanhao.tipo_cobertura = data.get("tipo_cobertura", garanhao.tipo_cobertura)
    garanhao.valor_cobertura = data.get("valor_cobertura", garanhao.valor_cobertura)
    garanhao.historico_coberturas = data.get("historico_coberturas", garanhao.historico_coberturas)
    garanhao.taxa_prenhez = data.get("taxa_prenhez", garanhao.taxa_prenhez)
    garanhao.qualidade_semen = data.get("qualidade_semen", garanhao.qualidade_semen)
    garanhao.observacoes = data.get("observacoes", garanhao.observacoes)
    garanhao.data_cadastro = data.get("data_cadastro", garanhao.data_cadastro)
    db.session.commit()
    return jsonify({"message": "Garanhão atualizado com sucesso!"})

@garanhoes_bp.route("/<int:garanhao_id>", methods=["DELETE"])
def delete_garanhao(garanhao_id):
    garanhao = Garanhao.query.get_or_404(garanhao_id)
    db.session.delete(garanhao)
    db.session.commit()
    return jsonify({"message": "Garanhão deletado com sucesso!"})

