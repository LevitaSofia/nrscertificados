"""
Sistema de Gestão de EPIs - Modelos de Banco de Dados
Desenvolvido conforme especificações detalhadas do prompt
Data: 12/07/2025
"""

from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime, timedelta


def init_db(database_instance):


    # Instância global do SQLAlchemy (será inicializada via init_db)
db = None


def init_db(database_instance):
    """
    Inicializar o módulo com a instância do SQLAlchemy do app principal.
    Deve ser chamada antes de usar os modelos.
    """
    global db
    db = database_instance


def get_db():
    """
    Retorna a instância do SQLAlchemy inicializada.
    Lança erro se não inicializada.
    """
    if db is None:
        raise RuntimeError(
            "O banco de dados EPI não foi inicializado. Chame init_db(app.db) antes de usar os modelos.")
    return db


class EPI:
    """
    Modelo para cadastro de EPIs no inventário
    Representa cada tipo de EPI disponível na empresa
    """

    @classmethod
    def __declare_last__(cls):
        global db
        if db is None:
            raise RuntimeError(
                "O banco de dados EPI não foi inicializado. Chame init_db(app.db) antes de usar os modelos.")

    __tablename__ = 'epis'
    id = property(lambda self: get_db().Column(
        get_db().Integer, primary_key=True))
    nome = property(lambda self: get_db().Column(
        get_db().String(200), nullable=False))
    descricao = property(lambda self: get_db().Column(get_db().Text))
    ca = property(lambda self: get_db().Column(
        get_db().String(20), nullable=False, unique=True))
    validade_ca = property(lambda self: get_db().Column(
        get_db().Date, nullable=False))
    fabricante = property(lambda self: get_db().Column(get_db().String(100)))
    tipo_protecao = property(lambda self: get_db().Column(get_db().String(50)))
    estoque_atual = property(
        lambda self: get_db().Column(get_db().Integer, default=0))
    estoque_minimo_alerta = property(
        lambda self: get_db().Column(get_db().Integer, default=5))
    imagem_url = property(lambda self: get_db().Column(get_db().String(255)))
    data_cadastro = property(lambda self: get_db().Column(
        get_db().DateTime, default=datetime.utcnow))
    ultima_atualizacao = property(lambda self: get_db().Column(
        get_db().DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))
    ativo = property(lambda self: get_db().Column(
        get_db().Boolean, default=True))
    entregas = property(lambda self: get_db().relationship(
        'EntregaEPI', backref='epi', lazy=True))

    def __repr__(self):
        return f'<EPI {self.nome} - CA: {self.ca}>'

    def to_dict(self):
        """Converte o objeto EPI para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ca': self.ca,
            'validade_ca': self.validade_ca.isoformat() if self.validade_ca else None,
            'fabricante': self.fabricante,
            'tipo_protecao': self.tipo_protecao,
            'estoque_atual': self.estoque_atual,
            'estoque_minimo_alerta': self.estoque_minimo_alerta,
            'imagem_url': self.imagem_url,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ativo': self.ativo
        }

    def esta_proximo_vencimento(self, dias=30):
        """Verifica se o CA está próximo do vencimento"""
        if not self.validade_ca:
            return False
        data_limite = datetime.now().date() + timedelta(days=dias)
        return self.validade_ca <= data_limite

    def esta_estoque_baixo(self):
        """Verifica se o estoque está abaixo do mínimo"""
        return self.estoque_atual <= self.estoque_minimo_alerta


class DeclaracaoEPI:
    """
    Modelo para declarações mensais de EPIs
    Cada registro representa uma declaração completa de um funcionário
    """

    @classmethod
    def __declare_last__(cls):
        global db
        if db is None:
            raise RuntimeError(
                "O banco de dados EPI não foi inicializado. Chame init_db(app.db) antes de usar os modelos.")

    __tablename__ = 'declaracoes_epi'
    id = property(lambda self: get_db().Column(
        get_db().Integer, primary_key=True))
    funcionario_id = property(lambda self: get_db().Column(
        get_db().String(50), nullable=False))
    funcionario_nome = property(lambda self: get_db().Column(
        get_db().String(200), nullable=False))
    funcionario_cargo = property(
        lambda self: get_db().Column(get_db().String(100)))
    funcionario_admissao = property(
        lambda self: get_db().Column(get_db().Date))
    data_declaracao = property(lambda self: get_db().Column(
        get_db().Date, nullable=False, default=datetime.utcnow))
    declaracao_nr06_aceita = property(
        lambda self: get_db().Column(get_db().Boolean, default=False))
    orientacao_riscos_aceita = property(
        lambda self: get_db().Column(get_db().Boolean, default=False))
    data_registro = property(lambda self: get_db().Column(
        get_db().DateTime, default=datetime.utcnow))
    ultima_atualizacao = property(lambda self: get_db().Column(
        get_db().DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))
    usuario_responsavel = property(
        lambda self: get_db().Column(get_db().String(100)))
    observacoes = property(lambda self: get_db().Column(get_db().Text))
    status = property(lambda self: get_db().Column(
        get_db().String(20), default='ativa'))
    itens = property(lambda self: get_db().relationship(
        'ItemDeclaracaoEPI', backref='declaracao', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<DeclaracaoEPI {self.funcionario_nome} - {self.data_declaracao}>'

    def to_dict(self):
        """Converte a declaração para dicionário"""
        return {
            'id': self.id,
            'funcionario_id': self.funcionario_id,
            'funcionario_nome': self.funcionario_nome,
            'funcionario_cargo': self.funcionario_cargo,
            'funcionario_admissao': self.funcionario_admissao.isoformat() if self.funcionario_admissao else None,
            'data_declaracao': self.data_declaracao.isoformat() if self.data_declaracao else None,
            'declaracao_nr06_aceita': self.declaracao_nr06_aceita,
            'orientacao_riscos_aceita': self.orientacao_riscos_aceita,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None,
            'status': self.status,
            'itens': [item.to_dict() for item in self.itens]
        }


class ItemDeclaracaoEPI:
    """
    Modelo para itens individuais de uma declaração de EPI
    Cada registro representa um EPI específico entregue ao funcionário
    """

    @classmethod
    def __declare_last__(cls):
        global db
        if db is None:
            raise RuntimeError(
                "O banco de dados EPI não foi inicializado. Chame init_db(app.db) antes de usar os modelos.")

    __tablename__ = 'itens_declaracao_epi'
    id = property(lambda self: get_db().Column(
        get_db().Integer, primary_key=True))
    declaracao_id = property(lambda self: get_db().Column(
        get_db().Integer, get_db().ForeignKey('declaracoes_epi.id'), nullable=False))
    epi_id = property(lambda self: get_db().Column(
        get_db().Integer, get_db().ForeignKey('epis.id'), nullable=False))
    epi_nome = property(lambda self: get_db().Column(
        get_db().String(200), nullable=False))
    epi_ca = property(lambda self: get_db().Column(
        get_db().String(20), nullable=False))
    epi_validade_ca = property(
        lambda self: get_db().Column(get_db().Date, nullable=False))
    rd = property(lambda self: get_db().Column(get_db().Boolean, default=True))
    data_devolucao = property(lambda self: get_db().Column(get_db().Date))
    motivo_devolucao = property(
        lambda self: get_db().Column(get_db().String(100)))
    data_entrega = property(lambda self: get_db().Column(
        get_db().Date, nullable=False, default=datetime.utcnow))
    observacoes = property(lambda self: get_db().Column(get_db().Text))

    def __repr__(self):
        return f'<ItemDeclaracaoEPI {self.epi_nome} - RD: {self.rd}>'

    def to_dict(self):
        """Converte o item para dicionário"""
        return {
            'id': self.id,
            'epi_id': self.epi_id,
            'epi_nome': self.epi_nome,
            'epi_ca': self.epi_ca,
            'epi_validade_ca': self.epi_validade_ca.isoformat() if self.epi_validade_ca else None,
            'rd': self.rd,
            'data_devolucao': self.data_devolucao.isoformat() if self.data_devolucao else None,
            'motivo_devolucao': self.motivo_devolucao,
            'data_entrega': self.data_entrega.isoformat() if self.data_entrega else None,
            'observacoes': self.observacoes
        }

    def esta_em_posse(self):
        """Verifica se o EPI ainda está em posse do funcionário"""
        return self.rd and not self.data_devolucao


class ConfiguracaoAlerta:
    """
    Modelo para configurações de alertas do sistema
    """

    @classmethod
    def __declare_last__(cls):
        global db
        if db is None:
            raise RuntimeError(
                "O banco de dados EPI não foi inicializado. Chame init_db(app.db) antes de usar os modelos.")

    __tablename__ = 'configuracoes_alertas'
    id = property(lambda self: get_db().Column(
        get_db().Integer, primary_key=True))
    tipo_alerta = property(lambda self: get_db().Column(
        get_db().String(50), nullable=False))
    dias_antecedencia = property(
        lambda self: get_db().Column(get_db().Integer, default=30))
    emails_destino = property(lambda self: get_db().Column(get_db().Text))
    ativo = property(lambda self: get_db().Column(
        get_db().Boolean, default=True))
    data_criacao = property(lambda self: get_db().Column(
        get_db().DateTime, default=datetime.utcnow))
    ultima_atualizacao = property(lambda self: get_db().Column(
        get_db().DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))
    usuario_responsavel = property(
        lambda self: get_db().Column(get_db().String(100)))

    def __repr__(self):
        return f'<ConfiguracaoAlerta {self.tipo_alerta}>'

    def get_emails_lista(self):
        """Retorna a lista de emails como array"""
        if not self.emails_destino:
            return []
        return [email.strip() for email in self.emails_destino.split(',') if email.strip()]


class LogAtividade:
    """
    Modelo para log de atividades do sistema EPI
    """

    @classmethod
    def __declare_last__(cls):
        global db
        if db is None:
            raise RuntimeError(
                "O banco de dados EPI não foi inicializado. Chame init_db(app.db) antes de usar os modelos.")

    __tablename__ = 'log_atividades_epi'
    id = property(lambda self: get_db().Column(
        get_db().Integer, primary_key=True))
    usuario = property(lambda self: get_db().Column(
        get_db().String(100), nullable=False))
    acao = property(lambda self: get_db().Column(
        get_db().String(100), nullable=False))
    descricao = property(lambda self: get_db().Column(get_db().Text))
    tabela_afetada = property(
        lambda self: get_db().Column(get_db().String(50)))
    registro_id = property(lambda self: get_db().Column(get_db().Integer))
    dados_anteriores = property(lambda self: get_db().Column(get_db().Text))
    dados_novos = property(lambda self: get_db().Column(get_db().Text))
    data_acao = property(lambda self: get_db().Column(
        get_db().DateTime, default=datetime.utcnow))
    ip_usuario = property(lambda self: get_db().Column(get_db().String(45)))
    user_agent = property(lambda self: get_db().Column(get_db().String(255)))

    def __repr__(self):
        return f'<LogAtividade {self.usuario} - {self.acao}>'

# Funções auxiliares para inicialização do banco


def criar_tabelas_epi(app):
    """
    Função para criar todas as tabelas do sistema EPI
    """
    with app.app_context():
        db.create_all()
        print("✅ Tabelas do sistema EPI criadas com sucesso!")


def inserir_dados_exemplo():
    """
    Função para inserir dados de exemplo no sistema
    """
    try:
        # Verificar se já existem dados
        if EPI.query.first():
            print("ℹ️ Dados de exemplo já existem no banco")
            return

        # EPIs de exemplo
        epis_exemplo = [
            {
                'nome': 'Óculos de Segurança Incolor',
                'descricao': 'Óculos de proteção individual com lente incolor, anti-embaçante',
                'ca': '12345',
                'validade_ca': datetime(2030, 12, 31).date(),
                'fabricante': 'VONDER',
                'tipo_protecao': 'Visual',
                'estoque_atual': 50,
                'estoque_minimo_alerta': 10
            },
            {
                'nome': 'Protetor Auricular de Inserção',
                'descricao': 'Protetor auricular de espuma para inserção no canal auditivo',
                'ca': '23456',
                'validade_ca': datetime(2029, 6, 15).date(),
                'fabricante': '3M',
                'tipo_protecao': 'Auditiva',
                'estoque_atual': 200,
                'estoque_minimo_alerta': 50
            },
            {
                'nome': 'Botina de Segurança com Bico PVC',
                'descricao': 'Botina de segurança em couro com bico de PVC e solado antiderrapante',
                'ca': '34567',
                'validade_ca': datetime(2028, 3, 20).date(),
                'fabricante': 'MARLUVAS',
                'tipo_protecao': 'Pés',
                'estoque_atual': 25,
                'estoque_minimo_alerta': 5
            },
            {
                'nome': 'Luva de Látex Nitrílico',
                'descricao': 'Luva de proteção em látex nitrílico para trabalhos gerais',
                'ca': '45678',
                'validade_ca': datetime(2027, 11, 10).date(),
                'fabricante': 'DANNY',
                'tipo_protecao': 'Mãos',
                'estoque_atual': 8,  # Estoque baixo para testar alerta
                'estoque_minimo_alerta': 20
            },
            {
                'nome': 'Capacete de Segurança Branco',
                'descricao': 'Capacete de segurança em polietileno com suspensão ajustável',
                'ca': '56789',
                # Próximo do vencimento
                'validade_ca': datetime(2025, 8, 5).date(),
                'fabricante': 'MSA',
                'tipo_protecao': 'Cabeça',
                'estoque_atual': 30,
                'estoque_minimo_alerta': 10
            }
        ]

        # Inserir EPIs
        for epi_data in epis_exemplo:
            epi = EPI(**epi_data)
            db.session.add(epi)

        # Configurações de alerta padrão
        config_vencimento = ConfiguracaoAlerta(
            tipo_alerta='vencimento_epi',
            dias_antecedencia=30,
            emails_destino='seguranca@empresa.com, rh@empresa.com',
            usuario_responsavel='sistema'
        )

        config_estoque = ConfiguracaoAlerta(
            tipo_alerta='estoque_minimo',
            dias_antecedencia=0,
            emails_destino='almoxarifado@empresa.com, compras@empresa.com',
            usuario_responsavel='sistema'
        )

        db.session.add(config_vencimento)
        db.session.add(config_estoque)

        # Confirmar as inserções
        db.session.commit()
        print("✅ Dados de exemplo inseridos com sucesso!")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao inserir dados de exemplo: {str(e)}")

# Textos fixos da NR 06 para usar no sistema


TEXTO_NR06 = """
NORMA REGULAMENTADORA Nº 06 - EQUIPAMENTOS DE PROTEÇÃO INDIVIDUAL - EPI

6.7.1 Cabe ao empregado quanto ao EPI:
a) usar, utilizando-o apenas para a finalidade a que se destina;
b) responsabilizar-se pela guarda e conservação;
c) comunicar ao empregador qualquer alteração que o torne impróprio para uso;
d) cumprir as determinações do empregador sobre o uso adequado.
"""

TEXTO_DECLARACAO_RISCOS = """
DECLARAÇÃO DE CIÊNCIA SOBRE RISCOS DA FUNÇÃO

Declaro que recebi orientação adequada sobre os riscos à segurança e à saúde 
inerentes às atividades que desempenho, bem como sobre as medidas de prevenção 
que devo adotar para evitar acidentes do trabalho ou doenças ocupacionais.

Comprometo-me a utilizar adequadamente os equipamentos de proteção individual 
fornecidos pela empresa, conforme orientações recebidas, e a comunicar 
imediatamente qualquer situação de risco identificada no ambiente de trabalho.
"""


def buscar_funcionarios_simulados():
    """
    Função que simula a busca de funcionários no sistema principal
    Em produção, esta função seria substituída por uma consulta real ao BD de funcionários
    """
    return [
        {
            'id': 'FUNC001',
            'nome': 'André Roberto dos Santos',
            'cargo': 'Supervisor de Obra',
            'admissao': '2022-02-11',
            'setor': 'Construção Civil',
            'ativo': True
        },
        {
            'id': 'FUNC002',
            'nome': 'Maria Silva Santos',
            'cargo': 'Operador de Produção',
            'admissao': '2020-05-20',
            'setor': 'Produção',
            'ativo': True
        },
        {
            'id': 'FUNC003',
            'nome': 'João Carlos Oliveira',
            'cargo': 'Técnico de Segurança',
            'admissao': '2019-08-15',
            'setor': 'Segurança do Trabalho',
            'ativo': True
        },
        {
            'id': 'FUNC004',
            'nome': 'Ana Paula Ferreira',
            'cargo': 'Auxiliar de Produção',
            'admissao': '2023-01-10',
            'setor': 'Produção',
            'ativo': True
        },
        {
            'id': 'FUNC005',
            'nome': 'Carlos Eduardo Lima',
            'cargo': 'Soldador',
            'admissao': '2021-09-30',
            'setor': 'Metalúrgica',
            'ativo': True
        }
    ]
