# -*- coding: utf-8 -*-
"""
Modelos de banco de dados para o Sistema de Gestão de EPIs
Versão corrigida para evitar problemas de inicialização
"""
from datetime import datetime, date


def create_epi_models(db):
    """Cria e retorna as classes dos modelos EPI"""

    class EPI(db.Model):
        """Modelo para cadastro de EPIs (Inventário)"""
        __tablename__ = 'epis'

        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(200), nullable=False)
        descricao = db.Column(db.Text)
        codigo_ca = db.Column(db.String(20), nullable=False, unique=True)
        data_validade_ca = db.Column(db.Date, nullable=False)
        fabricante = db.Column(db.String(100))
        # Visual, Auditiva, Respiratória, etc.
        tipo_protecao = db.Column(db.String(50))
        estoque_atual = db.Column(db.Integer, default=0)
        estoque_minimo = db.Column(db.Integer, default=0)
        imagem_url = db.Column(db.String(255))
        ativo = db.Column(db.Boolean, default=True)
        data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
        data_atualizacao = db.Column(
            db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def __repr__(self):
            return f'<EPI {self.nome} - CA: {self.codigo_ca}>'

        def to_dict(self):
            return {
                'id': self.id,
                'nome': self.nome,
                'descricao': self.descricao,
                'codigo_ca': self.codigo_ca,
                'data_validade_ca': self.data_validade_ca.isoformat() if self.data_validade_ca else None,
                'fabricante': self.fabricante,
                'tipo_protecao': self.tipo_protecao,
                'estoque_atual': self.estoque_atual,
                'estoque_minimo': self.estoque_minimo,
                'imagem_url': self.imagem_url,
                'ativo': self.ativo
            }

        @property
        def dias_para_vencimento(self):
            """Calcula quantos dias faltam para o vencimento do CA"""
            if self.data_validade_ca:
                delta = self.data_validade_ca - date.today()
                return delta.days
            return None

        @property
        def status_validade(self):
            """Retorna o status da validade do CA"""
            dias = self.dias_para_vencimento
            if dias is None:
                return 'indefinido'
            elif dias < 0:
                return 'vencido'
            elif dias <= 30:
                return 'vence_em_30_dias'
            elif dias <= 60:
                return 'vence_em_60_dias'
            else:
                return 'valido'

    class DeclaracaoEPI(db.Model):
        """Modelo para declarações de recebimento de EPI por funcionário"""
        __tablename__ = 'declaracoes_epi'

        id = db.Column(db.Integer, primary_key=True)
        funcionario_id = db.Column(db.Integer, nullable=False)
        data_declaracao = db.Column(
            db.Date, nullable=False, default=date.today)
        observacoes = db.Column(db.Text)
        assinado = db.Column(db.Boolean, default=False)
        data_assinatura = db.Column(db.DateTime)
        pdf_path = db.Column(db.String(255))
        data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f'<DeclaracaoEPI Funcionario:{self.funcionario_id} Data:{self.data_declaracao}>'

        def to_dict(self):
            return {
                'id': self.id,
                'funcionario_id': self.funcionario_id,
                'data_declaracao': self.data_declaracao.isoformat() if self.data_declaracao else None,
                'observacoes': self.observacoes,
                'assinado': self.assinado,
                'data_assinatura': self.data_assinatura.isoformat() if self.data_assinatura else None,
                'pdf_path': self.pdf_path
            }

    class EntregaEPI(db.Model):
        """Modelo para registro de entregas/devoluções de EPIs"""
        __tablename__ = 'entregas_epi'

        id = db.Column(db.Integer, primary_key=True)
        declaracao_id = db.Column(db.Integer, db.ForeignKey(
            'declaracoes_epi.id'), nullable=False)
        epi_id = db.Column(db.Integer, db.ForeignKey(
            'epis.id'), nullable=False)
        data_entrega = db.Column(db.Date, nullable=False, default=date.today)
        data_devolucao = db.Column(db.Date)
        recebido = db.Column(db.Boolean, default=True)
        quantidade = db.Column(db.Integer, default=1)
        motivo_devolucao = db.Column(db.String(100))
        observacoes = db.Column(db.Text)
        data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f'<EntregaEPI EPI:{self.epi_id} Declaracao:{self.declaracao_id}>'

        def to_dict(self):
            return {
                'id': self.id,
                'declaracao_id': self.declaracao_id,
                'epi_id': self.epi_id,
                'data_entrega': self.data_entrega.isoformat() if self.data_entrega else None,
                'data_devolucao': self.data_devolucao.isoformat() if self.data_devolucao else None,
                'recebido': self.recebido,
                'quantidade': self.quantidade,
                'motivo_devolucao': self.motivo_devolucao,
                'observacoes': self.observacoes
            }

    class AlertaEPI(db.Model):
        """Modelo para alertas automáticos do sistema de EPIs"""
        __tablename__ = 'alertas_epi'

        id = db.Column(db.Integer, primary_key=True)
        tipo_alerta = db.Column(db.String(50), nullable=False)
        titulo = db.Column(db.String(200), nullable=False)
        mensagem = db.Column(db.Text, nullable=False)
        nivel_urgencia = db.Column(db.String(20), default='medio')
        ativo = db.Column(db.Boolean, default=True)
        lido = db.Column(db.Boolean, default=False)
        data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
        data_leitura = db.Column(db.DateTime)
        referencia_id = db.Column(db.Integer)
        referencia_tipo = db.Column(db.String(50))

        def __repr__(self):
            return f'<AlertaEPI {self.tipo_alerta}: {self.titulo}>'

        def to_dict(self):
            return {
                'id': self.id,
                'tipo_alerta': self.tipo_alerta,
                'titulo': self.titulo,
                'mensagem': self.mensagem,
                'nivel_urgencia': self.nivel_urgencia,
                'ativo': self.ativo,
                'lido': self.lido,
                'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
                'data_leitura': self.data_leitura.isoformat() if self.data_leitura else None,
                'referencia_id': self.referencia_id,
                'referencia_tipo': self.referencia_tipo
            }

    class LogValidacaoCA(db.Model):
        """Modelo para log de validações de CA junto aos órgãos competentes"""
        __tablename__ = 'logs_validacao_ca'

        id = db.Column(db.Integer, primary_key=True)
        epi_id = db.Column(db.Integer, db.ForeignKey(
            'epis.id'), nullable=False)
        codigo_ca = db.Column(db.String(20), nullable=False)
        data_validacao = db.Column(db.DateTime, default=datetime.utcnow)
        resultado_validacao = db.Column(db.String(20))
        dados_resposta = db.Column(db.Text)
        url_consulta = db.Column(db.String(500))
        observacoes = db.Column(db.Text)

        def __repr__(self):
            return f'<LogValidacaoCA CA:{self.codigo_ca} Resultado:{self.resultado_validacao}>'

    class ConfiguracaoEPI(db.Model):
        """Modelo para configurações do sistema de EPIs"""
        __tablename__ = 'configuracoes_epi'

        id = db.Column(db.Integer, primary_key=True)
        chave = db.Column(db.String(100), nullable=False, unique=True)
        valor = db.Column(db.Text, nullable=False)
        descricao = db.Column(db.String(255))
        tipo_dado = db.Column(db.String(20), default='string')
        data_atualizacao = db.Column(
            db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def __repr__(self):
            return f'<ConfiguracaoEPI {self.chave}: {self.valor}>'

        def to_dict(self):
            return {
                'id': self.id,
                'chave': self.chave,
                'valor': self.valor,
                'descricao': self.descricao,
                'tipo_dado': self.tipo_dado
            }

    # Retornar todas as classes criadas
    return {
        'EPI': EPI,
        'DeclaracaoEPI': DeclaracaoEPI,
        'EntregaEPI': EntregaEPI,
        'AlertaEPI': AlertaEPI,
        'LogValidacaoCA': LogValidacaoCA,
        'ConfiguracaoEPI': ConfiguracaoEPI
    }
