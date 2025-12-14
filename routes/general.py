from flask import Blueprint, jsonify
from models.properties import Propriedade
from models.database import db_session
from auth.middleware import token_required

general_bp = Blueprint("general", __name__)

@general_bp.route("/propriedades", methods=["GET"])
@token_required
def list_props(current_user):
    try:
        props = db_session.query(Propriedade).filter_by(tenant_id=current_user.tenant_id).all()
        return jsonify([{"id": p.id, "nome": p.nome} for p in props]), 200
    except: return jsonify([]), 200
