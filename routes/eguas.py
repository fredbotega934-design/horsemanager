from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Egua, Usuario

eguas_bp = Blueprint("eguas", __name__)

@eguas_bp.route("/", methods=["GET"])
@jwt_required()
def get_eguas():
    """Listar todas as éguas do tenant do usuário"""
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(user_id)
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    eguas = Egua.query.filter_by(tenant_id=usuario.tenant_id).all()
    return jsonify([egua.to_dict() for egua in eguas])

@eguas_bp.route("/<int:egua_id>", methods=["GET"])
@jwt_required()
def get_egua(egua_id):
    """Obter uma égua específica"""
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(user_id)
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    egua = Egua.query.filter_by(id=egua_id, tenant_id=usuario.tenant_id).first()
    
    if not egua:
        return jsonify({'error': 'Égua não encontrada'}), 404
    
    return jsonify(egua.to_dict())

@eguas_bp.route("/", methods=["POST"])
@jwt_required()
def add_egua():
    """Adicionar nova égua"""
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(user_id)
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('nome'):
        return jsonify({'error': 'Nome da égua é obrigatório'}), 400
    
    new_egua = Egua(
        nome=data['nome'],
        tenant_id=usuario.tenant_id,
        idade=data.get('idade'),
        raca=data.get('raca'),
        registro=data.get('registro'),
        tipo=data.get('tipo', 'receptora'),
        status=data.get('status', 'ativa'),
        taxa_prenhez=data.get('taxa_prenhez', 0.0)
    )
    
    db.session.add(new_egua)
    db.session.commit()
    
    return jsonify({
        'message': 'Égua adicionada com sucesso!',
        'egua': new_egua.to_dict()
    }), 201

@eguas_bp.route("/<int:egua_id>", methods=["PUT"])
@jwt_required()
def update_egua(egua_id):
    """Atualizar égua existente"""
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(user_id)
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    egua = Egua.query.filter_by(id=egua_id, tenant_id=usuario.tenant_id).first()
    
    if not egua:
        return jsonify({'error': 'Égua não encontrada'}), 404
    
    data = request.get_json()
    
    # Atualizar campos
    if 'nome' in data:
        egua.nome = data['nome']
    if 'idade' in data:
        egua.idade = data['idade']
    if 'raca' in data:
        egua.raca = data['raca']
    if 'registro' in data:
        egua.registro = data['registro']
    if 'tipo' in data:
        egua.tipo = data['tipo']
    if 'status' in data:
        egua.status = data['status']
    if 'taxa_prenhez' in data:
        egua.taxa_prenhez = data['taxa_prenhez']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Égua atualizada com sucesso!',
        'egua': egua.to_dict()
    })

@eguas_bp.route("/<int:egua_id>", methods=["DELETE"])
@jwt_required()
def delete_egua(egua_id):
    """Deletar égua"""
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(user_id)
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    egua = Egua.query.filter_by(id=egua_id, tenant_id=usuario.tenant_id).first()
    
    if not egua:
        return jsonify({'error': 'Égua não encontrada'}), 404
    
    db.session.delete(egua)
    db.session.commit()
    
    return jsonify({'message': 'Égua deletada com sucesso!'})

@eguas_bp.route("/doadoras", methods=["GET"])
@jwt_required()
def get_doadoras():
    """Listar éguas doadoras"""
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(user_id)
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    doadoras = Egua.query.filter_by(
        tenant_id=usuario.tenant_id,
        tipo='doadora'
    ).all()
    
    return jsonify([egua.to_dict() for egua in doadoras])

@eguas_bp.route("/receptoras", methods=["GET"])
@jwt_required()
def get_receptoras():
    """Listar éguas receptoras"""
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(user_id)
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    receptoras = Egua.query.filter_by(
        tenant_id=usuario.tenant_id,
        tipo='receptora'
    ).all()
    
    return jsonify([egua.to_dict() for egua in receptoras])
