from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

from models.user import db, Usuario
from tenant.tenant_manager import (
    Tenant, TenantManager, TenantConfig, TenantStatus, PlanoTenant,
    tenant_required, tenant_access_required
)
from auth.middleware import role_required

tenants_bp = Blueprint('tenants', __name__)

@tenants_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('admin')
def criar_tenant():
    """Cria um novo tenant (apenas admins globais)"""
    data = request.get_json()
    
    nome = data.get('nome')
    slug = data.get('slug')
    plano = data.get('plano', 'basico')
    
    if not nome or not slug:
        return jsonify({'erro': 'Nome e slug são obrigatórios'}), 400
    
    try:
        # Validar plano
        plano_enum = PlanoTenant(plano)
        
        # Criar tenant
        tenant = TenantManager.criar_tenant(nome, slug, plano_enum)
        
        return jsonify({
            'mensagem': 'Tenant criado com sucesso',
            'tenant': tenant.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('admin')
def listar_tenants():
    """Lista todos os tenants (apenas admins globais)"""
    try:
        tenants = TenantManager.listar_tenants_ativos()
        
        return jsonify({
            'tenants': [tenant.to_dict() for tenant in tenants],
            'total': len(tenants)
        })
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/<tenant_id>', methods=['GET'])
@jwt_required()
@tenant_access_required
def obter_tenant(current_user, tenant_id):
    """Obtém informações de um tenant específico"""
    try:
        tenant = TenantManager.obter_tenant_por_id(tenant_id)
        
        if not tenant:
            return jsonify({'erro': 'Tenant não encontrado'}), 404
        
        return jsonify({
            'tenant': tenant.to_dict()
        })
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/<tenant_id>/configuracoes', methods=['GET'])
@jwt_required()
@tenant_access_required
def obter_configuracoes_tenant(current_user, tenant_id):
    """Obtém configurações do tenant"""
    try:
        tenant = TenantManager.obter_tenant_por_id(tenant_id)
        
        if not tenant:
            return jsonify({'erro': 'Tenant não encontrado'}), 404
        
        # Apenas proprietários podem ver todas as configurações
        if current_user.papel != 'proprietario':
            # Veterinários veem apenas configurações básicas
            config = tenant.get_configuracoes()
            config_limitada = {
                'nome_haras': config.nome_haras,
                'configuracoes_sistema': {
                    'timezone': config.configuracoes_sistema.get('timezone'),
                    'formato_data': config.configuracoes_sistema.get('formato_data'),
                    'idioma': config.configuracoes_sistema.get('idioma')
                },
                'personalizacao': config.personalizacao
            }
            return jsonify({'configuracoes': config_limitada})
        
        return jsonify({
            'configuracoes': tenant.get_configuracoes().__dict__
        })
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/<tenant_id>/configuracoes', methods=['PUT'])
@jwt_required()
@tenant_access_required
@role_required('proprietario')
def atualizar_configuracoes_tenant(current_user, tenant_id):
    """Atualiza configurações do tenant (apenas proprietários)"""
    try:
        tenant = TenantManager.obter_tenant_por_id(tenant_id)
        
        if not tenant:
            return jsonify({'erro': 'Tenant não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar configurações
        tenant.atualizar_configuracoes(data)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Configurações atualizadas com sucesso',
            'configuracoes': tenant.get_configuracoes().__dict__
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/<tenant_id>/status', methods=['PUT'])
@jwt_required()
@role_required('admin')
def alterar_status_tenant(tenant_id):
    """Altera status do tenant (apenas admins globais)"""
    try:
        tenant = TenantManager.obter_tenant_por_id(tenant_id)
        
        if not tenant:
            return jsonify({'erro': 'Tenant não encontrado'}), 404
        
        data = request.get_json()
        novo_status = data.get('status')
        motivo = data.get('motivo', '')
        
        if novo_status == 'ativo':
            tenant.ativar()
        elif novo_status == 'suspenso':
            tenant.suspender(motivo)
        elif novo_status == 'cancelado':
            tenant.cancelar()
        else:
            return jsonify({'erro': 'Status inválido'}), 400
        
        db.session.commit()
        
        return jsonify({
            'mensagem': f'Status alterado para {novo_status}',
            'tenant': tenant.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/<tenant_id>/plano', methods=['PUT'])
@jwt_required()
@role_required('admin')
def alterar_plano_tenant(tenant_id):
    """Altera plano do tenant (apenas admins globais)"""
    try:
        tenant = TenantManager.obter_tenant_por_id(tenant_id)
        
        if not tenant:
            return jsonify({'erro': 'Tenant não encontrado'}), 404
        
        data = request.get_json()
        novo_plano = data.get('plano')
        
        try:
            plano_enum = PlanoTenant(novo_plano)
            tenant.upgrade_plano(plano_enum)
            db.session.commit()
            
            return jsonify({
                'mensagem': f'Plano alterado para {novo_plano}',
                'tenant': tenant.to_dict()
            })
            
        except ValueError:
            return jsonify({'erro': 'Plano inválido'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/<tenant_id>/uso', methods=['GET'])
@jwt_required()
@tenant_access_required
def obter_uso_tenant(current_user, tenant_id):
    """Obtém informações de uso do tenant"""
    try:
        tenant = TenantManager.obter_tenant_por_id(tenant_id)
        
        if not tenant:
            return jsonify({'erro': 'Tenant não encontrado'}), 404
        
        # Atualizar uso atual
        tenant.atualizar_uso()
        db.session.commit()
        
        uso = {
            'limites': {
                'usuarios': tenant.limite_usuarios,
                'animais': tenant.limite_animais,
                'storage_mb': tenant.limite_storage_mb
            },
            'uso_atual': {
                'usuarios': tenant.usuarios_ativos,
                'animais': tenant.animais_cadastrados,
                'storage_mb': tenant.storage_usado_mb
            },
            'percentual_uso': {
                'usuarios': round((tenant.usuarios_ativos / tenant.limite_usuarios) * 100, 1),
                'animais': round((tenant.animais_cadastrados / tenant.limite_animais) * 100, 1),
                'storage': round((tenant.storage_usado_mb / tenant.limite_storage_mb) * 100, 1)
            },
            'alertas': []
        }
        
        # Gerar alertas de uso
        if uso['percentual_uso']['usuarios'] > 80:
            uso['alertas'].append({
                'tipo': 'usuarios',
                'nivel': 'warning' if uso['percentual_uso']['usuarios'] < 95 else 'danger',
                'mensagem': f"Uso de usuários em {uso['percentual_uso']['usuarios']}%"
            })
        
        if uso['percentual_uso']['animais'] > 80:
            uso['alertas'].append({
                'tipo': 'animais',
                'nivel': 'warning' if uso['percentual_uso']['animais'] < 95 else 'danger',
                'mensagem': f"Uso de animais em {uso['percentual_uso']['animais']}%"
            })
        
        if uso['percentual_uso']['storage'] > 80:
            uso['alertas'].append({
                'tipo': 'storage',
                'nivel': 'warning' if uso['percentual_uso']['storage'] < 95 else 'danger',
                'mensagem': f"Uso de storage em {uso['percentual_uso']['storage']}%"
            })
        
        return jsonify(uso)
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/<tenant_id>/usuarios', methods=['GET'])
@jwt_required()
@tenant_access_required
@role_required('proprietario')
def listar_usuarios_tenant(current_user, tenant_id):
    """Lista usuários do tenant (apenas proprietários)"""
    try:
        usuarios = Usuario.query.filter_by(tenant_id=tenant_id).all()
        
        usuarios_data = []
        for usuario in usuarios:
            usuarios_data.append({
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email,
                'papel': usuario.papel,
                'ativo': usuario.ativo,
                'data_criacao': usuario.data_criacao.isoformat() if usuario.data_criacao else None,
                'ultimo_login': usuario.ultimo_login.isoformat() if usuario.ultimo_login else None
            })
        
        return jsonify({
            'usuarios': usuarios_data,
            'total': len(usuarios_data)
        })
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/<tenant_id>/dashboard', methods=['GET'])
@jwt_required()
@tenant_access_required
def dashboard_tenant(current_user, tenant_id):
    """Dashboard específico do tenant"""
    try:
        tenant = TenantManager.obter_tenant_por_id(tenant_id)
        
        if not tenant:
            return jsonify({'erro': 'Tenant não encontrado'}), 404
        
        # Atualizar uso
        tenant.atualizar_uso()
        
        # Calcular dias restantes (se trial)
        dias_restantes = None
        if tenant.status == TenantStatus.TRIAL and tenant.data_expiracao:
            dias_restantes = (tenant.data_expiracao - datetime.utcnow()).days
        
        # Estatísticas básicas
        from models.models import Egua, Garanhao, TransferenciaEmbriao
        
        total_eguas = Egua.query.filter_by(tenant_id=tenant_id).count()
        total_garanhoes = Garanhao.query.filter_by(tenant_id=tenant_id).count()
        total_transferencias = TransferenciaEmbriao.query.filter_by(tenant_id=tenant_id).count()
        
        # Transferências do mês atual
        inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        transferencias_mes = TransferenciaEmbriao.query.filter(
            TransferenciaEmbriao.tenant_id == tenant_id,
            TransferenciaEmbriao.data_transferencia >= inicio_mes
        ).count()
        
        dashboard_data = {
            'tenant_info': {
                'nome': tenant.nome,
                'plano': tenant.plano.value,
                'status': tenant.status.value,
                'dias_restantes_trial': dias_restantes
            },
            'estatisticas': {
                'total_eguas': total_eguas,
                'total_garanhoes': total_garanhoes,
                'total_transferencias': total_transferencias,
                'transferencias_mes': transferencias_mes
            },
            'uso_recursos': {
                'usuarios': f"{tenant.usuarios_ativos}/{tenant.limite_usuarios}",
                'animais': f"{tenant.animais_cadastrados}/{tenant.limite_animais}",
                'storage': f"{tenant.storage_usado_mb}/{tenant.limite_storage_mb} MB"
            },
            'alertas_sistema': []
        }
        
        # Alertas específicos
        if dias_restantes is not None and dias_restantes <= 7:
            dashboard_data['alertas_sistema'].append({
                'tipo': 'trial_expirando',
                'nivel': 'warning',
                'mensagem': f"Trial expira em {dias_restantes} dias"
            })
        
        if tenant.usuarios_ativos >= tenant.limite_usuarios:
            dashboard_data['alertas_sistema'].append({
                'tipo': 'limite_usuarios',
                'nivel': 'danger',
                'mensagem': "Limite de usuários atingido"
            })
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/verificar-expirados', methods=['GET'])
@jwt_required()
@role_required('admin')
def verificar_tenants_expirados():
    """Verifica tenants com trial expirado (apenas admins)"""
    try:
        tenants_expirados = TenantManager.verificar_tenants_expirados()
        
        expirados_data = []
        for tenant in tenants_expirados:
            dias_expirado = (datetime.utcnow() - tenant.data_expiracao).days
            expirados_data.append({
                'id': tenant.id,
                'nome': tenant.nome,
                'slug': tenant.slug,
                'data_expiracao': tenant.data_expiracao.isoformat(),
                'dias_expirado': dias_expirado
            })
        
        return jsonify({
            'tenants_expirados': expirados_data,
            'total': len(expirados_data)
        })
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@tenants_bp.route('/atualizar-uso', methods=['POST'])
@jwt_required()
@role_required('admin')
def atualizar_uso_todos():
    """Atualiza uso de todos os tenants (apenas admins)"""
    try:
        TenantManager.atualizar_uso_todos_tenants()
        
        return jsonify({
            'mensagem': 'Uso de todos os tenants atualizado com sucesso'
        })
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500
