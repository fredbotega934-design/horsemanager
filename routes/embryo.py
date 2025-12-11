from flask import Blueprint, request, jsonify
from models.embryo import Embriao
from models.database import db_session
from auth.middleware import token_required, role_required
from datetime import datetime

embryo_bp = Blueprint("embryo", __name__)

@embryo_bp.route("", methods=["POST"])
@token_required
def add_embryo(current_user):
    data = request.get_json()
    try:
        novo = Embriao(
            tenant_id=current_user.tenant_id,
            doadora_id=data.get('doadora'),
            garanhao_nome=data.get('garanhao'),
            data_producao=datetime.strptime(data.get('data'), '%Y-%m-%d').date(),
            laboratorio_origem=data.get('lab'),
            grau_qualidade=data.get('grau'), # G1, G2
            estagio_desenvolvimento=data.get('estagio'), # Blasto, Morula
            status="Congelado", # Padrao inicial
            botijao=data.get('botijao'),
            caneca=data.get('caneca')
        )
        db_session.add(novo)
        db_session.commit()
        return jsonify({"message": "Embrião Congelado com Sucesso", "id": novo.id}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

@embryo_bp.route("", methods=["GET"])
@token_required
def list_embryos(current_user):
    # Lista apenas os que estao no estoque (Congelados ou Frescos aguardando TE)
    embrioes = db_session.query(Embriao).filter_by(tenant_id=current_user.tenant_id).filter(Embriao.status.in_(['Congelado', 'Fresco'])).all()
    
    lista = []
    for e in embrioes:
        lista.append({
            "id": e.id,
            "cruzamento": f"Doadora {e.doadora_id} x {e.garanhao_nome}",
            "qualidade": f"{e.estagio_desenvolvimento} (G{e.grau_qualidade})",
            "local": f"Botijão {e.botijao} / Caneca {e.caneca}",
            "data": e.data_producao.strftime("%d/%m/%Y")
        })
    return jsonify(lista), 200
