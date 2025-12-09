#!/usr/bin/env python3
"""
Script para criar dados de teste multi-tenant
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from tenant.tenant_manager import Tenant, TenantManager, PlanoTenant, TenantStatus
from models.user import Usuario
from models.models import Egua, Garanhao, TransferenciaEmbriao
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json

def criar_dados_tenant():
    """Cria dados de teste para demonstrar multi-tenancy"""
    
    with app.app_context():
        print("🏗️  Criando dados multi-tenant...")
        
        # Criar tabelas se não existirem
        db.create_all()
        
        # Limpar dados existentes de tenants
        print("🧹 Limpando dados existentes...")
        Tenant.query.delete()
        
        # Criar Tenant 1: Haras São João (Profissional)
        print("🏇 Criando Haras São João...")
        tenant1 = TenantManager.criar_tenant(
            nome="Haras São João",
            slug="haras-sao-joao",
            plano=PlanoTenant.PROFISSIONAL
        )
        tenant1.ativar()
        
        # Configurações personalizadas para Haras São João
        config1 = {
            'endereco': {
                'rua': 'Estrada Rural, 1500',
                'cidade': 'Ribeirão Preto',
                'estado': 'SP',
                'cep': '14000-000',
                'pais': 'Brasil'
            },
            'contato': {
                'telefone': '(16) 3333-4444',
                'email': 'contato@harassaojoao.com.br',
                'website': 'www.harassaojoao.com.br'
            },
            'personalizacao': {
                'logo_url': '/assets/logo-sao-joao.png',
                'cor_primaria': '#2E7D32',
                'cor_secundaria': '#4CAF50',
                'tema': 'claro'
            }
        }
        tenant1.atualizar_configuracoes(config1)
        
        # Criar Tenant 2: Fazenda Esperança (Básico)
        print("🐎 Criando Fazenda Esperança...")
        tenant2 = TenantManager.criar_tenant(
            nome="Fazenda Esperança",
            slug="fazenda-esperanca",
            plano=PlanoTenant.BASICO
        )
        # Manter em trial
        
        # Configurações para Fazenda Esperança
        config2 = {
            'endereco': {
                'rua': 'Rodovia BR-050, Km 25',
                'cidade': 'Uberaba',
                'estado': 'MG',
                'cep': '38000-000',
                'pais': 'Brasil'
            },
            'contato': {
                'telefone': '(34) 2222-3333',
                'email': 'info@fazendaesperanca.com.br',
                'website': 'www.fazendaesperanca.com.br'
            },
            'personalizacao': {
                'logo_url': '/assets/logo-esperanca.png',
                'cor_primaria': '#1976D2',
                'cor_secundaria': '#2196F3',
                'tema': 'claro'
            }
        }
        tenant2.atualizar_configuracoes(config2)
        
        # Criar Tenant 3: Haras Elite (Enterprise)
        print("👑 Criando Haras Elite...")
        tenant3 = TenantManager.criar_tenant(
            nome="Haras Elite",
            slug="haras-elite",
            plano=PlanoTenant.ENTERPRISE
        )
        tenant3.ativar()
        
        # Configurações para Haras Elite
        config3 = {
            'endereco': {
                'rua': 'Avenida dos Campeões, 100',
                'cidade': 'Sorocaba',
                'estado': 'SP',
                'cep': '18000-000',
                'pais': 'Brasil'
            },
            'contato': {
                'telefone': '(15) 4444-5555',
                'email': 'contato@haraselite.com.br',
                'website': 'www.haraselite.com.br'
            },
            'personalizacao': {
                'logo_url': '/assets/logo-elite.png',
                'cor_primaria': '#7B1FA2',
                'cor_secundaria': '#9C27B0',
                'tema': 'escuro'
            }
        }
        tenant3.atualizar_configuracoes(config3)
        
        # Criar usuários para cada tenant
        print("👥 Criando usuários...")
        
        # Usuários Haras São João
        usuario1 = Usuario(
            nome="João Silva",
            email="joao@harassaojoao.com.br",
            senha=generate_password_hash("123456"),
            papel="proprietario",
            tenant_id=tenant1.id
        )
        
        usuario2 = Usuario(
            nome="Dr. Maria Santos",
            email="maria@harassaojoao.com.br",
            senha=generate_password_hash("123456"),
            papel="veterinario",
            tenant_id=tenant1.id
        )
        
        # Usuários Fazenda Esperança
        usuario3 = Usuario(
            nome="Carlos Oliveira",
            email="carlos@fazendaesperanca.com.br",
            senha=generate_password_hash("123456"),
            papel="proprietario",
            tenant_id=tenant2.id
        )
        
        # Usuários Haras Elite
        usuario4 = Usuario(
            nome="Ana Costa",
            email="ana@haraselite.com.br",
            senha=generate_password_hash("123456"),
            papel="proprietario",
            tenant_id=tenant3.id
        )
        
        usuario5 = Usuario(
            nome="Dr. Roberto Lima",
            email="roberto@haraselite.com.br",
            senha=generate_password_hash("123456"),
            papel="veterinario",
            tenant_id=tenant3.id
        )
        
        usuario6 = Usuario(
            nome="Dra. Fernanda Rocha",
            email="fernanda@haraselite.com.br",
            senha=generate_password_hash("123456"),
            papel="veterinario",
            tenant_id=tenant3.id
        )
        
        # Adicionar usuários
        db.session.add_all([usuario1, usuario2, usuario3, usuario4, usuario5, usuario6])
        
        # Criar animais para cada tenant
        print("🐴 Criando animais...")
        
        # Animais Haras São João
        eguas_sj = [
            Egua(nome="Estrela Dourada", raca="Mangalarga", idade=8, peso=450, tenant_id=tenant1.id),
            Egua(nome="Lua Prateada", raca="Quarto de Milha", idade=6, peso=480, tenant_id=tenant1.id),
            Egua(nome="Brisa Matinal", raca="Mangalarga", idade=10, peso=460, tenant_id=tenant1.id)
        ]
        
        garanhoes_sj = [
            Garanhao(nome="Trovão Negro", raca="Mangalarga", idade=12, peso=520, tenant_id=tenant1.id),
            Garanhao(nome="Vento Forte", raca="Quarto de Milha", idade=8, peso=540, tenant_id=tenant1.id)
        ]
        
        # Animais Fazenda Esperança
        eguas_fe = [
            Egua(nome="Esperança Dourada", raca="Mangalarga", idade=7, peso=440, tenant_id=tenant2.id),
            Egua(nome="Sonho Real", raca="Campolina", idade=9, peso=470, tenant_id=tenant2.id)
        ]
        
        garanhoes_fe = [
            Garanhao(nome="Rei da Fazenda", raca="Mangalarga", idade=10, peso=510, tenant_id=tenant2.id)
        ]
        
        # Animais Haras Elite
        eguas_he = [
            Egua(nome="Elite Princess", raca="Puro Sangue Inglês", idade=5, peso=500, tenant_id=tenant3.id),
            Egua(nome="Golden Star", raca="Puro Sangue Inglês", idade=7, peso=490, tenant_id=tenant3.id),
            Egua(nome="Diamond Queen", raca="Hanoveriano", idade=8, peso=520, tenant_id=tenant3.id),
            Egua(nome="Royal Beauty", raca="Oldenburg", idade=6, peso=510, tenant_id=tenant3.id)
        ]
        
        garanhoes_he = [
            Garanhao(nome="Elite Champion", raca="Puro Sangue Inglês", idade=9, peso=580, tenant_id=tenant3.id),
            Garanhao(nome="Golden Thunder", raca="Hanoveriano", idade=11, peso=600, tenant_id=tenant3.id),
            Garanhao(nome="Royal Storm", raca="Oldenburg", idade=7, peso=570, tenant_id=tenant3.id)
        ]
        
        # Adicionar animais
        todos_animais = eguas_sj + garanhoes_sj + eguas_fe + garanhoes_fe + eguas_he + garanhoes_he
        db.session.add_all(todos_animais)
        
        # Criar transferências de exemplo
        print("🧬 Criando transferências...")
        
        transferencias = [
            # Haras São João
            TransferenciaEmbriao(
                egua_doadora_id=1, egua_receptora_id=2, garanhao_id=1,
                data_transferencia=datetime.now() - timedelta(days=30),
                resultado="prenhez_confirmada",
                tenant_id=tenant1.id
            ),
            TransferenciaEmbriao(
                egua_doadora_id=2, egua_receptora_id=3, garanhao_id=2,
                data_transferencia=datetime.now() - timedelta(days=15),
                resultado="em_andamento",
                tenant_id=tenant1.id
            ),
            
            # Fazenda Esperança
            TransferenciaEmbriao(
                egua_doadora_id=4, egua_receptora_id=5, garanhao_id=3,
                data_transferencia=datetime.now() - timedelta(days=20),
                resultado="prenhez_confirmada",
                tenant_id=tenant2.id
            ),
            
            # Haras Elite
            TransferenciaEmbriao(
                egua_doadora_id=6, egua_receptora_id=7, garanhao_id=4,
                data_transferencia=datetime.now() - timedelta(days=25),
                resultado="prenhez_confirmada",
                tenant_id=tenant3.id
            ),
            TransferenciaEmbriao(
                egua_doadora_id=8, egua_receptora_id=9, garanhao_id=5,
                data_transferencia=datetime.now() - timedelta(days=10),
                resultado="em_andamento",
                tenant_id=tenant3.id
            )
        ]
        
        db.session.add_all(transferencias)
        
        # Atualizar uso dos tenants
        print("📊 Atualizando uso dos tenants...")
        for tenant in [tenant1, tenant2, tenant3]:
            tenant.atualizar_uso()
        
        # Commit todas as mudanças
        db.session.commit()
        
        print("✅ Dados multi-tenant criados com sucesso!")
        print("\n📋 Resumo dos Tenants:")
        print(f"1. {tenant1.nome} ({tenant1.slug}) - {tenant1.plano.value} - {tenant1.status.value}")
        print(f"   Usuários: {tenant1.usuarios_ativos}/{tenant1.limite_usuarios}")
        print(f"   Animais: {tenant1.animais_cadastrados}/{tenant1.limite_animais}")
        
        print(f"\n2. {tenant2.nome} ({tenant2.slug}) - {tenant2.plano.value} - {tenant2.status.value}")
        print(f"   Usuários: {tenant2.usuarios_ativos}/{tenant2.limite_usuarios}")
        print(f"   Animais: {tenant2.animais_cadastrados}/{tenant2.limite_animais}")
        
        print(f"\n3. {tenant3.nome} ({tenant3.slug}) - {tenant3.plano.value} - {tenant3.status.value}")
        print(f"   Usuários: {tenant3.usuarios_ativos}/{tenant3.limite_usuarios}")
        print(f"   Animais: {tenant3.animais_cadastrados}/{tenant3.limite_animais}")
        
        print("\n🔑 Credenciais de teste:")
        print("Haras São João:")
        print("  Proprietário: joao@harassaojoao.com.br / 123456")
        print("  Veterinário: maria@harassaojoao.com.br / 123456")
        print("\nFazenda Esperança:")
        print("  Proprietário: carlos@fazendaesperanca.com.br / 123456")
        print("\nHaras Elite:")
        print("  Proprietário: ana@haraselite.com.br / 123456")
        print("  Veterinário: roberto@haraselite.com.br / 123456")
        print("  Veterinário: fernanda@haraselite.com.br / 123456")

if __name__ == "__main__":
    criar_dados_tenant()
