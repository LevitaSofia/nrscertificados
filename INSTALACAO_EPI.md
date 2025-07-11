# 📋 Guia de Instalação e Configuração - Módulo de Gestão de EPIs

## 🎯 Visão Geral

Este documento fornece instruções completas para instalar e configurar o módulo de Gestão de EPIs no seu sistema existente de gerenciamento de funcionários.

## 📁 Estrutura dos Arquivos

```
certificados-nr/
├── models_epi.py              # Modelos de dados do módulo EPI
├── routes_epi.py              # Rotas e endpoints do módulo
├── services_epi.py            # Serviços auxiliares e lógica de negócio
├── integracao_epi.py          # Arquivo de integração com o app principal
├── requirements.txt           # Dependências atualizadas
├── templates/epi/             # Templates HTML do módulo
│   ├── index.html            # Dashboard principal
│   ├── cadastro_epi.html     # Lista e busca de EPIs
│   ├── novo_epi.html         # Cadastro de novo EPI
│   ├── editar_epi.html       # Edição de EPI
│   ├── gestao_entregas.html  # Gestão de entregas
│   ├── historico_epi.html    # Histórico detalhado
│   ├── relatorios.html       # Relatórios e gráficos
│   └── configuracoes.html    # Configurações do sistema
└── docs/
    └── gestao_epi_requisitos.md  # Documento de requisitos
```

## 🛠️ Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados

#### Para SQLite (padrão):
```python
# No seu app.py, certifique-se de ter:
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/certificados.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

#### Para PostgreSQL (recomendado para produção):
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/database_name'
```

#### Para MySQL:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/database_name'
```

### 3. Integrar com o App Principal

#### Opção A: Integração Automática (Recomendada)

```python
# No seu app.py principal, adicione:
from integracao_epi import inicializar_modulo_epi

# Após criar o app Flask e configurar o banco:
app = Flask(__name__)
# ... suas configurações existentes ...

# Inicializar módulo de EPIs
if inicializar_modulo_epi(app):
    print("✅ Módulo de Gestão de EPIs carregado com sucesso!")
else:
    print("❌ Erro ao carregar módulo de EPIs")

if __name__ == '__main__':
    app.run(debug=True)
```

#### Opção B: Integração Manual

```python
# No seu app.py principal:
from models_epi import *
from routes_epi import epi_bp

# Registrar o blueprint
app.register_blueprint(epi_bp)

# Criar tabelas do banco
with app.app_context():
    db.create_all()
```

### 4. Configurar Permissões de Usuário

Adicione as seguintes colunas à sua tabela de usuários:

```sql
ALTER TABLE usuarios ADD COLUMN perm_epi_visualizar BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN perm_epi_cadastrar BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN perm_epi_editar BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN perm_epi_excluir BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN perm_epi_relatorios BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN perm_epi_configuracoes BOOLEAN DEFAULT FALSE;
```

### 5. Criar Diretórios Necessários

O sistema criará automaticamente os diretórios necessários, mas você pode criá-los manualmente:

```bash
mkdir -p static/epi_images
mkdir -p static/epi_uploads
mkdir -p static/epi_backups
mkdir -p static/epi_exports
mkdir -p static/epi_pdfs
```

## ⚙️ Configuração

### 1. Configurações Básicas

Acesse `/epi/configuracoes` para configurar:

#### Sistema:
- Nome da empresa
- CNPJ
- Endereço
- Logo (URL)
- Cor do tema

#### Alertas:
- Dias de antecedência para alertar vencimento CA (padrão: 30)
- Frequência de verificação (diária/semanal/mensal)
- Tipos de alertas (vencimento CA, estoque baixo, devolução atrasada)

#### E-mails:
- Servidor SMTP
- Porta (padrão: 587)
- E-mail remetente
- Senha
- E-mails destinatários
- SSL/TLS

#### API Externa:
- URL da API de validação de CA
- Token de autenticação
- Timeout
- Cache de resultados

### 2. Configurações Avançadas

#### Backup Automático:
```python
# Configurar no arquivo integracao_epi.py
BACKUP_FREQUENCIA = 'semanal'  # diario, semanal, mensal
BACKUP_RETENCAO = 30  # dias para manter backups
```

#### Jobs Automáticos:
```python
# Os jobs são configurados automaticamente:
# - Alertas: diário às 8h
# - Backup: domingo às 2h
# - Limpeza: diário às 23h
```

## 🔗 Integração com Menu Principal

### Adicionar ao Menu do Sistema

```python
# No seu template base, adicione:
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
        <i class="fas fa-hard-hat"></i> EPIs
    </a>
    <ul class="dropdown-menu">
        <li><a class="dropdown-item" href="{{ url_for('epi.index') }}">
            <i class="fas fa-tachometer-alt"></i> Dashboard
        </a></li>
        <li><a class="dropdown-item" href="{{ url_for('epi.cadastro') }}">
            <i class="fas fa-list"></i> Lista de EPIs
        </a></li>
        <li><a class="dropdown-item" href="{{ url_for('epi.novo') }}">
            <i class="fas fa-plus"></i> Cadastrar EPI
        </a></li>
        <li><a class="dropdown-item" href="{{ url_for('epi.gestao_entregas') }}">
            <i class="fas fa-hand-holding"></i> Gestão de Entregas
        </a></li>
        <li><a class="dropdown-item" href="{{ url_for('epi.relatorios') }}">
            <i class="fas fa-chart-bar"></i> Relatórios
        </a></li>
        <li><a class="dropdown-item" href="{{ url_for('epi.configuracoes') }}">
            <i class="fas fa-cogs"></i> Configurações
        </a></li>
    </ul>
</li>
```

### Dashboard Principal

```python
# No seu dashboard principal, adicione widgets:
{% if current_user.perm_epi_visualizar %}
<div class="col-md-3">
    <div class="card bg-primary text-white">
        <div class="card-body">
            <div class="d-flex justify-content-between">
                <div>
                    <h6>EPIs Cadastrados</h6>
                    <h3>{{ epi_stats.total_epis }}</h3>
                </div>
                <div>
                    <i class="fas fa-hard-hat fa-2x"></i>
                </div>
            </div>
            <a href="{{ url_for('epi.index') }}" class="btn btn-light btn-sm mt-2">
                Ver Detalhes
            </a>
        </div>
    </div>
</div>
{% endif %}
```

## 🔐 Controle de Acesso

### Verificação de Permissões

```python
from integracao_epi import verificar_permissoes_usuario

# Em suas rotas:
@app.route('/alguma-rota')
@login_required
def minha_rota():
    if not verificar_permissoes_usuario(current_user, 'visualizar'):
        abort(403)
    
    # Sua lógica aqui...
```

### Decorador de Permissão

```python
from functools import wraps
from flask import abort
from flask_login import current_user

def requer_permissao_epi(acao):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not verificar_permissoes_usuario(current_user, acao):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Uso:
@app.route('/epi/nova-funcionalidade')
@login_required
@requer_permissao_epi('editar')
def nova_funcionalidade():
    pass
```

## 📊 Funcionalidades Principais

### 1. Gestão de EPIs
- ✅ Cadastro completo de EPIs
- ✅ Validação de CA via API
- ✅ Controle de estoque
- ✅ Upload de imagens
- ✅ Status de validade automático

### 2. Gestão de Entregas
- ✅ Entrega para funcionários
- ✅ Geração de declarações PDF
- ✅ Controle de devoluções
- ✅ Histórico completo

### 3. Relatórios
- ✅ Vencimentos de CA
- ✅ Controle de estoque
- ✅ Entregas por período
- ✅ Análise por categoria
- ✅ Exportação Excel/PDF

### 4. Alertas Automáticos
- ✅ Vencimento de CA
- ✅ Estoque baixo
- ✅ Devoluções atrasadas
- ✅ Notificações por e-mail

### 5. Configurações
- ✅ Personalização completa
- ✅ Backup automático
- ✅ Controle de usuários
- ✅ Integração com APIs

## 🚀 Primeiros Passos

### 1. Após a Instalação

1. Acesse `/epi` para ver o dashboard
2. Configure o sistema em `/epi/configuracoes`
3. Cadastre o primeiro EPI em `/epi/novo`
4. Configure permissões de usuários
5. Teste a funcionalidade de entregas

### 2. Dados de Exemplo

```python
# Para popular com dados de exemplo:
python scripts/popular_dados_exemplo.py
```

### 3. Backup Inicial

```python
# Criar primeiro backup:
curl -X POST http://localhost:5000/epi/api/criar-backup
```

## 🐛 Solução de Problemas

### Erro: Tabelas não criadas
```python
# Execute manualmente:
from app import app, db
with app.app_context():
    db.create_all()
```

### Erro: Módulo não encontrado
```bash
# Verifique se está no diretório correto:
pip install -r requirements.txt
```

### Erro: Permissões negadas
```sql
-- Verifique as colunas de permissão:
DESCRIBE usuarios;
```

### Erro: Static files não encontrados
```python
# Verifique se os diretórios foram criados:
import os
os.makedirs('static/epi_images', exist_ok=True)
```

## 📞 Suporte

### Logs de Debug
```python
# Ativar logs detalhados:
app.config['DEBUG'] = True
app.config['SQLALCHEMY_ECHO'] = True
```

### Verificar Status
```python
# Endpoint de status:
GET /epi/api/status
```

### Exportar Configurações
```python
# Backup das configurações:
GET /epi/api/exportar-configuracoes
```

## 🔄 Atualizações

### Versão do Módulo
- Versão atual: 1.0.0
- Compatibilidade: Flask 2.3+, Python 3.8+
- Banco de dados: SQLite, PostgreSQL, MySQL

### Histórico de Versões
- 1.0.0: Versão inicial completa
- 1.0.1: Correções de bugs (planejada)
- 1.1.0: Novas funcionalidades (planejada)

---

## ✅ Checklist de Instalação

- [ ] Dependências instaladas
- [ ] Banco de dados configurado
- [ ] Módulo integrado ao app principal
- [ ] Permissões de usuário configuradas
- [ ] Diretórios criados
- [ ] Configurações básicas definidas
- [ ] Teste de funcionalidades realizado
- [ ] Backup inicial criado
- [ ] Menu principal atualizado
- [ ] Documentação revisada

**🎉 Parabéns! O módulo de Gestão de EPIs está pronto para uso!**
