#!/usr/bin/env python3
"""
Script simplificado para criar dados de teste multi-tenant
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
import json

def criar_dados_tenant_simples():
    """Cria dados de teste multi-tenant diretamente no SQLite"""
    
    # Conectar ao banco de dados
    conn = sqlite3.connect('haras.db')
    cursor = conn.cursor()
    
    print("🏗️  Criando dados multi-tenant...")
    
    # Criar tabela de tenants se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'trial',
            plano TEXT DEFAULT 'basico',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_ativacao TIMESTAMP,
            data_expiracao TIMESTAMP,
            ultima_atividade TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            configuracoes TEXT,
            limite_usuarios INTEGER DEFAULT 5,
            limite_animais INTEGER DEFAULT 100,
            limite_storage_mb INTEGER DEFAULT 1000,
            usuarios_ativos INTEGER DEFAULT 0,
            animais_cadastrados INTEGER DEFAULT 0,
            storage_usado_mb INTEGER DEFAULT 0
        )
    ''')
    
    # Limpar dados existentes
    cursor.execute('DELETE FROM tenants')
    
    # Criar tenants
    tenants = [
        {
            'id': str(uuid.uuid4()),
            'nome': 'Haras São João',
            'slug': 'haras-sao-joao',
            'status': 'ativo',
            'plano': 'profissional',
            'data_ativacao': datetime.now().isoformat(),
            'data_expiracao': (datetime.now() + timedelta(days=365)).isoformat(),
            'limite_usuarios': 10,
            'limite_animais': 200,
            'limite_storage_mb': 2000,
            'usuarios_ativos': 2,
            'animais_cadastrados': 5,
            'storage_usado_mb': 150,
            'configuracoes': json.dumps({
                'nome_haras': 'Haras São João',
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
                'configuracoes_sistema': {
                    'timezone': 'America/Sao_Paulo',
                    'moeda': 'BRL',
                    'idioma': 'pt-BR',
                    'formato_data': 'DD/MM/YYYY',
                    'notificacoes_email': True,
                    'backup_automatico': True
                },
                'personalizacao': {
                    'logo_url': '/assets/logo-sao-joao.png',
                    'cor_primaria': '#2E7D32',
                    'cor_secundaria': '#4CAF50',
                    'tema': 'claro'
                }
            })
        },
        {
            'id': str(uuid.uuid4()),
            'nome': 'Fazenda Esperança',
            'slug': 'fazenda-esperanca',
            'status': 'trial',
            'plano': 'basico',
            'data_expiracao': (datetime.now() + timedelta(days=15)).isoformat(),
            'limite_usuarios': 3,
            'limite_animais': 50,
            'limite_storage_mb': 500,
            'usuarios_ativos': 1,
            'animais_cadastrados': 3,
            'storage_usado_mb': 75,
            'configuracoes': json.dumps({
                'nome_haras': 'Fazenda Esperança',
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
                'configuracoes_sistema': {
                    'timezone': 'America/Sao_Paulo',
                    'moeda': 'BRL',
                    'idioma': 'pt-BR',
                    'formato_data': 'DD/MM/YYYY',
                    'notificacoes_email': True,
                    'backup_automatico': False
                },
                'personalizacao': {
                    'logo_url': '/assets/logo-esperanca.png',
                    'cor_primaria': '#1976D2',
                    'cor_secundaria': '#2196F3',
                    'tema': 'claro'
                }
            })
        },
        {
            'id': str(uuid.uuid4()),
            'nome': 'Haras Elite',
            'slug': 'haras-elite',
            'status': 'ativo',
            'plano': 'enterprise',
            'data_ativacao': datetime.now().isoformat(),
            'data_expiracao': (datetime.now() + timedelta(days=365)).isoformat(),
            'limite_usuarios': 50,
            'limite_animais': 1000,
            'limite_storage_mb': 10000,
            'usuarios_ativos': 3,
            'animais_cadastrados': 7,
            'storage_usado_mb': 320,
            'configuracoes': json.dumps({
                'nome_haras': 'Haras Elite',
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
                'configuracoes_sistema': {
                    'timezone': 'America/Sao_Paulo',
                    'moeda': 'BRL',
                    'idioma': 'pt-BR',
                    'formato_data': 'DD/MM/YYYY',
                    'notificacoes_email': True,
                    'backup_automatico': True
                },
                'personalizacao': {
                    'logo_url': '/assets/logo-elite.png',
                    'cor_primaria': '#7B1FA2',
                    'cor_secundaria': '#9C27B0',
                    'tema': 'escuro'
                }
            })
        }
    ]
    
    # Inserir tenants
    for tenant in tenants:
        cursor.execute('''
            INSERT INTO tenants (
                id, nome, slug, status, plano, data_ativacao, data_expiracao,
                limite_usuarios, limite_animais, limite_storage_mb,
                usuarios_ativos, animais_cadastrados, storage_usado_mb, configuracoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tenant['id'], tenant['nome'], tenant['slug'], tenant['status'], tenant['plano'],
            tenant.get('data_ativacao'), tenant['data_expiracao'],
            tenant['limite_usuarios'], tenant['limite_animais'], tenant['limite_storage_mb'],
            tenant['usuarios_ativos'], tenant['animais_cadastrados'], tenant['storage_usado_mb'],
            tenant['configuracoes']
        ))
    
    # Commit e fechar
    conn.commit()
    conn.close()
    
    print("✅ Dados multi-tenant criados com sucesso!")
    print("\n📋 Resumo dos Tenants:")
    for i, tenant in enumerate(tenants, 1):
        print(f"{i}. {tenant['nome']} ({tenant['slug']}) - {tenant['plano']} - {tenant['status']}")
        print(f"   Usuários: {tenant['usuarios_ativos']}/{tenant['limite_usuarios']}")
        print(f"   Animais: {tenant['animais_cadastrados']}/{tenant['limite_animais']}")
        print(f"   Storage: {tenant['storage_usado_mb']}/{tenant['limite_storage_mb']} MB")
        if tenant['status'] == 'trial':
            print(f"   ⚠️  Trial expira em breve!")
        print()

if __name__ == "__main__":
    criar_dados_tenant_simples()
