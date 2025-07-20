from flask import Flask
from routes_epi_completo_simples import epi_bp
import sqlite3
import os


def inicializar_epi(app: Flask):
    """
    Inicializar sistema EPI no Flask app existente
    """
    try:
        # Registrar Blueprint
        app.register_blueprint(epi_bp)

        # Criar tabelas se não existirem
        criar_tabelas_epi()

        print("✅ Sistema EPI inicializado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao inicializar sistema EPI: {e}")
        return False


def criar_tabelas_epi():
    """
    Criar tabelas necessárias para o sistema EPI
    """
    try:
        conn = sqlite3.connect('certificados.db')
        cursor = conn.cursor()

        # Tabela de EPIs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS epi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                ca TEXT NOT NULL,
                validade_ca DATE,
                fabricante TEXT,
                tipo_protecao TEXT,
                estoque_atual INTEGER DEFAULT 0,
                estoque_minimo_alerta INTEGER DEFAULT 5,
                descricao TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabela de Declarações de EPI (Entregas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS declaracao_epi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funcionario_id INTEGER NOT NULL,
                epi_id INTEGER NOT NULL,
                data_entrega DATE NOT NULL,
                data_devolucao DATE,
                quantidade INTEGER DEFAULT 1,
                status TEXT DEFAULT 'Entregue',
                validade_prevista DATE,
                observacoes TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios (id),
                FOREIGN KEY (epi_id) REFERENCES epi (id)
            )
        ''')

        # Tabela de Configurações do Sistema EPI
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracao_epi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT UNIQUE NOT NULL,
                valor TEXT,
                tipo TEXT DEFAULT 'string',
                descricao TEXT,
                data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Inserir configurações padrão se não existirem
        configuracoes_padrao = [
            ('estoque_minimo_global', '5', 'integer',
             'Estoque mínimo padrão para novos EPIs'),
            ('dias_alerta_ca_critico', '30', 'integer',
             'Dias para alerta crítico de vencimento de CA'),
            ('dias_alerta_ca_atencao', '90', 'integer',
             'Dias para alerta de atenção de vencimento de CA'),
            ('email_responsavel', '', 'string',
             'Email do responsável pelos alertas'),
            ('nome_empresa', 'Minha Empresa Ltda', 'string', 'Nome da empresa'),
            ('ativo_alerta_estoque', 'true', 'boolean', 'Alertas de estoque ativos'),
            ('ativo_alerta_ca', 'true', 'boolean', 'Alertas de CA ativos'),
        ]

        for config in configuracoes_padrao:
            cursor.execute('''
                INSERT OR IGNORE INTO configuracao_epi (chave, valor, tipo, descricao)
                VALUES (?, ?, ?, ?)
            ''', config)

        conn.commit()
        print("✅ Tabelas EPI criadas/verificadas com sucesso!")

        # Inserir dados de exemplo se as tabelas estão vazias
        inserir_dados_exemplo(cursor, conn)

    except Exception as e:
        print(f"❌ Erro ao criar tabelas EPI: {e}")
    finally:
        conn.close()


def inserir_dados_exemplo(cursor, conn):
    """
    Inserir dados de exemplo para teste
    """
    try:
        # Verificar se já existem EPIs
        count_epis = cursor.execute('SELECT COUNT(*) FROM epi').fetchone()[0]

        if count_epis == 0:
            # Inserir EPIs de exemplo
            epis_exemplo = [
                ('Óculos de Segurança Incolor', '12345', '2025-12-31', '3M',
                 'Visual', 15, 5, 'Óculos de proteção individual contra impactos'),
                ('Luva de Segurança Látex', '67890', '2024-08-30', 'VONDER',
                 'Mãos', 25, 10, 'Luvas de proteção em látex natural'),
                ('Capacete de Segurança Branco', '54321', '2025-06-15', 'MSA',
                 'Cabeça', 8, 3, 'Capacete classe A para proteção da cabeça'),
                ('Protetor Auricular de Inserção', '98765', '2024-12-20',
                 '3M', 'Auditiva', 50, 15, 'Protetor auricular descartável'),
                ('Botina de Segurança', '11111', '2025-03-10', 'MARLUVAS',
                 'Pés', 12, 5, 'Botina de segurança com bico de aço'),
                ('Respirador PFF2', '22222', '2024-09-25', 'DELTAPLUS',
                 'Respiratória', 30, 20, 'Respirador descartável PFF2'),
            ]

            cursor.executemany('''
                INSERT INTO epi (nome, ca, validade_ca, fabricante, tipo_protecao, 
                               estoque_atual, estoque_minimo_alerta, descricao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', epis_exemplo)

            conn.commit()
            print("✅ EPIs de exemplo inseridos!")

    except Exception as e:
        print(f"⚠️ Erro ao inserir dados de exemplo: {e}")


def verificar_sistema_epi():
    """
    Verificar se o sistema EPI está funcionando corretamente
    """
    try:
        conn = sqlite3.connect('certificados.db')
        cursor = conn.cursor()

        # Verificar tabelas
        tabelas = ['epi', 'declaracao_epi', 'configuracao_epi']
        for tabela in tabelas:
            result = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (tabela,)
            ).fetchone()

            if result:
                print(f"✅ Tabela {tabela} encontrada")
            else:
                print(f"❌ Tabela {tabela} não encontrada")
                return False

        # Verificar dados
        count_epis = cursor.execute('SELECT COUNT(*) FROM epi').fetchone()[0]
        print(f"📊 Total de EPIs cadastrados: {count_epis}")

        return True

    except Exception as e:
        print(f"❌ Erro ao verificar sistema EPI: {e}")
        return False
    finally:
        conn.close()


# Para teste direto
if __name__ == "__main__":
    criar_tabelas_epi()
    verificar_sistema_epi()
