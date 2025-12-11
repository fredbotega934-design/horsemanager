"""
Rotas para gerenciamento de usuários com controle de acesso baseado em papéis
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import db, Usuario
from auth.middleware import user_management_required, role_required, tenant_access_required
import json

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_access_required
def list_users(current_user, tenant_id):
    """
    Listar usuários do tenant
    Proprietários veem todos os usuários do seu haras
    Admins veem todos os usuários
    """
    try:
        if current_user.role == 'admin':
            # Admin pode ver usuários de todos os tenants
            if request.args.get('all') == 'true':
                usuarios = Usuario.query.all()
            else:
                usuarios = Usuario.query.filter_by(tenant_id=tenant_id).all()
        else:
            # Proprietários veem apenas usuários do seu tenant
            usuarios = Usuario.query.filter_by(tenant_id=current_user.tenant_id).all()
        
        # Filtrar informações sensíveis para veterinários
        users_data = []
        for usuario in usuarios:
            user_data = usuario.to_dict()
            
            # Veterinários não podem ver dados de outros usuários
            if current_user.role == 'veterinario' and usuario.id != current_user.id:
                continue
            
            # Remover senha_hash de todas as respostas
            user_data.pop('senha_hash', None)
            users_data.append(user_data)
        
        return jsonify(users_data)
        
    except Exception as e:
        return jsonify({'error': 'Erro ao listar usuários', 'details': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@tenant_access_required
def get_user(user_id, current_user, tenant_id):
    """
    Obter detalhes de um usuário específico
    """
    try:
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar permissões de acesso
        if current_user.role == 'veterinario':
            # Veterinários só podem ver seus próprios dados
            if usuario.id != current_user.id:
                return jsonify({'error': 'Acesso negado'}), 403
        elif current_user.role == 'proprietario':
            # Proprietários só podem ver usuários do seu tenant
            if usuario.tenant_id != current_user.tenant_id:
                return jsonify({'error': 'Acesso negado'}), 403
        # Admins podem ver qualquer usuário
        
        user_data = usuario.to_dict()
        user_data.pop('senha_hash', None)
        
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({'error': 'Erro ao obter usuário', 'details': str(e)}), 500

@users_bp.route('/', methods=['POST'])
@jwt_required()
@user_management_required
def create_user(current_user):
    """
    Criar novo usuário (apenas proprietários e admins)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Validar campos obrigatórios
        required_fields = ['nome', 'email', 'senha', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se email já existe
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Validar papel
        valid_roles = ['proprietario', 'veterinario', 'admin']
        if data['role'] not in valid_roles:
            return jsonify({'error': 'Papel inválido'}), 400
        
        # Apenas admins podem criar outros admins
        if data['role'] == 'admin' and current_user.role != 'admin':
            return jsonify({'error': 'Apenas admins podem criar outros admins'}), 403
        
        # Definir tenant_id
        tenant_id = data.get('tenant_id', current_user.tenant_id)
        
        # Proprietários só podem criar usuários em seu próprio tenant
        if current_user.role == 'proprietario' and tenant_id != current_user.tenant_id:
            return jsonify({'error': 'Você só pode criar usuários em seu próprio haras'}), 403
        
        # Criar novo usuário
        novo_usuario = Usuario(
            nome=data['nome'],
            email=data['email'],
            senha=data['senha'],
            role=data['role'],
            tenant_id=tenant_id,
            crmv=data.get('crmv'),
            especialidade=data.get('especialidade'),
            telefone=data.get('telefone')
        )
        
        # Se for veterinário, definir o proprietário
        if data['role'] == 'veterinario':
            novo_usuario.proprietario_id = current_user.id
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        # Retornar dados do usuário criado (sem senha)
        user_data = novo_usuario.to_dict()
        user_data.pop('senha_hash', None)
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar usuário', 'details': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@tenant_access_required
def update_user(user_id, current_user, tenant_id):
    """
    Atualizar dados de usuário
    """
    try:
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar permissões
        if current_user.role == 'veterinario':
            # Veterinários só podem editar seus próprios dados
            if usuario.id != current_user.id:
                return jsonify({'error': 'Acesso negado'}), 403
        elif current_user.role == 'proprietario':
            # Proprietários podem editar usuários do seu tenant
            if usuario.tenant_id != current_user.tenant_id:
                return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Campos que podem ser atualizados
        updatable_fields = ['nome', 'telefone', 'especialidade']
        
        # Proprietários e admins podem atualizar mais campos
        if current_user.role in ['proprietario', 'admin']:
            updatable_fields.extend(['email', 'ativo', 'crmv'])
        
        # Apenas admins podem alterar papel e tenant
        if current_user.role == 'admin':
            updatable_fields.extend(['role', 'tenant_id'])
        
        # Atualizar campos permitidos
        for field in updatable_fields:
            if field in data:
                setattr(usuario, field, data[field])
        
        # Atualizar senha se fornecida
        if 'senha' in data and data['senha']:
            usuario.set_senha(data['senha'])
        
        db.session.commit()
        
        user_data = usuario.to_dict()
        user_data.pop('senha_hash', None)
        
        return jsonify({
            'message': 'Usuário atualizado com sucesso',
            'user': user_data
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar usuário', 'details': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@user_management_required
def delete_user(user_id, current_user):
    """
    Deletar usuário (apenas proprietários e admins)
    """
    try:
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Não permitir auto-exclusão
        if usuario.id == current_user.id:
            return jsonify({'error': 'Você não pode deletar sua própria conta'}), 403
        
        # Proprietários só podem deletar usuários do seu tenant
        if current_user.role == 'proprietario':
            if usuario.tenant_id != current_user.tenant_id:
                return jsonify({'error': 'Acesso negado'}), 403
            
            # Proprietários não podem deletar outros proprietários
            if usuario.role == 'proprietario':
                return jsonify({'error': 'Você não pode deletar outros proprietários'}), 403
        
        # Apenas admins podem deletar outros admins
        if usuario.role == 'admin' and current_user.role != 'admin':
            return jsonify({'error': 'Apenas admins podem deletar outros admins'}), 403
        
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({'message': 'Usuário deletado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar usuário', 'details': str(e)}), 500

@users_bp.route('/veterinarios', methods=['GET'])
@jwt_required()
@role_required('proprietario', 'admin')
def list_veterinarios(current_user):
    """
    Listar veterinários do tenant (apenas proprietários e admins)
    """
    try:
        if current_user.role == 'admin':
            tenant_id = request.args.get('tenant_id', current_user.tenant_id)
        else:
            tenant_id = current_user.tenant_id
        
        veterinarios = Usuario.query.filter_by(
            tenant_id=tenant_id,
            role='veterinario'
        ).all()
        
        vets_data = []
        for vet in veterinarios:
            vet_data = vet.to_dict()
            vet_data.pop('senha_hash', None)
            vets_data.append(vet_data)
        
        return jsonify(vets_data)
        
    except Exception as e:
        return jsonify({'error': 'Erro ao listar veterinários', 'details': str(e)}), 500

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile(current_user=None):
    """
    Obter perfil do usuário logado
    """
    try:
        if not current_user:
            user_id = get_jwt_identity()
            current_user = Usuario.query.get(int(user_id))
        
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        profile_data = current_user.to_dict()
        profile_data.pop('senha_hash', None)
        
        return jsonify(profile_data)
        
    except Exception as e:
        return jsonify({'error': 'Erro ao obter perfil', 'details': str(e)}), 500

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Atualizar perfil do usuário logado
    """
    try:
        user_id = get_jwt_identity()
        usuario = Usuario.query.get(int(user_id))
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Campos que qualquer usuário pode atualizar em seu próprio perfil
        updatable_fields = ['nome', 'telefone', 'especialidade']
        
        for field in updatable_fields:
            if field in data:
                setattr(usuario, field, data[field])
        
        # Atualizar senha se fornecida
        if 'senha' in data and data['senha']:
            usuario.set_senha(data['senha'])
        
        db.session.commit()
        
        profile_data = usuario.to_dict()
        profile_data.pop('senha_hash', None)
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': profile_data
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar perfil', 'details': str(e)}), 500
