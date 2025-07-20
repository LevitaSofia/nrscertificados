"""
Sistema de Gestão de EPIs - Integração Simplificada
Versão que evita conflitos com SQLAlchemy existente
Data: 12/07/2025
"""


def inicializar_epi_simplificado(app):
    """
    Inicialização simplificada do sistema EPI
    Evita conflitos com SQLAlchemy já existente
    """

    print("\n" + "="*60)
    print("🚀 INICIALIZANDO SISTEMA SIMPLIFICADO DE GESTÃO DE EPIs")
    print("="*60)

    try:
        # 1. Registrar blueprint usando a instância existente do SQLAlchemy
        print("📋 Registrando blueprint EPI...")

        # Importar e configurar modelos usando o db do app principal
        configurar_modelos_epi(app)

        # Registrar blueprint
        from routes_epi_simplificado import criar_blueprint_epi
        epi_bp = criar_blueprint_epi(app)
        app.register_blueprint(epi_bp)

        print("✅ Blueprint EPI registrado com sucesso!")

        # 2. Criar tabelas se necessário
        with app.app_context():
            criar_tabelas_epi_simplificado(app)

        print("🎉 SISTEMA EPI SIMPLIFICADO INICIALIZADO COM SUCESSO!")
        print("="*60)
        print("📍 Acesse: http://localhost:5000/epi")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print(f"❌ ERRO NA INICIALIZAÇÃO: {str(e)}")
        print("="*60 + "\n")
        return False


def configurar_modelos_epi(app):
    """
    Configura os modelos EPI usando a instância SQLAlchemy existente
    """
    try:
        # Importar a instância db do app principal
        import sys
        main_module = sys.modules.get('__main__')

        if main_module and hasattr(main_module, 'db'):
            app_db = main_module.db

            # Definir modelos EPI usando a instância existente
            definir_modelos_epi(app_db)

            print("✅ Modelos EPI configurados com instância existente!")
        else:
            raise Exception(
                "Instância SQLAlchemy não encontrada no app principal")

    except Exception as e:
        print(f"❌ Erro ao configurar modelos: {str(e)}")
        raise


def definir_modelos_epi(db):
    """
    Define os modelos EPI usando a instância db fornecida
    """
    from datetime import datetime, timedelta

    # Definir modelos diretamente usando a instância db
    class EPI(db.Model):
        __tablename__ = 'epis'

        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(200), nullable=False)
        descricao = db.Column(db.Text)
        ca = db.Column(db.String(20), nullable=False, unique=True)
        validade_ca = db.Column(db.Date, nullable=False)
        fabricante = db.Column(db.String(100))
        tipo_protecao = db.Column(db.String(50))
        estoque_atual = db.Column(db.Integer, default=0)
        estoque_minimo_alerta = db.Column(db.Integer, default=5)
        data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
        ativo = db.Column(db.Boolean, default=True)

        def __repr__(self):
            return f'<EPI {self.nome} - CA: {self.ca}>'

    class DeclaracaoEPI(db.Model):
        __tablename__ = 'declaracoes_epi'

        id = db.Column(db.Integer, primary_key=True)
        funcionario_id = db.Column(db.String(50), nullable=False)
        funcionario_nome = db.Column(db.String(200), nullable=False)
        data_declaracao = db.Column(
            db.Date, nullable=False, default=datetime.utcnow)
        declaracao_nr06_aceita = db.Column(db.Boolean, default=False)
        orientacao_riscos_aceita = db.Column(db.Boolean, default=False)
        data_registro = db.Column(db.DateTime, default=datetime.utcnow)
        status = db.Column(db.String(20), default='ativa')

        def __repr__(self):
            return f'<DeclaracaoEPI {self.funcionario_nome} - {self.data_declaracao}>'

    # Disponibilizar modelos globalmente
    import sys
    sys.modules[__name__].EPI = EPI
    sys.modules[__name__].DeclaracaoEPI = DeclaracaoEPI


def criar_tabelas_epi_simplificado(app):
    """
    Cria as tabelas EPI se não existirem
    """
    try:
        import sys
        main_module = sys.modules.get('__main__')

        if main_module and hasattr(main_module, 'db'):
            db = main_module.db
            db.create_all()
            print("✅ Tabelas EPI verificadas/criadas!")
        else:
            print("❌ Instância db não encontrada")

    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {str(e)}")

# Dados de exemplo simples


def inserir_dados_exemplo_simples(app):
    """
    Insere alguns EPIs de exemplo
    """
    try:
        with app.app_context():
            # Verificar se já existem dados
            EPI = getattr(sys.modules[__name__], 'EPI', None)
            if EPI and EPI.query.count() == 0:
                from datetime import datetime

                epi1 = EPI(
                    nome='Óculos de Segurança',
                    ca='12345',
                    validade_ca=datetime(2030, 12, 31).date(),
                    estoque_atual=50
                )

                epi2 = EPI(
                    nome='Protetor Auricular',
                    ca='23456',
                    validade_ca=datetime(2029, 6, 15).date(),
                    estoque_atual=100
                )

                import sys
                main_module = sys.modules.get('__main__')
                if main_module and hasattr(main_module, 'db'):
                    db = main_module.db
                    db.session.add(epi1)
                    db.session.add(epi2)
                    db.session.commit()
                    print("✅ Dados de exemplo inseridos!")

    except Exception as e:
        print(f"❌ Erro ao inserir dados: {str(e)}")


if __name__ == "__main__":
    print("🧪 Teste do módulo de integração EPI simplificado")
    print("Use inicializar_epi_simplificado(app) para integrar ao Flask")
