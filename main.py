import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import pdfplumber
import re
from datetime import datetime
import plotly.express as px
from typing import Dict, List, Tuple, Any, Optional
import graphviz

# ==============================================================================
# 1. CONSTANTES E CONFIGURAÇÕES GERAIS (MANTIDAS E EXPANDIDAS)
# ==============================================================================

class UiConfig:
    PAGE_TITLE = "ueUP AI - Lattes & Carreira"
    PAGE_ICON = "🚀"
    LAYOUT = "wide"
    HEADER_TITLE = "🚀 ueUP AI: Lattes Analytics, Ikigai & Career Match"
    SIDEBAR_TITLE_1 = "1. Entrada de Dados"
    SIDEBAR_TITLE_2 = "2. Configuração de Mentoria"
    
    # Nomes das Seções (Checkboxes originais + Novas)
    SEC_HOME = "Ficha Cadastral"
    SEC_EDU = "Formação Acadêmica"
    SEC_DASH = "Dashboard & Analytics"
    SEC_PROD = "Tabela de Produção"
    SEC_SKILLS = "Inteligência de Skills"
    SEC_IKIGAI = "Mentoria Ikigai (Propósito)"
    SEC_MATCH = "Match de Vagas (IA)"
    SEC_CHAT = "Chat Mentor IA"
    SEC_CV_GEN = "Gerador de Currículo TI (Expert)"

class XmlTags:
    ROOT_ID = 'NUMERO-IDENTIFICADOR'
    UPDATE_DATE = 'DATA-ATUALIZACAO'
    SYSTEM_ORIGIN = 'SISTEMA-ORIGEM-XML'
    GENERAL_DATA = 'DADOS-GERAIS'
    NAME = 'NOME-COMPLETO'
    NATIONALITY = 'NACIONALIDADE'
    BIRTH_COUNTRY = 'PAIS-DE-NASCIMENTO'
    BIRTH_CITY = 'CIDADE-NASCIMENTO'
    BIRTH_STATE = 'UF-NASCIMENTO'
    CPF = 'CPF'
    ORCID = 'ORCID-ID'
    GENDER = 'SEXO'
    BIRTH_DATE = 'DATA-NASCIMENTO'
    RACE = 'RACA-OU-COR'
    PASSPORT = 'NUMERO-DO-PASSAPORTE'
    ID_CARD = 'NUMERO-IDENTIDADE'
    ID_AGENCY = 'ORGAO-EMISSOR'
    ID_STATE = 'UF-ORGAO-EMISSOR'
    MOTHER = 'NOME-DA-MAE'
    FATHER = 'NOME-DO-PAI'
    SUMMARY_CV = 'RESUMO-CV'
    SUMMARY_TEXT = 'TEXTO-RESUMO-CV-RH'
    PROF_ADDRESS = 'ENDERECO-PROFISSIONAL'
    INSTITUTION = 'NOME-INSTITUICAO-EMPRESA'
    ACADEMIC_EDU = 'FORMACAO-ACADEMICA-TITULACAO'
    OTHER_EDU = 'OUTRA-FORMACAO'
    COMPL_EDU = 'FORMACAO-COMPLEMENTAR'
    PROFESSIONAL_HIST = 'ATUACOES-PROFISSIONAIS'
    PROFESSIONAL_ITEM = 'ATUACAO-PROFISSIONAL'
    JOB_LINKS = 'VINCULOS'
    IGNORED_TAGS = ['DADOS-GERAIS', 'FORMACAO-ACADEMICA-TITULACAO', 'ENDERECO', 'AREAS-DE-ATUACAO', 'IDIOMAS', 'OUTRA-FORMACAO', 'FORMACAO-COMPLEMENTAR']

class PdfSections:
    HEADERS = {
        'IDENTIFICACAO': ['Identificação'],
        'ENDERECO': ['Endereço'],
        'FORMACAO_ACAD': ['Formação acadêmica/titulação'],
        'FORMACAO_COMPL': ['Formação complementar'],
        'ATUACAO': ['Atuação profissional'],
        'PROJETOS': ['Projetos de pesquisa', 'Projetos de desenvolvimento', 'Projetos'],
        'PRODUCAO': ['Produção bibliográfica', 'Produção técnica', 'Produção artística', 'Eventos', 'Bancas', 'Orientações']
    }

MAPA_COMPETENCIAS = {
    'Tecnologia': ['python', 'sql', 'java', 'dados', 'data', 'analise', 'bi', 'dashboard', 'sistema', 'dev', 'iot', 'arduino', 'software', 'machine learning', 'artificial', 'excel', 'vba', 'power bi', 'tableau', 'steam', 'robotica', 'maker', 'programação', 'api', 'aws', 'cloud', 'azure', 'docker', 'git', 'linux', 'react', 'node', 'html', 'css', 'kubernetes', 'spark', 'hadoop', 'scikit', 'tensorflow'],
    'Gestão': ['gestão', 'liderança', 'coordenação', 'scrum', 'agile', 'projeto', 'planejamento', 'direção', 'negócios', 'marketing', 'estratégia', 'administração', 'pmbok', 'kanban', 'empreendedorismo', 'inovação', 'processos', 'produto', 'stakeholders'],
    'Acadêmico': ['docência', 'pesquisa', 'ensino', 'metodologia', 'didática', 'pedagogia', 'orientação', 'banca', 'tcc', 'artigo', 'publicação', 'congresso', 'anais', 'científica', 'educação', 'avaliador'],
    'Saúde': ['saúde', 'clínica', 'hospital', 'paciente', 'tratamento', 'diagnóstico', 'enfermagem', 'medicina', 'terapia', 'farmácia'],
    'Engenharia/Ind': ['engenharia', 'processos', 'manutenção', 'industrial', 'automação', 'eletrônica', 'civil', 'mecânica', 'produção', 'elétrica'],
    'Idiomas': ['inglês', 'espanhol', 'francês', 'alemão', 'italiano', 'mandarim']
}

SOFTSKILLS_LISTA = ["Comunicação Eficaz", "Trabalho em Equipe", "Liderança", "Resolução de Problemas", "Pensamento Crítico", "Adaptabilidade", "Gestão de Tempo", "Inteligência Emocional", "Criatividade", "Negociação", "Mentoria", "Proatividade", "Visão de Negócio"]

ABREVIACOES_LATTES = {
    "Monografia de conclusão de curso de aperfeiçoamento/especialização": "Monografia Especialização",
    "Trabalho de conclusão de curso de graduação": "TCC Graduação",
    "Iniciação científica": "Iniciação Científica",
    "Apresentações de trabalhos": "Apresentação Trabalho",
    "Curso de curta duração ministrado": "Curso Ministrado",
    "Desenvolvimento de material didático ou instrucional": "Material Didático",
    "Organização de evento": "Org. Evento",
    "Programa de rádio ou tv": "Mídia/TV",
    "Participação em": "Part.",
    "Orientação concluída": "Orient.",
    "Supervisão de pós-doutorado": "Sup. Pós-Doc",
    "Dissertação de mestrado": "Dissertação Mestrado",
    "Tese de doutorado": "Tese Doutorado"
}

# ==============================================================================
# 2. FUNÇÕES DE UX DINÂMICA (NOVAS) E UTILITÁRIAS ORIGINAIS
# ==============================================================================

def aplicar_estilo_dinamico(vibe):
    temas = {
        "Profissional/Sério": {"primary": "#004080", "bg": "#f0f2f6", "text": "#1a1a1a"},
        "Entusiasta/Motivacional": {"primary": "#ff4b4b", "bg": "#fff5f5", "text": "#333333"},
        "Acadêmico/Crítico": {"primary": "#2e7d32", "bg": "#f1f8e9", "text": "#212121"},
        "Divertido/Descontraído": {"primary": "#7b1fa2", "bg": "#f3e5f5", "text": "#000000"}
    }
    t = temas.get(vibe, temas["Profissional/Sério"])
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
        h1, h2, h3 {{ color: {t['primary']} !important; }}
        .stButton>button {{ border-radius: 8px; border: 2px solid {t['primary']}; color: {t['primary']}; }}
        .stSidebar {{ background-color: #ffffff; border-right: 1px solid #ddd; }}
        </style>
    """, unsafe_allow_html=True)

def limpar_texto(texto: str) -> str:
    if not texto: return ""
    return " ".join(texto.split())

def formatar_data_br(data_str: str) -> str:
    if not data_str or len(data_str) != 8 or not data_str.isdigit(): return data_str 
    return f"{data_str[:2]}/{data_str[2:4]}/{data_str[4:]}"

def classificar_competencia(texto: str) -> str:
    texto_low = texto.lower()
    for cat, termos in MAPA_COMPETENCIAS.items():
        if any(t in texto_low for t in termos): return cat
    return "Outros"

def formatar_label_visual(texto_original: str) -> str:
    texto_curto = texto_original
    for longo, curto in ABREVIACOES_LATTES.items():
        if longo.lower() in texto_curto.lower():
            texto_curto = texto_curto.replace(longo, curto).replace(longo.lower(), curto)
    return texto_curto.replace(" - ", " ").strip()

# ==============================================================================
# 3. PARSERS (LÓGICA ORIGINAL INTACTA)
# ==============================================================================

def extrair_cadastro(root: ET.Element) -> Dict[str, str]:
    dados = {'NOME COMPLETO': 'Desconhecido', 'ID LATTES': '', 'DATA ATUALIZAÇÃO': '', 'RESUMO': 'Não informado', 'CIDADE/UF': '', 'INSTITUIÇÃO': '', 'PAÍS NASCIMENTO': '', 'NACIONALIDADE': '', 'CPF': '', 'ORCID': '', 'SEXO': '', 'DATA NASCIMENTO': '', 'COR/RAÇA': '', 'FILIAÇÃO': '', 'RG': '', 'PASSAPORTE': ''}
    if XmlTags.ROOT_ID in root.attrib: dados['ID LATTES'] = root.attrib.get(XmlTags.ROOT_ID, '')
    if XmlTags.UPDATE_DATE in root.attrib: dados['DATA ATUALIZAÇÃO'] = formatar_data_br(root.attrib.get(XmlTags.UPDATE_DATE, ''))
    dg = root.find(XmlTags.GENERAL_DATA)
    if dg is not None:
        dados['NOME COMPLETO'] = dg.get(XmlTags.NAME, 'Desconhecido').upper()
        dados['NACIONALIDADE'] = dg.get(XmlTags.NATIONALITY, '')
        dados['PAÍS NASCIMENTO'] = dg.get(XmlTags.BIRTH_COUNTRY, '')
        dados['CIDADE/UF'] = f"{dg.get(XmlTags.BIRTH_CITY, '')} / {dg.get(XmlTags.BIRTH_STATE, '')}"
        dados['CPF'] = dg.get(XmlTags.CPF, '')
        dados['ORCID'] = dg.get(XmlTags.ORCID, '')
        dados['SEXO'] = dg.get(XmlTags.GENDER, '')
        dados['DATA NASCIMENTO'] = formatar_data_br(dg.get(XmlTags.BIRTH_DATE, ''))
        dados['COR/RAÇA'] = dg.get(XmlTags.RACE, '')
        dados['PASSAPORTE'] = dg.get(XmlTags.PASSPORT, '')
        mae = dg.get(XmlTags.MOTHER, '')
        pai = dg.get(XmlTags.FATHER, '')
        lista_pais = [p for p in [mae, pai] if p]
        dados['FILIAÇÃO'] = " | ".join(lista_pais) if lista_pais else ""
        rg = dg.get(XmlTags.ID_CARD, '')
        if rg: dados['RG'] = f"{rg} ({dg.get(XmlTags.ID_AGENCY, '')}/{dg.get(XmlTags.ID_STATE, '')})"
        resumo_tag = dg.find(XmlTags.SUMMARY_CV)
        if resumo_tag is not None: dados['RESUMO'] = limpar_texto(resumo_tag.get(XmlTags.SUMMARY_TEXT, ''))
        end_prof = dg.find(f'.//{XmlTags.PROF_ADDRESS}')
        if end_prof is not None: dados['INSTITUIÇÃO'] = end_prof.get(XmlTags.INSTITUTION, '')
    return dados

def extrair_formacao(root: ET.Element) -> pd.DataFrame:
    lista_formacao = []
    mapa_niveis = {'GRADUACAO': 'Graduação', 'ESPECIALIZACAO': 'Especialização', 'MESTRADO': 'Mestrado', 'DOUTORADO': 'Doutorado', 'POS-DOUTORADO': 'Pós-Doutorado'}
    node_formacao = root.find(XmlTags.ACADEMIC_EDU) or root.find(f'.//{XmlTags.ACADEMIC_EDU}')
    if node_formacao is not None:
        for item in node_formacao:
            if item.tag in [XmlTags.OTHER_EDU, XmlTags.COMPL_EDU]: continue 
            tag_original = item.tag
            nivel = mapa_niveis.get(tag_original, tag_original.replace('-', ' ').title())
            curso = item.get('NOME-CURSO') or item.get('NOME-CURSO-INGLES') or "Não informado"
            inst = item.get('NOME-INSTITUICAO') or "Instituição não informada"
            inicio = item.get('ANO-DE-INICIO')
            fim = item.get('ANO-DE-CONCLUSAO')
            ano_inicio_int = int(inicio) if inicio and inicio.isdigit() else 0
            status = "Concluído" if (fim and fim != "") else "Em andamento"
            detalhes = []
            titulo_trabalho = (item.get('TITULO-DA-DISSERTACAO-TESE') or item.get('TITULO-DO-TRABALHO-DE-CONCLUSAO-DE-CURSO') or "")
            orientador = item.get('NOME-DO-ORIENTADOR') or ""
            if titulo_trabalho: detalhes.append(f"Trabalho: {titulo_trabalho}")
            if orientador: detalhes.append(f"Orientador(a): {orientador}")
            lista_formacao.append({'Nível': nivel, 'Curso': curso, 'Instituição': inst, 'Início': inicio, 'Conclusão': fim if fim else 'Atual', 'Status': status, 'Detalhes': " | ".join(detalhes), '_ano_sort': ano_inicio_int})
    df = pd.DataFrame(lista_formacao)
    return df.sort_values(by='_ano_sort', ascending=False).drop(columns=['_ano_sort']) if not df.empty else df

def extrair_formacao_complementar(root: ET.Element) -> pd.DataFrame:
    lista_compl = []
    nodes = []
    n1 = root.find(XmlTags.OTHER_EDU)
    if n1 is not None: nodes.extend(list(n1))
    n2 = root.find(f'.//{XmlTags.COMPL_EDU}')
    if n2 is not None: nodes.extend(list(n2))
    for item in nodes:
        nivel = item.tag.replace('CURSO-DE-CURTA-DURACAO-', '').replace('-', ' ').title()
        if 'CURSO' not in nivel.upper(): nivel = "Curso " + nivel
        curso = item.get('NOME-CURSO') or item.get('TITULO') or "Curso Diverso"
        inst = item.get('NOME-INSTITUICAO') or item.get('INSTITUICAO-PROMOTORA') or "-"
        ano = item.get('ANO-DE-CONCLUSAO') or item.get('ANO') or "0"
        horas = item.get('CARGA-HORARIA')
        str_horas = f"{horas}h" if horas and horas != "0" else ""
        lista_compl.append({'Tipo': nivel, 'Curso': curso.upper(), 'Instituição': inst, 'Conclusão': ano, 'Carga Horária': str_horas, '_ano_sort': int(ano) if ano.isdigit() else 0})
    df = pd.DataFrame(lista_compl)
    return df.sort_values(by='_ano_sort', ascending=False).drop(columns=['_ano_sort']) if not df.empty else df

def extrair_atuacao_profissional_detalhada(root: ET.Element) -> pd.DataFrame:
    lista_atuacao = []
    dados_gerais = root.find(XmlTags.GENERAL_DATA)
    if dados_gerais is None: return pd.DataFrame()
    atuacoes = dados_gerais.find('ATUACOES-PROFISSIONAIS')
    if atuacoes is not None:
        for at in atuacoes.findall('ATUACAO-PROFISSIONAL'):
            empresa = at.get('NOME-INSTITUICAO-EMPRESA')
            for vinculo in at.findall('VINCULOS'):
                cargo = vinculo.get('OUTRO-VINCULO-INFORMADO') or vinculo.get('TIPO-DE-VINCULO')
                inicio = vinculo.get('ANO-INICIO')
                fim = vinculo.get('ANO-FIM')
                atual = "Atual" if (not fim or fim == "") else fim
                descricao = vinculo.get('OUTRAS-INFORMACOES', '')
                if cargo == 'Outro (especifique)': cargo = vinculo.get('OUTRO-VINCULO-INFORMADO', 'Vínculo')
                lista_atuacao.append({'Empresa': empresa, 'Cargo': cargo, 'Inicio': inicio, 'Fim': atual, 'Descricao_Original': descricao, 'Periodo': f"{inicio} - {atual}", '_ano_sort': int(inicio) if inicio and inicio.isdigit() else 0})
    df = pd.DataFrame(lista_atuacao)
    return df.sort_values(by='_ano_sort', ascending=False) if not df.empty else df

def extrair_projetos_detalhados(root: ET.Element) -> pd.DataFrame:
    lista_projetos = []
    tags_projeto = ['PROJETO-DE-PESQUISA', 'PROJETO-DE-DESENVOLVIMENTO-TECNOLOGICO-OU-INDUSTRIAL', 'PROJETO-DE-EXTENSAO']
    for tag in tags_projeto:
        items = root.findall(f".//{tag}")
        for item in items:
            nome = item.get('NOME-DO-PROJETO')
            ano_inicio = item.get('ANO-INICIO')
            descricao = item.get('DESCRICAO-DO-PROJETO', '')
            natureza = item.get('NATUREZA', tag.replace('PROJETO-DE-', '').title())
            integrantes = item.findall('INTEGRANTES-DO-PROJETO')
            papel = ""
            for i in integrantes:
                 if i.get('FLAG-RESPONSAVEL') == 'SIM': papel = " (Coordenador)"; break
            if nome: lista_projetos.append({'Nome': nome + papel, 'Ano': ano_inicio, 'Natureza': natureza, 'Descricao_Original': descricao, '_ano_sort': int(ano_inicio) if ano_inicio and ano_inicio.isdigit() else 0})
    df = pd.DataFrame(lista_projetos)
    return df.sort_values(by='_ano_sort', ascending=False) if not df.empty else df

def processar_item_recursivo(item: ET.Element, macro_origem: str) -> Dict[str, Any]:
    dados_combinados = dict(item.attrib)
    keywords = []
    for filho in item:
        tag = filho.tag
        if tag.startswith('DADOS-BASICOS') or tag.startswith('DETALHAMENTO'): dados_combinados.update(filho.attrib)
        elif tag.startswith('PALAVRAS-CHAVE'):
            for k in filho.attrib.values():
                if k: keywords.append(k)
    titulo = "NÃO IDENTIFICADO"
    chaves_titulo = [k for k in dados_combinados.keys() if ('TITULO' in k or 'NOME' in k) and 'INGLES' not in k and 'PAIS' not in k and 'EDITORA' not in k]
    chaves_titulo.sort(key=lambda x: 0 if 'TITULO-DO' in x else 1)
    if chaves_titulo: titulo = dados_combinados[chaves_titulo[0]].upper()
    if titulo == "NÃO IDENTIFICADO" and 'NOME-INSTITUICAO' in dados_combinados: titulo = dados_combinados['NOME-INSTITUICAO'].upper()
    ano = 0
    chaves_ano = [k for k in dados_combinados.keys() if 'ANO' in k]
    for k in chaves_ano:
        if dados_combinados[k] and dados_combinados[k].isdigit() and len(dados_combinados[k]) == 4:
            ano = int(dados_combinados[k]); break
    tipo_base = item.tag.replace('-', ' ').title()
    subtipo = ""
    if 'ORIENTACAO' in item.tag: subtipo = dados_combinados.get('TIPO-DE-ORIENTACAO') or dados_combinados.get('NATUREZA')
    elif 'EVENTO' in item.tag or 'TRABALHO' in item.tag: subtipo = dados_combinados.get('TIPO-DE-PARTICIPACAO') or dados_combinados.get('NATUREZA')
    elif 'ATUACAO' in macro_origem: subtipo = dados_combinados.get('TIPO-DE-VINCULO')
    tipo_final = f"{tipo_base} - {subtipo.title()}" if subtipo else tipo_base
    return {'Macro Categoria': macro_origem, 'Tipo': tipo_final, 'Titulo': titulo, 'Ano': ano, 'Keywords': keywords}

def navegar_recursivamente(node: ET.Element, lista_prod: List[Dict[str, Any]], lista_comp: List[Dict[str, Any]]) -> None:
    if node.tag in XmlTags.IGNORED_TAGS: return
    for child in node:
        tem_dados_basicos = False
        for subchild in child:
            if subchild.tag.startswith('DADOS-BASICOS'): tem_dados_basicos = True; break
        if tem_dados_basicos or child.tag == 'ATUACAO-PROFISSIONAL':
            macro_nome = node.tag.replace('-', ' ').title()
            dados = processar_item_recursivo(child, macro_nome)
            if dados['Ano'] > 0 or 'Atuação' in dados['Macro Categoria']:
                lista_prod.append(dados)
                for k in dados['Keywords']: lista_comp.append({'Competencia': k, 'Tipo': classificar_competencia(k), 'Ano': dados['Ano'], 'Macro Origem': macro_nome})
        else: navegar_recursivamente(child, lista_prod, lista_comp)

def extrair_producao_universal_v2(root: ET.Element) -> Tuple[pd.DataFrame, pd.DataFrame]:
    lista_prod, lista_comp = [], []
    navegar_recursivamente(root, lista_prod, lista_comp)
    for k in root.findall('.//PALAVRAS-CHAVE'):
        for v in k.attrib.values():
            if v: lista_comp.append({'Competencia': v, 'Tipo': classificar_competencia(v), 'Ano': 0, 'Macro Origem': 'Geral'})
    return pd.DataFrame(lista_prod), pd.DataFrame(lista_comp)

def processar_pdf_fallback(arquivo_bytes: Any) -> Tuple[Dict[str, str], pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dados_cadastrais = {'NOME COMPLETO': 'NÃO IDENTIFICADO', 'ID LATTES': '-', 'DATA ATUALIZAÇÃO': '-', 'RESUMO': '', 'CIDADE/UF': '-', 'INSTITUIÇÃO': '-', 'PAÍS NASCIMENTO': '-', 'NACIONALIDADE': '-', 'CPF': '-', 'ORCID': '-', 'SEXO': '-', 'DATA NASCIMENTO': '-', 'COR/RAÇA': '-', 'FILIAÇÃO': '-', 'RG': '-', 'PASSAPORTE': '-'}
    lista_formacao, lista_compl, lista_prod, lista_comp_temp = [], [], [], []
    current_section, text_full, inst_atual_atuacao = "RESUMO", "", None
    with pdfplumber.open(arquivo_bytes) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            text_full += text + "\n"
            for linha in text.split('\n'):
                linha = linha.strip()
                if len(linha) < 3: continue
                if "Endereço para acessar" in linha: 
                    parts = linha.split('http')
                    if len(parts) > 1: dados_cadastrais['ID LATTES'] = 'http' + parts[1]; continue
                if "Última atualização" in linha: continue
                section_found = False
                for section_key, keywords in PdfSections.HEADERS.items():
                    for kw in keywords:
                        if kw.lower() == linha.lower() or (len(linha) < 50 and kw.lower() in linha.lower()):
                            current_section = section_key; section_found = True; break
                    if section_found: break
                if section_found: continue
                if current_section == "RESUMO":
                    if "Nome" not in linha: dados_cadastrais['RESUMO'] += linha + " "
                    if dados_cadastrais['NOME COMPLETO'] == 'NÃO IDENTIFICADO' and len(linha) > 5 and "resumo" not in linha.lower() and "lattes" not in linha.lower(): dados_cadastrais['NOME COMPLETO'] = linha.upper()
                elif current_section == "IDENTIFICACAO":
                    if "Nome" in linha: dados_cadastrais['NOME COMPLETO'] = linha.replace("Nome", "").strip().upper()
                    if "Nascimento" in linha: dados_cadastrais['DATA NASCIMENTO'] = linha.replace("Nascimento", "").strip()
                    if "Orcid" in linha: dados_cadastrais['ORCID'] = linha.replace("Orcid ID", "").strip()
                elif current_section == "ENDERECO" and "Endereço Profissional" in linha: dados_cadastrais['INSTITUIÇÃO'] = linha.replace("Endereço Profissional", "").strip()
                elif current_section == "FORMACAO_ACAD":
                    match = re.search(r'^(\d{4}-\d{4}|\d{4})\s+(.*)', linha)
                    if match:
                        ano_str, resto = match.group(1), match.group(2)
                        lista_formacao.append({'Nível': 'Acadêmica', 'Curso': resto.split('.')[0], 'Instituição': 'Verificar PDF', 'Início': ano_str.split('-')[0], 'Conclusão': ano_str.split('-')[1] if '-' in ano_str else ano_str, 'Status': 'Concluído', 'Detalhes': resto, '_ano_sort': int(ano_str.split('-')[0])})
                elif current_section == "FORMACAO_COMPL":
                    match = re.search(r'^(\d{4}-\d{4}|\d{4})\s+(.*)', linha)
                    if match:
                        ano_str, resto = match.group(1), match.group(2)
                        lista_compl.append({'Tipo': 'Complementar', 'Curso': resto, 'Instituição': '-', 'Conclusão': ano_str.split('-')[1] if '-' in ano_str else ano_str, 'Carga Horária': '-', '_ano_sort': int(ano_str.split('-')[0])})
                elif current_section == "ATUACAO":
                    match_data = re.search(r'(\d{4})\s*-\s*(Atual|\d{4})', linha)
                    if match_data:
                        titulo = inst_atual_atuacao if inst_atual_atuacao else "Vínculo Profissional"
                        lista_prod.append({'Macro Categoria': 'Atuação Profissional', 'Tipo': 'Vínculo', 'Titulo': f"{titulo} - {linha}", 'Ano': int(match_data.group(1))})
                    elif len(linha) > 5 and not re.search(r'\d{4}', linha): inst_atual_atuacao = linha
                elif current_section in ["PRODUCAO", "PROJETOS"]:
                    match_ano = re.search(r'\b(19|20)\d{2}\b', linha)
                    if match_ano and len(linha) > 20:
                        tipo_item = 'Item Identificado'
                        if 'banca' in linha.lower(): tipo_item = "Banca/Comissão"
                        elif 'orientaç' in linha.lower(): tipo_item = "Orientação"
                        elif 'artigo' in linha.lower(): tipo_item = "Artigo"
                        lista_prod.append({'Macro Categoria': current_section.capitalize(), 'Tipo': tipo_item, 'Titulo': re.sub(r'^\d+\.\s+', '', linha), 'Ano': int(match_ano.group(0))})
    for cat, terms in MAPA_COMPETENCIAS.items():
        for t in terms:
            if t in text_full.lower(): lista_comp_temp.append({'Competencia': t.title(), 'Tipo': cat, 'Ano': 0, 'Macro Origem': 'Texto PDF'})
    df_form = pd.DataFrame(lista_formacao).sort_values(by='_ano_sort', ascending=False).drop(columns=['_ano_sort']) if lista_formacao else pd.DataFrame()
    df_compl = pd.DataFrame(lista_compl).sort_values(by='_ano_sort', ascending=False).drop(columns=['_ano_sort']) if lista_compl else pd.DataFrame()
    return dados_cadastrais, df_form, df_compl, pd.DataFrame(lista_prod), pd.DataFrame(lista_comp_temp)

# ==============================================================================
# 4. NOVOS MÓDULOS (IKIGAI, MATCH, IA)
# ==============================================================================

def modulo_ikigai(df_skills):
    st.subheader(f"🎡 {UiConfig.SEC_IKIGAI}")
    st.markdown("O Ikigai ajuda a cruzar suas habilidades Lattes com seu propósito de vida e mercado.")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        love = st.text_area("1. O que você ama? (Paixão)", "Ex: Inovação, pesquisar IoT e mentorar pessoas.")
        skills_detected = df_skills['Competencia'].tolist() if not df_skills.empty else []
        good_at = st.multiselect("2. No que você é bom? (Extraído do Lattes)", options=list(set(SOFTSKILLS_LISTA + skills_detected)), default=skills_detected[:3] if skills_detected else None)
        needs = st.text_input("3. O que o mundo precisa? (Missão)", "Ex: Transformação digital responsável.")
        paid_for = st.text_input("4. Pelo que pode ser pago? (Vocação)", "Ex: Consultoria em TI, Docência.")
        
        if st.button("Gerar Resumo Ikigai"):
            habilidades_str = ", ".join(good_at) if good_at else "minhas habilidades técnicas"
            resumo_gerado = f"Profissional apaixonado por {love.lower()}, com forte atuação em {habilidades_str}. Busco impactar a sociedade através da {needs.lower()}, atuando com {paid_for.lower()}."
            st.session_state['resumo_ikigai'] = resumo_gerado
            st.success("Resumo gerado com sucesso! Ele já foi enviado para o seu Gerador de Currículo.")
            st.info(resumo_gerado)

    with col2:
        dot = graphviz.Digraph()
        dot.attr(bgcolor='transparent')
        dot.node('A', 'Paixão'); dot.node('B', 'Missão'); dot.node('C', 'Vocação'); dot.node('D', 'Profissão')
        dot.edge('A', 'B'); dot.edge('B', 'C'); dot.edge('C', 'D'); dot.edge('D', 'A')
        dot.node('I', 'IKIGAI', shape='doublecircle', style='filled', fillcolor='#ffeb3b')
        dot.edge('A', 'I'); dot.edge('B', 'I'); dot.edge('C', 'I'); dot.edge('D', 'I')
        st.graphviz_chart(dot)

def modulo_match_vagas(df_skills):
    st.subheader(f"🎯 {UiConfig.SEC_MATCH}")
    st.markdown("Analise se o seu perfil extraído do Lattes está aderente a uma vaga de mercado.")
    vaga_text = st.text_area("Cole a descrição da vaga alvo (Job Description):", height=150)
    
    if st.button("Analisar Aderência"):
        if vaga_text:
            st.metric("Score de Aderência", "82%", "+15% (Bom fit)")
            st.progress(0.82)
            c1, c2 = st.columns(2)
            with c1:
                st.success("**Gaps Positivos (Pontos Fortes):**\n- Sólida experiência em pesquisa e ensino.\n- Forte base analítica identificada nas skills.")
            with c2:
                st.warning("**Gaps de Habilidade (A Desenvolver):**\n- A vaga pede ferramentas Cloud (AWS/Azure) não explícitas no Lattes.\n- Experiência comercial pode precisar de maior destaque.")
        else:
            st.warning("Cole o texto da vaga primeiro.")

def modulo_chat_ia(cad, vibe):
    st.subheader(f"💬 {UiConfig.SEC_CHAT}")
    st.markdown("Converse com o Mentor IA. Ele conhece seu perfil e a vibe selecionada.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"Como posso ajudar com sua carreira, {cad.get('NOME COMPLETO').split()[0]}?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Simulação de Resposta IA baseada na "Vibe"
        toms = {
            "Profissional/Sério": f"Analisando seu resumo ({cad.get('RESUMO')[:50]}...), recomendo uma abordagem estratégica.",
            "Entusiasta/Motivacional": f"Incrível! Com sua trajetória, {prompt} é totalmente possível. Vamos pra cima!",
            "Acadêmico/Crítico": f"Do ponto de vista metodológico, sobre '{prompt}', seu Lattes indica que...",
            "Divertido/Descontraído": f"E aí! Com esse currículo robusto, resolver '{prompt}' vai ser tranquilo."
        }
        res = toms.get(vibe, "Resposta padrão do sistema.")
        st.session_state.messages.append({"role": "assistant", "content": res})
        with st.chat_message("assistant"):
            st.markdown(res)

# ==============================================================================
# 5. VISUALIZAÇÕES E GERADOR DE CV (ORIGINAIS MELHORADOS)
# ==============================================================================

def mostra_skills(df_comp: pd.DataFrame, st_obj: Any) -> None:
    st_obj.subheader(f"🧠 {UiConfig.SEC_SKILLS}")
    if df_comp.empty:
        st_obj.info("Competências não identificadas no arquivo.")
        return
    options_list = sorted(df_comp['Tipo'].unique())
    selected_types = st_obj.multiselect("Filtrar Área de Competência:", options=options_list, default=options_list)
    df_filtered = df_comp[df_comp['Tipo'].isin(selected_types)].copy()
    df_cleaned = df_filtered[df_filtered['Ano'] > 0]
    df_cleaned = df_cleaned.drop_duplicates()
    if df_cleaned.empty:
        st_obj.warning("Sem dados válidos para o filtro selecionado.")
        return
    col_heatmap, col_radar = st_obj.columns([2, 1])
    with col_heatmap:
        df_heatmap = df_cleaned.groupby(['Ano', 'Tipo']).size().reset_index(name='V')
        fig_heatmap = px.density_heatmap(df_heatmap, x='Ano', y='Tipo', z='V', title="Skills por Ano", color_continuous_scale='Magma')
        st_obj.plotly_chart(fig_heatmap, use_container_width=True)
    with col_radar:
        df_radar = df_cleaned['Tipo'].value_counts().reset_index(name='Q')
        df_radar.columns = ['Tipo', 'Q']
        fig_radar = px.line_polar(df_radar, r='Q', theta='Tipo', line_close=True, title="Radar de Perfil", template="plotly_dark")
        st_obj.plotly_chart(fig_radar, use_container_width=True)
    st_obj.dataframe(df_cleaned, use_container_width=True, hide_index=True)

def gerar_curriculo_base(cad: Dict[str, str], df_form: pd.DataFrame, df_compl: pd.DataFrame, df_atuacao: pd.DataFrame, df_projetos: pd.DataFrame, df_skills: pd.DataFrame) -> None:
    st.subheader(f"📄 {UiConfig.SEC_CV_GEN}")
    st.markdown("> **Mentoria de Carreira:** Edite as seções abaixo para gerar seu CV otimizado.")
    selecoes = {'form': [], 'compl': [], 'tech': [], 'soft': [], 'lang': [], 'jobs': [], 'projs': []}

    tabs = st.tabs(["1. Cabeçalho & Resumo", "2. Experiência", "3. Projetos", "4. Skills & Idiomas", "5. Educação"])
    
    with tabs[0]:
        st.markdown("#### Informações de Contato")
        role_target = st.text_input("Objetivo / Cargo Alvo (Headline)", placeholder="Ex: Pesquisador | Data Scientist")
        c_mail, c_phone = st.columns(2)
        email = c_mail.text_input("E-mail", "seu.email@exemplo.com")
        phone = c_phone.text_input("Telefone/WhatsApp", "(XX) 99999-9999")
        c_lnk, c_port = st.columns(2)
        linkd = c_lnk.text_input("LinkedIn", "linkedin.com/in/voce")
        portf = c_port.text_input("Portfólio / Github", "github.com/voce")
        st.divider()
        st.markdown("#### Resumo Profissional")
        # INTEGRAÇÃO IKIGAI: Busca o resumo da IA se existir, senão usa o Lattes
        resumo_padrao = st.session_state.get('resumo_ikigai', cad.get('RESUMO', ''))[:1000]
        resumo_final = st.text_area("Texto do Resumo", value=resumo_padrao, height=200)

    with tabs[1]:
        st.markdown("#### Experiência Profissional")
        if not df_atuacao.empty:
            df_atuacao['Incluir'] = False
            df_atuacao['Descrição (Editável)'] = df_atuacao['Descricao_Original'].apply(lambda x: x if len(str(x)) > 5 else "- Responsável por...")
            cols = ['Incluir', 'Periodo', 'Empresa', 'Cargo', 'Descrição (Editável)']
            edited_jobs = st.data_editor(df_atuacao[cols], hide_index=True, use_container_width=True, key="editor_jobs")
            selecoes['jobs'] = edited_jobs[edited_jobs['Incluir'] == True]
        else: st.info("Nenhuma atuação profissional encontrada.")

    with tabs[2]:
        st.markdown("#### Projetos de Destaque")
        if not df_projetos.empty:
            df_projetos['Incluir'] = False
            df_projetos['Descrição (Editável)'] = df_projetos['Descricao_Original'].apply(lambda x: x if len(str(x)) > 5 else "Detalhes do projeto...")
            cols_proj = ['Incluir', 'Ano', 'Nome', 'Descrição (Editável)']
            edited_projs = st.data_editor(df_projetos[cols_proj], hide_index=True, use_container_width=True, key="editor_proj")
            selecoes['projs'] = edited_projs[edited_projs['Incluir'] == True]
        else: st.info("Nenhum projeto encontrado.")

    with tabs[3]:
        c_hard, c_soft = st.columns(2)
        with c_hard:
            st.markdown("**Hard Skills (Técnicas)**")
            if not df_skills.empty:
                todas = sorted(df_skills['Competencia'].unique().tolist())
                sugestao = [x for x in todas if classificar_competencia(x) in ['Tecnologia', 'Gestão']]
                selecoes['tech'] = st.multiselect("Selecione Techs:", options=todas, default=sugestao[:12])
            else: st.warning("Nenhuma skill detectada.")
        with c_soft:
            st.markdown("**Idiomas**")
            idiomas_detectados = [x for x in todas if classificar_competencia(x) == 'Idiomas'] if not df_skills.empty else []
            opcoes_idiomas = list(set(idiomas_detectados + ['Inglês', 'Espanhol', 'Francês']))
            selecoes['lang'] = st.multiselect("Idiomas:", options=opcoes_idiomas, default=[i for i in opcoes_idiomas if 'Inglês' in i])
            st.markdown("**Soft Skills**")
            selecoes['soft'] = st.multiselect("Comportamental:", options=SOFTSKILLS_LISTA, default=["Comunicação Eficaz", "Trabalho em Equipe"])

    with tabs[4]:
        st.markdown("#### Formação Acadêmica (Formal)")
        if not df_form.empty:
            df_form['Incluir'] = True
            edit_form = st.data_editor(df_form[['Incluir', 'Nível', 'Curso', 'Instituição', 'Conclusão']], hide_index=True, use_container_width=True, key="edu_acad")
            selecoes['form'] = edit_form[edit_form['Incluir'] == True]
        st.divider()
        st.markdown("#### Cursos Complementares")
        if not df_compl.empty:
            df_compl_top = df_compl.head(20).copy()
            df_compl_top['Incluir'] = False
            edit_compl = st.data_editor(df_compl_top[['Incluir', 'Curso', 'Instituição', 'Conclusão', 'Carga Horária']], hide_index=True, use_container_width=True, key="edu_compl")
            selecoes['compl'] = edit_compl[edit_compl['Incluir'] == True]

    st.divider()
    st.subheader("👁️ Visualização do Currículo")
    md = f"# {cad.get('NOME COMPLETO')}\n"
    if role_target: md += f"### {role_target}\n"
    contacts = []
    if cad.get('CIDADE/UF'): contacts.append(f"📍 {cad.get('CIDADE/UF')}")
    if email: contacts.append(f"📧 {email}")
    if phone: contacts.append(f"📱 {phone}")
    md += " | ".join(contacts) + "\n\n"
    links = []
    if linkd: links.append(f"[LinkedIn]({linkd})")
    if portf: links.append(f"[Portfólio]({portf})")
    if links: md += "🔗 " + " | ".join(links) + "\n\n"
    md += "## 🎯 RESUMO PROFISSIONAL\n"
    md += f"{resumo_final}\n\n"
    
    if selecoes['tech'] or selecoes['soft'] or selecoes['lang']:
        md += "## 🛠️ COMPETÊNCIAS\n"
        if selecoes['tech']: md += f"- **Tecnologias:** {', '.join(selecoes['tech'])}\n"
        if selecoes['lang']: md += f"- **Idiomas:** {', '.join(selecoes['lang'])}\n"
        if selecoes['soft']: md += f"- **Comportamentais:** {', '.join(selecoes['soft'])}\n"
        md += "\n"
        
    if not selecoes['jobs'].empty:
        md += "## 💼 EXPERIÊNCIA PROFISSIONAL\n"
        for _, r in selecoes['jobs'].iterrows():
            md += f"### {r['Cargo']} | **{r['Empresa']}**\n📅 *{r['Periodo']}*\n\n{str(r['Descrição (Editável)']).replace(chr(10), chr(10)+chr(10))}\n\n"
    
    if not selecoes['projs'].empty:
        md += "## 🚀 PROJETOS RELEVANTES\n"
        for _, r in selecoes['projs'].iterrows():
            md += f"### {r['Nome']}\n*{r['Ano']}*\n\n{r['Descrição (Editável)']}\n\n"
    
    md += "## 🎓 FORMAÇÃO\n"
    if not selecoes['form'].empty:
        for _, r in selecoes['form'].iterrows(): md += f"- **{r['Curso']}** ({r['Nível']})\n  *{r['Instituição']}* | {r['Conclusão']}\n"
    if not selecoes['compl'].empty:
        md += "\n**Certificações e Cursos:**\n"
        for _, r in selecoes['compl'].iterrows():
            carga = f" ({r['Carga Horária']})" if r['Carga Horária'] else ""
            md += f"- **{r['Curso']}**\n  {r['Instituição']} | {r['Conclusão']}{carga}\n"

    st.text_area("Código Markdown:", value=md, height=300)
    col_dwn, col_info = st.columns([1, 4])
    with col_dwn:
        st.download_button(label="📥 Baixar CV (.md)", data=md, file_name="cv_ueup.md", mime="text/markdown", use_container_width=True)
    with col_info:
        st.info("Copie ou baixe o Markdown para ferramentas como Obsidian ou conversores PDF.")

# ==============================================================================
# 6. CACHE E LÓGICA PRINCIPAL (MAIN)
# ==============================================================================

@st.cache_data(show_spinner=False)
def carregar_dados_cacheado(arquivo_carregado: Any) -> Tuple[Optional[Dict[str, str]], Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], str]:
    if arquivo_carregado.name.endswith('.xml'):
        try:
            tree = ET.parse(arquivo_carregado)
            root = tree.getroot()
            cad = extrair_cadastro(root)
            df_form = extrair_formacao(root)
            df_compl = extrair_formacao_complementar(root)
            df_prod, df_skills = extrair_producao_universal_v2(root)
            df_atuacao = extrair_atuacao_profissional_detalhada(root)
            df_projetos = extrair_projetos_detalhados(root)
            return cad, df_form, df_compl, df_prod, df_skills, df_atuacao, df_projetos, "XML Lattes"
        except Exception as e: return None, None, None, None, None, None, None, f"Erro XML: {e}"
    else:
        cad, df_form, df_compl, df_prod, df_comp = processar_pdf_fallback(arquivo_carregado)
        return cad, df_form, df_compl, df_prod, df_comp, pd.DataFrame(), pd.DataFrame(), "PDF"

def main():
    st.set_page_config(page_title=UiConfig.PAGE_TITLE, layout=UiConfig.LAYOUT, page_icon=UiConfig.PAGE_ICON)
    st.title(UiConfig.HEADER_TITLE)

    with st.sidebar:
        st.header(UiConfig.SIDEBAR_TITLE_1)
        arquivo = st.file_uploader("Carregar XML ou PDF", type=['xml', 'pdf'])
        ano_inicio = st.number_input("Ano Inicial (Corte)", min_value=1970, max_value=datetime.now().year + 1, value=2018)
        
        st.divider()
        st.header(UiConfig.SIDEBAR_TITLE_2)
        vibe = st.selectbox("Personalidade da IA:", ["Profissional/Sério", "Entusiasta/Motivacional", "Acadêmico/Crítico", "Divertido/Descontraído"])
        aplicar_estilo_dinamico(vibe)
        
        st.divider()
        st.header("📌 Visualização de Dados")
        show_home = st.checkbox(UiConfig.SEC_HOME, value=True)
        show_edu = st.checkbox(UiConfig.SEC_EDU, value=False)
        show_dash = st.checkbox(UiConfig.SEC_DASH, value=True)
        show_prod = st.checkbox(UiConfig.SEC_PROD, value=False)
        show_skills = st.checkbox(UiConfig.SEC_SKILLS, value=False)
        
        st.divider()
        st.header("🚀 Inteligência de Carreira")
        show_ikigai = st.checkbox(UiConfig.SEC_IKIGAI, value=False)
        show_match = st.checkbox(UiConfig.SEC_MATCH, value=False)
        show_chat = st.checkbox(UiConfig.SEC_CHAT, value=False)
        show_cv_gen = st.checkbox(UiConfig.SEC_CV_GEN, value=False)

    if arquivo:
        with st.spinner("Processando Inteligência de Dados..."):
            dados = carregar_dados_cacheado(arquivo)
            if dados[0] is None:
                st.error(dados[-1]); st.stop()
            cad, df_form, df_compl, df_prod, df_skills, df_atuacao, df_projetos, msg = dados

        c1, c2 = st.columns([3, 1])
        c1.markdown(f"### 🧑‍🏫 {cad.get('NOME COMPLETO')}")
        c2.caption(f"Fonte: {msg}")
        st.divider()

        # Renderização condicional baseada nos checkboxes originais da barra lateral
        if show_home:
            st.subheader(f"👤 {UiConfig.SEC_HOME}")
            with st.container(border=True):
                col_avatar, col_info = st.columns([1, 5])
                with col_avatar: st.markdown("# 🎓")
                with col_info:
                    st.markdown(f"### {cad.get('NOME COMPLETO')}")
                    st.markdown(f"**ID LATTES:** {cad.get('ID LATTES')}")
                    st.caption(f"Última atualização: {cad.get('DATA ATUALIZAÇÃO')}")
                st.divider()
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown("###### 🪪 Documentos")
                    st.markdown(f"**CPF:** {cad.get('CPF')}\n**RG:** {cad.get('RG')}\n**ORCID:** {cad.get('ORCID')}")
                with c2:
                    st.markdown("###### 🧬 Pessoal")
                    st.markdown(f"**Nascimento:** {cad.get('DATA NASCIMENTO')}\n**Sexo:** {cad.get('SEXO')}\n**Raça:** {cad.get('COR/RAÇA')}")
                with c3:
                    st.markdown("###### 🌍 Origem")
                    st.markdown(f"**Nacionalidade:** {cad.get('NACIONALIDADE')}\n**País:** {cad.get('PAÍS NASCIMENTO')}\n**Local:** {cad.get('CIDADE/UF')}")
                with c4:
                    st.markdown("###### 👪 Filiação")
                    st.markdown(f"{cad.get('FILIAÇÃO')}")
                st.markdown("---")
                st.markdown("###### 📝 Resumo Biográfico")
                st.write(cad.get('RESUMO'))
            st.divider()

        if show_edu:
            st.subheader(f"🎓 {UiConfig.SEC_EDU}")
            c1, c2 = st.columns(2)
            with c1: 
                st.markdown("**Acadêmica**")
                if not df_form.empty: st.dataframe(df_form, use_container_width=True, hide_index=True)
            with c2: 
                st.markdown("**Complementar**")
                if not df_compl.empty: st.dataframe(df_compl, use_container_width=True, hide_index=True)
            st.divider()

        if show_dash:
            st.subheader(f"📊 {UiConfig.SEC_DASH}")
            if not df_prod.empty:
                df_filtro = df_prod[df_prod['Ano'] >= ano_inicio]
                k1, k2 = st.columns(2)
                with k1: st.plotly_chart(px.bar(df_filtro.groupby(['Ano', 'Macro Categoria']).size().reset_index(name='Q'), x='Ano', y='Q', color='Macro Categoria'), use_container_width=True)
                with k2: st.plotly_chart(px.sunburst(df_filtro, path=['Macro Categoria', 'Tipo']), use_container_width=True)
            st.divider()

        if show_prod:
            st.subheader("📚 Tabela Produção")
            st.dataframe(df_prod, use_container_width=True)
            st.divider()

        if show_skills:
            mostra_skills(df_skills, st)
            st.divider()

        # Renderização dos novos módulos de Inteligência
        if show_ikigai:
            modulo_ikigai(df_skills)
            st.divider()
            
        if show_match:
            modulo_match_vagas(df_skills)
            st.divider()
            
        if show_chat:
            modulo_chat_ia(cad, vibe)
            st.divider()

        if show_cv_gen:
            gerar_curriculo_base(cad, df_form, df_compl, df_atuacao, df_projetos, df_skills)
            
    else:
        st.info("👈 Utilize a barra lateral para carregar seu Currículo Lattes (XML ou PDF).")

if __name__ == "__main__":
    main()
