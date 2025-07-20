"""
Integração simplificada do módulo de Gestão de EPIs
"""
from flask import Blueprint


def init_epi_module_simple(app):
    """
    Inicializa o módulo de Gestão de EPIs no app principal - Versão Simplificada
    """
    try:
        # Verificar se já foi inicializado
        if hasattr(app, '_epi_initialized'):
            print("✅ Módulo de Gestão de EPIs já foi inicializado anteriormente!")
            return True

        # Marcar como inicializado
        app._epi_initialized = True

        # Registrar o blueprint apenas se ainda não estiver registrado
        if 'epi' not in app.blueprints:
            from routes_epi import epi_bp
            app.register_blueprint(epi_bp)
            print("✅ Blueprint 'epi' registrado com sucesso!")
        else:
            print("🔵 Blueprint 'epi' já estava registrado.")

        print("✅ Módulo de Gestão de EPIs inicializado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao inicializar módulo de EPIs: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
