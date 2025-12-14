from flask import Blueprint, request, jsonify
from models.properties import Propriedade
from models.database import db_session
from auth.middleware import token_required, role_required

general_bp = Blueprint("general", __name__)

# --- PROPRIEDADES ---
@general_bp.route("/propriedades", methods=["GET"])
@token_required
def list_props(current_user):
    try:
        props = db_session.query(Propriedade).filter_by(tenant_id=current_user.tenant_id).all()
        return jsonify([{"id": p.id, "nome": p.nome} for p in props]), 200
    except Exception as e:
        return jsonify([]), 200

@general_bp.route("/propriedades", methods=["POST"])
@token_required
def add_prop(current_user):
    data = request.get_json()
    try:
        nova = Propriedade(tenant_id=current_user.tenant_id, nome=data.get("nome"))
        db_session.add(nova)
        db_session.commit()
        return jsonify({"message": "Propriedade Criada"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

@general_bp.route("/propriedades/<int:id>", methods=["DELETE"])
@token_required
def delete_prop(current_user, id):
    try:
        prop = db_session.query(Propriedade).get(id)
        if prop:
            db_session.delete(prop)
            db_session.commit()
            return jsonify({"message": "Propriedade Removida"}), 200
        return jsonify({"error": "Nao encontrada"}), 404
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
