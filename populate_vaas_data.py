#!/usr/bin/env python3
"""
Script para popular dados de teste do sistema VaaS
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta, date
from decimal import Decimal
import json

from src.models.user import db, Usuario
from src.models.vaas import (
    PlanoVaaS, AssinaturaVaaS, ContratoVeterinario, 
    AtendimentoVaaS, FaturaVaaS, MetricaVaaS
)

# Importar app depois dos modelos
from src.app import app

def criar_planos_vaas():
    """Criar planos VaaS de exemplo"""
    print("Criando planos VaaS...")
    
    planos = [
        {
            'nome': 'VaaS Básico',
            'descricao': 'Plano ideal para haras pequenos com até 2 veterinários',
            'preco_mensal': Decimal('299.00'),
            'max_veterinarios': 2,
            'max_consultas_mes': 20,
            'max_procedimentos_mes': 10,
            'recursos_inclusos': json.dumps([
                'Dashboard de monitoramento',
                'Relatórios básicos',
                'Suporte por email',
                'Backup automático'
            ])
        },
        {
            'nome': 'VaaS Profissional',
            'descricao': 'Plano completo para haras médios com até 5 veterinários',
            'preco_mensal': Decimal('599.00'),
            'max_veterinarios': 5,
            'max_consultas_mes': 50,
            'max_procedimentos_mes': 30,
            'recursos_inclusos': json.dumps([
                'Dashboard avançado',
                'Relatórios detalhados',
                'Analytics em tempo real',
                'Suporte prioritário',
                'Integração com laboratórios',
                'Backup automático'
            ])
        },
        {
            'nome': 'VaaS Enterprise',
            'descricao': 'Solução completa para grandes haras com veterinários ilimitados',
            'preco_mensal': Decimal('1299.00'),
            'max_veterinarios': 999,
            'max_consultas_mes': 200,
            'max_procedimentos_mes': 100,
            'recursos_inclusos': json.dumps([
                'Dashboard personalizado',
                'Relatórios executivos',
                'Analytics avançado',
                'Suporte 24/7',
                'Integração completa',
                'API personalizada',
                'Backup em tempo real',
                'Consultoria especializada'
            ])
        }
    ]
    
    for plano_data in planos:
        plano_existente = PlanoVaaS.query.filter_by(nome=plano_data['nome']).first()
        if not plano_existente:
            plano = PlanoVaaS(**plano_data)
            db.session.add(plano)
    
    db.session.commit()
    print("Planos VaaS criados com sucesso!")

def criar_assinatura_teste():
    """Criar assinatura de teste para o proprietário"""
    print("Criando assinatura VaaS de teste...")
    
    # Buscar proprietário de teste
    proprietario = Usuario.query.filter_by(email='joao@haras.com').first()
    if not proprietario:
        print("Proprietário de teste não encontrado!")
        return
    
    # Buscar plano profissional
    plano = PlanoVaaS.query.filter_by(nome='VaaS Profissional').first()
    if not plano:
        print("Plano VaaS não encontrado!")
        return
    
    # Verificar se já existe assinatura
    assinatura_existente = AssinaturaVaaS.query.filter_by(
        tenant_id=proprietario.tenant_id,
        status='ativa'
    ).first()
    
    if not assinatura_existente:
        assinatura = AssinaturaVaaS(
            tenant_id=proprietario.tenant_id,
            proprietario_id=proprietario.id,
            plano_id=plano.id,
            data_inicio=datetime.utcnow() - timedelta(days=15),
            data_fim=datetime.utcnow() + timedelta(days=15),
            status='ativa',
            veterinarios_contratados=2
        )
        db.session.add(assinatura)
        db.session.commit()
        print("Assinatura VaaS criada com sucesso!")
    else:
        print("Assinatura VaaS já existe!")

def criar_contratos_veterinarios():
    """Criar contratos de veterinários de teste"""
    print("Criando contratos de veterinários...")
    
    # Buscar proprietário e assinatura
    proprietario = Usuario.query.filter_by(email='joao@haras.com').first()
    if not proprietario:
        print("Proprietário não encontrado!")
        return
    
    assinatura = AssinaturaVaaS.query.filter_by(
        tenant_id=proprietario.tenant_id,
        status='ativa'
    ).first()
    
    if not assinatura:
        print("Assinatura VaaS não encontrada!")
        return
    
    # Buscar veterinários
    veterinarios = Usuario.query.filter_by(role='veterinario').all()
    
    for i, veterinario in enumerate(veterinarios[:2]):  # Contratar apenas 2
        contrato_existente = ContratoVeterinario.query.filter_by(
            tenant_id=proprietario.tenant_id,
            veterinario_id=veterinario.id,
            status='ativo'
        ).first()
        
        if not contrato_existente:
            # Associar veterinário ao tenant
            veterinario.tenant_id = proprietario.tenant_id
            
            contrato = ContratoVeterinario(
                tenant_id=proprietario.tenant_id,
                proprietario_id=proprietario.id,
                veterinario_id=veterinario.id,
                assinatura_id=assinatura.id,
                data_inicio=datetime.utcnow() - timedelta(days=10),
                status='ativo',
                valor_hora=Decimal('150.00'),
                valor_consulta=Decimal('200.00'),
                valor_procedimento=Decimal('350.00'),
                permissoes_especiais=json.dumps({
                    'acesso_financeiro_limitado': False,
                    'pode_agendar_procedimentos': True,
                    'pode_emitir_laudos': True
                }),
                horarios_disponibilidade=json.dumps({
                    'segunda': ['08:00', '17:00'],
                    'terca': ['08:00', '17:00'],
                    'quarta': ['08:00', '17:00'],
                    'quinta': ['08:00', '17:00'],
                    'sexta': ['08:00', '17:00'],
                    'sabado': ['08:00', '12:00']
                })
            )
            db.session.add(contrato)
    
    db.session.commit()
    print("Contratos de veterinários criados com sucesso!")

def criar_atendimentos_teste():
    """Criar atendimentos de teste"""
    print("Criando atendimentos VaaS de teste...")
    
    # Buscar contratos ativos
    contratos = ContratoVeterinario.query.filter_by(status='ativo').all()
    
    if not contratos:
        print("Nenhum contrato ativo encontrado!")
        return
    
    # Criar atendimentos dos últimos 30 dias
    tipos_atendimento = ['consulta', 'procedimento', 'emergencia']
    descricoes = [
        'Exame clínico geral',
        'Transferência de embrião',
        'Ultrassonografia reprodutiva',
        'Coleta de embrião',
        'Inseminação artificial',
        'Exame andrológico',
        'Palpação retal',
        'Tratamento hormonal',
        'Cirurgia menor',
        'Atendimento de emergência'
    ]
    
    for contrato in contratos:
        # Criar 10-15 atendimentos por veterinário
        num_atendimentos = 12 if contrato.veterinario_id % 2 == 0 else 15
        
        for i in range(num_atendimentos):
            data_atendimento = datetime.utcnow() - timedelta(
                days=30 - (i * 2),
                hours=8 + (i % 8),
                minutes=(i * 15) % 60
            )
            
            tipo = tipos_atendimento[i % len(tipos_atendimento)]
            descricao = descricoes[i % len(descricoes)]
            
            # Calcular valor baseado no tipo
            if tipo == 'consulta':
                valor_cobrado = contrato.valor_consulta
                duracao = 60
            elif tipo == 'procedimento':
                valor_cobrado = contrato.valor_procedimento
                duracao = 120
            else:  # emergencia
                valor_cobrado = contrato.valor_hora * 2  # Valor dobrado para emergência
                duracao = 90
            
            atendimento = AtendimentoVaaS(
                tenant_id=contrato.tenant_id,
                contrato_id=contrato.id,
                veterinario_id=contrato.veterinario_id,
                animal_id=(i % 6) + 1,  # Simular IDs de animais
                data_atendimento=data_atendimento,
                tipo_atendimento=tipo,
                duracao_minutos=duracao,
                descricao=descricao,
                observacoes=f'Atendimento realizado com sucesso. Animal em boas condições.',
                valor_cobrado=valor_cobrado,
                forma_cobranca=tipo if tipo != 'emergencia' else 'hora',
                status='realizado'
            )
            
            db.session.add(atendimento)
    
    db.session.commit()
    print("Atendimentos VaaS criados com sucesso!")

def criar_metricas_teste():
    """Criar métricas de teste dos últimos 30 dias"""
    print("Criando métricas VaaS de teste...")
    
    # Buscar tenant do proprietário
    proprietario = Usuario.query.filter_by(email='joao@haras.com').first()
    if not proprietario:
        print("Proprietário não encontrado!")
        return
    
    tenant_id = proprietario.tenant_id
    
    # Criar métricas dos últimos 30 dias
    for i in range(30):
        data_metrica = date.today() - timedelta(days=29-i)
        
        # Verificar se já existe métrica para esta data
        metrica_existente = MetricaVaaS.query.filter_by(
            tenant_id=tenant_id,
            data_metrica=data_metrica
        ).first()
        
        if not metrica_existente:
            # Simular dados variáveis
            base_atendimentos = 3 + (i % 5)
            base_receita = 600 + (i * 50) + ((i % 7) * 100)
            
            metrica = MetricaVaaS(
                tenant_id=tenant_id,
                data_metrica=data_metrica,
                total_atendimentos=base_atendimentos,
                total_consultas=base_atendimentos // 2,
                total_procedimentos=base_atendimentos - (base_atendimentos // 2),
                tempo_total_atendimento=base_atendimentos * 75,  # 75 min por atendimento
                receita_dia=Decimal(str(base_receita)),
                custo_veterinarios=Decimal(str(base_receita * 0.6)),
                economia_gerada=Decimal(str(base_receita * 0.3)),
                nota_satisfacao_media=Decimal('4.5') + (Decimal(i % 10) / 10),
                veterinarios_ativos=2,
                taxa_utilizacao=Decimal(str(40 + (i % 30)))
            )
            
            db.session.add(metrica)
    
    db.session.commit()
    print("Métricas VaaS criadas com sucesso!")

def main():
    """Função principal"""
    print("Iniciando população de dados VaaS...")
    
    with app.app_context():
        try:
            # Criar tabelas se não existirem
            db.create_all()
            
            # Popular dados
            criar_planos_vaas()
            criar_assinatura_teste()
            criar_contratos_veterinarios()
            criar_atendimentos_teste()
            criar_metricas_teste()
            
            print("\n✅ Dados VaaS populados com sucesso!")
            print("\nDados criados:")
            print(f"- {PlanoVaaS.query.count()} planos VaaS")
            print(f"- {AssinaturaVaaS.query.count()} assinaturas")
            print(f"- {ContratoVeterinario.query.count()} contratos de veterinários")
            print(f"- {AtendimentoVaaS.query.count()} atendimentos")
            print(f"- {MetricaVaaS.query.count()} métricas diárias")
            
        except Exception as e:
            print(f"❌ Erro ao popular dados: {e}")
            db.session.rollback()

if __name__ == '__main__':
    main()
