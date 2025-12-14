import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text

# Rotas
from routes.receptoras import receptoras_bp
from routes.financeiro import financeiro_bp
from routes.custo_prenhez import custo_bp
from routes.biotech import biotech_bp
from routes.embryo import embryo_bp
from routes.general import general_bp

from models.database import db_session, init_db, engine, Base
from models.user import Usuario

# Modelos (Importar todos para que o SQLAlchemy os conheça)
import models.receptora
import models.financeiro
import models.custo_prenhez
import models.biotech
import models.embryo
import models.properties

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-key')
    CORS(app)
    JWTManager(app)

    # Registro de Blueprints
    app.register_blueprint(receptoras_bp, url_prefix='/api/receptoras')
    app.register_blueprint(financeiro_bp, url_prefix='/api/financeiro')
    app.register_blueprint(custo_bp, url_prefix='/api/custo_prenhez')
    app.register_blueprint(biotech_bp, url_prefix='/api/biotech')
    app.register_blueprint(embryo_bp, url_prefix='/api/embrioes')
    app.register_blueprint(general_bp, url_prefix='/api/geral')
    
    @app.teardown_appcontext
    def shutdown(e=None): db_session.remove()
    
    @app.route('/api/login', methods=['POST'])
    def login():
        d = request.get_json()
        u = db_session.query(Usuario).filter_by(email=d.get('email')).first()
        if u and check_password_hash(u.password_hash, d.get('password')):
            t = create_access_token(identity=str(u.id), additional_claims={"role":u.role,"tenant_id":u.tenant_id})
            return jsonify({"token":t, "user":{"nome":u.nome, "role":u.role}}), 200
        return jsonify({"msg":"Erro de credenciais"}), 401

    @app.route('/api/criar-admin', methods=['GET'])
    def setup():
        try:
            Base.metadata.create_all(bind=engine)
            if not db_session.query(Usuario).filter_by(email="admin@haras.com").first():
                db_session.add(Usuario(nome="Admin", email="admin@haras.com", password_hash=generate_password_hash("admin123"), role="proprietario", tenant_id="padrao"))
                db_session.commit()
            return jsonify({"msg":"Banco Atualizado e Admin Criado"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/resetar-banco-completo', methods=['GET'])
    def reset_db():
        try:
            # 1. FORÇA BRUTA: Limpar tabelas zumbis que travam o reset
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS itens_procedimento CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS itens_custo CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS procedimentos CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS calculos_prenhez CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS procedimento_itens CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS calculo_procedimentos CASCADE"))
                conn.commit()

            # 2. Drop All padrão do SQLAlchemy (para o resto)
            Base.metadata.drop_all(bind=engine)
            
            # 3. Recriar tudo do zero
            Base.metadata.create_all(bind=engine)
            
            # 4. Criar Admin
            admin = Usuario(nome="Admin", email="admin@haras.com", password_hash=generate_password_hash("admin123"), role="proprietario", tenant_id="padrao")
            db_session.add(admin)
            db_session.commit()
            return jsonify({"message": "BANCO RESETADO COM SUCESSO."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/')
    def index():
        return app.send_static_file('dashboard-integrado.html')

    @app.route('/<path:path>')
    def static_files(path):
        return app.send_static_file(path)
    
    @app.route('/health')
    def health(): return jsonify({'status': 'online'})
    
    return app

app = create_app()
if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
