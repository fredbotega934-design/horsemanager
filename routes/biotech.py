from flask import Blueprint, request, jsonify
from models.biotech import SessaoOPU
from models.receptora import Receptora
from models.database import db_session
from auth.middleware import token_required, role_required
from datetime import datetime

biotech_bp = Blueprint("biotech", __name__)

@biotech_bp.route("/opu", methods=["POST"])
@token_required
def registrar_opu(current_user):
    data = request.get_json()
    
    try:
        # Calculo Automatico de Eficiencia
        aspirados = int(data.get('aspirados', 0))
        recuperados = int(data.get('recuperados', 0))
        taxa = (recuperados / aspirados * 100) if aspirados > 0 else 0.0
        
        nova_sessao = SessaoOPU(
            tenant_id=current_user.tenant_id,
            receptora_id=data.get('animal_id'),
            veterinario_responsavel=data.get('vet'),
            data_procedimento=datetime.now(),
            
            # Funil
            foliculos_visualizados=int(data.get('visualizados', 0)),
            foliculos_aspirados=aspirados,
            oocitos_recuperados=recuperados,
            taxa_recuperacao=taxa,
            
            # Tecnica
            pressao_vacuo=data.get('vacuo'),
            
            # Seguranca
            antibiotico_profilatico=data.get('antibiotico', False),
            tipo_antibiotico=data.get('nome_antibiotico'),
            complicacoes_intra=data.get('complicacoes'),
            
            laboratorio_destino=data.get('lab')
        )
        
        db_session.add(nova_sessao)
        db_session.commit()
        
        return jsonify({
            "message": "Sessão de OPU Registrada",
            "kpi_recuperacao": f"{taxa:.1f}%",
            "alerta": "Baixa Recuperação (<50%)" if taxa < 50 else "Eficiência Adequada"
        }), 201
        
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

@biotech_bp.route("/opu/animal/<int:id>", methods=["GET"])
@token_required
def listar_opus(current_user, id):
    sessoes = db_session.query(SessaoOPU).filter_by(receptora_id=id).order_by(SessaoOPU.data_procedimento.desc()).all()
    lista = []
    for s in sessoes:
        lista.append({
            "data": s.data_procedimento.strftime("%d/%m/%Y"),
            "vet": s.veterinario_responsavel,
            "resumo": f"{s.oocitos_recuperados} Oócitos / {s.foliculos_aspirados} Folículos",
            "taxa": f"{s.taxa_recuperacao:.1f}%",
            "seguranca": "⚠️ Complicação" if s.complicacoes_intra else "OK"
        })
    return jsonify(lista), 200
