#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste com inicialização forçada do módulo EPI
"""

from app import app, db

print("=== TESTE COM INICIALIZAÇÃO FORÇADA ===")

# Forçar inicialização do banco
with app.app_context():
    db.create_all()
    print("✅ Banco de dados inicializado")

    # Inicializar módulo EPI
    try:
        from integracao_epi import init_epi_module
        result = init_epi_module(app)
        print(f"Resultado da inicialização EPI: {result}")
    except Exception as e:
        print(f"❌ Erro ao carregar módulo EPI: {str(e)}")
        import traceback
        traceback.print_exc()

print(f"Blueprints registrados: {list(app.blueprints.keys())}")

if 'epi' in app.blueprints:
    print("✅ Blueprint EPI registrado com sucesso!")
    print(
        f"Rotas do EPI: {[rule.rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith('epi.')]}")
else:
    print("❌ Blueprint EPI NÃO registrado!")

print("=== FIM DO TESTE ===")
