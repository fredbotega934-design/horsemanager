from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.models import ProcedimentoOPU

procedimentos_opu_bp = Blueprint("procedimentos_opu", __name__)

@procedimentos_opu_bp.route("/", methods=["GET"])
def get_procedimentos_opu():
    procedimentos = ProcedimentoOPU.query.all()
    return jsonify([
        {
            "id": p.id,
            "egua_id": p.egua_id,
            "tipo_procedimento": p.tipo_procedimento,
            "data_procedimento": p.data_procedimento,
            "foliculos_aspirados": p.foliculos_aspirados,
            "ccos_recuperados": p.ccos_recuperados,
            "taxa_recuperacao": p.taxa_recuperacao,
            "ciclo_estral": p.ciclo_estral,
            "dia_ciclo": p.dia_ciclo,
            "medicacao_utilizada": p.medicacao_utilizada,
            "protocolo_hormonal": p.protocolo_hormonal,
            "veterinario_responsavel": p.veterinario_responsavel,
            "crmv_veterinario": p.crmv_veterinario,
            "tecnico_responsavel": p.tecnico_responsavel,
            "equipamento_utilizado": p.equipamento_utilizado,
            "complicacoes": p.complicacoes,
            "pressao_aspiracao": p.pressao_aspiracao,
            "rotacao_agulha": p.rotacao_agulha,
            "metodo_lavagem": p.metodo_lavagem,
            "numero_lavagens_foliculo": p.numero_lavagens_foliculo,
            "medicacao_pos_opu": p.medicacao_pos_opu,
            "observacoes": p.observacoes,
            "proxima_opu": p.proxima_opu,
            "tamanhos_foliculos": p.tamanhos_foliculos,
            "qualidade_ccos": p.qualidade_ccos,
            "tempo_procedimento": p.tempo_procedimento,
            "custo_procedimento": p.custo_procedimento,
            "status": p.status,
            "custo_por_oocito": round(p.custo_procedimento / p.ccos_recuperados, 2) if p.ccos_recuperados > 0 else 0.0
        }
        for p in procedimentos
    ])

@procedimentos_opu_bp.route("/<int:procedimento_id>", methods=["GET"])
def get_procedimento_opu(procedimento_id):
    procedimento = ProcedimentoOPU.query.get_or_404(procedimento_id)
    return jsonify({
        "id": procedimento.id,
        "egua_id": procedimento.egua_id,
        "tipo_procedimento": procedimento.tipo_procedimento,
        "data_procedimento": procedimento.data_procedimento,
        "foliculos_aspirados": procedimento.foliculos_aspirados,
        "ccos_recuperados": procedimento.ccos_recuperados,
        "taxa_recuperacao": procedimento.taxa_recuperacao,
        "ciclo_estral": procedimento.ciclo_estral,
        "dia_ciclo": procedimento.dia_ciclo,
        "medicacao_utilizada": procedimento.medicacao_utilizada,
        "protocolo_hormonal": procedimento.protocolo_hormonal,
        "veterinario_responsavel": procedimento.veterinario_responsavel,
        "crmv_veterinario": procedimento.crmv_veterinario,
        "tecnico_responsavel": procedimento.tecnico_responsavel,
        "equipamento_utilizado": procedimento.equipamento_utilizado,
        "complicacoes": procedimento.complicacoes,
        "pressao_aspiracao": procedimento.pressao_aspiracao,
        "rotacao_agulha": procedimento.rotacao_agulha,
        "metodo_lavagem": procedimento.metodo_lavagem,
        "numero_lavagens_foliculo": procedimento.numero_lavagens_foliculo,
        "medicacao_pos_opu": procedimento.medicacao_pos_opu,
        "observacoes": procedimento.observacoes,
        "proxima_opu": procedimento.proxima_opu,
        "tamanhos_foliculos": procedimento.tamanhos_foliculos,
        "qualidade_ccos": procedimento.qualidade_ccos,
        "tempo_procedimento": procedimento.tempo_procedimento,
        "custo_procedimento": procedimento.custo_procedimento,
        "status": procedimento.status,
    })

@procedimentos_opu_bp.route("/", methods=["POST"])
def add_procedimento_opu():
    data = request.get_json()
    new_procedimento = ProcedimentoOPU(
        egua_id=data["egua_id"],
        tipo_procedimento=data.get("tipo_procedimento"),
        data_procedimento=data.get("data_procedimento"),
        foliculos_aspirados=data.get("foliculos_aspirados"),
        ccos_recuperados=data.get("ccos_recuperados"),
        taxa_recuperacao=data.get("taxa_recuperacao"),
        ciclo_estral=data.get("ciclo_estral"),
        dia_ciclo=data.get("dia_ciclo"),
        medicacao_utilizada=data.get("medicacao_utilizada"),
        protocolo_hormonal=data.get("protocolo_hormonal"),
        veterinario_responsavel=data.get("veterinario_responsavel"),
        crmv_veterinario=data.get("crmv_veterinario"),
        tecnico_responsavel=data.get("tecnico_responsavel"),
        equipamento_utilizado=data.get("equipamento_utilizado"),
        complicacoes=data.get("complicacoes"),
        pressao_aspiracao=data.get("pressao_aspiracao"),
        rotacao_agulha=data.get("rotacao_agulha"),
        metodo_lavagem=data.get("metodo_lavagem"),
        numero_lavagens_foliculo=data.get("numero_lavagens_foliculo"),
        medicacao_pos_opu=data.get("medicacao_pos_opu"),
        observacoes=data.get("observacoes"),
        proxima_opu=data.get("proxima_opu"),
        tamanhos_foliculos=data.get("tamanhos_foliculos"),
        qualidade_ccos=data.get("qualidade_ccos"),
        tempo_procedimento=data.get("tempo_procedimento"),
        custo_procedimento=data.get("custo_procedimento"),
        status=data.get("status"),
    )
    db.session.add(new_procedimento)
    db.session.commit()
    return jsonify({"message": "Procedimento OPU adicionado com sucesso!", "id": new_procedimento.id}), 201

@procedimentos_opu_bp.route("/<int:procedimento_id>", methods=["PUT"])
def update_procedimento_opu(procedimento_id):
    procedimento = ProcedimentoOPU.query.get_or_404(procedimento_id)
    data = request.get_json()
    procedimento.egua_id = data.get("egua_id", procedimento.egua_id)
    procedimento.tipo_procedimento = data.get("tipo_procedimento", procedimento.tipo_procedimento)
    procedimento.data_procedimento = data.get("data_procedimento", procedimento.data_procedimento)
    procedimento.foliculos_aspirados = data.get("foliculos_aspirados", procedimento.foliculos_aspirados)
    procedimento.ccos_recuperados = data.get("ccos_recuperados", procedimento.ccos_recuperados)
    procedimento.taxa_recuperacao = data.get("taxa_recuperacao", procedimento.taxa_recuperacao)
    procedimento.ciclo_estral = data.get("ciclo_estral", procedimento.ciclo_estral)
    procedimento.dia_ciclo = data.get("dia_ciclo", procedimento.dia_ciclo)
    procedimento.medicacao_utilizada = data.get("medicacao_utilizada", procedimento.medicacao_utilizada)
    procedimento.protocolo_hormonal = data.get("protocolo_hormonal", procedimento.protocolo_hormonal)
    procedimento.veterinario_responsavel = data.get("veterinario_responsavel", procedimento.veterinario_responsavel)
    procedimento.crmv_veterinario = data.get("crmv_veterinario", procedimento.crmv_veterinario)
    procedimento.tecnico_responsavel = data.get("tecnico_responsavel", procedimento.tecnico_responsavel)
    procedimento.equipamento_utilizado = data.get("equipamento_utilizado", procedimento.equipamento_utilizado)
    procedimento.complicacoes = data.get("complicacoes", procedimento.complicacoes)
    procedimento.pressao_aspiracao = data.get("pressao_aspiracao", procedimento.pressao_aspiracao)
    procedimento.rotacao_agulha = data.get("rotacao_agulha", procedimento.rotacao_agulha)
    procedimento.metodo_lavagem = data.get("metodo_lavagem", procedimento.metodo_lavagem)
    procedimento.numero_lavagens_foliculo = data.get("numero_lavagens_foliculo", procedimento.numero_lavagens_foliculo)
    procedimento.medicacao_pos_opu = data.get("medicacao_pos_opu", procedimento.medicacao_pos_opu)
    procedimento.observacoes = data.get("observacoes", procedimento.observacoes)
    procedimento.proxima_opu = data.get("proxima_opu", procedimento.proxima_opu)
    procedimento.tamanhos_foliculos = data.get("tamanhos_foliculos", procedimento.tamanhos_foliculos)
    procedimento.qualidade_ccos = data.get("qualidade_ccos", procedimento.qualidade_ccos)
    procedimento.tempo_procedimento = data.get("tempo_procedimento", procedimento.tempo_procedimento)
    procedimento.custo_procedimento = data.get("custo_procedimento", procedimento.custo_procedimento)
    procedimento.status = data.get("status", procedimento.status)
    db.session.commit()
    return jsonify({"message": "Procedimento OPU atualizado com sucesso!"})

@procedimentos_opu_bp.route("/<int:procedimento_id>", methods=["DELETE"])
def delete_procedimento_opu(procedimento_id):
    procedimento = ProcedimentoOPU.query.get_or_404(procedimento_id)
    db.session.delete(procedimento)
    db.session.commit()
    return jsonify({"message": "Procedimento OPU deletado com sucesso!"})
