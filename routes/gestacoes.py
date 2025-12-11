from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.models import Gestacao

gestacoes_bp = Blueprint("gestacoes", __name__)

@gestacoes_bp.route("/", methods=["GET"])
def get_gestacoes():
    gestacoes = Gestacao.query.all()
    return jsonify([
        {
            "id": g.id,
            "egua_id": g.egua_id,
            "doadora_id": g.doadora_id,
            "garanhao_id": g.garanhao_id,
            "embriao_id": g.embriao_id,
            "tipo_gestacao": g.tipo_gestacao,
            "data_cobertura": g.data_cobertura,
            "data_diagnostico": g.data_diagnostico,
            "idade_gestacional": g.idade_gestacional,
            "data_prevista_parto": g.data_prevista_parto,
            "status_gestacao": g.status_gestacao,
            "exames_gestacao": g.exames_gestacao,
            "complicacoes": g.complicacoes,
            "observacoes": g.observacoes,
            "custo_acompanhamento": g.custo_acompanhamento,
        }
        for g in gestacoes
    ])

@gestacoes_bp.route("/<int:gestacao_id>", methods=["GET"])
def get_gestacao(gestacao_id):
    gestacao = Gestacao.query.get_or_404(gestacao_id)
    return jsonify({
        "id": gestacao.id,
        "egua_id": gestacao.egua_id,
        "doadora_id": gestacao.doadora_id,
        "garanhao_id": gestacao.garanhao_id,
        "embriao_id": gestacao.embriao_id,
        "tipo_gestacao": gestacao.tipo_gestacao,
        "data_cobertura": gestacao.data_cobertura,
        "data_diagnostico": gestacao.data_diagnostico,
        "idade_gestacional": gestacao.idade_gestacional,
        "data_prevista_parto": gestacao.data_prevista_parto,
        "status_gestacao": gestacao.status_gestacao,
        "exames_gestacao": gestacao.exames_gestacao,
        "complicacoes": gestacao.complicacoes,
        "observacoes": gestacao.observacoes,
        "custo_acompanhamento": gestacao.custo_acompanhamento,
    })

@gestacoes_bp.route("/", methods=["POST"])
def add_gestacao():
    data = request.get_json()
    new_gestacao = Gestacao(
        egua_id=data["egua_id"],
        doadora_id=data.get("doadora_id"),
        garanhao_id=data.get("garanhao_id"),
        embriao_id=data.get("embriao_id"),
        tipo_gestacao=data.get("tipo_gestacao"),
        data_cobertura=data.get("data_cobertura"),
        data_diagnostico=data.get("data_diagnostico"),
        idade_gestacional=data.get("idade_gestacional"),
        data_prevista_parto=data.get("data_prevista_parto"),
        status_gestacao=data.get("status_gestacao"),
        exames_gestacao=data.get("exames_gestacao"),
        complicacoes=data.get("complicacoes"),
        observacoes=data.get("observacoes"),
        custo_acompanhamento=data.get("custo_acompanhamento"),
    )
    db.session.add(new_gestacao)
    db.session.commit()
    return jsonify({"message": "Gestação adicionada com sucesso!", "id": new_gestacao.id}), 201

@gestacoes_bp.route("/<int:gestacao_id>", methods=["PUT"])
def update_gestacao(gestacao_id):
    gestacao = Gestacao.query.get_or_404(gestacao_id)
    data = request.get_json()
    gestacao.egua_id = data.get("egua_id", gestacao.egua_id)
    gestacao.doadora_id = data.get("doadora_id", gestacao.doadora_id)
    gestacao.garanhao_id = data.get("garanhao_id", gestacao.garanhao_id)
    gestacao.embriao_id = data.get("embriao_id", gestacao.embriao_id)
    gestacao.tipo_gestacao = data.get("tipo_gestacao", gestacao.tipo_gestacao)
    gestacao.data_cobertura = data.get("data_cobertura", gestacao.data_cobertura)
    gestacao.data_diagnostico = data.get("data_diagnostico", gestacao.data_diagnostico)
    gestacao.idade_gestacional = data.get("idade_gestacional", gestacao.idade_gestacional)
    gestacao.data_prevista_parto = data.get("data_prevista_parto", gestacao.data_prevista_parto)
    gestacao.status_gestacao = data.get("status_gestacao", gestacao.status_gestacao)
    gestacao.exames_gestacao = data.get("exames_gestacao", gestacao.exames_gestacao)
    gestacao.complicacoes = data.get("complicacoes", gestacao.complicacoes)
    gestacao.observacoes = data.get("observacoes", gestacao.observacoes)
    gestacao.custo_acompanhamento = data.get("custo_acompanhamento", gestacao.custo_acompanhamento)
    db.session.commit()
    return jsonify({"message": "Gestação atualizada com sucesso!"})

@gestacoes_bp.route("/<int:gestacao_id>", methods=["DELETE"])
def delete_gestacao(gestacao_id):
    gestacao = Gestacao.query.get_or_404(gestacao_id)
    db.session.delete(gestacao)
    db.session.commit()
    return jsonify({"message": "Gestação deletada com sucesso!"})

