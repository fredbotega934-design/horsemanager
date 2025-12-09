#!/usr/bin/env python3
"""
Script para criar dados VaaS no banco SQLite correto
"""

import sqlite3
import json
from datetime import datetime, timedelta, date

DB_PATH = 'src/instance/haras.db'

def criar_tabelas_vaas():
    """Criar tabelas VaaS no banco SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabela de planos VaaS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planos_vaas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            descricao TEXT,
            preco_mensal DECIMAL(10,2) NOT NULL,
            max_veterinarios INTEGER NOT NULL,
            max_consultas_mes INTEGER,
            max_procedimentos_mes INTEGER,
            recursos_inclusos TEXT,
            ativo BOOLEAN DEFAULT 1,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar tabela de assinaturas VaaS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assinaturas_vaas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id VARCHAR(50) NOT NULL,
            proprietario_id INTEGER NOT NULL,
            plano_id INTEGER NOT NULL,
            data_inicio DATETIME NOT NULL,
            data_fim DATETIME,
            data_cancelamento DATETIME,
            status VARCHAR(50) DEFAULT 'ativa',
            veterinarios_contratados INTEGER DEFAULT 0,
            limite_personalizado_consultas INTEGER,
            limite_personalizado_procedimentos INTEGER,
            FOREIGN KEY (proprietario_id) REFERENCES usuarios (id),
            FOREIGN KEY (plano_id) REFERENCES planos_vaas (id)
        )
    ''')
    
    # Criar tabela de contratos de veterinários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contratos_veterinario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id VARCHAR(50) NOT NULL,
            proprietario_id INTEGER NOT NULL,
            veterinario_id INTEGER NOT NULL,
            assinatura_id INTEGER NOT NULL,
            data_inicio DATETIME NOT NULL,
            data_fim DATETIME,
            status VARCHAR(50) DEFAULT 'ativo',
            valor_hora DECIMAL(10,2),
            valor_consulta DECIMAL(10,2),
            valor_procedimento DECIMAL(10,2),
            permissoes_especiais TEXT,
            horarios_disponibilidade TEXT,
            FOREIGN KEY (proprietario_id) REFERENCES usuarios (id),
            FOREIGN KEY (veterinario_id) REFERENCES usuarios (id),
            FOREIGN KEY (assinatura_id) REFERENCES assinaturas_vaas (id)
        )
    ''')
    
    # Criar tabela de atendimentos VaaS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atendimentos_vaas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id VARCHAR(50) NOT NULL,
            contrato_id INTEGER NOT NULL,
            veterinario_id INTEGER NOT NULL,
            animal_id INTEGER,
            data_atendimento DATETIME NOT NULL,
            tipo_atendimento VARCHAR(100) NOT NULL,
            duracao_minutos INTEGER,
            descricao TEXT,
            observacoes TEXT,
            valor_cobrado DECIMAL(10,2) NOT NULL,
            forma_cobranca VARCHAR(50),
            status VARCHAR(50) DEFAULT 'realizado',
            data_faturamento DATETIME,
            FOREIGN KEY (contrato_id) REFERENCES contratos_veterinario (id),
            FOREIGN KEY (veterinario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Criar tabela de métricas VaaS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metricas_vaas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id VARCHAR(50) NOT NULL,
            data_metrica DATE NOT NULL,
            total_atendimentos INTEGER DEFAULT 0,
            total_consultas INTEGER DEFAULT 0,
            total_procedimentos INTEGER DEFAULT 0,
            tempo_total_atendimento INTEGER DEFAULT 0,
            receita_dia DECIMAL(10,2) DEFAULT 0,
            custo_veterinarios DECIMAL(10,2) DEFAULT 0,
            economia_gerada DECIMAL(10,2) DEFAULT 0,
            nota_satisfacao_media DECIMAL(3,2),
            veterinarios_ativos INTEGER DEFAULT 0,
            taxa_utilizacao DECIMAL(5,2) DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Tabelas VaaS criadas com sucesso!")

def popular_dados_vaas():
    """Popular todos os dados VaaS"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Criar planos VaaS
        print("Criando planos VaaS...")
        planos = [
            ('VaaS Básico', 'Plano ideal para haras pequenos com até 2 veterinários', 299.00, 2, 20, 10, 
             json.dumps(['Dashboard de monitoramento', 'Relatórios básicos', 'Suporte por email', 'Backup automático'])),
            ('VaaS Profissional', 'Plano completo para haras médios com até 5 veterinários', 599.00, 5, 50, 30,
             json.dumps(['Dashboard avançado', 'Relatórios detalhados', 'Analytics em tempo real', 'Suporte prioritário', 'Integração com laboratórios', 'Backup automático'])),
            ('VaaS Enterprise', 'Solução completa para grandes haras com veterinários ilimitados', 1299.00, 999, 200, 100,
             json.dumps(['Dashboard personalizado', 'Relatórios executivos', 'Analytics avançado', 'Suporte 24/7', 'Integração completa', 'API personalizada', 'Backup em tempo real', 'Consultoria especializada']))
        ]
        
        for plano in planos:
            cursor.execute('''
                INSERT OR IGNORE INTO planos_vaas 
                (nome, descricao, preco_mensal, max_veterinarios, max_consultas_mes, max_procedimentos_mes, recursos_inclusos)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', plano)
        
        # 2. Buscar proprietário
        cursor.execute("SELECT id, tenant_id FROM usuarios WHERE email = 'joao@haras.com'")
        proprietario = cursor.fetchone()
        
        if not proprietario:
            print("❌ Proprietário não encontrado!")
            return
        
        # 3. Buscar plano profissional
        cursor.execute("SELECT id FROM planos_vaas WHERE nome = 'VaaS Profissional'")
        plano = cursor.fetchone()
        
        if not plano:
            print("❌ Plano não encontrado!")
            return
        
        # 4. Criar assinatura
        print("Criando assinatura VaaS...")
        data_inicio = (datetime.now() - timedelta(days=15)).isoformat()
        data_fim = (datetime.now() + timedelta(days=15)).isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO assinaturas_vaas 
            (tenant_id, proprietario_id, plano_id, data_inicio, data_fim, status, veterinarios_contratados)
            VALUES (?, ?, ?, ?, ?, 'ativa', 2)
        ''', (proprietario[1], proprietario[0], plano[0], data_inicio, data_fim))
        
        assinatura_id = cursor.lastrowid
        
        # 5. Buscar veterinários e criar contratos
        print("Criando contratos de veterinários...")
        cursor.execute("SELECT id FROM usuarios WHERE role = 'veterinario' LIMIT 2")
        veterinarios = cursor.fetchall()
        
        data_inicio_contrato = (datetime.now() - timedelta(days=10)).isoformat()
        
        for vet_id in veterinarios:
            # Atualizar tenant_id do veterinário
            cursor.execute("UPDATE usuarios SET tenant_id = ? WHERE id = ?", (proprietario[1], vet_id[0]))
            
            # Criar contrato
            cursor.execute('''
                INSERT OR REPLACE INTO contratos_veterinario 
                (tenant_id, proprietario_id, veterinario_id, assinatura_id, data_inicio, status, 
                 valor_hora, valor_consulta, valor_procedimento, permissoes_especiais, horarios_disponibilidade)
                VALUES (?, ?, ?, ?, ?, 'ativo', 150.00, 200.00, 350.00, ?, ?)
            ''', (
                proprietario[1], proprietario[0], vet_id[0], assinatura_id, data_inicio_contrato,
                json.dumps({'acesso_financeiro_limitado': False, 'pode_agendar_procedimentos': True, 'pode_emitir_laudos': True}),
                json.dumps({'segunda': ['08:00', '17:00'], 'terca': ['08:00', '17:00'], 'quarta': ['08:00', '17:00'], 'quinta': ['08:00', '17:00'], 'sexta': ['08:00', '17:00'], 'sabado': ['08:00', '12:00']})
            ))
        
        # 6. Criar atendimentos
        print("Criando atendimentos VaaS...")
        cursor.execute("SELECT id, tenant_id, veterinario_id FROM contratos_veterinario WHERE status = 'ativo'")
        contratos = cursor.fetchall()
        
        tipos_atendimento = ['consulta', 'procedimento', 'emergencia']
        descricoes = [
            'Exame clínico geral', 'Transferência de embrião', 'Ultrassonografia reprodutiva',
            'Coleta de embrião', 'Inseminação artificial', 'Exame andrológico',
            'Palpação retal', 'Tratamento hormonal', 'Cirurgia menor', 'Atendimento de emergência'
        ]
        
        for contrato in contratos:
            for i in range(12):  # 12 atendimentos por veterinário
                data_atendimento = (datetime.now() - timedelta(days=30 - (i * 2), hours=8 + (i % 8))).isoformat()
                tipo = tipos_atendimento[i % len(tipos_atendimento)]
                descricao = descricoes[i % len(descricoes)]
                
                # Calcular valores
                if tipo == 'consulta':
                    valor_cobrado = 200.00
                    duracao = 60
                elif tipo == 'procedimento':
                    valor_cobrado = 350.00
                    duracao = 120
                else:  # emergencia
                    valor_cobrado = 300.00
                    duracao = 90
                
                cursor.execute('''
                    INSERT INTO atendimentos_vaas 
                    (tenant_id, contrato_id, veterinario_id, animal_id, data_atendimento, tipo_atendimento,
                     duracao_minutos, descricao, observacoes, valor_cobrado, forma_cobranca, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'realizado')
                ''', (
                    contrato[1], contrato[0], contrato[2], (i % 6) + 1, data_atendimento, tipo,
                    duracao, descricao, 'Atendimento realizado com sucesso. Animal em boas condições.',
                    valor_cobrado, tipo if tipo != 'emergencia' else 'hora'
                ))
        
        # 7. Criar métricas
        print("Criando métricas VaaS...")
        tenant_id = proprietario[1]
        
        for i in range(30):
            data_metrica = (date.today() - timedelta(days=29-i)).isoformat()
            base_atendimentos = 3 + (i % 5)
            base_receita = 600 + (i * 50) + ((i % 7) * 100)
            
            cursor.execute('''
                INSERT OR REPLACE INTO metricas_vaas 
                (tenant_id, data_metrica, total_atendimentos, total_consultas, total_procedimentos,
                 tempo_total_atendimento, receita_dia, custo_veterinarios, economia_gerada,
                 nota_satisfacao_media, veterinarios_ativos, taxa_utilizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2, ?)
            ''', (
                tenant_id, data_metrica, base_atendimentos, base_atendimentos // 2, 
                base_atendimentos - (base_atendimentos // 2), base_atendimentos * 75,
                base_receita, base_receita * 0.6, base_receita * 0.3,
                4.5 + ((i % 10) / 10), 40 + (i % 30)
            ))
        
        conn.commit()
        print("✅ Todos os dados VaaS criados com sucesso!")
        
        # Verificar dados criados
        cursor.execute("SELECT COUNT(*) FROM planos_vaas")
        planos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM assinaturas_vaas")
        assinaturas_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contratos_veterinario")
        contratos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM atendimentos_vaas")
        atendimentos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM metricas_vaas")
        metricas_count = cursor.fetchone()[0]
        
        print(f"\n📊 Resumo dos dados criados:")
        print(f"- {planos_count} planos VaaS")
        print(f"- {assinaturas_count} assinaturas")
        print(f"- {contratos_count} contratos de veterinários")
        print(f"- {atendimentos_count} atendimentos")
        print(f"- {metricas_count} métricas diárias")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 Iniciando criação de dados VaaS...")
    
    criar_tabelas_vaas()
    popular_dados_vaas()
    
    print("\n🎉 Processo concluído!")

if __name__ == '__main__':
    main()
