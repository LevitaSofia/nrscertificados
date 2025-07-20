#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de carregamento do módulo EPI
"""

from app import app

print("=== TESTE DE MÓDULO EPI ===")
print(f"Flask app: {app}")
print(f"Blueprints registrados: {list(app.blueprints.keys())}")

if 'epi' in app.blueprints:
    print("✅ Blueprint EPI registrado com sucesso!")
    epi_bp = app.blueprints['epi']
    print(
        f"Rotas do EPI: {[rule.rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith('epi.')]}")
else:
    print("❌ Blueprint EPI NÃO registrado!")

# Testar se conseguimos acessar as rotas
with app.test_client() as client:
    try:
        print("\nTestando rota /epi/:")
        response = client.get('/epi/')
        print(f"Status: {response.status_code}")
        if response.status_code != 404:
            print("✅ Rota /epi/ acessível")
        else:
            print("❌ Rota /epi/ não encontrada")

        print("\nTestando rota /epi/cadastro:")
        response = client.get('/epi/cadastro')
        print(f"Status: {response.status_code}")
        if response.status_code != 404:
            print("✅ Rota /epi/cadastro acessível")
        else:
            print("❌ Rota /epi/cadastro não encontrada")

    except Exception as e:
        print(f"Erro ao testar rotas: {e}")

print("\n=== FIM DO TESTE ===")
