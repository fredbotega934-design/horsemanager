from src.main import app
from src.models.user import db
from src.models.models import Cliente, Egual, ProcedimentoOPU, Garanhao, Embriao, TransferenciaEmbriao, Gestacao, Parto, AnaliseLaboratorial, Financeiro

with app.app_context():
    db.create_all()

    # Limpar dados existentes
    Cliente.query.delete()
    Egual.query.delete()
    ProcedimentoOPU.query.delete()
    Garanhao.query.delete()
    Embriao.query.delete()
    TransferenciaEmbriao.query.delete()
    Gestacao.query.delete()
    Parto.query.delete()
    AnaliseLaboratorial.query.delete()
    Financeiro.query.delete()
    db.session.commit()

    # Clientes
    cliente1 = Cliente(nome_cliente="Haras Estrela", telefone="(11) 98765-4321", email="contato@harasestrela.com", whatsapp="(11) 98765-4321", localizacao="São Paulo", endereco_completo="Rua do Haras, 123", cep="01000-000", cnpj_cpf="12.345.678/0001-90", responsavel_tecnico="Dr. Ricardo", crmv_responsavel="CRMV-SP 1234", tipo_cliente="haras", observacoes="Cliente de longa data", data_cadastro="2020-01-01", status="ativo", contrato_vigente=True, data_inicio_contrato="2020-01-01", data_fim_contrato="2025-12-31")
    cliente2 = Cliente(nome_cliente="Fazenda Lua", telefone="(21) 99876-5432", email="contato@fazendaluar.com", whatsapp="(21) 99876-5432", localizacao="Rio de Janeiro", endereco_completo="Av. da Fazenda, 456", cep="20000-000", cnpj_cpf="98.765.432/0001-10", responsavel_tecnico="Dra. Fernanda", crmv_responsavel="CRMV-RJ 5678", tipo_cliente="particular", observacoes="Novo cliente", data_cadastro="2023-05-10", status="ativo", contrato_vigente=True, data_inicio_contrato="2023-05-10", data_fim_contrato="2026-05-09")
    db.session.add_all([cliente1, cliente2])
    db.session.commit()

    # Éguas
    egua1 = Egual(nome_egua="Estrela Dourada", cliente_id=cliente1.id, idade=8, raca="Mangalarga Marchador", registro="REG-00001", data_nascimento="2017-03-15", pelagem="Alazã", altura="1.55m", peso="450kg", microchip="123456789012345", pai="Pai Estrelado", mae="Mãe Dourada", classificacao="doadora", status_reprodutivo="ativa", historico_gestacoes=3, historico_partos=3, historico_abortos=0, ultima_cobertura="2024-02-01", ultimo_parto="2024-01-01", ciclo_estral_atual="Diestro", data_ultimo_cio="2024-03-10", intervalo_cio_medio=21, condicao_corporal=4, observacoes="Excelente doadora.", data_cadastro="2020-01-01")
    egua2 = Egual(nome_egua="Lua Prateada", cliente_id=cliente2.id, idade=6, raca="Mangalarga Marchador", registro="REG-00002", data_nascimento="2019-05-20", pelagem="Tordilha", altura="1.50m", peso="420kg", microchip="987654321098765", pai="Pai Luar", mae="Mãe Prata", classificacao="receptora", status_reprodutivo="vazia", historico_gestacoes=2, historico_partos=2, historico_abortos=0, ultima_cobertura="2023-11-15", ultimo_parto="2023-10-01", ciclo_estral_atual="Estro", data_ultimo_cio="2024-03-25", intervalo_cio_medio=20, condicao_corporal=3, observacoes="Boa receptora.", data_cadastro="2023-05-10")
    egua3 = Egual(nome_egua="Aurora", cliente_id=cliente1.id, idade=5, raca="Quarto de Milha", registro="REG-00003", data_nascimento="2020-01-10", pelagem="Castanha", altura="1.58m", peso="480kg", microchip="112233445566778", pai="Pai Sol", mae="Mãe Brilhante", classificacao="doadora", status_reprodutivo="ativa", historico_gestacoes=1, historico_partos=1, historico_abortos=0, ultima_cobertura="2024-03-01", ultimo_parto="2024-02-01", ciclo_estral_atual="Diestro", data_ultimo_cio="2024-03-20", intervalo_cio_medio=22, condicao_corporal=5, observacoes="Doadora jovem com alto potencial.", data_cadastro="2024-01-01")
    db.session.add_all([egua1, egua2, egua3])
    db.session.commit()

    # Procedimentos OPU
    procedimento1 = ProcedimentoOPU(egua_id=egua1.id, tipo_procedimento="OPU", data_procedimento="2025-03-20", foliculos_aspirados=12, ccos_recuperados=10, taxa_recuperacao=83.3, ciclo_estral="Diestro", dia_ciclo=10, medicacao_utilizada="Buscopan Composto", protocolo_hormonal="Protocolo Padrão OPU", veterinario_responsavel="Dr. João Silva", crmv_veterinario="CRMV-SP 12345", tecnico_responsavel="Maria Souza", equipamento_utilizado="Ultrassom GE", complicacoes="Nenhuma", observacoes="Procedimento bem-sucedido.", proxima_opu="2025-04-10", tamanhos_foliculos="{'10mm': 5, '15mm': 4, '20mm': 3}", qualidade_ccos="{'Grau 1': 8, 'Grau 2': 2}", tempo_procedimento=30, custo_procedimento=500.0, status="Concluído")
    procedimento2 = ProcedimentoOPU(egua_id=egua3.id, tipo_procedimento="OPU", data_procedimento="2025-03-25", foliculos_aspirados=15, ccos_recuperados=13, taxa_recuperacao=86.7, ciclo_estral="Diestro", dia_ciclo=12, medicacao_utilizada="Buscopan", protocolo_hormonal="Protocolo OPU Avançado", veterinario_responsavel="Dra. Ana Costa", crmv_veterinario="CRMV-RJ 54321", tecnico_responsavel="Pedro Alves", equipamento_utilizado="Ultrassom Portátil", complicacoes="Leve hemorragia", observacoes="Recuperação rápida.", proxima_opu="2025-04-15", tamanhos_foliculos="{'10mm': 7, '15mm': 5, '20mm': 3}", qualidade_ccos="{'Grau 1': 10, 'Grau 2': 3}", tempo_procedimento=40, custo_procedimento=600.0, status="Concluído")
    db.session.add_all([procedimento1, procedimento2])
    db.session.commit()

    # Garanhões
    garanhao1 = Garanhao(nome_garanhao="Sol Negro", proprietario_id=cliente1.id, idade=10, raca="Mangalarga Marchador", registro="GAR-00001", data_nascimento="2015-08-01", pelagem="Preta", altura="1.60m", peso="500kg", microchip="987654321098765", pai="Pai Sombrio", mae="Mãe Noite", status_reprodutivo="ativo", tipo_cobertura="['IA', 'Monta Natural']", valor_cobertura=5000.0, historico_coberturas=50, taxa_prenhez=0.85, qualidade_semen="{'motilidade': '80%', 'concentracao': '100x10^6'}", observacoes="Garanhão de linhagem superior.", data_cadastro="2019-01-01")
    garanhao2 = Garanhao(nome_garanhao="Vento Forte", proprietario_id=cliente2.id, idade=7, raca="Quarto de Milha", registro="GAR-00002", data_nascimento="2018-04-10", pelagem="Castanha", altura="1.62m", peso="520kg", microchip="111222333444555", pai="Pai Veloz", mae="Mãe Brisa", status_reprodutivo="ativo", tipo_cobertura="['IA']", valor_cobertura=7000.0, historico_coberturas=30, taxa_prenhez=0.90, qualidade_semen="{'motilidade': '90%', 'concentracao': '120x10^6'}", observacoes="Excelente garanhão para reprodução.", data_cadastro="2022-06-01")
    db.session.add_all([garanhao1, garanhao2])
    db.session.commit()

    # Embriões
    embriao1 = Embriao(doadora_id=egua1.id, garanhao_id=garanhao1.id, data_coleta="2025-03-20", metodo_coleta="OPU", qualidade="Grau A", grau_desenvolvimento="Mórula", diametro="200um", status="Congelado", data_congelamento="2025-03-21", metodo_congelamento="Vitrificação", recipiente_armazenamento="Palheta 0.25ml", posicao_tanque="Tanque 1, Canister 2, Goblet 3", observacoes="Embrião de excelente qualidade.", custo_producao=1500.0)
    embriao2 = Embriao(doadora_id=egua3.id, garanhao_id=garanhao2.id, data_coleta="2025-03-25", metodo_coleta="OPU", qualidade="Grau B", grau_desenvolvimento="Blastocisto", diametro="250um", status="Fresco", observacoes="Embrião de boa qualidade.", custo_producao=1800.0)
    db.session.add_all([embriao1, embriao2])
    db.session.commit()

    # Transferências de Embrião
    transferencia1 = TransferenciaEmbriao(doadora_id=egua1.id, receptora_id=egua2.id, embriao_id=embriao1.id, data_transferencia="2025-03-28", dia_ciclo_doadora=10, dia_ciclo_receptora=7, sincronia=3, metodo_transferencia="Transcervical", veterinario_responsavel="Dra. Ana Costa", crmv_veterinario="CRMV-RJ 54321", qualidade_embriao="Grau A", grau_desenvolvimento="Mórula", diametro_embriao="200um", medicacao_pre_te="Flunixin Meglumine", medicacao_pos_te="Progesterona", complicacoes="Nenhuma", resultado_te="Positiva", data_diagnostico="2025-04-14", metodo_diagnostico="Ultrassom", observacoes="Transferência bem-sucedida.", custo_procedimento=800.0, status="Concluída")
    db.session.add(transferencia1)
    db.session.commit()

    # Gestações
    gestacao1 = Gestacao(egua_id=egua2.id, doadora_id=egua1.id, garanhao_id=garanhao1.id, embriao_id=embriao1.id, tipo_gestacao="TE", data_cobertura="2025-03-28", data_diagnostico="2025-04-14", idade_gestacional=17, data_prevista_parto="2026-02-28", status_gestacao="Em Andamento", exames_gestacao="{'ultrassom_d14': 'Positivo', 'ultrassom_d30': 'Positivo'}", complicacoes="Nenhuma", observacoes="Gestação inicial saudável.", custo_acompanhamento=300.0)
    db.session.add(gestacao1)
    db.session.commit()

    # Partos
    parto1 = Parto(gestacao_id=gestacao1.id, egua_id=egua2.id, data_parto="2026-02-28", tipo_parto="Natural", duracao_parto=30, veterinario_responsavel="Dra. Ana Costa", peso_potro="40kg", sexo_potro="Macho", nome_potro="Potro Estrelado", registro_potro="POT-00001", condicoes_nascimento="Normal", complicacoes="Nenhuma", observacoes="Potro saudável e vigoroso.", custo_parto=200.0)
    db.session.add(parto1)
    db.session.commit()

    # Análises Laboratoriais
    analise1 = AnaliseLaboratorial(egua_id=egua1.id, tipo_analise="Exame de Sangue", material_coletado="Sangue", data_coleta="2025-03-05", parametros_analisados="{'hemograma': 'Normal', 'hormonios': 'Normal'}", laboratorio="Lab Equino", veterinario_solicitante="Dr. João Silva", resultado_geral="Tudo ok.", observacoes="Exame de rotina.", custo_analise=150.0)
    analise2 = AnaliseLaboratorial(egua_id=egua2.id, tipo_analise="Cultura Uterina", material_coletado="Swab Uterino", data_coleta="2025-03-10", parametros_analisados="{'bacterias': 'Ausente', 'fungos': 'Ausente'}", laboratorio="Lab Equino", veterinario_solicitante="Dra. Ana Costa", resultado_geral="Negativo para infecções.", observacoes="Pré-transferência.", custo_analise=200.0)
    db.session.add_all([analise1, analise2])
    db.session.commit()

    # Financeiro
    financeiro1 = Financeiro(cliente_id=cliente1.id, tipo_transacao="Receita", categoria="Serviços de OPU", descricao="Serviço de OPU para Estrela Dourada", valor=500.0, data_transacao="2025-03-20", data_vencimento="2025-03-20", status_pagamento="Pago", forma_pagamento="Transferência Bancária", observacoes="Pagamento recebido.")
    financeiro2 = Financeiro(cliente_id=cliente2.id, tipo_transacao="Despesa", categoria="Medicamentos", descricao="Compra de hormônios para sincronização", valor=300.0, data_transacao="2025-03-18", data_vencimento="2025-03-18", status_pagamento="Pago", forma_pagamento="Cartão de Crédito", observacoes="Medicamentos para receptora.")
    db.session.add_all([financeiro1, financeiro2])
    db.session.commit()

    print("Banco de dados populado com sucesso!")
