#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de teste
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app
from src.models.user import db, Usuario, Egua, Garanhao, Embriao, TransferenciaEmbriao, Gestacao, Parto
from datetime import datetime, timedelta
import random

def criar_dados_teste():
    """Cria dados de teste no banco de dados"""
    
    with app.app_context():
        # Criar tabelas (já criadas no app.py)
        print("Conectando ao banco de dados...")
        
        # Limpar dados existentes
        db.session.query(Parto).delete()
        db.session.query(Gestacao).delete()
        db.session.query(TransferenciaEmbriao).delete()
        db.session.query(Embriao).delete()
        db.session.query(Garanhao).delete()
        db.session.query(Egua).delete()
        db.session.query(Usuario).delete()
        db.session.commit()
        
        print("Criando usuários de teste...")
        
        # Criar proprietário
        proprietario = Usuario(
            nome="João Silva",
            email="joao@haras.com",
            senha="123456",
            role="proprietario",
            tenant_id="haras001"
        )
        db.session.add(proprietario)
        
        # Criar veterinário
        veterinario = Usuario(
            nome="Dr. Maria Santos",
            email="maria@vet.com",
            senha="123456",
            role="veterinario",
            tenant_id="haras001",
            crmv="SP-12345",
            especialidade="Reprodução Equina",
            telefone="(11) 99999-9999",
            proprietario_id=1
        )
        db.session.add(veterinario)
        
        db.session.commit()
        
        print("Criando éguas de teste...")
        
        # Criar éguas doadoras
        doadoras = [
            {"nome": "Estrela Dourada", "idade": 8, "raca": "Mangalarga", "taxa_prenhez": 85.0},
            {"nome": "Bela Vista", "idade": 6, "raca": "Quarto de Milha", "taxa_prenhez": 72.0},
            {"nome": "Rainha do Campo", "idade": 10, "raca": "Crioulo", "taxa_prenhez": 90.0},
            {"nome": "Princesa Real", "idade": 7, "raca": "Mangalarga", "taxa_prenhez": 78.0},
        ]
        
        for i, doadora_data in enumerate(doadoras):
            egua = Egua(
                nome=doadora_data["nome"],
                tenant_id="haras001",
                idade=doadora_data["idade"],
                raca=doadora_data["raca"],
                registro=f"DOA{i+1:03d}",
                tipo="doadora",
                status="ativa",
                taxa_prenhez=doadora_data["taxa_prenhez"]
            )
            db.session.add(egua)
        
        # Criar éguas receptoras
        receptoras = [
            {"nome": "Luna Prateada", "idade": 5, "raca": "SRD"},
            {"nome": "Esperança", "idade": 4, "raca": "SRD"},
            {"nome": "Vitória", "idade": 6, "raca": "SRD"},
            {"nome": "Serena", "idade": 5, "raca": "SRD"},
            {"nome": "Alegria", "idade": 7, "raca": "SRD"},
            {"nome": "Bonita", "idade": 4, "raca": "SRD"},
        ]
        
        for i, receptora_data in enumerate(receptoras):
            egua = Egua(
                nome=receptora_data["nome"],
                tenant_id="haras001",
                idade=receptora_data["idade"],
                raca=receptora_data["raca"],
                registro=f"REC{i+1:03d}",
                tipo="receptora",
                status="disponivel",
                taxa_prenhez=0.0
            )
            db.session.add(egua)
        
        db.session.commit()
        
        print("Criando garanhões de teste...")
        
        # Criar garanhões
        garanhoes = [
            {"nome": "Trovão Negro", "idade": 12, "raca": "Mangalarga", "taxa_prenhez": 88.0},
            {"nome": "Relâmpago", "idade": 9, "raca": "Quarto de Milha", "taxa_prenhez": 82.0},
            {"nome": "Imperador", "idade": 15, "raca": "Crioulo", "taxa_prenhez": 85.0},
        ]
        
        for i, garanhao_data in enumerate(garanhoes):
            garanhao = Garanhao(
                nome=garanhao_data["nome"],
                tenant_id="haras001",
                idade=garanhao_data["idade"],
                raca=garanhao_data["raca"],
                registro=f"GAR{i+1:03d}",
                taxa_prenhez=garanhao_data["taxa_prenhez"]
            )
            db.session.add(garanhao)
        
        db.session.commit()
        
        print("Criando embriões de teste...")
        
        # Criar embriões
        graus = ["A", "B", "C"]
        for i in range(15):
            embriao = Embriao(
                tenant_id="haras001",
                doadora_id=random.randint(1, 4),  # IDs das doadoras
                garanhao_id=random.randint(1, 3),  # IDs dos garanhões
                grau=random.choice(graus),
                status="disponivel",
                data_coleta=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(embriao)
        
        db.session.commit()
        
        print("Criando transferências de teste...")
        
        # Criar transferências
        for i in range(10):
            transferencia = TransferenciaEmbriao(
                tenant_id="haras001",
                doadora_id=random.randint(1, 4),
                receptora_id=random.randint(5, 10),  # IDs das receptoras
                embriao_id=random.randint(1, 15),
                data_transferencia=datetime.now() - timedelta(days=random.randint(1, 60)),
                status="realizada"
            )
            db.session.add(transferencia)
        
        db.session.commit()
        
        print("Criando gestações de teste...")
        
        # Criar gestações
        for i in range(7):
            data_confirmacao = datetime.now() - timedelta(days=random.randint(30, 120))
            gestacao = Gestacao(
                tenant_id="haras001",
                receptora_id=random.randint(5, 10),
                embriao_id=random.randint(1, 15),
                data_confirmacao=data_confirmacao,
                data_prevista_parto=(data_confirmacao + timedelta(days=330)).date(),
                status="confirmada"
            )
            db.session.add(gestacao)
        
        db.session.commit()
        
        print("Criando partos de teste...")
        
        # Criar partos
        sexos = ["macho", "fêmea"]
        for i in range(3):
            parto = Parto(
                tenant_id="haras001",
                gestacao_id=i+1,
                data_parto=datetime.now() - timedelta(days=random.randint(1, 30)),
                sexo_potro=random.choice(sexos),
                peso_potro=random.uniform(35.0, 55.0)
            )
            db.session.add(parto)
        
        db.session.commit()
        
        print("Dados de teste criados com sucesso!")
        print("\nCredenciais de acesso:")
        print("Proprietário: joao@haras.com / 123456")
        print("Veterinário: maria@vet.com / 123456")

if __name__ == "__main__":
    criar_dados_teste()
