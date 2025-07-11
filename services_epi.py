"""
Serviços auxiliares para o sistema de Gestão de EPIs
"""
import requests
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from flask import current_app
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

class EPIService:
    """Serviço principal para gestão de EPIs"""
    
    @staticmethod
    def validar_ca_online(ca: str) -> Dict:
        """
        Valida um CA (Certificado de Aprovação) via API do Ministério do Trabalho
        """
        try:
            # URL da API oficial (simulada - implementar com a API real)
            # url = f"https://api.trabalho.gov.br/ca/validar/{ca}"
            
            # Por enquanto, simulação da validação
            import random
            import time
            
            # Simula delay da API
            time.sleep(random.uniform(0.5, 2.0))
            
            # Simula resposta baseada no CA
            ca_num = int(''.join(filter(str.isdigit, ca))) if ca else 0
            
            if ca_num % 5 == 0:  # Simula CA inválido
                return {
                    'status': 'invalido',
                    'mensagem': 'CA não encontrado na base de dados do Ministério do Trabalho',
                    'data_consulta': datetime.utcnow().isoformat()
                }
            elif ca_num % 7 == 0:  # Simula CA vencido
                return {
                    'status': 'vencido',
                    'mensagem': 'CA encontrado mas está vencido',
                    'fabricante': 'Fabricante Exemplo LTDA',
                    'produto': 'EPI Exemplo',
                    'validade': (date.today() - timedelta(days=30)).isoformat(),
                    'situacao': 'Vencido',
                    'data_consulta': datetime.utcnow().isoformat()
                }
            else:  # Simula CA válido
                return {
                    'status': 'valido',
                    'mensagem': 'CA válido e em conformidade',
                    'fabricante': 'Fabricante Confiável LTDA',
                    'produto': f'EPI Segurança Modelo {ca}',
                    'validade': (date.today() + timedelta(days=365)).isoformat(),
                    'situacao': 'Ativo',
                    'data_consulta': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'erro',
                'mensagem': f'Erro ao consultar API: {str(e)}',
                'data_consulta': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def verificar_vencimentos(dias_antecedencia: int = 30) -> List[Dict]:
        """
        Verifica EPIs com CA próximo ao vencimento
        """
        from models_epi import EPI
        
        data_limite = date.today() + timedelta(days=dias_antecedencia)
        
        epis_vencendo = EPI.query.filter(
            EPI.validade_ca <= data_limite,
            EPI.status == 'ativo'
        ).all()
        
        alertas = []
        for epi in epis_vencendo:
            dias_para_vencer = (epi.validade_ca - date.today()).days
            
            if dias_para_vencer < 0:
                nivel = 'error'
                mensagem = f'CA VENCIDO há {abs(dias_para_vencer)} dias'
            elif dias_para_vencer <= 7:
                nivel = 'error'
                mensagem = f'CA vence em {dias_para_vencer} dias - URGENTE'
            elif dias_para_vencer <= 15:
                nivel = 'warning'
                mensagem = f'CA vence em {dias_para_vencer} dias'
            else:
                nivel = 'info'
                mensagem = f'CA vence em {dias_para_vencer} dias'
            
            alertas.append({
                'epi_id': epi.id,
                'epi_nome': epi.nome,
                'ca': epi.ca,
                'validade': epi.validade_ca.isoformat(),
                'dias_para_vencer': dias_para_vencer,
                'nivel': nivel,
                'mensagem': mensagem
            })
        
        return alertas
    
    @staticmethod
    def verificar_estoque_baixo() -> List[Dict]:
        """
        Verifica EPIs com estoque baixo
        """
        from models_epi import EPI
        
        epis_estoque_baixo = EPI.query.filter(
            EPI.estoque_atual <= EPI.estoque_minimo,
            EPI.status == 'ativo'
        ).all()
        
        alertas = []
        for epi in epis_estoque_baixo:
            if epi.estoque_atual <= 0:
                nivel = 'error'
                mensagem = 'Estoque ZERADO'
            elif epi.estoque_atual <= (epi.estoque_minimo * 0.5):
                nivel = 'error'
                mensagem = f'Estoque CRÍTICO: {epi.estoque_atual} unidades'
            else:
                nivel = 'warning'
                mensagem = f'Estoque baixo: {epi.estoque_atual} unidades'
            
            alertas.append({
                'epi_id': epi.id,
                'epi_nome': epi.nome,
                'estoque_atual': epi.estoque_atual,
                'estoque_minimo': epi.estoque_minimo,
                'nivel': nivel,
                'mensagem': mensagem
            })
        
        return alertas

class DeclaracaoService:
    """Serviço para geração de declarações de entrega de EPIs em PDF"""
    
    @staticmethod
    def gerar_declaracao_pdf(entrega_data: Dict, arquivo_path: str) -> bool:
        """
        Gera declaração de entrega de EPI em PDF
        """
        try:
            doc = SimpleDocTemplate(arquivo_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Estilos customizados
            titulo_style = ParagraphStyle(
                'TituloCustom',
                parent=styles['Heading1'],
                fontSize=16,
                alignment=1,  # Centralizado
                spaceAfter=30
            )
            
            subtitulo_style = ParagraphStyle(
                'SubtituloCustom',
                parent=styles['Heading2'],
                fontSize=12,
                alignment=1,
                spaceAfter=20
            )
            
            normal_style = styles['Normal']
            normal_style.fontSize = 10
            
            # Conteúdo do PDF
            story = []
            
            # Cabeçalho
            story.append(Paragraph("DECLARAÇÃO DE ENTREGA DE EPI", titulo_style))
            story.append(Paragraph("Equipamento de Proteção Individual", subtitulo_style))
            story.append(Spacer(1, 20))
            
            # Dados do funcionário
            funcionario_info = f"""
            <b>DADOS DO FUNCIONÁRIO:</b><br/>
            Nome: {entrega_data.get('funcionario_nome', '')}<br/>
            CPF: {entrega_data.get('funcionario_cpf', '')}<br/>
            Cargo: {entrega_data.get('funcionario_cargo', '')}<br/>
            """
            story.append(Paragraph(funcionario_info, normal_style))
            story.append(Spacer(1, 20))
            
            # Dados da entrega
            data_entrega = entrega_data.get('data_entrega', date.today().strftime('%d/%m/%Y'))
            numero_declaracao = entrega_data.get('numero_declaracao', 'N/A')
            
            entrega_info = f"""
            <b>DADOS DA ENTREGA:</b><br/>
            Data da Entrega: {data_entrega}<br/>
            Número da Declaração: {numero_declaracao}<br/>
            """
            story.append(Paragraph(entrega_info, normal_style))
            story.append(Spacer(1, 20))
            
            # Tabela de EPIs
            story.append(Paragraph("<b>EPIs ENTREGUES:</b>", normal_style))
            story.append(Spacer(1, 10))
            
            # Cabeçalho da tabela
            tabela_data = [['EPI', 'CA', 'Quantidade', 'Validade CA']]
            
            # Dados dos EPIs
            epis = entrega_data.get('epis', [])
            for epi in epis:
                tabela_data.append([
                    epi.get('nome', ''),
                    epi.get('ca', ''),
                    str(epi.get('quantidade', 1)),
                    epi.get('validade_ca', '')
                ])
            
            # Criação da tabela
            tabela = Table(tabela_data, colWidths=[3*inch, 1.5*inch, 1*inch, 1.5*inch])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(tabela)
            story.append(Spacer(1, 30))
            
            # Declaração
            declaracao_texto = """
            Declaro que recebi os equipamentos de proteção individual (EPIs) relacionados acima,
            estando ciente de que:
            <br/><br/>
            1. É obrigatório o uso dos EPIs durante a execução das atividades;
            2. Os EPIs devem ser mantidos em bom estado de conservação;
            3. Qualquer defeito ou dano deve ser comunicado imediatamente;
            4. A não utilização dos EPIs pode resultar em medidas disciplinares;
            5. A devolução dos EPIs deve ocorrer conforme estabelecido pela empresa.
            """
            story.append(Paragraph(declaracao_texto, normal_style))
            story.append(Spacer(1, 40))
            
            # Assinaturas
            assinatura_texto = """
            <br/><br/>
            _________________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; _________________________________<br/>
            Assinatura do Funcionário &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Responsável pela Entrega<br/>
            <br/>
            Data: ___/___/______
            """
            story.append(Paragraph(assinatura_texto, normal_style))
            
            # Gerar PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {str(e)}")
            return False

class RelatorioService:
    """Serviço para geração de relatórios do sistema de EPIs"""
    
    @staticmethod
    def relatorio_vencimentos(formato: str = 'dict') -> Dict:
        """
        Gera relatório de vencimentos de CA
        """
        from models_epi import EPI
        
        hoje = date.today()
        
        # EPIs vencidos
        vencidos = EPI.query.filter(
            EPI.validade_ca < hoje,
            EPI.status == 'ativo'
        ).all()
        
        # EPIs vencendo em 30 dias
        vencendo_30 = EPI.query.filter(
            EPI.validade_ca >= hoje,
            EPI.validade_ca <= hoje + timedelta(days=30),
            EPI.status == 'ativo'
        ).all()
        
        # EPIs vencendo em 60 dias
        vencendo_60 = EPI.query.filter(
            EPI.validade_ca > hoje + timedelta(days=30),
            EPI.validade_ca <= hoje + timedelta(days=60),
            EPI.status == 'ativo'
        ).all()
        
        relatorio = {
            'data_geracao': datetime.now().isoformat(),
            'resumo': {
                'total_vencidos': len(vencidos),
                'total_vencendo_30_dias': len(vencendo_30),
                'total_vencendo_60_dias': len(vencendo_60)
            },
            'vencidos': [epi.to_dict() if hasattr(epi, 'to_dict') else {
                'id': epi.id,
                'nome': epi.nome,
                'ca': epi.ca,
                'validade_ca': epi.validade_ca.isoformat(),
                'dias_vencido': (hoje - epi.validade_ca).days
            } for epi in vencidos],
            'vencendo_30_dias': [epi.to_dict() if hasattr(epi, 'to_dict') else {
                'id': epi.id,
                'nome': epi.nome,
                'ca': epi.ca,
                'validade_ca': epi.validade_ca.isoformat(),
                'dias_para_vencer': (epi.validade_ca - hoje).days
            } for epi in vencendo_30],
            'vencendo_60_dias': [epi.to_dict() if hasattr(epi, 'to_dict') else {
                'id': epi.id,
                'nome': epi.nome,
                'ca': epi.ca,
                'validade_ca': epi.validade_ca.isoformat(),
                'dias_para_vencer': (epi.validade_ca - hoje).days
            } for epi in vencendo_60]
        }
        
        return relatorio
    
    @staticmethod
    def relatorio_estoque(formato: str = 'dict') -> Dict:
        """
        Gera relatório de estoque de EPIs
        """
        from models_epi import EPI
        
        # EPIs sem estoque
        sem_estoque = EPI.query.filter(
            EPI.estoque_atual <= 0,
            EPI.status == 'ativo'
        ).all()
        
        # EPIs com estoque baixo
        estoque_baixo = EPI.query.filter(
            EPI.estoque_atual > 0,
            EPI.estoque_atual <= EPI.estoque_minimo,
            EPI.status == 'ativo'
        ).all()
        
        # EPIs com estoque ok
        estoque_ok = EPI.query.filter(
            EPI.estoque_atual > EPI.estoque_minimo,
            EPI.status == 'ativo'
        ).all()
        
        relatorio = {
            'data_geracao': datetime.now().isoformat(),
            'resumo': {
                'total_sem_estoque': len(sem_estoque),
                'total_estoque_baixo': len(estoque_baixo),
                'total_estoque_ok': len(estoque_ok)
            },
            'sem_estoque': [epi.to_dict() if hasattr(epi, 'to_dict') else {
                'id': epi.id,
                'nome': epi.nome,
                'ca': epi.ca,
                'estoque_atual': epi.estoque_atual,
                'estoque_minimo': epi.estoque_minimo
            } for epi in sem_estoque],
            'estoque_baixo': [epi.to_dict() if hasattr(epi, 'to_dict') else {
                'id': epi.id,
                'nome': epi.nome,
                'ca': epi.ca,
                'estoque_atual': epi.estoque_atual,
                'estoque_minimo': epi.estoque_minimo
            } for epi in estoque_baixo],
            'estoque_ok': [epi.to_dict() if hasattr(epi, 'to_dict') else {
                'id': epi.id,
                'nome': epi.nome,
                'ca': epi.ca,
                'estoque_atual': epi.estoque_atual,
                'estoque_minimo': epi.estoque_minimo
            } for epi in estoque_ok]
        }
        
        return relatorio

class AlertaService:
    """Serviço para gerenciamento de alertas automáticos"""
    
    @staticmethod
    def gerar_alertas_automaticos():
        """
        Gera alertas automáticos para vencimentos e estoque baixo
        """
        from models_epi import AlertaEPI, db
        
        alertas_criados = []
        
        # Alertas de vencimento
        vencimentos = EPIService.verificar_vencimentos()
        for item in vencimentos:
            # Verifica se já existe alerta similar ativo
            alerta_existente = AlertaEPI.query.filter_by(
                tipo='validade_ca',
                epi_id=item['epi_id'],
                status='ativo'
            ).first()
            
            if not alerta_existente:
                alerta = AlertaEPI(
                    tipo='validade_ca',
                    epi_id=item['epi_id'],
                    titulo=f"CA do EPI {item['epi_nome']} vencendo",
                    mensagem=item['mensagem'],
                    nivel=item['nivel']
                )
                db.session.add(alerta)
                alertas_criados.append(alerta)
        
        # Alertas de estoque baixo
        estoques = EPIService.verificar_estoque_baixo()
        for item in estoques:
            # Verifica se já existe alerta similar ativo
            alerta_existente = AlertaEPI.query.filter_by(
                tipo='estoque_baixo',
                epi_id=item['epi_id'],
                status='ativo'
            ).first()
            
            if not alerta_existente:
                alerta = AlertaEPI(
                    tipo='estoque_baixo',
                    epi_id=item['epi_id'],
                    titulo=f"Estoque baixo do EPI {item['epi_nome']}",
                    mensagem=item['mensagem'],
                    nivel=item['nivel']
                )
                db.session.add(alerta)
                alertas_criados.append(alerta)
        
        try:
            db.session.commit()
            return len(alertas_criados)
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar alertas: {str(e)}")
            return 0

# Funções utilitárias
def gerar_numero_declaracao() -> str:
    """Gera número único para declaração"""
    from datetime import datetime
    import random
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = random.randint(1000, 9999)
    return f"DECL-{timestamp}-{random_num}"

def formatar_cpf(cpf: str) -> str:
    """Formata CPF para exibição"""
    if not cpf:
        return ''
    
    # Remove caracteres não numéricos
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    
    return cpf

def validar_cpf(cpf: str) -> bool:
    """Valida CPF"""
    if not cpf:
        return False
    
    # Remove caracteres não numéricos
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf_limpo) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf_limpo == cpf_limpo[0] * 11:
        return False
    
    # Algoritmo de validação do CPF
    def calcular_digito(cpf_parcial):
        soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Verifica primeiro dígito verificador
    if int(cpf_limpo[9]) != calcular_digito(cpf_limpo[:9]):
        return False
    
    # Verifica segundo dígito verificador
    if int(cpf_limpo[10]) != calcular_digito(cpf_limpo[:10]):
        return False
    
    return True
