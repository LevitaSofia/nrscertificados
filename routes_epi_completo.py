"""
Sistema de Gestão de EPIs - Rotas e Views
Implementação completa conforme especificações do prompt
Data: 12/07/2025
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from datetime import datetime, timedelta, date
import json
import io
import base64
from models_epi_completo import (
    db, EPI, DeclaracaoEPI, ItemDeclaracaoEPI, ConfiguracaoAlerta, LogAtividade,
    buscar_funcionarios_simulados, TEXTO_NR06, TEXTO_DECLARACAO_RISCOS
)

# Criar blueprint para o módulo EPI
epi_bp = Blueprint('epi', __name__, url_prefix='/epi')

# ================================
# ROTAS PRINCIPAIS - NAVEGAÇÃO
# ================================


@epi_bp.route('/')
def dashboard():
    """
    Dashboard principal do sistema EPI
    Exibe resumos e estatísticas gerais
    """
    try:
        # Estatísticas gerais
        total_epis = EPI.query.filter_by(ativo=True).count()
        epis_estoque_baixo = EPI.query.filter(
            EPI.estoque_atual <= EPI.estoque_minimo_alerta).count()

        # EPIs próximos do vencimento (30 dias)
        data_limite = datetime.now().date() + timedelta(days=30)
        epis_vencendo = EPI.query.filter(
            EPI.validade_ca <= data_limite).count()

        # Declarações do mês atual
        inicio_mes = datetime.now().replace(day=1).date()
        declaracoes_mes = DeclaracaoEPI.query.filter(
            DeclaracaoEPI.data_declaracao >= inicio_mes
        ).count()

        # Últimas atividades
        ultimas_atividades = LogAtividade.query.order_by(
            LogAtividade.data_acao.desc()
        ).limit(10).all()

        estatisticas = {
            'total_epis': total_epis,
            'epis_estoque_baixo': epis_estoque_baixo,
            'epis_vencendo': epis_vencendo,
            'declaracoes_mes': declaracoes_mes
        }

        return render_template('epi/dashboard.html',
                               estatisticas=estatisticas,
                               ultimas_atividades=ultimas_atividades)

    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return render_template('epi/dashboard.html',
                               estatisticas={},
                               ultimas_atividades=[])

# ================================
# MÓDULO 1: INVENTÁRIO DE EPIS
# ================================


@epi_bp.route('/inventario')
def inventario():
    """
    Página principal do inventário de EPIs
    """
    try:
        # Parâmetros de busca e filtros
        busca = request.args.get('busca', '')
        tipo_protecao = request.args.get('tipo_protecao', '')
        ordenar_por = request.args.get('ordenar_por', 'nome')
        ordem = request.args.get('ordem', 'asc')

        # Query base
        query = EPI.query.filter_by(ativo=True)

        # Aplicar filtros
        if busca:
            query = query.filter(
                db.or_(
                    EPI.nome.ilike(f'%{busca}%'),
                    EPI.ca.ilike(f'%{busca}%'),
                    EPI.fabricante.ilike(f'%{busca}%')
                )
            )

        if tipo_protecao:
            query = query.filter(EPI.tipo_protecao == tipo_protecao)

        # Aplicar ordenação
        if ordenar_por == 'nome':
            query = query.order_by(
                EPI.nome.asc() if ordem == 'asc' else EPI.nome.desc())
        elif ordenar_por == 'ca':
            query = query.order_by(
                EPI.ca.asc() if ordem == 'asc' else EPI.ca.desc())
        elif ordenar_por == 'validade_ca':
            query = query.order_by(EPI.validade_ca.asc(
            ) if ordem == 'asc' else EPI.validade_ca.desc())
        elif ordenar_por == 'estoque':
            query = query.order_by(EPI.estoque_atual.asc(
            ) if ordem == 'asc' else EPI.estoque_atual.desc())

        # Executar query
        epis = query.all()

        # Tipos de proteção para o filtro
        tipos_protecao = db.session.query(EPI.tipo_protecao.distinct()).filter(
            EPI.tipo_protecao.isnot(None),
            EPI.ativo == True
        ).all()
        tipos_protecao = [tipo[0] for tipo in tipos_protecao if tipo[0]]

        return render_template('epi/inventario.html',
                               epis=epis,
                               tipos_protecao=tipos_protecao,
                               filtros={
                                   'busca': busca,
                                   'tipo_protecao': tipo_protecao,
                                   'ordenar_por': ordenar_por,
                                   'ordem': ordem
                               })

    except Exception as e:
        flash(f'Erro ao carregar inventário: {str(e)}', 'error')
        return render_template('epi/inventario.html', epis=[], tipos_protecao=[])


@epi_bp.route('/inventario/novo')
def novo_epi():
    """
    Formulário para cadastro de novo EPI
    """
    return render_template('epi/formulario_epi.html', epi=None, modo='novo')


@epi_bp.route('/inventario/editar/<int:epi_id>')
def editar_epi(epi_id):
    """
    Formulário para edição de EPI existente
    """
    try:
        epi = EPI.query.get_or_404(epi_id)
        return render_template('epi/formulario_epi.html', epi=epi, modo='editar')
    except Exception as e:
        flash(f'Erro ao carregar EPI: {str(e)}', 'error')
        return redirect(url_for('epi.inventario'))


@epi_bp.route('/inventario/salvar', methods=['POST'])
def salvar_epi():
    """
    Salva ou atualiza um EPI no banco de dados
    """
    try:
        epi_id = request.form.get('epi_id')

        # Validações básicas
        nome = request.form.get('nome', '').strip()
        ca = request.form.get('ca', '').strip()
        validade_ca_str = request.form.get('validade_ca', '').strip()

        if not nome or not ca or not validade_ca_str:
            flash('Nome, CA e Validade do CA são obrigatórios!', 'error')
            return redirect(request.referrer or url_for('epi.inventario'))

        # Converter data
        try:
            validade_ca = datetime.strptime(validade_ca_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data de validade do CA inválida!', 'error')
            return redirect(request.referrer or url_for('epi.inventario'))

        # Verificar se é edição ou novo cadastro
        if epi_id:
            epi = EPI.query.get_or_404(epi_id)
            dados_anteriores = epi.to_dict()
            acao = 'editou_epi'
        else:
            # Verificar se CA já existe
            epi_existente = EPI.query.filter_by(ca=ca, ativo=True).first()
            if epi_existente:
                flash(f'Já existe um EPI cadastrado com o CA {ca}!', 'error')
                return redirect(request.referrer or url_for('epi.inventario'))

            epi = EPI()
            dados_anteriores = None
            acao = 'cadastrou_epi'

        # Preencher dados do EPI
        epi.nome = nome
        epi.descricao = request.form.get('descricao', '').strip()
        epi.ca = ca
        epi.validade_ca = validade_ca
        epi.fabricante = request.form.get('fabricante', '').strip()
        epi.tipo_protecao = request.form.get('tipo_protecao', '').strip()

        # Campos numéricos
        try:
            epi.estoque_atual = int(request.form.get('estoque_atual', 0))
            epi.estoque_minimo_alerta = int(
                request.form.get('estoque_minimo_alerta', 5))
        except ValueError:
            flash('Valores de estoque devem ser números inteiros!', 'error')
            return redirect(request.referrer or url_for('epi.inventario'))

        epi.imagem_url = request.form.get('imagem_url', '').strip()

        # Salvar no banco
        if not epi_id:
            db.session.add(epi)

        db.session.commit()

        # Registrar log de atividade
        registrar_log_atividade(
            acao=acao,
            descricao=f'EPI: {epi.nome} (CA: {epi.ca})',
            tabela_afetada='epis',
            registro_id=epi.id,
            dados_anteriores=dados_anteriores,
            dados_novos=epi.to_dict()
        )

        flash(f'EPI {epi.nome} salvo com sucesso!', 'success')
        return redirect(url_for('epi.inventario'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar EPI: {str(e)}', 'error')
        return redirect(request.referrer or url_for('epi.inventario'))


@epi_bp.route('/inventario/excluir/<int:epi_id>', methods=['POST'])
def excluir_epi(epi_id):
    """
    Exclui (desativa) um EPI do inventário
    """
    try:
        epi = EPI.query.get_or_404(epi_id)

        # Verificar se EPI tem entregas ativas
        entregas_ativas = db.session.query(ItemDeclaracaoEPI).join(DeclaracaoEPI).filter(
            ItemDeclaracaoEPI.epi_id == epi_id,
            ItemDeclaracaoEPI.rd == True,
            ItemDeclaracaoEPI.data_devolucao.is_(None),
            DeclaracaoEPI.status == 'ativa'
        ).count()

        if entregas_ativas > 0:
            flash(
                f'Não é possível excluir o EPI {epi.nome} pois ele está em posse de funcionários!', 'error')
            return redirect(url_for('epi.inventario'))

        # Desativação lógica
        dados_anteriores = epi.to_dict()
        epi.ativo = False
        db.session.commit()

        # Registrar log
        registrar_log_atividade(
            acao='excluiu_epi',
            descricao=f'EPI: {epi.nome} (CA: {epi.ca})',
            tabela_afetada='epis',
            registro_id=epi.id,
            dados_anteriores=dados_anteriores,
            dados_novos=epi.to_dict()
        )

        flash(f'EPI {epi.nome} excluído com sucesso!', 'success')
        return redirect(url_for('epi.inventario'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir EPI: {str(e)}', 'error')
        return redirect(url_for('epi.inventario'))


@epi_bp.route('/api/verificar-ca/<ca>')
def verificar_ca_api(ca):
    """
    API simulada para verificação de CA
    Em produção, conectaria com API real do MTE
    """
    try:
        # Simulação de resposta da API
        if ca == '12345':
            return jsonify({
                'success': True,
                'situacao': 'Ativo',
                'validade_ca': '2030-12-31',
                'fabricante': 'VONDER',
                'descricao_oficial': 'Óculos de segurança incolor'
            })
        elif ca == '99999':
            return jsonify({
                'success': True,
                'situacao': 'Vencido',
                'validade_ca': '2024-01-01',
                'fabricante': 'Fabricante X',
                'descricao_oficial': 'EPI com CA vencido'
            })
        else:
            return jsonify({
                'success': False,
                'situacao': 'Não Encontrado',
                'mensagem': 'CA não encontrado na base de dados do MTE'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'erro': f'Erro na consulta da API: {str(e)}'
        }), 500

# ================================
# MÓDULO 2: GESTÃO DE ENTREGAS
# ================================


@epi_bp.route('/entregas')
def gestao_entregas():
    """
    Página principal da gestão de entregas de EPIs
    """
    try:
        funcionarios = buscar_funcionarios_simulados()

        # Buscar declarações recentes
        declaracoes_recentes = DeclaracaoEPI.query.order_by(
            DeclaracaoEPI.data_declaracao.desc()
        ).limit(10).all()

        return render_template('epi/gestao_entregas.html',
                               funcionarios=funcionarios,
                               declaracoes_recentes=declaracoes_recentes)

    except Exception as e:
        flash(f'Erro ao carregar gestão de entregas: {str(e)}', 'error')
        return render_template('epi/gestao_entregas.html',
                               funcionarios=[],
                               declaracoes_recentes=[])


@epi_bp.route('/entregas/funcionario/<funcionario_id>')
def detalhes_funcionario(funcionario_id):
    """
    Exibe detalhes e histórico de EPIs de um funcionário específico
    """
    try:
        # Buscar dados do funcionário
        funcionarios = buscar_funcionarios_simulados()
        funcionario = next(
            (f for f in funcionarios if f['id'] == funcionario_id), None)

        if not funcionario:
            flash('Funcionário não encontrado!', 'error')
            return redirect(url_for('epi.gestao_entregas'))

        # Buscar histórico de declarações do funcionário
        declaracoes = DeclaracaoEPI.query.filter_by(
            funcionario_id=funcionario_id
        ).order_by(DeclaracaoEPI.data_declaracao.desc()).all()

        # Buscar EPIs atualmente em posse do funcionário
        epis_em_posse = db.session.query(ItemDeclaracaoEPI).join(DeclaracaoEPI).join(EPI).filter(
            DeclaracaoEPI.funcionario_id == funcionario_id,
            ItemDeclaracaoEPI.rd == True,
            ItemDeclaracaoEPI.data_devolucao.is_(None),
            DeclaracaoEPI.status == 'ativa'
        ).all()

        # Buscar todos os EPIs disponíveis para nova declaração
        epis_disponiveis = EPI.query.filter_by(ativo=True).all()

        return render_template('epi/detalhes_funcionario.html',
                               funcionario=funcionario,
                               declaracoes=declaracoes,
                               epis_em_posse=epis_em_posse,
                               epis_disponiveis=epis_disponiveis)

    except Exception as e:
        flash(f'Erro ao carregar detalhes do funcionário: {str(e)}', 'error')
        return redirect(url_for('epi.gestao_entregas'))


@epi_bp.route('/entregas/nova-declaracao', methods=['POST'])
def nova_declaracao():
    """
    Cria uma nova declaração de EPIs para um funcionário
    """
    try:
        # Dados básicos da declaração
        funcionario_id = request.form.get('funcionario_id')
        data_declaracao_str = request.form.get('data_declaracao')
        declaracao_nr06_aceita = bool(
            request.form.get('declaracao_nr06_aceita'))
        orientacao_riscos_aceita = bool(
            request.form.get('orientacao_riscos_aceita'))
        observacoes = request.form.get('observacoes', '').strip()

        # Validações
        if not funcionario_id:
            flash('Funcionário deve ser selecionado!', 'error')
            return redirect(request.referrer or url_for('epi.gestao_entregas'))

        if not declaracao_nr06_aceita or not orientacao_riscos_aceita:
            flash('Ambas as declarações de ciência devem ser aceitas!', 'error')
            return redirect(request.referrer or url_for('epi.gestao_entregas'))

        # Buscar dados do funcionário
        funcionarios = buscar_funcionarios_simulados()
        funcionario = next(
            (f for f in funcionarios if f['id'] == funcionario_id), None)

        if not funcionario:
            flash('Funcionário não encontrado!', 'error')
            return redirect(url_for('epi.gestao_entregas'))

        # Converter data
        try:
            if data_declaracao_str:
                data_declaracao = datetime.strptime(
                    data_declaracao_str, '%Y-%m-%d').date()
            else:
                data_declaracao = datetime.now().date()
        except ValueError:
            flash('Data da declaração inválida!', 'error')
            return redirect(request.referrer or url_for('epi.gestao_entregas'))

        # Criar nova declaração
        declaracao = DeclaracaoEPI(
            funcionario_id=funcionario_id,
            funcionario_nome=funcionario['nome'],
            funcionario_cargo=funcionario['cargo'],
            funcionario_admissao=datetime.strptime(
                funcionario['admissao'], '%Y-%m-%d').date(),
            data_declaracao=data_declaracao,
            declaracao_nr06_aceita=declaracao_nr06_aceita,
            orientacao_riscos_aceita=orientacao_riscos_aceita,
            observacoes=observacoes,
            usuario_responsavel=request.form.get(
                'usuario_responsavel', 'Sistema')
        )

        db.session.add(declaracao)
        db.session.flush()  # Para obter o ID da declaração

        # Processar itens da declaração
        epis_selecionados = request.form.getlist('epis_selecionados')

        if not epis_selecionados:
            flash('Pelo menos um EPI deve ser selecionado!', 'error')
            db.session.rollback()
            return redirect(request.referrer or url_for('epi.gestao_entregas'))

        # Criar itens da declaração
        for epi_id in epis_selecionados:
            epi = EPI.query.get(epi_id)
            if not epi:
                continue

            # Verificar se funcionário já possui este EPI ativo
            item_existente = db.session.query(ItemDeclaracaoEPI).join(DeclaracaoEPI).filter(
                DeclaracaoEPI.funcionario_id == funcionario_id,
                ItemDeclaracaoEPI.epi_id == epi_id,
                ItemDeclaracaoEPI.rd == True,
                ItemDeclaracaoEPI.data_devolucao.is_(None),
                DeclaracaoEPI.status == 'ativa'
            ).first()

            if item_existente:
                flash(
                    f'Funcionário já possui o EPI {epi.nome} em posse!', 'warning')
                continue

            # Criar item da declaração
            item = ItemDeclaracaoEPI(
                declaracao_id=declaracao.id,
                epi_id=epi.id,
                epi_nome=epi.nome,
                epi_ca=epi.ca,
                epi_validade_ca=epi.validade_ca,
                rd=True,  # Por padrão, novo item é considerado entregue
                data_entrega=data_declaracao
            )

            db.session.add(item)

            # Reduzir estoque do EPI
            if epi.estoque_atual > 0:
                epi.estoque_atual -= 1

        db.session.commit()

        # Registrar log
        registrar_log_atividade(
            acao='criou_declaracao',
            descricao=f'Declaração para {funcionario["nome"]} - {len(epis_selecionados)} EPIs',
            tabela_afetada='declaracoes_epi',
            registro_id=declaracao.id,
            dados_novos=declaracao.to_dict()
        )

        flash(
            f'Declaração criada com sucesso para {funcionario["nome"]}!', 'success')
        return redirect(url_for('epi.detalhes_funcionario', funcionario_id=funcionario_id))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar declaração: {str(e)}', 'error')
        return redirect(request.referrer or url_for('epi.gestao_entregas'))

# ================================
# CONTINUAÇÃO DAS ROTAS...
# (Vou continuar na próxima parte devido ao limite de tamanho)
# ================================


def registrar_log_atividade(acao, descricao, tabela_afetada=None, registro_id=None,
                            dados_anteriores=None, dados_novos=None):
    """
    Função auxiliar para registrar atividades no log
    """
    try:
        log = LogAtividade(
            usuario=request.form.get('usuario_responsavel', 'Sistema'),
            acao=acao,
            descricao=descricao,
            tabela_afetada=tabela_afetada,
            registro_id=registro_id,
            dados_anteriores=json.dumps(
                dados_anteriores) if dados_anteriores else None,
            dados_novos=json.dumps(dados_novos) if dados_novos else None,
            ip_usuario=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:255]
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao registrar log: {str(e)}")
