from flask import Blueprint, request, jsonify
from models.receptora import Receptora, ExameGinecologico
from models.database import db_session
from auth.middleware import token_required, role_required
from datetime import datetime, date

receptoras_bp = Blueprint("receptoras", __name__)

@receptoras_bp.route("", methods=["GET"])
@token_required
def get_animais(current_user):
    prop = request.args.get('propriedade')
    cat = request.args.get('categoria')
    
    query = db_session.query(Receptora).filter_by(tenant_id=current_user.tenant_id)
    if prop: query = query.filter_by(propriedade=prop)
    if cat: query = query.filter_by(categoria=cat)
    
    animais = query.all()
    lista = []
    hoje = date.today()
    
    for a in animais:
        # CALCULO DO CICLO (D-Day)
        d_day = "-"
        if a.data_ovulacao and a.status_saude != "Prenhe":
            dias = (hoje - a.data_ovulacao).days
            d_day = f"D{dias}" # Ex: D7
        
        # Resumo do ultimo toque
        ultimo = a.exames[0] if a.exames else None
        resumo = f"OE:{ultimo.ovario_esq} OD:{ultimo.ovario_dir}" if ultimo else "-"
        
        lista.append({
            "id": a.id,
            "nome": a.nome,
            "registro": a.identificacao,
            "status": a.status_saude,
            "ciclo": d_day, # Aqui esta a informacao de ouro
            "resumo": resumo
        })
    return jsonify(lista), 200

@receptoras_bp.route("/exames/lote", methods=["POST"])
@token_required
def save_batch_exams(current_user):
    lista_exames = request.get_json()
    count = 0
    try:
        for item in lista_exames:
            if item.get('oe') or item.get('od') or item.get('diag'):
                novo = ExameGinecologico(
                    receptora_id=item['id'],
                    data_exame=datetime.now().date(),
                    ovario_esq=item.get('oe'),
                    ovario_dir=item.get('od'),
                    utero_edema=item.get('edema'),
                    utero_tonus=item.get('tonus'),
                    diagnostico=item.get('diag')
                )
                db_session.add(novo)
                
                # --- AUTOMACAO DE CICLO ---
                egua = db_session.query(Receptora).get(item['id'])
                
                # Se o vet escreveu "Ovulou" ou "CL Recent", atualiza a data base
                diag_lower = (item.get('diag') or "").lower()
                obs_lower = ((item.get('oe') or "") + (item.get('od') or "")).lower()
                
                if "ovulou" in diag_lower or "ovulou" in obs_lower:
                    egua.data_ovulacao = datetime.now().date()
                    egua.status_saude = "Ovulada/Apta"
                
                # Se confirmou prenhez
                if "prenhe" in diag_lower:
                    egua.status_saude = "Prenhe"
                
                count += 1
        db_session.commit()
        return jsonify({"message": "Atualizado"}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

# Rota de cadastro simples (mantida)
@receptoras_bp.route("", methods=["POST"])
@token_required
def add_animal(current_user):
    data = request.get_json()
    try:
        novo = Receptora(
            tenant_id=current_user.tenant_id,
            nome=data.get("nome"),
            identificacao=data.get("identificacao"),
            propriedade=data.get("propriedade"),
            categoria=data.get("categoria"),
            status_saude="Vazia"
        )
        db_session.add(novo)
        db_session.commit()
        return jsonify({"message": "OK"}), 201
    except: return jsonify({"error": "Erro"}), 500
