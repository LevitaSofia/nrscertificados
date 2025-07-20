#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, Funcionario
from datetime import datetime


def criar_admin_simples():
    with app.app_context():
        # Remover usuário existente se houver
        admin_existente = Funcionario.query.filter_by(
            cpf='11111111111').first()
        if admin_existente:
            db.session.delete(admin_existente)
            db.session.commit()

        # Criar novo usuário admin
        admin = Funcionario(
            nome='Administrador',
            cpf='11111111111',
            rg='1111111',
            funcao='Administrador',
            email='admin@sistema.com',
            telefone='(11) 11111-1111',
            ativo=True,
            admin=True,
            primeiro_login=False,
            data_admissao=datetime.now().date(),
            data_nascimento=datetime(1990, 1, 1).date()
        )

        # Definir senha simples
        admin.set_password('123')

        db.session.add(admin)
        db.session.commit()

        print("="*50)
        print("✅ USUÁRIO ADMINISTRADOR CRIADO!")
        print("="*50)
        print("🔑 CREDENCIAIS DE ACESSO:")
        print("   CPF: 11111111111")
        print("   Senha: 123")
        print("="*50)
        print("🌐 URL de acesso:")
        print("   http://127.0.0.1:5000/login")
        print("="*50)


if __name__ == "__main__":
    criar_admin_simples()
