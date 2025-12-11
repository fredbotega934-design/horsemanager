from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.models import AnaliseLaboratorial

analises_laboratoriais_bp = Blueprint("analises_laboratoriais", __name__)

@analises_laboratoriais_bp.route("/", methods=["GET"])
def get_analises_laboratoriais():
    analises = AnaliseLaboratorial.query.all()
    return jsonify([
        {
            "id": a.id,
            "egua_id": a.egua_id,
            "embriao_uid": a.embriao_uid,
            "tipo_analise": a.tipo_analise,
            "material_coletado": a.material_coletado,
            "data_coleta": a.data_coleta,
            "parametros_analisados": a.parametros_analisados,
            "laboratorio": a.laboratorio,
            "veterinario_solicitante": a.veterinario_solicitante,
            "resultado_geral": a.resultado_geral,
            "observacoes": a.observacoes,
            "custo_analise": a.custo_analise,
            "taxa_maturacao": a.taxa_maturacao,
            "taxa_clivagem": a.taxa_clivagem,
            "taxa_blastocisto": a.taxa_blastocisto,
            "custo_por_blastocisto": round(a.custo_analise / (a.taxa_blastocisto / 100), 2) if a.taxa_blastocisto and a.taxa_blastocisto > 0 else 0.0
        }
        for a in analises
    ])

@analises_laboratoriais_bp.route("/<int:analise_id>", methods=["GET"])
def get_analise_laboratorial(analise_id):
    analise = AnaliseLaboratorial.query.get_or_404(analise_id)
    return jsonify({
        "id": analise.id,
        "egua_id": analise.egua_id,
        "embriao_uid": analise.embriao_uid,
        "tipo_analise": analise.tipo_analise,
        "material_coletado": analise.material_coletado,
        "data_coleta": analise.data_coleta,
        "parametros_analisados": analise.parametros_analisados,
        "laboratorio": analise.laboratorio,
        "veterinario_solicitante": analise.veterinario_solicitante,
        "resultado_geral": analise.resultado_geral,
        "observacoes": analise.observacoes,
        "custo_analise": analise.custo_analise,
        "taxa_maturacao": analise.taxa_maturacao,
        "taxa_clivagem": analise.taxa_clivagem,
        "taxa_blastocisto": analise.taxa_blastocisto,
    })

@analises_laboratoriais_bp.route("/", methods=["POST"])
def add_analise_laboratorial():
    data = request.get_json()
    new_analise = AnaliseLaboratorial(
        egua_id=data["egua_id"],
        embriao_uid=data.get("embriao_uid"),
        tipo_analise=data.get("tipo_analise"),
        material_coletado=data.get("material_coletado"),
        data_coleta=data.get("data_coleta"),
        parametros_analisados=data.get("parametros_analisados"),
        laboratorio=data.get("laboratorio"),
        veterinario_solicitante=data.get("veterinario_solicitante"),
        resultado_geral=data.get("resultado_geral"),
        observacoes=data.get("observacoes"),
        custo_analise=data.get("custo_analise"),
        taxa_maturacao=data.get("taxa_maturacao"),
        taxa_clivagem=data.get("taxa_clivagem"),
        taxa_blastocisto=data.get("taxa_blastocisto"),
    )
    db.session.add(new_analise)
    db.session.commit()
    return jsonify({"message": "Análise Laboratorial adicionada com sucesso!", "id": new_analise.id}), 201

@analises_laboratoriais_bp.route("/<int:analise_id>", methods=["PUT"])
def update_analise_laboratorial(analise_id):
    analise = AnaliseLaboratorial.query.get_or_404(analise_id)
    data = request.get_json()
    analise.egua_id = data.get("egua_id", analise.egua_id)
    analise.embriao_uid = data.get("embriao_uid", analise.embriao_uid)
    analise.tipo_analise = data.get("tipo_analise", analise.tipo_analise)
    analise.material_coletado = data.get("material_coletado", analise.material_coletado)
    analise.data_coleta = data.get("data_coleta", analise.data_coleta)
    analise.parametros_analisados = data.get("parametros_analisados", analise.parametros_analisados)
    analise.laboratorio = data.get("laboratorio", analise.laboratorio)
    analise.veterinario_solicitante = data.get("veterinario_solicitante", analise.veterinario_solicitante)
    analise.resultado_geral = data.get("resultado_geral", analise.resultado_geral)
    analise.observacoes = data.get("observacoes", analise.observacoes)
    analise.custo_analise = data.get("custo_analise", analise.custo_analise)
    analise.taxa_maturacao = data.get("taxa_maturacao", analise.taxa_maturacao)
    analise.taxa_clivagem = data.get("taxa_clivagem", analise.taxa_clivagem)
    analise.taxa_blastocisto = data.get("taxa_blastocisto", analise.taxa_blastocisto)
    db.session.commit()
    return jsonify({"message": "Análise Laboratorial atualizada com sucesso!"})

@analises_laboratoriais_bp.route("/<int:analise_id>", methods=["DELETE"])
def delete_analise_laboratorial(analise_id):
    analise = AnaliseLaboratorial.query.get_or_404(analise_id)
    db.session.delete(analise)
    db.session.commit()
    return jsonify({"message": "Análise Laboratorial deletada com sucesso!"})

