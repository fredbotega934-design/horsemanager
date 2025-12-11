from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.models import Cliente

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.route("/", methods=["GET"])
def get_clientes():
    clientes = Cliente.query.all()
    response = jsonify([
        {
            "id": cliente.id,
            "nome_cliente": cliente.nome_cliente,
            "telefone": cliente.telefone,
            "email": cliente.email,
            "whatsapp": cliente.whatsapp,
            "localizacao": cliente.localizacao,
            "endereco_completo": cliente.endereco_completo,
            "cep": cliente.cep,
            "cnpj_cpf": cliente.cnpj_cpf,
            "responsavel_tecnico": cliente.responsavel_tecnico,
            "crmv_responsavel": cliente.crmv_responsavel,
            "tipo_cliente": cliente.tipo_cliente,
            "observacoes": cliente.observacoes,
            "data_cadastro": cliente.data_cadastro,
            "status": cliente.status,
            "contrato_vigente": cliente.contrato_vigente,
            "data_inicio_contrato": cliente.data_inicio_contrato,
            "data_fim_contrato": cliente.data_fim_contrato,
        }
        for cliente in clientes
    ])
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:8080")
    return response

@clientes_bp.route("/<int:cliente_id>", methods=["GET"])
def get_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return jsonify({
        "id": cliente.id,
        "nome_cliente": cliente.nome_cliente,
        "telefone": cliente.telefone,
        "email": cliente.email,
        "whatsapp": cliente.whatsapp,
        "localizacao": cliente.localizacao,
        "endereco_completo": cliente.endereco_completo,
        "cep": cliente.cep,
        "cnpj_cpf": cliente.cnpj_cpf,
        "responsavel_tecnico": cliente.responsavel_tecnico,
        "crmv_responsavel": cliente.crmv_responsavel,
        "tipo_cliente": cliente.tipo_cliente,
        "observacoes": cliente.observacoes,
        "data_cadastro": cliente.data_cadastro,
        "status": cliente.status,
        "contrato_vigente": cliente.contrato_vigente,
        "data_inicio_contrato": cliente.data_inicio_contrato,
        "data_fim_contrato": cliente.data_fim_contrato,
    })

@clientes_bp.route("/", methods=["POST"])
def add_cliente():
    data = request.get_json()
    new_cliente = Cliente(
        nome_cliente=data["nome_cliente"],
        telefone=data.get("telefone"),
        email=data.get("email"),
        whatsapp=data.get("whatsapp"),
        localizacao=data.get("localizacao"),
        endereco_completo=data.get("endereco_completo"),
        cep=data.get("cep"),
        cnpj_cpf=data.get("cnpj_cpf"),
        responsavel_tecnico=data.get("responsavel_tecnico"),
        crmv_responsavel=data.get("crmv_responsavel"),
        tipo_cliente=data.get("tipo_cliente"),
        observacoes=data.get("observacoes"),
        data_cadastro=data.get("data_cadastro"),
        status=data.get("status"),
        contrato_vigente=data.get("contrato_vigente"),
        data_inicio_contrato=data.get("data_inicio_contrato"),
        data_fim_contrato=data.get("data_fim_contrato"),
    )
    db.session.add(new_cliente)
    db.session.commit()
    return jsonify({"message": "Cliente adicionado com sucesso!", "id": new_cliente.id}), 201

@clientes_bp.route("/<int:cliente_id>", methods=["PUT"])
def update_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    data = request.get_json()
    cliente.nome_cliente = data.get("nome_cliente", cliente.nome_cliente)
    cliente.telefone = data.get("telefone", cliente.telefone)
    cliente.email = data.get("email", cliente.email)
    cliente.whatsapp = data.get("whatsapp", cliente.whatsapp)
    cliente.localizacao = data.get("localizacao", cliente.localizacao)
    cliente.endereco_completo = data.get("endereco_completo", cliente.endereco_completo)
    cliente.cep = data.get("cep", cliente.cep)
    cliente.cnpj_cpf = data.get("cnpj_cpf", cliente.cnpj_cpf)
    cliente.responsavel_tecnico = data.get("responsavel_tecnico", cliente.responsavel_tecnico)
    cliente.crmv_responsavel = data.get("crmv_responsavel", cliente.crmv_responsavel)
    cliente.tipo_cliente = data.get("tipo_cliente", cliente.tipo_cliente)
    cliente.observacoes = data.get("observacoes", cliente.observacoes)
    cliente.data_cadastro = data.get("data_cadastro", cliente.data_cadastro)
    cliente.status = data.get("status", cliente.status)
    cliente.contrato_vigente = data.get("contrato_vigente", cliente.contrato_vigente)
    cliente.data_inicio_contrato = data.get("data_inicio_contrato", cliente.data_inicio_contrato)
    cliente.data_fim_contrato = data.get("data_fim_contrato", cliente.data_fim_contrato)
    db.session.commit()
    return jsonify({"message": "Cliente atualizado com sucesso!"})

@clientes_bp.route("/<int:cliente_id>", methods=["DELETE"])
def delete_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    return jsonify({"message": "Cliente deletado com sucesso!"})
