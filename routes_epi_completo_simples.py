from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
import sqlite3
from datetime import datetime, date
import json

epi_bp = Blueprint('epi', __name__, url_prefix='/epi')


def get_db_connection():
    """Obter conexão com o banco de dados"""
    try:
        conn = sqlite3.connect('certificados.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        current_app.logger.error(f"Erro ao conectar com banco: {e}")
        return None

# Rotas principais


@epi_bp.route('/')
@epi_bp.route('/dashboard')
def dashboard():
    """Dashboard principal do sistema EPI"""
    return render_template('epi/dashboard_simples.html')


@epi_bp.route('/inventario')
def inventario():
    """Página de inventário de EPIs"""
    return render_template('epi/inventario_simples.html')


@epi_bp.route('/formulario')
@epi_bp.route('/formulario/<int:epi_id>')
def formulario_epi(epi_id=None):
    """Formulário para cadastro/edição de EPI"""
    epi = None
    modo = 'novo'

    if epi_id:
        conn = get_db_connection()
        if conn:
            try:
                epi = conn.execute(
                    'SELECT * FROM epi WHERE id = ?',
                    (epi_id,)
                ).fetchone()
                modo = 'editar' if epi else 'novo'
            finally:
                conn.close()

    return render_template('epi/formulario_epi_simples.html', epi=epi, modo=modo)


@epi_bp.route('/entregas')
def entregas():
    """Página de entregas de EPI"""
    return render_template('epi/entregas_simples.html')


@epi_bp.route('/relatorios')
def relatorios():
    """Página de relatórios"""
    return render_template('epi/relatorios_simples.html')


@epi_bp.route('/configuracoes')
def configuracoes():
    """Página de configurações"""
    return render_template('epi/configuracoes_simples.html')

# APIs para o frontend


@epi_bp.route('/api/estatisticas')
def api_estatisticas():
    """API para estatísticas do dashboard"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão'})

    try:
        # Total de EPIs
        total_epis = conn.execute(
            'SELECT COUNT(*) as count FROM epi').fetchone()['count']

        # EPIs com estoque baixo
        estoque_baixo = conn.execute(
            'SELECT COUNT(*) as count FROM epi WHERE estoque_atual <= estoque_minimo_alerta'
        ).fetchone()['count']

        # Entregas do mês atual
        primeiro_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        entregas_mes = conn.execute(
            'SELECT COUNT(*) as count FROM declaracao_epi WHERE data_entrega >= ?',
            (primeiro_dia_mes,)
        ).fetchone()['count']

        # CAs vencendo (próximos 30 dias)
        data_limite = (datetime.now().replace(day=1).strftime('%Y-%m-%d'))
        cas_vencendo = conn.execute(
            "SELECT COUNT(*) as count FROM epi WHERE julianday(validade_ca) - julianday('now') <= 30"
        ).fetchone()['count']

        return jsonify({
            'success': True,
            'total_epis': total_epis,
            'estoque_baixo': estoque_baixo,
            'entregas_mes': entregas_mes,
            'cas_vencendo': cas_vencendo
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()


@epi_bp.route('/api/epis')
def api_epis():
    """API para listar EPIs com paginação e filtros"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão'})

    try:
        # Parâmetros da requisição
        pagina = int(request.args.get('pagina', 1))
        por_pagina = int(request.args.get('por_pagina', 10))
        busca = request.args.get('busca', '').strip()
        tipo_protecao = request.args.get('tipo_protecao', '').strip()
        status = request.args.get('status', '').strip()

        # Construir query base
        where_conditions = []
        params = []

        if busca:
            where_conditions.append(
                '(nome LIKE ? OR ca LIKE ? OR fabricante LIKE ?)')
            busca_param = f'%{busca}%'
            params.extend([busca_param, busca_param, busca_param])

        if tipo_protecao:
            where_conditions.append('tipo_protecao = ?')
            params.append(tipo_protecao)

        if status == 'estoque_baixo':
            where_conditions.append('estoque_atual <= estoque_minimo_alerta')
        elif status == 'ca_vencendo':
            where_conditions.append(
                "julianday(validade_ca) - julianday('now') <= 30")
        elif status == 'ca_vencido':
            where_conditions.append(
                "julianday(validade_ca) - julianday('now') < 0")

        where_clause = 'WHERE ' + \
            ' AND '.join(where_conditions) if where_conditions else ''

        # Contar total de registros
        count_query = f'SELECT COUNT(*) as total FROM epi {where_clause}'
        total_registros = conn.execute(count_query, params).fetchone()['total']

        # Calcular offset
        offset = (pagina - 1) * por_pagina

        # Buscar EPIs
        query = f'''
            SELECT id, nome, ca, validade_ca, fabricante, tipo_protecao, 
                   estoque_atual, estoque_minimo_alerta, descricao,
                   CASE 
                       WHEN julianday(validade_ca) - julianday('now') < 0 THEN 'CA Vencido'
                       WHEN julianday(validade_ca) - julianday('now') <= 30 THEN 'CA Vencendo'
                       WHEN estoque_atual <= estoque_minimo_alerta THEN 'Estoque Baixo'
                       ELSE 'OK'
                   END as status
            FROM epi 
            {where_clause}
            ORDER BY nome
            LIMIT ? OFFSET ?
        '''

        epis = conn.execute(query, params + [por_pagina, offset]).fetchall()

        # Converter para lista de dicionários
        epis_list = []
        for epi in epis:
            epi_dict = dict(epi)
            # Converter datas para string
            if epi_dict['validade_ca']:
                epi_dict['validade_ca'] = epi_dict['validade_ca']
            epis_list.append(epi_dict)

        total_paginas = (total_registros + por_pagina - 1) // por_pagina

        return jsonify({
            'success': True,
            'epis': epis_list,
            'total_registros': total_registros,
            'total_paginas': total_paginas,
            'pagina_atual': pagina
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao listar EPIs: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()


@epi_bp.route('/api/verificar-ca/<ca>')
def api_verificar_ca(ca):
    """API para verificar CA do EPI"""
    try:
        # Simulação de verificação de CA
        # Em um ambiente real, isso faria uma consulta à API do MTE

        # CAs de exemplo para teste
        cas_validos = {
            '12345': {'validade': '2025-12-31', 'fabricante': '3M', 'situacao': 'Ativo'},
            '67890': {'validade': '2024-06-30', 'fabricante': 'VONDER', 'situacao': 'Ativo'},
            '11111': {'validade': '2023-01-15', 'fabricante': 'MSA', 'situacao': 'Vencido'}
        }

        if ca in cas_validos:
            ca_info = cas_validos[ca]
            return jsonify({
                'success': True,
                'validade_ca': ca_info['validade'],
                'fabricante': ca_info['fabricante'],
                'situacao': ca_info['situacao']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'CA não encontrado na base de dados'
            })

    except Exception as e:
        current_app.logger.error(f"Erro ao verificar CA: {e}")
        return jsonify({'success': False, 'message': str(e)})


@epi_bp.route('/salvar_epi', methods=['POST'])
def salvar_epi():
    """Salvar EPI (novo ou edição)"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return redirect(url_for('epi.inventario'))

    try:
        epi_id = request.form.get('epi_id')
        nome = request.form.get('nome')
        ca = request.form.get('ca')
        validade_ca = request.form.get('validade_ca')
        fabricante = request.form.get('fabricante', '')
        tipo_protecao = request.form.get('tipo_protecao', '')
        estoque_atual = int(request.form.get('estoque_atual', 0))
        estoque_minimo_alerta = int(
            request.form.get('estoque_minimo_alerta', 5))
        descricao = request.form.get('descricao', '')

        if epi_id:
            # Atualizar EPI existente
            conn.execute('''
                UPDATE epi SET 
                    nome = ?, ca = ?, validade_ca = ?, fabricante = ?, 
                    tipo_protecao = ?, estoque_atual = ?, estoque_minimo_alerta = ?, 
                    descricao = ?
                WHERE id = ?
            ''', (nome, ca, validade_ca, fabricante, tipo_protecao,
                  estoque_atual, estoque_minimo_alerta, descricao, epi_id))

            flash('EPI atualizado com sucesso!', 'success')
        else:
            # Inserir novo EPI
            conn.execute('''
                INSERT INTO epi (nome, ca, validade_ca, fabricante, tipo_protecao, 
                               estoque_atual, estoque_minimo_alerta, descricao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, ca, validade_ca, fabricante, tipo_protecao,
                  estoque_atual, estoque_minimo_alerta, descricao))

            flash('EPI cadastrado com sucesso!', 'success')

        conn.commit()

    except Exception as e:
        current_app.logger.error(f"Erro ao salvar EPI: {e}")
        flash(f'Erro ao salvar EPI: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('epi.inventario'))


@epi_bp.route('/api/funcionarios')
def api_funcionarios():
    """API para listar funcionários"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão'})

    try:
        funcionarios = conn.execute(
            'SELECT id, nome FROM funcionarios ORDER BY nome'
        ).fetchall()

        funcionarios_list = [dict(func) for func in funcionarios]

        return jsonify({
            'success': True,
            'funcionarios': funcionarios_list
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao listar funcionários: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()


@epi_bp.route('/api/epis-disponiveis')
def api_epis_disponiveis():
    """API para listar EPIs com estoque disponível"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão'})

    try:
        epis = conn.execute(
            'SELECT id, nome, estoque_atual FROM epi WHERE estoque_atual > 0 ORDER BY nome'
        ).fetchall()

        epis_list = [dict(epi) for epi in epis]

        return jsonify({
            'success': True,
            'epis': epis_list
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao listar EPIs disponíveis: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

# APIs para entregas


@epi_bp.route('/api/entregas')
def api_entregas():
    """API para listar entregas com paginação e filtros"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão'})

    try:
        # Parâmetros da requisição
        pagina = int(request.args.get('pagina', 1))
        por_pagina = int(request.args.get('por_pagina', 10))
        funcionario = request.args.get('funcionario', '').strip()
        epi = request.args.get('epi', '').strip()
        data_inicio = request.args.get('data_inicio', '').strip()
        data_fim = request.args.get('data_fim', '').strip()
        status = request.args.get('status', '').strip()

        # Construir query base
        where_conditions = []
        params = []

        if funcionario:
            where_conditions.append('f.nome LIKE ?')
            params.append(f'%{funcionario}%')

        if epi:
            where_conditions.append('e.nome LIKE ?')
            params.append(f'%{epi}%')

        if data_inicio:
            where_conditions.append('d.data_entrega >= ?')
            params.append(data_inicio)

        if data_fim:
            where_conditions.append('d.data_entrega <= ?')
            params.append(data_fim)

        if status:
            where_conditions.append('d.status = ?')
            params.append(status)

        where_clause = 'WHERE ' + \
            ' AND '.join(where_conditions) if where_conditions else ''

        # Contar total de registros
        count_query = f'''
            SELECT COUNT(*) as total 
            FROM declaracao_epi d
            LEFT JOIN funcionarios f ON d.funcionario_id = f.id
            LEFT JOIN epi e ON d.epi_id = e.id
            {where_clause}
        '''
        total_registros = conn.execute(count_query, params).fetchone()['total']

        # Calcular offset
        offset = (pagina - 1) * por_pagina

        # Buscar entregas
        query = f'''
            SELECT d.id, d.data_entrega, d.data_devolucao, d.quantidade, 
                   d.status, d.observacoes, f.nome as funcionario_nome, 
                   e.nome as epi_nome
            FROM declaracao_epi d
            LEFT JOIN funcionarios f ON d.funcionario_id = f.id
            LEFT JOIN epi e ON d.epi_id = e.id
            {where_clause}
            ORDER BY d.data_entrega DESC
            LIMIT ? OFFSET ?
        '''

        entregas = conn.execute(
            query, params + [por_pagina, offset]).fetchall()

        entregas_list = [dict(entrega) for entrega in entregas]
        total_paginas = (total_registros + por_pagina - 1) // por_pagina

        return jsonify({
            'success': True,
            'entregas': entregas_list,
            'total_registros': total_registros,
            'total_paginas': total_paginas,
            'pagina_atual': pagina
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao listar entregas: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()


@epi_bp.route('/api/entregas', methods=['POST'])
def api_criar_entrega():
    """API para criar nova entrega"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão'})

    try:
        funcionario_id = request.form.get('funcionario_id')
        epi_id = request.form.get('epi_id')
        quantidade = int(request.form.get('quantidade', 1))
        data_entrega = request.form.get('data_entrega')
        validade_prevista = request.form.get('validade_prevista')
        observacoes = request.form.get('observacoes', '')
        gerar_declaracao = request.form.get('gerar_declaracao') == 'on'

        # Verificar estoque disponível
        epi = conn.execute(
            'SELECT estoque_atual FROM epi WHERE id = ?',
            (epi_id,)
        ).fetchone()

        if not epi or epi['estoque_atual'] < quantidade:
            return jsonify({
                'success': False,
                'message': 'Estoque insuficiente'
            })

        # Criar entrega
        cursor = conn.execute('''
            INSERT INTO declaracao_epi 
            (funcionario_id, epi_id, data_entrega, quantidade, status, 
             validade_prevista, observacoes)
            VALUES (?, ?, ?, ?, 'Entregue', ?, ?)
        ''', (funcionario_id, epi_id, data_entrega, quantidade,
              validade_prevista, observacoes))

        entrega_id = cursor.lastrowid

        # Atualizar estoque
        conn.execute(
            'UPDATE epi SET estoque_atual = estoque_atual - ? WHERE id = ?',
            (quantidade, epi_id)
        )

        conn.commit()

        response = {'success': True, 'entrega_id': entrega_id}

        if gerar_declaracao:
            response['pdf_url'] = f'/epi/api/declaracao-pdf/{entrega_id}'

        return jsonify(response)

    except Exception as e:
        current_app.logger.error(f"Erro ao criar entrega: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

# APIs de relatórios simples


@epi_bp.route('/api/estatisticas-gerais')
def api_estatisticas_gerais():
    """API para estatísticas gerais dos relatórios"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão'})

    try:
        # Estatísticas básicas
        stats = {}

        # Total EPIs
        stats['total_epis'] = conn.execute(
            'SELECT COUNT(*) as count FROM epi'
        ).fetchone()['count']

        # Entregas do mês
        primeiro_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        stats['entregas_mes'] = conn.execute(
            'SELECT COUNT(*) as count FROM declaracao_epi WHERE data_entrega >= ?',
            (primeiro_dia_mes,)
        ).fetchone()['count']

        # Estoque baixo
        stats['estoque_baixo'] = conn.execute(
            'SELECT COUNT(*) as count FROM epi WHERE estoque_atual <= estoque_minimo_alerta'
        ).fetchone()['count']

        # CAs vencendo
        stats['cas_vencendo'] = conn.execute(
            "SELECT COUNT(*) as count FROM epi WHERE julianday(validade_ca) - julianday('now') <= 30"
        ).fetchone()['count']

        return jsonify({
            'success': True,
            **stats
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas gerais: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()
