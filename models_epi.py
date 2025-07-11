# -*- coding: utf-8 -*-
"""
Modelos de banco de dados para o Sistema de Gestão de EPIs
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

# Assumindo que db já está definido no app principal
# from app import db

class EPI(db.Model):
    """Modelo para cadastro de EPIs (Inventário)"""
    __tablename__ = 'epis'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    codigo_ca = db.Column(db.String(20), nullable=False, unique=True)
    data_validade_ca = db.Column(db.Date, nullable=False)
    fabricante = db.Column(db.String(100))
    tipo_protecao = db.Column(db.String(50))  # Visual, Auditiva, Respiratória, etc.
    estoque_atual = db.Column(db.Integer, default=0)
    estoque_minimo = db.Column(db.Integer, default=0)
    imagem_url = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    entregas = relationship("EntregaEPI", back_populates="epi")
    
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
    funcionario_id = db.Column(db.Integer, nullable=False)  # Referência ao ID do funcionário
    data_declaracao = db.Column(db.Date, nullable=False, default=date.today)
    observacoes = db.Column(db.Text)
    assinado = db.Column(db.Boolean, default=False)
    data_assinatura = db.Column(db.DateTime)
    pdf_path = db.Column(db.String(255))  # Caminho para o PDF gerado
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    entregas = relationship("EntregaEPI", back_populates="declaracao")
    
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
    declaracao_id = db.Column(db.Integer, ForeignKey('declaracoes_epi.id'), nullable=False)
    epi_id = db.Column(db.Integer, ForeignKey('epis.id'), nullable=False)
    data_entrega = db.Column(db.Date, nullable=False, default=date.today)
    data_devolucao = db.Column(db.Date)
    recebido = db.Column(db.Boolean, default=True)  # Campo RD
    quantidade = db.Column(db.Integer, default=1)
    motivo_devolucao = db.Column(db.String(100))  # Danificado, Vencido, Substituição, etc.
    observacoes = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    declaracao = relationship("DeclaracaoEPI", back_populates="entregas")
    epi = relationship("EPI", back_populates="entregas")
    
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
    
    @property
    def status(self):
        """Retorna o status da entrega"""
        if self.data_devolucao:
            return 'devolvido'
        elif self.recebido:
            return 'em_posse'
        else:
            return 'pendente'


class AlertaEPI(db.Model):
    """Modelo para configuração de alertas"""
    __tablename__ = 'alertas_epi'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # 'validade_ca', 'estoque_minimo'
    dias_antecedencia = db.Column(db.Integer)  # Para alertas de validade
    ativo = db.Column(db.Boolean, default=True)
    emails_destino = db.Column(db.Text)  # JSON com lista de emails
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AlertaEPI {self.tipo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'dias_antecedencia': self.dias_antecedencia,
            'ativo': self.ativo,
            'emails_destino': self.emails_destino
        }


class LogValidacaoCA(db.Model):
    """Modelo para log de validações de CA via API"""
    __tablename__ = 'log_validacao_ca'
    
    id = db.Column(db.Integer, primary_key=True)
    epi_id = db.Column(db.Integer, ForeignKey('epis.id'), nullable=False)
    codigo_ca = db.Column(db.String(20), nullable=False)
    status_anterior = db.Column(db.String(20))
    status_atual = db.Column(db.String(20))
    data_validade_anterior = db.Column(db.Date)
    data_validade_atual = db.Column(db.Date)
    resposta_api = db.Column(db.Text)  # JSON da resposta da API
    sucesso = db.Column(db.Boolean, default=False)
    data_validacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    epi = relationship("EPI")
    
    def __repr__(self):
        return f'<LogValidacaoCA CA:{self.codigo_ca} Data:{self.data_validacao}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'epi_id': self.epi_id,
            'codigo_ca': self.codigo_ca,
            'status_anterior': self.status_anterior,
            'status_atual': self.status_atual,
            'data_validade_anterior': self.data_validade_anterior.isoformat() if self.data_validade_anterior else None,
            'data_validade_atual': self.data_validade_atual.isoformat() if self.data_validade_atual else None,
            'sucesso': self.sucesso,
            'data_validacao': self.data_validacao.isoformat() if self.data_validacao else None
        }
