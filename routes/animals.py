from flask import Blueprint, request, jsonify
from models.database import db_session
from models.animals import Egua, Receptora
from auth.middleware import token_required

animals_bp = Blueprint("animals", __name__)

@animals_bp.route("/eguas", methods=["GET"])
@token_required
def list_eguas(current_user):
    try:
        lista = db_session.query(Egua).filter_by(tenant_id=current_user.tenant_id).all()
        return jsonify([{"id":e.id, "nome":e.nome, "status":e.status, "historico":e.historico or ""} for e in lista]), 200
    except Exception as e:
        print(f"Erro GET Eguas: {e}")
        return jsonify([]), 200

@animals_bp.route("/eguas", methods=["POST"])
@token_required
def add_egua(current_user):
    data = request.get_json()
    try:
        nova = Egua(
            tenant_id=current_user.tenant_id, 
            nome=data.get("nome"), 
            status=data.get("status"), 
            historico=data.get("historico", "")
        )
        db_session.add(nova)
        db_session.commit()
        return jsonify({"msg": "Salvo"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

@animals_bp.route("/eguas/<int:id>", methods=["PUT"])
@token_required
def update_egua(current_user, id):
    data = request.get_json()
    try:
        egua = db_session.query(Egua).get(id)
        if egua:
            if 'historico' in data: 
                antigo = egua.historico or ""
                novo = f"{data['historico']} ({data.get('data','')})"
                egua.historico = novo + " | " + antigo # Novo na frente
            db_session.commit()
            return jsonify({"msg": "Atualizado"}), 200
        return jsonify({"error": "Nao achou"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@animals_bp.route("/receptoras", methods=["GET"])
@token_required
def list_recept(current_user):
    try:
        lista = db_session.query(Receptora).filter_by(tenant_id=current_user.tenant_id).all()
        return jsonify([{"id":r.id, "nome":r.nome, "status":r.status, "lote":r.lote} for r in lista]), 200
    except: return jsonify([]), 200

@animals_bp.route("/receptoras", methods=["POST"])
@token_required
def add_recept(current_user):
    data = request.get_json()
    try:
        nova = Receptora(
            tenant_id=current_user.tenant_id, 
            nome=data.get("nome"), 
            status=data.get("status"), 
            lote=data.get("lote")
        )
        db_session.add(nova)
        db_session.commit()
        return jsonify({"msg": "Salvo"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
