from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.models import TransferenciaEmbriao

transferencias_embriao_bp = Blueprint("transferencias_embriao", __name__)

@transferencias_embriao_bp.route("/", methods=["GET"])
def get_transferencias_embriao():
    transferencias = TransferenciaEmbriao.query.all()
    return jsonify([
        {
            "id": t.id,
            "doadora_id": t.doadora_id,
            "receptora_id": t.receptora_id,
            "embriao_id": t.embriao_id,
            "data_transferencia": t.data_transferencia,
            "dia_ciclo_doadora": t.dia_ciclo_doadora,
            "dia_ciclo_receptora": t.dia_ciclo_receptora,
            "sincronia": t.sincronia,
            "metodo_transferencia": t.metodo_transferencia,
            "veterinario_responsavel": t.veterinario_responsavel,
            "crmv_veterinario": t.crmv_veterinario,
            "qualidade_embriao": t.qualidade_embriao,
            "grau_desenvolvimento": t.grau_desenvolvimento,
            "diametro_embriao": t.diametro_embriao,
            "medicacao_pre_te": t.medicacao_pre_te,
            "medicacao_pos_te": t.medicacao_pos_te,
            "complicacoes": t.complicacoes,
            "resultado_te": t.resultado_te,
            "data_diagnostico": t.data_diagnostico,
            "metodo_diagnostico": t.metodo_diagnostico,
            "observacoes": t.observacoes,
            "custo_procedimento": t.custo_procedimento,
            "status": t.status,
        }
        for t in transferencias
    ])

@transferencias_embriao_bp.route("/<int:transferencia_id>", methods=["GET"])
def get_transferencia_embriao(transferencia_id):
    transferencia = TransferenciaEmbriao.query.get_or_404(transferencia_id)
    return jsonify({
        "id": transferencia.id,
        "doadora_id": transferencia.doadora_id,
        "receptora_id": transferencia.receptora_id,
        "embriao_id": transferencia.embriao_id,
        "data_transferencia": transferencia.data_transferencia,
        "dia_ciclo_doadora": transferencia.dia_ciclo_doadora,
        "dia_ciclo_receptora": transferencia.dia_ciclo_receptora,
        "sincronia": transferencia.sincronia,
        "metodo_transferencia": transferencia.metodo_transferencia,
        "veterinario_responsavel": transferencia.veterinario_responsavel,
        "crmv_veterinario": transferencia.crmv_veterinario,
        "qualidade_embriao": transferencia.qualidade_embriao,
        "grau_desenvolvimento": transferencia.grau_desenvolvimento,
        "diametro_embriao": transferencia.diametro_embriao,
        "medicacao_pre_te": transferencia.medicacao_pre_te,
        "medicacao_pos_te": transferencia.medicacao_pos_te,
        "complicacoes": transferencia.complicacoes,
        "resultado_te": transferencia.resultado_te,
        "data_diagnostico": transferencia.data_diagnostico,
        "metodo_diagnostico": transferencia.metodo_diagnostico,
        "observacoes": transferencia.observacoes,
        "custo_procedimento": transferencia.custo_procedimento,
        "status": transferencia.status,
    })

@transferencias_embriao_bp.route("/", methods=["POST"])
def add_transferencia_embriao():
    data = request.get_json()
    new_transferencia = TransferenciaEmbriao(
        doadora_id=data["doadora_id"],
        receptora_id=data["receptora_id"],
        embriao_id=data["embriao_id"],
        data_transferencia=data.get("data_transferencia"),
        dia_ciclo_doadora=data.get("dia_ciclo_doadora"),
        dia_ciclo_receptora=data.get("dia_ciclo_receptora"),
        sincronia=data.get("sincronia"),
        metodo_transferencia=data.get("metodo_transferencia"),
        veterinario_responsavel=data.get("veterinario_responsavel"),
        crmv_veterinario=data.get("crmv_veterinario"),
        qualidade_embriao=data.get("qualidade_embriao"),
        grau_desenvolvimento=data.get("grau_desenvolvimento"),
        diametro_embriao=data.get("diametro_embriao"),
        medicacao_pre_te=data.get("medicacao_pre_te"),
        medicacao_pos_te=data.get("medicacao_pos_te"),
        complicacoes=data.get("complicacoes"),
        resultado_te=data.get("resultado_te"),
        data_diagnostico=data.get("data_diagnostico"),
        metodo_diagnostico=data.get("metodo_diagnostico"),
        observacoes=data.get("observacoes"),
        custo_procedimento=data.get("custo_procedimento"),
        status=data.get("status"),
    )
    db.session.add(new_transferencia)
    db.session.commit()
    return jsonify({"message": "Transferência de Embrião adicionada com sucesso!", "id": new_transferencia.id}), 201

@transferencias_embriao_bp.route("/<int:transferencia_id>", methods=["PUT"])
def update_transferencia_embriao(transferencia_id):
    transferencia = TransferenciaEmbriao.query.get_or_404(transferencia_id)
    data = request.get_json()
    transferencia.doadora_id = data.get("doadora_id", transferencia.doadora_id)
    transferencia.receptora_id = data.get("receptora_id", transferencia.receptora_id)
    transferencia.embriao_id = data.get("embriao_id", transferencia.embriao_id)
    transferencia.data_transferencia = data.get("data_transferencia", transferencia.data_transferencia)
    transferencia.dia_ciclo_doadora = data.get("dia_ciclo_doadora", transferencia.dia_ciclo_doadora)
    transferencia.dia_ciclo_receptora = data.get("dia_ciclo_receptora", transferencia.dia_ciclo_receptora)
    transferencia.sincronia = data.get("sincronia", transferencia.sincronia)
    transferencia.metodo_transferencia = data.get("metodo_transferencia", transferencia.metodo_transferencia)
    transferencia.veterinario_responsavel = data.get("veterinario_responsavel", transferencia.veterinario_responsavel)
    transferencia.crmv_veterinario = data.get("crmv_veterinario", transferencia.crmv_veterinario)
    transferencia.qualidade_embriao = data.get("qualidade_embriao", transferencia.qualidade_embriao)
    transferencia.grau_desenvolvimento = data.get("grau_desenvolvimento", transferencia.grau_desenvolvimento)
    transferencia.diametro_embriao = data.get("diametro_embriao", transferencia.diametro_embriao)
    transferencia.medicacao_pre_te = data.get("medicacao_pre_te", transferencia.medicacao_pre_te)
    transferencia.medicacao_pos_te = data.get("medicacao_pos_te", transferencia.medicacao_pos_te)
    transferencia.complicacoes = data.get("complicacoes", transferencia.complicacoes)
    transferencia.resultado_te = data.get("resultado_te", transferencia.resultado_te)
    transferencia.data_diagnostico = data.get("data_diagnostico", transferencia.data_diagnostico)
    transferencia.metodo_diagnostico = data.get("metodo_diagnostico", transferencia.metodo_diagnostico)
    transferencia.observacoes = data.get("observacoes", transferencia.observacoes)
    transferencia.custo_procedimento = data.get("custo_procedimento", transferencia.custo_procedimento)
    transferencia.status = data.get("status", transferencia.status)
    db.session.commit()
    return jsonify({"message": "Transferência de Embrião atualizada com sucesso!"})

@transferencias_embriao_bp.route("/<int:transferencia_id>", methods=["DELETE"])
def delete_transferencia_embriao(transferencia_id):
    transferencia = TransferenciaEmbriao.query.get_or_404(transferencia_id)
    db.session.delete(transferencia)
    db.session.commit()
    return jsonify({"message": "Transferência de Embrião deletada com sucesso!"})

