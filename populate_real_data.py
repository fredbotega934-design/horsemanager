from app_simple import app
from models.database import db_session
from models.custo_prenhez import ItemCusto, Procedimento, CalculoPrenhez

def populate():
    print("Iniciando populacao de dados reais...")
    
    # 1. CUSTOS FIXOS (Rateio Mensal) - Baseado na Categoria D.csv
    # Vamos criar como itens com categoria 'Custo Fixo'
    custos_fixos = [
        {"nome": "Aluguéis", "valor": 0.0, "cat": "Custo Fixo"},
        {"nome": "Pró Labore e Benefícios", "valor": 5000.00, "cat": "Custo Fixo"},
        {"nome": "Luz/Água/Gás/Telefone", "valor": 130.00, "cat": "Custo Fixo"},
        {"nome": "Sistemas/Maquinas", "valor": 576.33, "cat": "Custo Fixo"},
        {"nome": "Desp. Financeiras", "valor": 100.00, "cat": "Custo Fixo"},
        {"nome": "Investimentos", "valor": 500.00, "cat": "Custo Fixo"},
        {"nome": "Marketing", "valor": 100.00, "cat": "Custo Fixo"}
    ]
    
    db_itens_fixos = []
    for c in custos_fixos:
        # Assumindo rateio por procedimento (ex: 1/100 avos) ou valor cheio
        # Aqui cadastraremos o valor cheio para referencia
        item = ItemCusto(
            tenant_id="padrao",
            nome=c["nome"],
            categoria=c["cat"],
            valor_total=c["valor"],
            quantidade_total=1,
            unidade_medida="mês",
            dose_usada=1, # 1 mês
            custo_da_dose=c["valor"], 
            observacoes="Custo fixo mensal (base planilha)"
        )
        db_session.add(item)
        db_itens_fixos.append(item)

    # 2. CUSTOS VARIÁVEIS (Materiais e Mão de Obra) - Baseado em Ficha Técnica
    custos_variaveis = [
        {"nome": "Hormônio (Deslorelin/Sincrocio)", "valor": 80.00, "cat": "Insumo"},
        {"nome": "Materiais Descartáveis (Luvas/Seringas)", "valor": 25.00, "cat": "Insumo"},
        {"nome": "Sedativos", "valor": 40.00, "cat": "Insumo"},
        {"nome": "Lavagem Uterina", "valor": 60.00, "cat": "Procedimento Vet"},
        {"nome": "Mão de Obra Veterinária (Hora)", "valor": 150.00, "cat": "Mão de Obra"},
        {"nome": "Impostos (5% sobre venda)", "valor": 0.05, "cat": "Imposto"} # Tratado especial
    ]

    db_itens_var = []
    for c in custos_variaveis:
        item = ItemCusto(
            tenant_id="padrao",
            nome=c["nome"],
            categoria=c["cat"],
            valor_total=c["valor"],
            quantidade_total=1,
            unidade_medida="un",
            dose_usada=1,
            custo_da_dose=c["valor"],
            observacoes="Custo variável estimado"
        )
        db_session.add(item)
        db_itens_var.append(item)

    db_session.commit()
    print("Itens cadastrados!")

    # 3. CRIAR OS PERFIS (PROCEDIMENTOS COMPLEXOS)
    # Aqui criamos os 'Pacotes' baseados nas planilhas de Éguas
    
    perfis = [
        {"nome": "Perfil: Égua Normal", "tipo": "Reprodução", "itens": db_itens_var[:3]}, # Usa primeiros 3 itens
        {"nome": "Perfil: Égua Subfértil", "tipo": "Reprodução", "itens": db_itens_var}, # Usa todos (mais complexo)
        {"nome": "Perfil: Égua Infértil", "tipo": "Tratamento", "itens": db_itens_var + [db_itens_fixos[1]]} # Usa tudo + pro labore
    ]

    for p in perfis:
        custo_total = sum(i.custo_da_dose for i in p["itens"])
        proc = Procedimento(
            tenant_id="padrao",
            nome=p["nome"],
            tipo=p["tipo"],
            custo_total=custo_total,
            observacoes="Baseado na planilha de precificação"
        )
        for i in p["itens"]:
            proc.itens_usados.append(i)
        
        db_session.add(proc)

    db_session.commit()
    print("Perfis de Éguas cadastrados com sucesso!")

if __name__ == "__main__":
    with app.app_context():
        populate()
