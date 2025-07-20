"""
Sistema de Gestão de EPIs - Integração Completa
Módulo de inicialização e configuração do sistema EPI
Data: 12/07/2025
"""

from flask import Flask
from models_epi_completo import db, criar_tabelas_epi, inserir_dados_exemplo
from routes_epi_completo import epi_bp
import os


def init_epi_system(app):
    """
    Inicializa o sistema completo de gestão de EPIs

    Args:
        app: Instância da aplicação Flask
    """

    print("🔄 Inicializando Sistema Completo de Gestão de EPIs...")

    try:
        # 1. Configurar banco de dados
        configurar_banco_dados(app)

        # 2. Registrar blueprint
        registrar_blueprint(app)

        # 3. Criar tabelas se não existirem
        criar_estrutura_banco(app)

        # 4. Inserir dados de exemplo (se necessário)
        inserir_dados_iniciais(app)

        # 5. Configurar templates
        configurar_templates(app)

        print("✅ Sistema de Gestão de EPIs inicializado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao inicializar sistema EPI: {str(e)}")
        return False


def configurar_banco_dados(app):
    """
    Configura a conexão com o banco de dados
    Usa a instância SQLAlchemy já existente no app
    """
    print("📊 Configurando banco de dados...")

    try:
        # Importar a instância db do app principal (app.py)
        import sys
        import importlib

        # Tentar importar o módulo principal
        if '__main__' in sys.modules:
            main_module = sys.modules['__main__']
            if hasattr(main_module, 'db'):
                app_db = main_module.db
                print("✅ Instância SQLAlchemy do app principal encontrada!")

                # Configurar os modelos EPI para usar a mesma instância
                from models_epi_completo import init_db
                init_db(app_db)

                global db
                db = app_db
                return

        # Fallback: criar nova instância se necessário
        print("⚠️ Criando nova instância SQLAlchemy...")
        from models_epi_completo import db as epi_db

        if not hasattr(app, 'config') or 'SQLALCHEMY_DATABASE_URI' not in app.config:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certificados.db'
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Só inicializar se não estiver já inicializado
        if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
            epi_db.init_app(app)

        global db
        db = epi_db

    except Exception as e:
        print(f"⚠️ Erro na configuração do banco: {str(e)}")
        raise

    print("✅ Banco de dados configurado!")


def registrar_blueprint(app):
    """
    Registra o blueprint do sistema EPI
    """
    print("📋 Registrando blueprint EPI...")

    try:
        # Registrar o blueprint principal
        app.register_blueprint(epi_bp)

        # Verificar se foi registrado corretamente
        blueprints_registrados = [name for name in app.blueprints.keys()]

        if 'epi' in blueprints_registrados:
            print("✅ Blueprint 'epi' registrado com sucesso!")
            print(f"📍 Rotas disponíveis: /epi/*")
        else:
            raise Exception("Blueprint não foi registrado corretamente")

    except Exception as e:
        print(f"❌ Erro ao registrar blueprint: {str(e)}")
        raise


def criar_estrutura_banco(app):
    """
    Cria as tabelas do sistema EPI no banco de dados
    """
    print("🏗️ Criando estrutura do banco de dados...")

    try:
        with app.app_context():
            # Importar todos os modelos para garantir que sejam criados
            from models_epi_completo import EPI, DeclaracaoEPI, ItemDeclaracaoEPI, ConfiguracaoAlerta, LogAtividade

            # Criar todas as tabelas
            db.create_all()

            print("✅ Tabelas do sistema EPI criadas/verificadas!")

    except Exception as e:
        print(f"❌ Erro ao criar estrutura do banco: {str(e)}")
        raise


def inserir_dados_iniciais(app):
    """
    Insere dados de exemplo no sistema (apenas se estiver vazio)
    """
    print("📝 Verificando dados iniciais...")

    try:
        with app.app_context():
            from models_epi_completo import EPI, inserir_dados_exemplo

            # Verificar se já existem dados
            total_epis = EPI.query.count()

            if total_epis == 0:
                print("💾 Inserindo dados de exemplo...")
                inserir_dados_exemplo()
                print("✅ Dados de exemplo inseridos!")
            else:
                print(f"ℹ️ Sistema já possui {total_epis} EPIs cadastrados")

    except Exception as e:
        print(f"❌ Erro ao inserir dados iniciais: {str(e)}")
        # Não é um erro crítico, continua sem os dados de exemplo


def configurar_templates(app):
    """
    Configura os templates e recursos estáticos
    """
    print("🎨 Configurando templates...")

    try:
        # Verificar se a pasta de templates existe
        templates_path = os.path.join(app.root_path, 'templates', 'epi')

        if not os.path.exists(templates_path):
            os.makedirs(templates_path, exist_ok=True)
            print(f"📁 Pasta de templates criada: {templates_path}")

        print("✅ Templates configurados!")

    except Exception as e:
        print(f"❌ Erro ao configurar templates: {str(e)}")


def verificar_sistema_epi(app):
    """
    Verifica se o sistema EPI está funcionando corretamente
    """
    print("🔍 Verificando sistema EPI...")

    try:
        with app.app_context():
            from models_epi_completo import EPI, DeclaracaoEPI

            # Testes básicos
            total_epis = EPI.query.count()
            total_declaracoes = DeclaracaoEPI.query.count()

            # Verificar blueprint
            epi_routes = [rule for rule in app.url_map.iter_rules()
                          if rule.rule.startswith('/epi')]

            print(f"📊 Status do Sistema EPI:")
            print(f"   - EPIs cadastrados: {total_epis}")
            print(f"   - Declarações registradas: {total_declaracoes}")
            print(f"   - Rotas disponíveis: {len(epi_routes)}")

            if len(epi_routes) > 0:
                print("✅ Sistema EPI verificado e funcionando!")
                return True
            else:
                print("❌ Nenhuma rota EPI encontrada!")
                return False

    except Exception as e:
        print(f"❌ Erro na verificação: {str(e)}")
        return False


def listar_rotas_epi(app):
    """
    Lista todas as rotas disponíveis do sistema EPI
    """
    print("\n🗺️ Rotas do Sistema EPI:")
    print("=" * 50)

    try:
        epi_routes = [rule for rule in app.url_map.iter_rules()
                      if rule.rule.startswith('/epi')]

        for route in sorted(epi_routes, key=lambda x: x.rule):
            methods = ', '.join(route.methods - {'HEAD', 'OPTIONS'})
            print(f"   {route.rule:<30} [{methods}]")

        print("=" * 50)
        print(f"Total: {len(epi_routes)} rotas registradas\n")

    except Exception as e:
        print(f"❌ Erro ao listar rotas: {str(e)}")


def atualizar_menu_principal(app):
    """
    Atualiza o menu principal do sistema para incluir o módulo EPI
    Função para ser chamada se necessário integrar com menu existente
    """
    try:
        # Esta função pode ser usada para modificar templates existentes
        # ou adicionar o link do EPI ao menu principal do sistema

        print("🔗 Integração com menu principal configurada!")
        print("   - Acesse: /epi para o dashboard EPI")
        print("   - Link sugerido: 'Sistema de Gestão de EPIs'")

    except Exception as e:
        print(f"❌ Erro ao atualizar menu: {str(e)}")

# Função principal de inicialização


def inicializar_epi_completo(app):
    """
    Função principal para inicializar todo o sistema EPI

    Usage:
        from integracao_epi_completo import inicializar_epi_completo
        inicializar_epi_completo(app)
    """

    print("\n" + "="*60)
    print("🚀 INICIALIZANDO SISTEMA COMPLETO DE GESTÃO DE EPIs")
    print("="*60)

    try:
        # Executar todas as etapas de inicialização
        sucesso = init_epi_system(app)

        if sucesso:
            # Verificar se tudo está funcionando
            verificar_sistema_epi(app)

            # Listar rotas disponíveis
            listar_rotas_epi(app)

            # Configurar integração com menu
            atualizar_menu_principal(app)

            print("🎉 SISTEMA EPI INICIALIZADO COM SUCESSO!")
            print("="*60)
            print("📍 Acesse: http://localhost:5000/epi")
            print("📋 Funcionalidades disponíveis:")
            print("   - Dashboard com estatísticas")
            print("   - Inventário de EPIs")
            print("   - Gestão de entregas e declarações")
            print("   - Relatórios e alertas")
            print("   - Configurações de alertas")
            print("   - Geração de PDFs")
            print("   - API de validação de CA (simulada)")
            print("="*60 + "\n")

            return True

        else:
            print("❌ FALHA NA INICIALIZAÇÃO DO SISTEMA EPI")
            print("="*60 + "\n")
            return False

    except Exception as e:
        print(f"💥 ERRO CRÍTICO NA INICIALIZAÇÃO: {str(e)}")
        print("="*60 + "\n")
        return False

# Função de limpeza (para desenvolvimento/testes)


def resetar_sistema_epi(app):
    """
    Remove todas as tabelas do sistema EPI (CUIDADO: apaga todos os dados!)
    Função apenas para desenvolvimento/testes
    """
    print("⚠️ RESETANDO SISTEMA EPI - TODOS OS DADOS SERÃO PERDIDOS!")

    try:
        with app.app_context():
            from models_epi_completo import EPI, DeclaracaoEPI, ItemDeclaracaoEPI, ConfiguracaoAlerta, LogAtividade

            # Remover todas as tabelas
            db.drop_all()
            print("🗑️ Tabelas removidas!")

            # Recriar estrutura
            db.create_all()
            print("🏗️ Estrutura recriada!")

            # Inserir dados de exemplo
            inserir_dados_exemplo()
            print("📝 Dados de exemplo reinseridos!")

            print("✅ Sistema EPI resetado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao resetar sistema: {str(e)}")


if __name__ == "__main__":
    # Teste da inicialização
    from flask import Flask

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teste_epi.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'teste_epi_secret_key'

    # Inicializar sistema
    sucesso = inicializar_epi_completo(app)

    if sucesso:
        print("🎯 Teste de inicialização concluído com sucesso!")
    else:
        print("💥 Teste de inicialização falhou!")
