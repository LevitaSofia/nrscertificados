# -*- coding: utf-8 -*-
"""
Rotas para o Sistema de Gestão de EPIs
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
from flask import current_app, session
from datetime import datetime, date, timedelta
import json
import os
from werkzeug.utils import secure_filename
import requests
from sqlalchemy import and_, or_
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import io

# Importar modelos (assumindo que estão no app principal)
# from models_epi import EPI, DeclaracaoEPI, EntregaEPI, AlertaEPI, LogValidacaoCA
# from app import db

# Blueprint para EPIs
epi_bp = Blueprint('epi', __name__, url_prefix='/epi')

# Tipos de proteção disponíveis
TIPOS_PROTECAO = [
    'Proteção Visual',
    'Proteção Auditiva', 
    'Proteção Respiratória',
    'Proteção das Mãos',
    'Proteção dos Pés',
    'Proteção da Cabeça',
    'Proteção do Corpo',
    'Proteção contra Quedas',
    'Outros'
]

# ================== ROTAS DO MÓDULO DE CADASTRO DE EPIs ==================

@epi_bp.route('/')
def index():
    """Página principal do módulo de EPIs"""
    return render_template('epi/index.html')

@epi_bp.route('/cadastro')
def cadastro_epi():
    """Página de cadastro de EPIs"""
    epis = EPI.query.filter_by(ativo=True).all()
    return render_template('epi/cadastro_epi.html', epis=epis, tipos_protecao=TIPOS_PROTECAO)

@epi_bp.route('/cadastro/novo', methods=['GET', 'POST'])
def novo_epi():
    """Cadastrar novo EPI"""
    if request.method == 'POST':
        try:
            # Validar se CA já existe
            ca_existente = EPI.query.filter_by(codigo_ca=request.form['codigo_ca']).first()
            if ca_existente:
                flash('Código CA já cadastrado!', 'error')
                return redirect(url_for('epi.novo_epi'))
            
            # Processar upload de imagem
            imagem_url = None
            if 'imagem' in request.files:
                file = request.files['imagem']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    # Criar diretório se não existir
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'epis')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Salvar arquivo
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    imagem_url = f'/static/uploads/epis/{filename}'
            
            # Criar novo EPI
            novo_epi = EPI(
                nome=request.form['nome'],
                descricao=request.form.get('descricao', ''),
                codigo_ca=request.form['codigo_ca'],
                data_validade_ca=datetime.strptime(request.form['data_validade_ca'], '%Y-%m-%d').date(),
                fabricante=request.form.get('fabricante', ''),
                tipo_protecao=request.form.get('tipo_protecao', ''),
                estoque_atual=int(request.form.get('estoque_atual', 0)),
                estoque_minimo=int(request.form.get('estoque_minimo', 0)),
                imagem_url=imagem_url
            )
            
            db.session.add(novo_epi)
            db.session.commit()
            
            flash('EPI cadastrado com sucesso!', 'success')
            return redirect(url_for('epi.cadastro_epi'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar EPI: {str(e)}', 'error')
            return redirect(url_for('epi.novo_epi'))
    
    return render_template('epi/novo_epi.html', tipos_protecao=TIPOS_PROTECAO)

@epi_bp.route('/cadastro/editar/<int:epi_id>', methods=['GET', 'POST'])
def editar_epi(epi_id):
    """Editar EPI existente"""
    epi = EPI.query.get_or_404(epi_id)
    
    if request.method == 'POST':
        try:
            # Validar se CA já existe (exceto o atual)
            ca_existente = EPI.query.filter(
                and_(EPI.codigo_ca == request.form['codigo_ca'], EPI.id != epi_id)
            ).first()
            if ca_existente:
                flash('Código CA já cadastrado para outro EPI!', 'error')
                return redirect(url_for('epi.editar_epi', epi_id=epi_id))
            
            # Processar upload de nova imagem
            if 'imagem' in request.files:
                file = request.files['imagem']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'epis')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    epi.imagem_url = f'/static/uploads/epis/{filename}'
            
            # Atualizar dados
            epi.nome = request.form['nome']
            epi.descricao = request.form.get('descricao', '')
            epi.codigo_ca = request.form['codigo_ca']
            epi.data_validade_ca = datetime.strptime(request.form['data_validade_ca'], '%Y-%m-%d').date()
            epi.fabricante = request.form.get('fabricante', '')
            epi.tipo_protecao = request.form.get('tipo_protecao', '')
            epi.estoque_atual = int(request.form.get('estoque_atual', 0))
            epi.estoque_minimo = int(request.form.get('estoque_minimo', 0))
            epi.data_atualizacao = datetime.utcnow()
            
            db.session.commit()
            
            flash('EPI atualizado com sucesso!', 'success')
            return redirect(url_for('epi.cadastro_epi'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar EPI: {str(e)}', 'error')
    
    return render_template('epi/editar_epi.html', epi=epi, tipos_protecao=TIPOS_PROTECAO)

@epi_bp.route('/cadastro/excluir/<int:epi_id>', methods=['POST'])
def excluir_epi(epi_id):
    """Excluir (desativar) EPI"""
    try:
        epi = EPI.query.get_or_404(epi_id)
        
        # Verificar se há entregas ativas
        entregas_ativas = db.session.query(EntregaEPI).join(DeclaracaoEPI).filter(
            and_(EntregaEPI.epi_id == epi_id, EntregaEPI.data_devolucao.is_(None))
        ).count()
        
        if entregas_ativas > 0:
            flash('Não é possível excluir EPI que possui entregas ativas!', 'error')
        else:
            epi.ativo = False
            epi.data_atualizacao = datetime.utcnow()
            db.session.commit()
            flash('EPI excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir EPI: {str(e)}', 'error')
    
    return redirect(url_for('epi.cadastro_epi'))

@epi_bp.route('/api/epis')
def api_epis():
    """API para listar EPIs (para busca/filtro)"""
    try:
        query = EPI.query.filter_by(ativo=True)
        
        # Filtros
        if request.args.get('busca'):
            busca = f"%{request.args.get('busca')}%"
            query = query.filter(
                or_(EPI.nome.ilike(busca), EPI.codigo_ca.ilike(busca), EPI.fabricante.ilike(busca))
            )
        
        if request.args.get('tipo_protecao'):
            query = query.filter_by(tipo_protecao=request.args.get('tipo_protecao'))
        
        # Ordenação
        query = query.order_by(EPI.nome)
        
        epis = query.all()
        return jsonify([epi.to_dict() for epi in epis])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@epi_bp.route('/api/validar-ca/<codigo_ca>')
def validar_ca(codigo_ca):
    """Validar CA via API externa"""
    try:
        # Aqui seria implementada a integração com API do MTE
        # Por enquanto, retorna uma simulação
        
        # URL da API do MTE (exemplo - verificar se existe)
        # api_url = f"https://sit.trabalho.gov.br/api/ca/{codigo_ca}"
        
        # Simulação de resposta da API
        response_data = {
            'codigo_ca': codigo_ca,
            'valido': True,
            'data_validade': '2025-12-31',
            'situacao': 'Ativo',
            'fabricante': 'Fabricante Exemplo',
            'descricao': 'Descrição do EPI'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e), 'valido': False}), 500

# ================== ROTAS DO MÓDULO DE GESTÃO DE ENTREGAS ==================

@epi_bp.route('/entregas')
def gestao_entregas():
    """Página principal de gestão de entregas"""
    # Buscar funcionários (assumindo que há uma tabela de funcionários)
    # funcionarios = Funcionario.query.filter_by(ativo=True).all()
    
    declaracoes_recentes = DeclaracaoEPI.query.order_by(DeclaracaoEPI.data_declaracao.desc()).limit(10).all()
    
    return render_template('epi/gestao_entregas.html', 
                         declaracoes_recentes=declaracoes_recentes)

@epi_bp.route('/entregas/nova/<int:funcionario_id>')
def nova_entrega(funcionario_id):
    """Criar nova declaração de entrega para funcionário"""
    # funcionario = Funcionario.query.get_or_404(funcionario_id)
    epis_disponiveis = EPI.query.filter_by(ativo=True).all()
    
    # Buscar última declaração do funcionário para mostrar EPIs atuais
    ultima_declaracao = DeclaracaoEPI.query.filter_by(funcionario_id=funcionario_id)\
                                          .order_by(DeclaracaoEPI.data_declaracao.desc())\
                                          .first()
    
    epis_atuais = []
    if ultima_declaracao:
        epis_atuais = db.session.query(EntregaEPI).filter(
            and_(EntregaEPI.declaracao_id == ultima_declaracao.id,
                 EntregaEPI.data_devolucao.is_(None))
        ).all()
    
    return render_template('epi/nova_entrega.html',
                         funcionario_id=funcionario_id,
                         epis_disponiveis=epis_disponiveis,
                         epis_atuais=epis_atuais)

@epi_bp.route('/entregas/salvar', methods=['POST'])
def salvar_entrega():
    """Salvar nova declaração de entrega"""
    try:
        data = request.get_json()
        
        # Criar nova declaração
        declaracao = DeclaracaoEPI(
            funcionario_id=data['funcionario_id'],
            data_declaracao=datetime.strptime(data['data_declaracao'], '%Y-%m-%d').date(),
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(declaracao)
        db.session.flush()  # Para obter o ID
        
        # Processar entregas/devoluções
        for item in data['epis']:
            if item['acao'] == 'entregar':
                entrega = EntregaEPI(
                    declaracao_id=declaracao.id,
                    epi_id=item['epi_id'],
                    data_entrega=declaracao.data_declaracao,
                    quantidade=item.get('quantidade', 1),
                    recebido=True,
                    observacoes=item.get('observacoes', '')
                )
                db.session.add(entrega)
                
                # Atualizar estoque
                epi = EPI.query.get(item['epi_id'])
                if epi:
                    epi.estoque_atual = max(0, epi.estoque_atual - item.get('quantidade', 1))
            
            elif item['acao'] == 'devolver':
                # Marcar devolução na entrega existente
                entrega_existente = EntregaEPI.query.get(item['entrega_id'])
                if entrega_existente:
                    entrega_existente.data_devolucao = declaracao.data_declaracao
                    entrega_existente.motivo_devolucao = item.get('motivo_devolucao', '')
                    
                    # Devolver ao estoque
                    epi = EPI.query.get(entrega_existente.epi_id)
                    if epi:
                        epi.estoque_atual += entrega_existente.quantidade
        
        db.session.commit()
        
        return jsonify({'success': True, 'declaracao_id': declaracao.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@epi_bp.route('/entregas/historico/<int:funcionario_id>')
def historico_funcionario(funcionario_id):
    """Histórico de EPIs de um funcionário"""
    declaracoes = DeclaracaoEPI.query.filter_by(funcionario_id=funcionario_id)\
                                    .order_by(DeclaracaoEPI.data_declaracao.desc())\
                                    .all()
    
    return render_template('epi/historico_funcionario.html',
                         funcionario_id=funcionario_id,
                         declaracoes=declaracoes)

# ================== ROTAS DE GERAÇÃO DE PDF ==================

@epi_bp.route('/entregas/pdf/<int:declaracao_id>')
def gerar_pdf_declaracao(declaracao_id):
    """Gerar PDF da declaração de recebimento"""
    try:
        declaracao = DeclaracaoEPI.query.get_or_404(declaracao_id)
        entregas = EntregaEPI.query.filter_by(declaracao_id=declaracao_id).all()
        
        # funcionario = Funcionario.query.get(declaracao.funcionario_id)
        
        # Criar PDF em memória
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.red,
            alignment=1  # Center
        )
        
        # Cabeçalho
        story.append(Paragraph("ALTA TELAS REDES DE PROTEÇÃO - LTDA", title_style))
        story.append(Paragraph("DECLARAÇÃO DE RECEBIMENTO DE EPI", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Dados do funcionário
        # funcionario_data = [
        #     ['Nome:', funcionario.nome if funcionario else 'N/A'],
        #     ['Cargo:', funcionario.cargo if funcionario else 'N/A'],
        #     ['Data:', declaracao.data_declaracao.strftime('%d/%m/%Y')]
        # ]
        
        # Tabela de EPIs
        epi_data = [['DATA', 'RD', 'DESCRIÇÃO DO EPI', 'CA', 'VALIDADE', 'DATA DEVOLUÇÃO']]
        
        for entrega in entregas:
            epi_data.append([
                entrega.data_entrega.strftime('%d/%m/%Y'),
                'X' if entrega.recebido else '',
                entrega.epi.nome,
                entrega.epi.codigo_ca,
                entrega.epi.data_validade_ca.strftime('%d/%m/%Y'),
                entrega.data_devolucao.strftime('%d/%m/%Y') if entrega.data_devolucao else ''
            ])
        
        epi_table = Table(epi_data)
        epi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(epi_table)
        story.append(Spacer(1, 30))
        
        # Declaração NR-06
        nr06_text = """
        Declaro que recebi os Equipamentos de Proteção Individual relacionados acima, comprometendo-me a:
        a) Usar apenas para a finalidade a que se destina;
        b) Responsabilizar-me pela guarda e conservação;
        c) Comunicar ao empregador qualquer alteração que o torne impróprio para uso;
        d) Cumprir as determinações do empregador sobre o uso adequado.
        """
        
        story.append(Paragraph(nr06_text, styles['Normal']))
        story.append(Spacer(1, 50))
        
        # Linha de assinatura
        story.append(Paragraph("_" * 50, styles['Normal']))
        story.append(Paragraph("Assinatura do Colaborador", styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'declaracao_epi_{declaracao_id}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'error')
        return redirect(url_for('epi.gestao_entregas'))

# ================== ROTAS DE RELATÓRIOS E ALERTAS ==================

@epi_bp.route('/relatorios')
def relatorios():
    """Página de relatórios"""
    return render_template('epi/relatorios.html')

@epi_bp.route('/relatorios/validades')
def relatorio_validades():
    """Relatório de validades de EPIs"""
    periodo = request.args.get('periodo', '30')  # dias
    
    data_limite = date.today() + timedelta(days=int(periodo))
    
    epis_vencendo = EPI.query.filter(
        and_(EPI.ativo == True, EPI.data_validade_ca <= data_limite)
    ).order_by(EPI.data_validade_ca).all()
    
    return render_template('epi/relatorio_validades.html',
                         epis_vencendo=epis_vencendo,
                         periodo=periodo)

@epi_bp.route('/relatorios/estoque')
def relatorio_estoque():
    """Relatório de estoque de EPIs"""
    epis_estoque_baixo = EPI.query.filter(
        and_(EPI.ativo == True, EPI.estoque_atual <= EPI.estoque_minimo)
    ).order_by(EPI.estoque_atual).all()
    
    return render_template('epi/relatorio_estoque.html',
                         epis_estoque_baixo=epis_estoque_baixo)

@epi_bp.route('/configuracoes')
def configuracoes():
    """Página de configurações de alertas"""
    alertas = AlertaEPI.query.all()
    return render_template('epi/configuracoes.html', alertas=alertas)

@epi_bp.route('/configuracoes/salvar', methods=['POST'])
def salvar_configuracoes():
    """Salvar configurações de alertas"""
    try:
        data = request.get_json()
        
        for config in data['alertas']:
            if config.get('id'):
                # Atualizar existente
                alerta = AlertaEPI.query.get(config['id'])
                if alerta:
                    alerta.dias_antecedencia = config.get('dias_antecedencia')
                    alerta.ativo = config.get('ativo', False)
                    alerta.emails_destino = json.dumps(config.get('emails', []))
                    alerta.data_atualizacao = datetime.utcnow()
            else:
                # Criar novo
                alerta = AlertaEPI(
                    tipo=config['tipo'],
                    dias_antecedencia=config.get('dias_antecedencia'),
                    ativo=config.get('ativo', False),
                    emails_destino=json.dumps(config.get('emails', []))
                )
                db.session.add(alerta)
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
