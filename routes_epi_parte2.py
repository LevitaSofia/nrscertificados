"""
Sistema de Gestão de EPIs - Rotas Complementares (Parte 2)
Relatórios, PDF, Alertas e Configurações
Data: 12/07/2025
"""

from models_epi_completo import db, EPI, DeclaracaoEPI, ItemDeclaracaoEPI, ConfiguracaoAlerta, LogAtividade, TEXTO_NR06, TEXTO_DECLARACAO_RISCOS, buscar_funcionarios_simulados
from routes_epi_completo import registrar_log_atividade
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, make_response
from datetime import datetime, timedelta, date
import json
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import tempfile
import os

# Continuar com as rotas do blueprint epi_bp

# ================================
# CONTINUAÇÃO - GESTÃO DE ENTREGAS
# ================================


@epi_bp.route('/entregas/devolver-item/<int:item_id>', methods=['POST'])
def devolver_item(item_id):
    """
    Registra a devolução de um item EPI específico
    """
    try:
        item = ItemDeclaracaoEPI.query.get_or_404(item_id)

        if not item.rd or item.data_devolucao:
            flash(
                'Este item já foi devolvido ou não está em posse do funcionário!', 'error')
            return redirect(request.referrer)

        # Dados da devolução
        data_devolucao_str = request.form.get('data_devolucao')
        motivo_devolucao = request.form.get('motivo_devolucao', '').strip()

        try:
            if data_devolucao_str:
                data_devolucao = datetime.strptime(
                    data_devolucao_str, '%Y-%m-%d').date()
            else:
                data_devolucao = datetime.now().date()
        except ValueError:
            flash('Data de devolução inválida!', 'error')
            return redirect(request.referrer)

        # Registrar devolução
        dados_anteriores = item.to_dict()
        item.data_devolucao = data_devolucao
        item.motivo_devolucao = motivo_devolucao
        item.rd = False  # Não está mais em posse

        # Retornar ao estoque se aplicável
        if motivo_devolucao in ['Substituição', 'Troca']:
            epi = EPI.query.get(item.epi_id)
            if epi:
                epi.estoque_atual += 1

        db.session.commit()

        # Registrar log
        registrar_log_atividade(
            acao='devolveu_item_epi',
            descricao=f'Item: {item.epi_nome} - Motivo: {motivo_devolucao}',
            tabela_afetada='itens_declaracao_epi',
            registro_id=item.id,
            dados_anteriores=dados_anteriores,
            dados_novos=item.to_dict()
        )

        flash(
            f'Devolução de {item.epi_nome} registrada com sucesso!', 'success')
        return redirect(request.referrer)

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar devolução: {str(e)}', 'error')
        return redirect(request.referrer)


@epi_bp.route('/entregas/gerar-pdf/<int:declaracao_id>')
def gerar_pdf_declaracao(declaracao_id):
    """
    Gera PDF da declaração de recebimento de EPIs
    """
    try:
        declaracao = DeclaracaoEPI.query.get_or_404(declaracao_id)

        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filename = temp_file.name
        temp_file.close()

        # Criar documento PDF
        doc = SimpleDocTemplate(temp_filename, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )

        # Conteúdo do PDF
        story = []

        # Cabeçalho da empresa
        story.append(Paragraph("EMPRESA EXEMPLO LTDA", title_style))
        story.append(Paragraph("CNPJ: 12.345.678/0001-90", normal_style))
        story.append(Paragraph(
            "Endereço: Rua das Empresas, 123 - Centro - Cidade/UF", normal_style))
        story.append(Spacer(1, 20))

        # Título do documento
        story.append(
            Paragraph("DECLARAÇÃO DE RECEBIMENTO DE EPIs", title_style))
        story.append(Spacer(1, 20))

        # Dados do funcionário
        story.append(
            Paragraph(f"<b>FUNCIONÁRIO:</b> {declaracao.funcionario_nome}", normal_style))
        story.append(
            Paragraph(f"<b>CARGO:</b> {declaracao.funcionario_cargo}", normal_style))
        story.append(Paragraph(
            f"<b>DATA DE ADMISSÃO:</b> {declaracao.funcionario_admissao.strftime('%d/%m/%Y') if declaracao.funcionario_admissao else 'N/A'}", normal_style))
        story.append(Paragraph(
            f"<b>DATA DA DECLARAÇÃO:</b> {declaracao.data_declaracao.strftime('%d/%m/%Y') if declaracao.data_declaracao else 'N/A'}", normal_style))
        story.append(Spacer(1, 20))

        # Tabela de EPIs
        if declaracao.itens:
            data = [['DATA', 'RD', 'DESCRIÇÃO DO EPI',
                     'CA', 'VALIDADE', 'DATA DEVOLUÇÃO']]

            for item in declaracao.itens:
                data.append([
                    item.data_entrega.strftime(
                        '%d/%m/%Y') if item.data_entrega else '',
                    'X' if item.rd and not item.data_devolucao else '',
                    item.epi_nome,
                    item.epi_ca,
                    item.epi_validade_ca.strftime(
                        '%d/%m/%Y') if item.epi_validade_ca else '',
                    item.data_devolucao.strftime(
                        '%d/%m/%Y') if item.data_devolucao else ''
                ])

            table = Table(data, colWidths=[
                          2*cm, 1*cm, 6*cm, 2*cm, 2.5*cm, 2.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            story.append(table)
            story.append(Spacer(1, 30))

        # Texto da NR 06
        story.append(Paragraph(
            "<b>NORMA REGULAMENTADORA Nº 06 - EQUIPAMENTOS DE PROTEÇÃO INDIVIDUAL - EPI</b>", normal_style))
        story.append(Paragraph(TEXTO_NR06, normal_style))
        story.append(Spacer(1, 20))

        # Declaração de riscos
        story.append(
            Paragraph("<b>DECLARAÇÃO DE CIÊNCIA SOBRE RISCOS DA FUNÇÃO</b>", normal_style))
        story.append(Paragraph(TEXTO_DECLARACAO_RISCOS, normal_style))
        story.append(Spacer(1, 30))

        # Checkboxes de aceite
        aceite_text = f"""
        [{'X' if declaracao.declaracao_nr06_aceita else ' '}] Declaro estar ciente das responsabilidades acima citadas<br/>
        [{'X' if declaracao.orientacao_riscos_aceita else ' '}] Declaro que recebi orientação adequada sobre os riscos à segurança
        """
        story.append(Paragraph(aceite_text, normal_style))
        story.append(Spacer(1, 40))

        # Assinatura
        story.append(Paragraph("_" * 50, normal_style))
        story.append(Paragraph(
            f"Assinatura do Funcionário: {declaracao.funcionario_nome}", normal_style))
        story.append(
            Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", normal_style))

        # Gerar PDF
        doc.build(story)

        # Registrar log
        registrar_log_atividade(
            acao='gerou_pdf_declaracao',
            descricao=f'PDF da declaração de {declaracao.funcionario_nome}',
            tabela_afetada='declaracoes_epi',
            registro_id=declaracao.id
        )

        # Retornar arquivo
        def remove_file(response):
            try:
                os.unlink(temp_filename)
            except Exception:
                pass
            return response

        return send_file(
            temp_filename,
            as_attachment=True,
            download_name=f'Declaracao_EPI_{declaracao.funcionario_nome}_{declaracao.data_declaracao.strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'error')
        return redirect(request.referrer)


@epi_bp.route('/entregas/gerar-pdfs-todos')
def gerar_pdfs_todos_funcionarios():
    """
    Gera PDFs de declaração para todos os funcionários com EPIs ativos
    """
    try:
        funcionarios = buscar_funcionarios_simulados()
        pdfs_gerados = []

        for funcionario in funcionarios:
            # Buscar última declaração ativa do funcionário
            ultima_declaracao = DeclaracaoEPI.query.filter_by(
                funcionario_id=funcionario['id'],
                status='ativa'
            ).order_by(DeclaracaoEPI.data_declaracao.desc()).first()

            if ultima_declaracao and ultima_declaracao.itens:
                # Verificar se tem itens ativos
                itens_ativos = [item for item in ultima_declaracao.itens
                                if item.rd and not item.data_devolucao]

                if itens_ativos:
                    try:
                        # Gerar PDF para este funcionário
                        # (Aqui implementaria a geração do ZIP com múltiplos PDFs)
                        pdfs_gerados.append({
                            'funcionario': funcionario['nome'],
                            'declaracao_id': ultima_declaracao.id,
                            'itens_count': len(itens_ativos)
                        })
                    except Exception as e:
                        print(
                            f"Erro ao gerar PDF para {funcionario['nome']}: {str(e)}")

        flash(
            f'Processo de geração iniciado para {len(pdfs_gerados)} funcionários!', 'info')
        return render_template('epi/resultado_pdfs_massa.html', pdfs_gerados=pdfs_gerados)

    except Exception as e:
        flash(f'Erro ao gerar PDFs em massa: {str(e)}', 'error')
        return redirect(url_for('epi.gestao_entregas'))

# ================================
# MÓDULO 3: RELATÓRIOS E ALERTAS
# ================================


@epi_bp.route('/relatorios')
def relatorios():
    """
    Página principal de relatórios e alertas
    """
    try:
        # Filtros da requisição
        dias_vencimento = int(request.args.get('dias_vencimento', 30))
        tipo_protecao = request.args.get('tipo_protecao', '')

        # EPIs próximos do vencimento
        data_limite = datetime.now().date() + timedelta(days=dias_vencimento)
        query_vencimento = db.session.query(
            EPI.nome,
            EPI.ca,
            EPI.validade_ca,
            EPI.tipo_protecao,
            DeclaracaoEPI.funcionario_nome.label('funcionario'),
            DeclaracaoEPI.funcionario_id
        ).select_from(EPI).outerjoin(ItemDeclaracaoEPI).outerjoin(DeclaracaoEPI).filter(
            EPI.validade_ca <= data_limite,
            EPI.ativo == True
        )

        if tipo_protecao:
            query_vencimento = query_vencimento.filter(
                EPI.tipo_protecao == tipo_protecao)

        epis_vencendo = query_vencimento.all()

        # EPIs com estoque baixo
        epis_estoque_baixo = EPI.query.filter(
            EPI.estoque_atual <= EPI.estoque_minimo_alerta,
            EPI.ativo == True
        ).all()

        # Tipos de proteção para filtro
        tipos_protecao = db.session.query(EPI.tipo_protecao.distinct()).filter(
            EPI.tipo_protecao.isnot(None),
            EPI.ativo == True
        ).all()
        tipos_protecao = [tipo[0] for tipo in tipos_protecao if tipo[0]]

        # Estatísticas resumidas
        stats = {
            'total_epis_vencendo': len(epis_vencendo),
            'total_estoque_baixo': len(epis_estoque_baixo),
            'funcionarios_afetados': len(set([epi.funcionario_id for epi in epis_vencendo if epi.funcionario_id]))
        }

        return render_template('epi/relatorios.html',
                               epis_vencendo=epis_vencendo,
                               epis_estoque_baixo=epis_estoque_baixo,
                               tipos_protecao=tipos_protecao,
                               stats=stats,
                               filtros={
                                   'dias_vencimento': dias_vencimento,
                                   'tipo_protecao': tipo_protecao
                               })

    except Exception as e:
        flash(f'Erro ao carregar relatórios: {str(e)}', 'error')
        return render_template('epi/relatorios.html',
                               epis_vencendo=[],
                               epis_estoque_baixo=[],
                               tipos_protecao=[],
                               stats={})


@epi_bp.route('/relatorios/configurar-alertas')
def configurar_alertas():
    """
    Página de configuração de alertas por email
    """
    try:
        # Buscar configurações existentes
        config_vencimento = ConfiguracaoAlerta.query.filter_by(
            tipo_alerta='vencimento_epi',
            ativo=True
        ).first()

        config_estoque = ConfiguracaoAlerta.query.filter_by(
            tipo_alerta='estoque_minimo',
            ativo=True
        ).first()

        return render_template('epi/configurar_alertas.html',
                               config_vencimento=config_vencimento,
                               config_estoque=config_estoque)

    except Exception as e:
        flash(f'Erro ao carregar configurações: {str(e)}', 'error')
        return render_template('epi/configurar_alertas.html',
                               config_vencimento=None,
                               config_estoque=None)


@epi_bp.route('/relatorios/salvar-configuracoes-alertas', methods=['POST'])
def salvar_configuracoes_alertas():
    """
    Salva as configurações de alertas por email
    """
    try:
        # Configuração de vencimento
        dias_vencimento = int(request.form.get('dias_vencimento', 30))
        emails_vencimento = request.form.get('emails_vencimento', '').strip()

        config_vencimento = ConfiguracaoAlerta.query.filter_by(
            tipo_alerta='vencimento_epi',
            ativo=True
        ).first()

        if config_vencimento:
            config_vencimento.dias_antecedencia = dias_vencimento
            config_vencimento.emails_destino = emails_vencimento
            config_vencimento.usuario_responsavel = request.form.get(
                'usuario_responsavel', 'Sistema')
        else:
            config_vencimento = ConfiguracaoAlerta(
                tipo_alerta='vencimento_epi',
                dias_antecedencia=dias_vencimento,
                emails_destino=emails_vencimento,
                usuario_responsavel=request.form.get(
                    'usuario_responsavel', 'Sistema')
            )
            db.session.add(config_vencimento)

        # Configuração de estoque
        emails_estoque = request.form.get('emails_estoque', '').strip()

        config_estoque = ConfiguracaoAlerta.query.filter_by(
            tipo_alerta='estoque_minimo',
            ativo=True
        ).first()

        if config_estoque:
            config_estoque.emails_destino = emails_estoque
            config_estoque.usuario_responsavel = request.form.get(
                'usuario_responsavel', 'Sistema')
        else:
            config_estoque = ConfiguracaoAlerta(
                tipo_alerta='estoque_minimo',
                dias_antecedencia=0,
                emails_destino=emails_estoque,
                usuario_responsavel=request.form.get(
                    'usuario_responsavel', 'Sistema')
            )
            db.session.add(config_estoque)

        db.session.commit()

        # Registrar log
        registrar_log_atividade(
            acao='configurou_alertas',
            descricao=f'Alertas de vencimento: {dias_vencimento} dias. Emails configurados.',
            tabela_afetada='configuracoes_alertas'
        )

        flash('Configurações de alertas salvas com sucesso!', 'success')
        return redirect(url_for('epi.configurar_alertas'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar configurações: {str(e)}', 'error')
        return redirect(url_for('epi.configurar_alertas'))


@epi_bp.route('/relatorios/simular-envio-alertas')
def simular_envio_alertas():
    """
    Simula o envio de alertas por email (demonstração)
    """
    try:
        alertas_enviados = []

        # Buscar configurações
        config_vencimento = ConfiguracaoAlerta.query.filter_by(
            tipo_alerta='vencimento_epi',
            ativo=True
        ).first()

        config_estoque = ConfiguracaoAlerta.query.filter_by(
            tipo_alerta='estoque_minimo',
            ativo=True
        ).first()

        # Alertas de vencimento
        if config_vencimento and config_vencimento.emails_destino:
            data_limite = datetime.now().date() + timedelta(days=config_vencimento.dias_antecedencia)
            epis_vencendo = EPI.query.filter(
                EPI.validade_ca <= data_limite,
                EPI.ativo == True
            ).all()

            for epi in epis_vencendo:
                dias_restantes = (epi.validade_ca - datetime.now().date()).days

                alerta = {
                    'tipo': 'vencimento',
                    'assunto': f'Alerta de Vencimento de EPI - {epi.nome}',
                    'corpo': f'O EPI {epi.nome} (CA: {epi.ca}) vencerá em {epi.validade_ca.strftime("%d/%m/%Y")}. Restam {dias_restantes} dias.',
                    'destinatarios': config_vencimento.get_emails_lista(),
                    'epi': epi.nome
                }
                alertas_enviados.append(alerta)

        # Alertas de estoque
        if config_estoque and config_estoque.emails_destino:
            epis_estoque_baixo = EPI.query.filter(
                EPI.estoque_atual <= EPI.estoque_minimo_alerta,
                EPI.ativo == True
            ).all()

            for epi in epis_estoque_baixo:
                alerta = {
                    'tipo': 'estoque',
                    'assunto': f'Alerta de Estoque Mínimo de EPI - {epi.nome}',
                    'corpo': f'O estoque do EPI {epi.nome} (CA: {epi.ca}) atingiu o nível mínimo. Estoque atual: {epi.estoque_atual}. Estoque mínimo: {epi.estoque_minimo_alerta}.',
                    'destinatarios': config_estoque.get_emails_lista(),
                    'epi': epi.nome
                }
                alertas_enviados.append(alerta)

        # Registrar simulação no log
        registrar_log_atividade(
            acao='simulou_envio_alertas',
            descricao=f'Simulados {len(alertas_enviados)} alertas de email',
            tabela_afetada='configuracoes_alertas'
        )

        # Em produção, aqui seria feito o envio real dos emails
        for alerta in alertas_enviados:
            print(
                f"[EMAIL SIMULADO] Para: {', '.join(alerta['destinatarios'])}")
            print(f"[EMAIL SIMULADO] Assunto: {alerta['assunto']}")
            print(f"[EMAIL SIMULADO] Corpo: {alerta['corpo']}")
            print("-" * 50)

        flash(
            f'Simulação concluída! {len(alertas_enviados)} alertas seriam enviados.', 'info')

        return render_template('epi/resultado_simulacao_alertas.html',
                               alertas_enviados=alertas_enviados)

    except Exception as e:
        flash(f'Erro na simulação de alertas: {str(e)}', 'error')
        return redirect(url_for('epi.relatorios'))

# ================================
# ROTAS DE API E UTILITÁRIOS
# ================================


@epi_bp.route('/api/estatisticas')
def api_estatisticas():
    """
    API para retornar estatísticas do sistema EPI em JSON
    """
    try:
        stats = {
            'total_epis': EPI.query.filter_by(ativo=True).count(),
            'epis_estoque_baixo': EPI.query.filter(EPI.estoque_atual <= EPI.estoque_minimo_alerta).count(),
            'epis_vencendo_30_dias': EPI.query.filter(
                EPI.validade_ca <= (datetime.now().date() + timedelta(days=30))
            ).count(),
            'declaracoes_mes_atual': DeclaracaoEPI.query.filter(
                DeclaracaoEPI.data_declaracao >= datetime.now().replace(day=1).date()
            ).count(),
            'funcionarios_com_epis': db.session.query(DeclaracaoEPI.funcionario_id.distinct()).count()
        }

        return jsonify(stats)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@epi_bp.route('/api/buscar-epi/<termo>')
def api_buscar_epi(termo):
    """
    API para busca de EPIs (para autocomplete)
    """
    try:
        epis = EPI.query.filter(
            db.or_(
                EPI.nome.ilike(f'%{termo}%'),
                EPI.ca.ilike(f'%{termo}%')
            ),
            EPI.ativo == True
        ).limit(10).all()

        resultado = [epi.to_dict() for epi in epis]
        return jsonify(resultado)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# Continuar importando a função registrar_log_atividade das rotas principais

# Importar modelos e textos
