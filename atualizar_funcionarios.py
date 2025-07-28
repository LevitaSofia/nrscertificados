from app import app, db, Funcionario
from datetime import datetime
import re

def atualizar_banco_funcionarios():
    """Atualiza o banco de dados com a lista completa de funcionários"""
    
    funcionarios_data = [
        {
            'nome': 'ANDRE ROBERTO DOS SANTOS',
            'cpf': '313.673.508-08',
            'data_nascimento': '12/01/1980',
            'data_admissao': '11/02/2022',
            'telefone': '11 94870-7283',
            'email': 'andrealtatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Supervisor de obra'
        },
        {
            'nome': 'BRUNO PINHEIRO DE LIMA',
            'cpf': '401.201.328-93',
            'data_nascimento': '27/04/1990',
            'data_admissao': '17/04/2020',
            'telefone': '11 95273-9404',
            'email': 'brunoaltatelas@gmail.com',
            'senha': 'Alta972600#',
            'funcao': 'Encarregado de obra'
        },
        {
            'nome': 'CAIO VINICIUS PAES DO NASCIMENTO',
            'cpf': '414.038.588-02',
            'data_nascimento': '30/05/1991',
            'data_admissao': '23/06/2025',
            'telefone': '11 95487-5236',
            'email': 'caioaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'CARLOS ALBERTO DOS SANTOS',
            'cpf': '288.915.798-90',
            'data_nascimento': '21/11/1978',
            'data_admissao': '15/10/2024',
            'telefone': '16 98865-1612',
            'email': 'carlosaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'CLEUTON CLEBER VIEIRA ROMANO',
            'cpf': '270.176.758-00',
            'data_nascimento': '05/12/1979',
            'data_admissao': '04/04/2025',
            'telefone': '19 990058626',
            'email': 'cleutonaltatelas@gmail.com',
            'senha': 'Alta972600#',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'DIOGO PEREIRA CARDOSO',
            'cpf': '058.224.705-56',
            'data_nascimento': '30/12/1991',
            'data_admissao': '25/10/2024',
            'telefone': '16 98103-7258',
            'email': 'diogoaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de serralheiro'
        },
        {
            'nome': 'EDERSON GONÇALVES VIEIRA DA SILVA',
            'cpf': '495.685.328-97',
            'data_nascimento': '10/09/1999',
            'data_admissao': '28/03/2025',
            'telefone': '16 99430-4340',
            'email': 'edersongonsalvesaltatelas@gmail.com',
            'senha': 'Alta972600',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'ERDESSON QUIRINO DE LIMA',
            'cpf': '385.283.058-30',
            'data_nascimento': '17/10/1988',
            'data_admissao': '02/03/2020',
            'telefone': '16 98192-4980',
            'email': 'erdersonaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Encarregado de obra'
        },
        {
            'nome': 'EVERTON SAMPAIO MELO DA COSTA',
            'cpf': '258.334.658-00',
            'data_nascimento': '14/01/1976',
            'data_admissao': '08/10/2021',
            'telefone': '11 96917-5480',
            'email': 'evertonaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Encarregado de obra'
        },
        {
            'nome': 'FELIPE ARAUJO DOS SANTOS',
            'cpf': '101.876.985-46',
            'data_nascimento': '13/03/2003',
            'data_admissao': '22/05/2023',
            'telefone': '16 99292-3212',
            'email': 'felipealtatelas@gmail.com',
            'senha': 'Alta972600',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'FERNANDO SILVA DE SOUZA',
            'cpf': '005.378.972-59',
            'data_nascimento': '25/01/1989',
            'data_admissao': '25/10/2024',
            'telefone': '16 99278-2701',
            'email': 'fernandoaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'FILIPE DELFINO',
            'cpf': '350.969.688-39',
            'data_nascimento': '07/05/1987',
            'data_admissao': '23/05/2025',
            'telefone': '16 99261-7738',
            'email': 'filipedelfinoaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'GABRIEL JACKSON PEIXOTO RIBEIRO',
            'cpf': '438.515.568-28',
            'data_nascimento': '08/07/1996',
            'data_admissao': '19/08/2024',
            'telefone': '16 99361-7195',
            'email': 'gabrielaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'GUSTAVO ADOLFO CASTANEDA CARDENAS',
            'cpf': '023.066.106-81',
            'data_nascimento': '23/12/1986',
            'data_admissao': '26/05/2025',
            'telefone': '11 96293-9343',
            'email': 'gustavoaltatelas@gmail.com',
            'senha': 'Alta972600@',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'JARDIEL NUNES DA SILVA',
            'cpf': '070.368.533-36',
            'data_nascimento': '13/09/2000',
            'data_admissao': '09/01/2025',
            'telefone': '16 98191-9551',
            'email': 'jardielaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'JUNIEL DE SOUSA',
            'cpf': '011.619.363-86',
            'data_nascimento': '07/09/1984',
            'data_admissao': '18/04/2023',
            'telefone': '16 99204-7416',
            'email': 'junielaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Serralheiro'
        },
        {
            'nome': 'KAIQUE DE OLIVEIRA SANTOS',
            'cpf': '435.731.658-85',
            'data_nascimento': '02/12/1997',
            'data_admissao': '23/04/2020',
            'telefone': '16 99447-8913',
            'email': 'kaiquealtatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Encarregado de obra'
        },
        {
            'nome': 'LEANDRO RODRIGUES DE SOUZA',
            'cpf': '414.455.308-64',
            'data_nascimento': '26/07/1987',
            'data_admissao': '01/10/2022',
            'telefone': '16 99396-5158',
            'email': 'leandroaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Encarregado de obra'
        },
        {
            'nome': 'LEONARDO DOUGLAS DE OLIVEIRA CORREA',
            'cpf': '525.803.638-31',
            'data_nascimento': '05/03/2003',
            'data_admissao': '16/12/2022',
            'telefone': '11 93397-5926',
            'email': 'leonardoaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'LUCAS EDUARDO RIBEIRO FRANÇA E SILVA',
            'cpf': '468.944.148-07',
            'data_nascimento': '27/10/2006',
            'data_admissao': '31/01/2025',
            'telefone': '16 98836-9753',
            'email': 'lucasaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'LUCIANO DE JESUS',
            'cpf': '264.298.638-16',
            'data_nascimento': '06/11/1975',
            'data_admissao': '27/02/2025',
            'telefone': '16 99754-1563',
            'email': 'lucianoaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas',
            'observacao': 'AFASTADO PELO INSS'
        },
        {
            'nome': 'MAICON DOUGLAS DOS SANTOS INFORZATO',
            'cpf': '463.539.228-76',
            'data_nascimento': '01/05/1993',
            'data_admissao': '12/06/2024',
            'telefone': '16 98152-5822',
            'email': 'maiconaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'MATHEUS SOUSA COSTA',
            'cpf': '538.169.808-99',
            'data_nascimento': '01/12/2001',
            'data_admissao': '24/01/2025',
            'telefone': '16 99111-6444',
            'email': 'matheusaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'PABLO HENRIQUE RIBEIRO FRIZI',
            'cpf': '584.518.788-57',
            'data_nascimento': '22/12/2007',
            'data_admissao': '24/03/2025',
            'telefone': '16 99449-1102',
            'email': 'pabloaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Auxiliar de almoxarifado'
        },
        {
            'nome': 'PAULO FERREIRA CARDOSO',
            'cpf': '427.979.418-96',
            'data_nascimento': '27/10/1997',
            'data_admissao': '05/06/2025',
            'telefone': '16 99715-6763',
            'email': 'pauloaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'RAFAEL DE SOUZA COSTA',
            'cpf': '106.957.083-41',
            'data_nascimento': '09/05/2005',
            'data_admissao': '21/05/2025',
            'telefone': '89 9421-1070',
            'email': 'rafaelaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'RODRIGO APARECIDO COELHO PAULISTA',
            'cpf': '218.937.248-83',
            'data_nascimento': '02/12/1982',
            'data_admissao': '01/11/2024',
            'telefone': '16 99627-3207',
            'email': 'rodrigoaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'RONALDO HENRIQUE DO CARMO',
            'cpf': '342.202.368-21',
            'data_nascimento': '14/09/1986',
            'data_admissao': '12/08/2024',
            'telefone': '16 98846-2058',
            'email': 'ronaldoaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'VICTOR HUGO VIANA GARCEZ',
            'cpf': '384.657.848-76',
            'data_nascimento': '15/09/2000',
            'data_admissao': '15/07/2024',
            'telefone': '16 99307-5592',
            'email': 'victorhugoaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'VITOR BRENO DE SOUZA ARAUJO',
            'cpf': '485.789.938-88',
            'data_nascimento': '15/09/2001',
            'data_admissao': '19/07/2022',
            'telefone': '16 98187-3464',
            'email': 'vitorbrenoaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Instalador de telas'
        },
        {
            'nome': 'WAGNER ZAMBONI',
            'cpf': '286.246.658-17',
            'data_nascimento': '17/08/1980',
            'data_admissao': '19/05/2025',
            'telefone': '16 99722-6712',
            'email': 'wagneraltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'WENDEL HENRIQUE ANTONIO DA SILVA',
            'cpf': '504.069.548-95',
            'data_nascimento': '09/12/1998',
            'data_admissao': '14/03/2025',
            'telefone': '16 99166-2527',
            'email': 'wendelaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'WILLIAM RODRIGUES DA SILVA',
            'cpf': '524.429.368-01',
            'data_nascimento': '16/03/2001',
            'data_admissao': '24/04/2025',
            'telefone': '16 99650-8192',
            'email': 'williamaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'DOUGLAS DE SOUZA DE ALMEIDA',
            'cpf': '395.420.698-63',
            'data_nascimento': '26/01/1992',
            'data_admissao': '16/07/2025',
            'telefone': '16 99999-9999',
            'email': 'douglasaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        },
        {
            'nome': 'RANNERSON JANESON DE SANTANA SILVA',
            'cpf': '149.610.574-52',
            'data_nascimento': '18/05/2001',
            'data_admissao': '16/07/2025',
            'telefone': '16 99999-9998',
            'email': 'rannersonaltatelas@gmail.com',
            'senha': 'Alta972600$',
            'funcao': 'Ajudante de instalador de telas'
        }
    ]
    
    with app.app_context():
        sucessos = 0
        atualizacoes = 0
        erros = 0
        erros_detalhes = []
        
        print("🔄 Iniciando atualização completa do banco de dados...")
        print("=" * 60)
        
        for func_data in funcionarios_data:
            try:
                # Verificar se funcionário já existe
                funcionario_existente = Funcionario.query.filter_by(cpf=func_data['cpf']).first()
                
                # Converter datas
                data_nascimento = datetime.strptime(func_data['data_nascimento'], '%d/%m/%Y').date()
                data_admissao = datetime.strptime(func_data['data_admissao'], '%d/%m/%Y').date()
                
                if funcionario_existente:
                    # Atualizar funcionário existente
                    funcionario_existente.nome = func_data['nome']
                    funcionario_existente.funcao = func_data['funcao']
                    funcionario_existente.telefone = func_data['telefone']
                    funcionario_existente.email = func_data['email'] if func_data['email'] else None
                    funcionario_existente.data_nascimento = data_nascimento
                    funcionario_existente.data_admissao = data_admissao
                    funcionario_existente.ativo = True
                    
                    # Atualizar senha se fornecida
                    if func_data['senha']:
                        funcionario_existente.set_password(func_data['senha'])
                    
                    # Se for LUCIANO DE JESUS, marcar como afastado
                    if 'LUCIANO DE JESUS' in func_data['nome']:
                        funcionario_existente.ativo = False
                    
                    atualizacoes += 1
                    print(f"✅ Atualizado: {func_data['nome']} - {func_data['funcao']}")
                    
                else:
                    # Criar novo funcionário
                    funcionario = Funcionario(
                        nome=func_data['nome'],
                        cpf=func_data['cpf'],
                        data_nascimento=data_nascimento,
                        data_admissao=data_admissao,
                        telefone=func_data['telefone'],
                        email=func_data['email'] if func_data['email'] else None,
                        funcao=func_data['funcao'],
                        ativo=True,
                        admin=False,
                        primeiro_login=True
                    )
                    
                    # Definir senha
                    if func_data['senha']:
                        funcionario.set_password(func_data['senha'])
                    
                    # Se for LUCIANO DE JESUS, marcar como afastado
                    if 'LUCIANO DE JESUS' in func_data['nome']:
                        funcionario.ativo = False
                    
                    db.session.add(funcionario)
                    sucessos += 1
                    print(f"➕ Criado: {func_data['nome']} - {func_data['funcao']}")
                
            except Exception as e:
                erros += 1
                erro_msg = f"Erro ao processar {func_data['nome']}: {str(e)}"
                erros_detalhes.append(erro_msg)
                print(f"❌ {erro_msg}")
        
        # Commit das alterações
        try:
            db.session.commit()
            print("=" * 60)
            print("✅ ATUALIZAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!")
            print(f"📊 Resumo:")
            print(f"   ➕ Novos funcionários: {sucessos}")
            print(f"   🔄 Funcionários atualizados: {atualizacoes}")
            print(f"   ❌ Erros: {erros}")
            print(f"   📋 Total processado: {len(funcionarios_data)}")
            
            # Estatísticas por função
            print(f"\n📋 DISTRIBUIÇÃO POR FUNÇÃO:")
            funcoes = {}
            for func in funcionarios_data:
                funcao = func['funcao']
                funcoes[funcao] = funcoes.get(funcao, 0) + 1
            
            for funcao, quantidade in sorted(funcoes.items()):
                print(f"   • {funcao}: {quantidade} funcionários")
            
            if erros > 0:
                print("\n⚠️ Detalhes dos erros:")
                for erro in erros_detalhes:
                    print(f"   {erro}")
                    
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERRO ao salvar no banco: {str(e)}")
            
        print("=" * 60)

if __name__ == "__main__":
    atualizar_banco_funcionarios()
