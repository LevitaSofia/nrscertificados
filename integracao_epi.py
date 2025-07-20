"""
Integração do módulo de Gestão de EPIs com o app principal
"""
from flask import Blueprint
import os


def init_epi_module(app):
    """
    Inicializa o módulo de Gestão de EPIs no app principal
    """
    try:
        # Verificar se já foi inicializado
        if hasattr(app, '_epi_initialized'):
            print("✅ Módulo de Gestão de EPIs já foi inicializado anteriormente!")
            return True

        # Marcar como inicializado
        app._epi_initialized = True

        # Importar o db e modelos do app principal
        from app import db
        from models_epi import create_epi_models
        epi_models = create_epi_models(db)
        globals().update(epi_models)

        # Importar e configurar as rotas
        import routes_epi
        routes_epi.EPI = epi_models['EPI']
        routes_epi.DeclaracaoEPI = epi_models['DeclaracaoEPI']
        routes_epi.EntregaEPI = epi_models['EntregaEPI']
        routes_epi.AlertaEPI = epi_models['AlertaEPI']
        routes_epi.LogValidacaoCA = epi_models['LogValidacaoCA']
        routes_epi.ConfiguracaoEPI = epi_models['ConfiguracaoEPI']
        routes_epi.db = db
        from app import Funcionario
        routes_epi.Funcionario = Funcionario

        # Registrar o blueprint apenas se ainda não estiver registrado
        if 'epi' not in app.blueprints:
            from routes_epi import epi_bp
            app.register_blueprint(epi_bp)
            print("✅ Blueprint 'epi' registrado com sucesso!")
        else:
            print("🔵 Blueprint 'epi' já estava registrado.")

        # Criar as tabelas EPI no banco
        print("📊 Criando tabelas do módulo EPI...")
        db.create_all()

        print("⚙️ Inserindo configurações padrão...")
        try:
            inserir_configuracoes_padrao(epi_models['ConfiguracaoEPI'])
        except Exception as config_error:
            print(
                f"⚠️ Aviso: Erro ao inserir configurações padrão: {config_error}")

        print("✅ Módulo de Gestão de EPIs inicializado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao inicializar módulo de EPIs: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def inserir_configuracoes_padrao(ConfiguracaoEPI):
    """
    Insere configurações padrão do sistema se não existirem
    """
    from app import db

    configuracoes_padrao = [
        # Alertas
        ('alertas_ativos', 'true', 'Sistema de alertas automáticos ativo', 'boolean'),
        ('dias_alerta_vencimento', '30',
         'Dias de antecedência para alertar vencimento CA', 'integer'),
        ('frequencia_verificacao', 'diaria',
         'Frequência de verificação de alertas', 'string'),
        ('alerta_vencimento_ca', 'true', 'Alertar vencimento de CA', 'boolean'),
        ('alerta_estoque_baixo', 'true', 'Alertar estoque baixo', 'boolean'),
        ('alerta_devolucao_atraso', 'true',
         'Alertar devolução em atraso', 'boolean'),

        # E-mails
        ('emails_ativos', 'false', 'Envio de e-mails ativo', 'boolean'),
        ('smtp_servidor', '', 'Servidor SMTP para envio de e-mails', 'string'),
        ('smtp_porta', '587', 'Porta SMTP', 'integer'),
        ('email_remetente', '', 'E-mail remetente', 'string'),
        ('senha_email', '', 'Senha do e-mail remetente', 'string'),
        ('emails_destinatarios', '',
         'E-mails destinatários (separados por vírgula)', 'string'),
        ('email_ssl', 'true', 'Usar SSL/TLS', 'boolean'),

        # API Externa
        ('api_ca_ativa', 'false', 'API de validação de CA ativa', 'boolean'),
        ('api_ca_url', 'https://api.trabalho.gov.br/ca/validar',
         'URL da API de validação CA', 'string'),
        ('api_ca_token', '', 'Token de autenticação da API', 'string'),
        ('api_ca_timeout', '30', 'Timeout da API em segundos', 'integer'),
        ('api_ca_cache', 'true', 'Cache de resultados da API', 'boolean'),

        # Backup
        ('backup_frequencia', 'semanal', 'Frequência de backup automático', 'string'),
        ('backup_retencao', '30', 'Dias para manter backups', 'integer'),

        # Sistema
        ('empresa_nome', '', 'Nome da empresa', 'string'),
        ('empresa_cnpj', '', 'CNPJ da empresa', 'string'),
        ('empresa_endereco', '', 'Endereço da empresa', 'string'),
        ('logo_empresa', '', 'URL do logo da empresa', 'string'),
        ('cor_tema', '#007bff', 'Cor do tema do sistema', 'string'),
        ('debug_mode', 'false', 'Modo debug ativo', 'boolean'),
        ('manutencao', 'false', 'Modo manutenção ativo', 'boolean'),
        ('logs_detalhados', 'false', 'Logs detalhados ativos', 'boolean'),
    ]

    for chave, valor, descricao, tipo in configuracoes_padrao:
        try:
            config_existente = ConfiguracaoEPI.query.filter_by(
                chave=chave).first()
            if not config_existente:
                ConfiguracaoEPI.set_config(chave, valor, descricao, tipo)
        except Exception as e:
            print(f"⚠️ Erro ao inserir configuração {chave}: {e}")
            # Criar manualmente se o método set_config falhar
            try:
                config = ConfiguracaoEPI(
                    chave=chave,
                    valor=valor,
                    descricao=descricao,
                    tipo_dado=tipo
                )
                db.session.add(config)
                db.session.commit()
            except Exception as e2:
                print(f"⚠️ Erro ao inserir configuração manual {chave}: {e2}")
                continue

    print("✅ Configurações padrão do módulo EPI inseridas")


# Importar as rotas após a criação do blueprint


def criar_diretorios_epi():
    """
    Cria diretórios necessários para o módulo EPI
    """
    diretorios = [
        'static/epi_images',
        'static/epi_uploads',
        'static/epi_backups',
        'static/epi_exports',
        'static/epi_pdfs'
    ]

    for diretorio in diretorios:
        caminho = os.path.join(os.getcwd(), diretorio)
        os.makedirs(caminho, exist_ok=True)

    print("✅ Diretórios do módulo EPI criados")


def adicionar_menu_principal():
    """
    Retorna os itens de menu para adicionar ao menu principal do sistema
    """
    return {
        'nome': 'Gestão de EPIs',
        'icone': 'fas fa-hard-hat',
        'url': 'epi.index',
        'permissao': 'epi_visualizar',
        'submenus': [
            {
                'nome': 'Dashboard',
                'url': 'epi.index',
                'icone': 'fas fa-tachometer-alt'
            },
            {
                'nome': 'Lista de EPIs',
                'url': 'epi.cadastro',
                'icone': 'fas fa-list'
            },
            {
                'nome': 'Cadastrar EPI',
                'url': 'epi.novo',
                'icone': 'fas fa-plus'
            },
            {
                'nome': 'Gestão de Entregas',
                'url': 'epi.gestao_entregas',
                'icone': 'fas fa-hand-holding'
            },
            {
                'nome': 'Relatórios',
                'url': 'epi.relatorios',
                'icone': 'fas fa-chart-bar'
            },
            {
                'nome': 'Configurações',
                'url': 'epi.configuracoes',
                'icone': 'fas fa-cogs'
            }
        ]
    }


def verificar_permissoes_usuario(usuario, acao):
    """
    Verifica se o usuário tem permissão para determinada ação no módulo EPI
    """
    permissoes_map = {
        'visualizar': 'perm_epi_visualizar',
        'cadastrar': 'perm_epi_cadastrar',
        'editar': 'perm_epi_editar',
        'excluir': 'perm_epi_excluir',
        'relatorios': 'perm_epi_relatorios',
        'configuracoes': 'perm_epi_configuracoes'
    }

    permissao = permissoes_map.get(acao)
    if not permissao:
        return False

    return hasattr(usuario, permissao) and getattr(usuario, permissao, False)

# Jobs automáticos para execução em background


def configurar_jobs_automaticos():
    """
    Configura jobs automáticos do módulo EPI
    """
    import schedule
    import time
    import threading
    from services_epi import AlertaService

    def job_alertas():
        """Job para gerar alertas automáticos"""
        try:
            AlertaService.gerar_alertas_automaticos()
            print(
                f"✅ Alertas automáticos processados - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"❌ Erro ao processar alertas: {str(e)}")

    def job_backup():
        """Job para backup automático"""
        try:
            from services_epi import BackupService
            BackupService.criar_backup_automatico()
            print(
                f"✅ Backup automático executado - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"❌ Erro ao executar backup: {str(e)}")

    def job_limpeza():
        """Job para limpeza de arquivos antigos"""
        try:
            from services_epi import LimpezaService
            LimpezaService.limpar_arquivos_antigos()
            print(
                f"✅ Limpeza automática executada - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"❌ Erro na limpeza: {str(e)}")

    # Configurar agendamentos
    schedule.every().day.at("08:00").do(job_alertas)  # Alertas diários às 8h
    schedule.every().sunday.at("02:00").do(job_backup)  # Backup semanal domingo 2h
    schedule.every().day.at("23:00").do(job_limpeza)  # Limpeza diária às 23h

    def executar_jobs():
        """Executa os jobs agendados em thread separada"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto

    # Executar em thread para não bloquear o app principal
    thread_jobs = threading.Thread(target=executar_jobs, daemon=True)
    thread_jobs.start()

    print("✅ Jobs automáticos do módulo EPI configurados")

# Context processors para templates


def adicionar_context_processors(app):
    """
    Adiciona context processors para disponibilizar dados globais nos templates
    """

    @app.context_processor
    def epi_context():
        """Dados globais do módulo EPI disponíveis em todos os templates"""
        try:
            from models_epi import EPI, AlertaEPI, ConfiguracaoEPI

            # Estatísticas básicas
            total_epis = EPI.query.filter_by(status='ativo').count()
            alertas_pendentes = AlertaEPI.query.filter_by(
                status='ativo').count()

            # Configurações importantes
            empresa_nome = ConfiguracaoEPI.get_config(
                'empresa_nome', 'Sistema de Gestão')
            logo_empresa = ConfiguracaoEPI.get_config('logo_empresa', '')

            return {
                'epi_stats': {
                    'total_epis': total_epis,
                    'alertas_pendentes': alertas_pendentes
                },
                'epi_config': {
                    'empresa_nome': empresa_nome,
                    'logo_empresa': logo_empresa
                }
            }
        except Exception:
            # Em caso de erro, retorna dados padrão
            return {
                'epi_stats': {
                    'total_epis': 0,
                    'alertas_pendentes': 0
                },
                'epi_config': {
                    'empresa_nome': 'Sistema de Gestão',
                    'logo_empresa': ''
                }
            }

# Filtros personalizados para templates


def adicionar_template_filters(app):
    """
    Adiciona filtros personalizados para os templates do módulo EPI
    """

    @app.template_filter('formatar_cpf')
    def formatar_cpf(cpf):
        """Formata CPF para exibição"""
        from services_epi import formatar_cpf
        return formatar_cpf(cpf)

    @app.template_filter('status_validade_ca')
    def status_validade_ca(data_validade):
        """Retorna o status da validade do CA"""
        from datetime import date
        if not data_validade:
            return 'sem_data'

        dias_para_vencer = (data_validade - date.today()).days

        if dias_para_vencer < 0:
            return 'vencido'
        elif dias_para_vencer <= 30:
            return 'vencendo'
        else:
            return 'valido'

    @app.template_filter('status_estoque')
    def status_estoque(atual, minimo):
        """Retorna o status do estoque"""
        if atual <= 0:
            return 'sem_estoque'
        elif atual <= minimo:
            return 'baixo'
        else:
            return 'ok'

    @app.template_filter('moeda_br')
    def moeda_br(valor):
        """Formata valor para moeda brasileira"""
        if valor is None:
            return 'R$ 0,00'
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Função principal de inicialização


def inicializar_modulo_epi(app):
    """
    Função principal para inicializar completamente o módulo de Gestão de EPIs
    """
    print("🚀 Inicializando módulo de Gestão de EPIs...")

    try:
        # 1. Criar diretórios necessários
        criar_diretorios_epi()

        # 2. Inicializar módulo e banco de dados
        if not init_epi_module(app):
            return False

        # 3. Adicionar context processors
        adicionar_context_processors(app)

        # 4. Adicionar filtros de template
        adicionar_template_filters(app)

        # 5. Configurar jobs automáticos (opcional, pode ser desabilitado)
        try:
            configurar_jobs_automaticos()
        except Exception as e:
            print(f"⚠️ Jobs automáticos não configurados: {str(e)}")

        print("✅ Módulo de Gestão de EPIs inicializado com sucesso!")
        print("📋 Funcionalidades disponíveis:")
        print("   - Dashboard de EPIs")
        print("   - Cadastro e gestão de EPIs")
        print("   - Controle de entregas e devoluções")
        print("   - Validação de CAs via API")
        print("   - Geração de declarações em PDF")
        print("   - Relatórios de vencimentos e estoque")
        print("   - Sistema de alertas automáticos")
        print("   - Configurações avançadas")
        print("   - Backup automático")
        print("   - Integração com sistema principal")

        return True

    except Exception as e:
        print(f"❌ Erro crítico ao inicializar módulo de EPIs: {str(e)}")
        return False


# Exemplo de uso no app.py principal:
"""
from integracao_epi import inicializar_modulo_epi, adicionar_menu_principal

# No seu app.py, após criar o app Flask:
if __name__ == '__main__':
    # Inicializar módulo de EPIs
    inicializar_modulo_epi(app)
    
    # Adicionar ao menu principal (se aplicável)
    menu_epi = adicionar_menu_principal()
    # ... integrar com seu sistema de menu
    
    app.run(debug=True)
"""
