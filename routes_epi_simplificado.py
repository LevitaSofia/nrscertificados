"""
Sistema de Gestão de EPIs - Rotas Simplificadas
Versão que funciona com SQLAlchemy existente
Data: 12/07/2025
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
import sys


def criar_blueprint_epi(app):
    """
    Cria o blueprint EPI usando a instância SQLAlchemy existente
    """

    # Criar blueprint
    epi_bp = Blueprint('epi', __name__, url_prefix='/epi')

    # Obter instância db do app principal
    main_module = sys.modules.get('__main__')
    db = main_module.db if main_module and hasattr(main_module, 'db') else None

    if not db:
        raise Exception("Instância SQLAlchemy não encontrada")

    # ================================
    # ROTAS PRINCIPAIS
    # ================================

    @epi_bp.route('/')
    def dashboard():
        """Dashboard principal do sistema EPI"""
        try:
            # Estatísticas básicas (usando queries simples)
            with app.app_context():
                # Verificar se tabelas existem antes de fazer queries
                try:
                    total_epis = db.session.execute(
                        db.text("SELECT COUNT(*) FROM epis WHERE ativo = 1")).scalar() or 0
                except:
                    total_epis = 0

                try:
                    declaracoes_mes = db.session.execute(
                        db.text(
                            "SELECT COUNT(*) FROM declaracoes_epi WHERE strftime('%Y-%m', data_declaracao) = strftime('%Y-%m', 'now')")
                    ).scalar() or 0
                except:
                    declaracoes_mes = 0

                estatisticas = {
                    'total_epis': total_epis,
                    'epis_estoque_baixo': 0,  # Simplificado
                    'epis_vencendo': 0,       # Simplificado
                    'declaracoes_mes': declaracoes_mes
                }

            return render_template('epi/dashboard_simples.html',
                                   estatisticas=estatisticas,
                                   sistema_funcionando=True)

        except Exception as e:
            flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
            return render_template('epi/dashboard_simples.html',
                                   estatisticas={},
                                   sistema_funcionando=False,
                                   erro=str(e))

    @epi_bp.route('/inventario')
    def inventario():
        """Página de inventário de EPIs"""
        try:
            with app.app_context():
                # Query simples para listar EPIs
                epis_raw = db.session.execute(
                    db.text("SELECT * FROM epis WHERE ativo = 1 ORDER BY nome")
                ).fetchall() if db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='epis'")).fetchone() else []

                # Converter para dicionários
                epis = []
                for epi in epis_raw:
                    epis.append({
                        'id': epi.id if hasattr(epi, 'id') else epi[0],
                        'nome': epi.nome if hasattr(epi, 'nome') else epi[1],
                        'ca': epi.ca if hasattr(epi, 'ca') else epi[3],
                        'validade_ca': epi.validade_ca if hasattr(epi, 'validade_ca') else epi[4],
                        'estoque_atual': epi.estoque_atual if hasattr(epi, 'estoque_atual') else epi[7]
                    })

                return render_template('epi/inventario_simples.html', epis=epis)

        except Exception as e:
            flash(f'Erro ao carregar inventário: {str(e)}', 'error')
            return render_template('epi/inventario_simples.html', epis=[])

    @epi_bp.route('/inventario/novo')
    def novo_epi():
        """Formulário para novo EPI"""
        return render_template('epi/formulario_epi_simples.html', modo='novo')

    @epi_bp.route('/inventario/salvar', methods=['POST'])
    def salvar_epi():
        """Salva um novo EPI"""
        try:
            nome = request.form.get('nome', '').strip()
            ca = request.form.get('ca', '').strip()
            validade_ca = request.form.get('validade_ca', '').strip()
            estoque_atual = int(request.form.get('estoque_atual', 0))

            if not nome or not ca or not validade_ca:
                flash('Nome, CA e Validade são obrigatórios!', 'error')
                return redirect(url_for('epi.novo_epi'))

            with app.app_context():
                # Verificar se CA já existe
                ca_existente = db.session.execute(
                    db.text(
                        "SELECT COUNT(*) FROM epis WHERE ca = :ca AND ativo = 1"),
                    {'ca': ca}
                ).scalar()

                if ca_existente > 0:
                    flash(f'CA {ca} já está cadastrado!', 'error')
                    return redirect(url_for('epi.novo_epi'))

                # Inserir novo EPI
                db.session.execute(
                    db.text("""
                        INSERT INTO epis (nome, ca, validade_ca, estoque_atual, ativo, data_cadastro)
                        VALUES (:nome, :ca, :validade_ca, :estoque_atual, 1, :data_cadastro)
                    """),
                    {
                        'nome': nome,
                        'ca': ca,
                        'validade_ca': validade_ca,
                        'estoque_atual': estoque_atual,
                        'data_cadastro': datetime.now()
                    }
                )
                db.session.commit()

                flash(f'EPI {nome} cadastrado com sucesso!', 'success')
                return redirect(url_for('epi.inventario'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar EPI: {str(e)}', 'error')
            return redirect(url_for('epi.novo_epi'))

    @epi_bp.route('/entregas')
    def gestao_entregas():
        """Página de gestão de entregas"""
        try:
            # Funcionários simulados
            funcionarios = [
                {'id': 'FUNC001', 'nome': 'André Roberto dos Santos',
                    'cargo': 'Supervisor'},
                {'id': 'FUNC002', 'nome': 'Maria Silva Santos', 'cargo': 'Operador'},
                {'id': 'FUNC003', 'nome': 'João Carlos Oliveira', 'cargo': 'Técnico'},
            ]

            return render_template('epi/entregas_simples.html', funcionarios=funcionarios)

        except Exception as e:
            flash(f'Erro ao carregar entregas: {str(e)}', 'error')
            return render_template('epi/entregas_simples.html', funcionarios=[])

    @epi_bp.route('/relatorios')
    def relatorios():
        """Página de relatórios"""
        try:
            return render_template('epi/relatorios_simples.html')
        except Exception as e:
            flash(f'Erro ao carregar relatórios: {str(e)}', 'error')
            return render_template('epi/relatorios_simples.html')

    @epi_bp.route('/configuracoes')
    def configuracoes():
        """Página de configurações"""
        try:
            return render_template('epi/configuracoes_simples.html')
        except Exception as e:
            flash(f'Erro ao carregar configurações: {str(e)}', 'error')
            return render_template('epi/configuracoes_simples.html')

    # ================================
    # APIs SIMPLES
    # ================================

    @epi_bp.route('/api/verificar-ca/<ca>')
    def verificar_ca_api(ca):
        """API simulada para verificação de CA"""
        try:
            # Simulação simples
            if ca == '12345':
                return jsonify({
                    'success': True,
                    'situacao': 'Ativo',
                    'validade_ca': '2030-12-31'
                })
            elif ca == '99999':
                return jsonify({
                    'success': True,
                    'situacao': 'Vencido',
                    'validade_ca': '2024-01-01'
                })
            else:
                return jsonify({
                    'success': False,
                    'situacao': 'Não Encontrado'
                })

        except Exception as e:
            return jsonify({'success': False, 'erro': str(e)}), 500

    @epi_bp.route('/api/estatisticas')
    def api_estatisticas():
        """API para estatísticas"""
        try:
            with app.app_context():
                stats = {
                    'total_epis': 0,
                    'epis_estoque_baixo': 0,
                    'epis_vencendo': 0,
                    'declaracoes_mes': 0
                }

                try:
                    stats['total_epis'] = db.session.execute(
                        db.text("SELECT COUNT(*) FROM epis WHERE ativo = 1")
                    ).scalar() or 0
                except:
                    pass

                return jsonify(stats)

        except Exception as e:
            return jsonify({'erro': str(e)}), 500

    return epi_bp


def criar_tabelas_basicas(db):
    """
    Cria as tabelas básicas do sistema EPI
    """
    try:
        # Criar tabela EPIs
        db.session.execute(db.text("""
            CREATE TABLE IF NOT EXISTS epis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(200) NOT NULL,
                descricao TEXT,
                ca VARCHAR(20) NOT NULL UNIQUE,
                validade_ca DATE NOT NULL,
                fabricante VARCHAR(100),
                tipo_protecao VARCHAR(50),
                estoque_atual INTEGER DEFAULT 0,
                estoque_minimo_alerta INTEGER DEFAULT 5,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1
            )
        """))

        # Criar tabela Declarações
        db.session.execute(db.text("""
            CREATE TABLE IF NOT EXISTS declaracoes_epi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funcionario_id VARCHAR(50) NOT NULL,
                funcionario_nome VARCHAR(200) NOT NULL,
                data_declaracao DATE NOT NULL,
                declaracao_nr06_aceita BOOLEAN DEFAULT 0,
                orientacao_riscos_aceita BOOLEAN DEFAULT 0,
                data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'ativa'
            )
        """))

        db.session.commit()
        print("✅ Tabelas básicas criadas!")

    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {str(e)}")
        db.session.rollback()


if __name__ == "__main__":
    print("📋 Módulo de rotas EPI simplificadas")
    print("Use criar_blueprint_epi(app) para integrar")
