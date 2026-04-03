#1. **Expansão de Personalidade e Humor:** Adicionei mais 2 opções para cada. Agora temos a IA "Tecnológica/Direta" (Cyberpunk) e "Mentor Filosófico" (Socrático). No humor, adicionei "Empolgado e Criativo" e "Zen/Calmo". O CSS e a Barra de Energia reagem a todas elas instantaneamente.
#2. **Visual da Trilha Dinâmica Aprimorado:** Desenhei um "Card Layout" para mostrar o caminho (Passado, Presente e Futuro). Adicionei escalas de avaliação interativas (`st.slider` e `st.checkbox`) para o utilizador medir o seu próprio domínio nas competências (Metodologia Ativa).
#3. **Filtros e Design no Analytics:** O *Dashboard* agora tem filtros multicritério e gráficos mais ricos. A área de *Skills* ganhou um novo gráfico de Barras com as "Top 10 Habilidades Extraídas".
#4. **Ingestão Multimodal Expandida:** Adicionei a área de upload de "Evidências Extras" (Certificados, Imagens, Portfólio) diretamente na *Sidebar* para enriquecer o perfil, com contagem dinâmica no ecrã de Ingestão.

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
# 1. CONSTANTES E CONFIGURAÇÕES GERAIS
# ==============================================================================

class UiConfig:
    PAGE_TITLE = "ueUP AI - Lattes & Carreira"
    PAGE_ICON = "🚀"
    LAYOUT = "wide"
    HEADER_TITLE = "🚀 ueUP AI: Career Analytics, Ikigai & Trilhas Dinâmicas"
    
    SIDEBAR_TITLE_1 = "1. Personalização da IA"
    SIDEBAR_TITLE_2 = "2. Navegação da Jornada"
    SIDEBAR_TITLE_3 = "3. Ingestão Multimodal"
    
    # Secções Macro (Roteamento)
    SEC_ONBOARDING = "🌟 Início: Autodescoberta (Ikigai)"
    SEC_INGESTAO = "📥 Analytics & Perfil"
    SEC_TRILHA = "🗺️ Trilha Dinâmica (Modo Foco)"
    SEC_CV_GEN = "📄 Match de Vagas & Currículo"

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
# 2. FUNÇÕES DE UX DINÂMICA E CORES (AMPLIADAS E BLINDADAS 4.0)
# ==============================================================================

def aplicar_estilo_dinamico(vibe: str, humor: str) -> str:
    """CSS Blindado: Templates globais com 6 Vibes e 6 Humores."""
    temas = {
        "Profissional/Sério": {"primary": "#005bb5", "bg_side": "#0e1117", "bg_main": "#f4f6f9"},
        "Entusiasta/Motivacional": {"primary": "#d32f2f", "bg_side": "#1a0b0b", "bg_main": "#fff5f5"},
        "Acadêmico/Crítico": {"primary": "#006b3c", "bg_side": "#09140b", "bg_main": "#f0f5f1"},
        "Divertido/Descontraído": {"primary": "#7b1fa2", "bg_side": "#120a1f", "bg_main": "#f9f5fa"},
        "Tecnológico/Direto": {"primary": "#00E676", "bg_side": "#000000", "bg_main": "#e8fdf0"},
        "Mentor Filosófico": {"primary": "#B8860B", "bg_side": "#1c140d", "bg_main": "#fcfaf5"}
    }
    
    humor_cores = {
        "motivado": "#FFD700",       # Dourado
        "reflexivo": "#00E5FF",      # Ciano
        "sobrecarregado": "#FF5252", # Vermelho
        "cansado": "#9E9E9E",        # Cinza
        "empolgado": "#FF7F50",      # Laranja/Coral
        "zen": "#20B2AA"             # Verde Água
    }
    
    t = temas.get(vibe, temas["Profissional/Sério"])
    h_color = humor_cores.get(humor, "#005bb5")
    
    st.markdown(f"""
        <style>
        .stApp, [data-testid="stAppViewContainer"] {{
            background-color: {t['bg_main']} !important;
        }}
        [data-testid="stSidebar"] > div:first-child, [data-testid="stSidebar"] {{ 
            background-color: {t['bg_side']} !important; 
            border-right: 4px solid {h_color} !important; 
        }}
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {{ color: #ffffff !important; }}
        div[data-baseweb="select"] span {{ color: #1e1e1e !important; }}

        /* FILE UPLOADER BLINDADO (Aplica-se a todos os Uploaders da tela) */
        div[data-testid="stFileUploader"] section,
        [data-testid="stFileUploadDropzone"] {{ 
            background-color: #1e1e24 !important; 
            border: 2px dashed {t['primary']} !important; 
            border-radius: 8px !important; 
        }}
        div[data-testid="stFileUploader"] section *,
        [data-testid="stFileUploadDropzone"] * {{ color: #ffffff !important; }}
        div[data-testid="stFileUploader"] button,
        [data-testid="stFileUploadDropzone"] button {{ 
            background-color: {t['primary']} !important; 
            border: 1px solid {t['primary']} !important; 
        }}
        div[data-testid="stFileUploader"] button *,
        [data-testid="stFileUploadDropzone"] button * {{ 
            color: #ffffff !important; font-weight: 800 !important; 
        }}
        div[data-testid="stFileUploader"] [data-testid="stUploadedFile"],
        [data-testid="stUploadedFile"] {{ 
            background-color: #2b2b36 !important; border: 1px solid #444 !important; border-radius: 6px !important; 
        }}
        div[data-testid="stFileUploader"] [data-testid="stUploadedFile"] *,
        [data-testid="stUploadedFile"] * {{ color: #ffffff !important; }}

        header[data-testid="stHeader"] {{ border-bottom: 4px solid {h_color} !important; background-color: transparent !important; }}
        .main h1, .main h2, .main h3, .main h4, .main h5 {{ color: {t['primary']} !important; }}
        .main .stButton>button {{ border: 2px solid {t['primary']} !important; color: {t['primary']} !important; background-color: transparent !important; font-weight: bold; }}
        .main .stButton>button:hover {{ background-color: {t['primary']} !important; color: #ffffff !important; }}
        </style>
    """, unsafe_allow_html=True)
    return h_color

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
# 3. PARSERS E MOTOR DE EXTRAÇÃO (LÓGICA INTACTA)
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
        except Exception as e: 
            return None, None, None, None, None, None, None, f"Erro XML: {e}"
    else:
        cad, df_form, df_compl, df_prod, df_comp = processar_pdf_fallback(arquivo_carregado)
        return cad, df_form, df_compl, df_prod, df_comp, pd.DataFrame(), pd.DataFrame(), "PDF"

# ==============================================================================
# 4. MÓDULOS DE INTERFACE E VISUALIZAÇÃO (TELA A TELA)
# ==============================================================================

def modulo_ikigai_onboarding(df_skills: pd.DataFrame) -> None:
    """Jornada de Autodescoberta Dialógica."""
    st.subheader("🎡 O Seu IKIGAI")
    st.markdown("O Ikigai ajuda a cruzar suas habilidades com seu propósito de vida e mercado. Esqueça formulários chatos por um momento.")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        love = st.text_area("1. O que você ama? (Paixão)", "Ex: Inovação, pesquisar IoT e mentorar pessoas.")
        skills_detected = df_skills['Competencia'].tolist() if not df_skills.empty else []
        good_at = st.multiselect("2. No que você é bom? (Extraído das suas evidências)", options=list(set(SOFTSKILLS_LISTA + skills_detected)), default=skills_detected[:3] if skills_detected else None)
        needs = st.text_input("3. O que o mundo precisa? (Missão)", "Ex: Transformação digital responsável.")
        paid_for = st.text_input("4. Pelo que pode ser pago? (Vocação)", "Ex: Consultoria em TI, Docência.")
        
        if st.button("Gerar Resumo Ikigai", use_container_width=True):
            habilidades_str = ", ".join(good_at) if good_at else "minhas habilidades técnicas"
            resumo_gerado = f"Profissional apaixonado por {love.lower()}, com forte atuação em {habilidades_str}. Busco impactar a sociedade através da {needs.lower()}, atuando com {paid_for.lower()}."
            st.session_state['resumo_ikigai'] = resumo_gerado
            st.success("Resumo gerado com sucesso! Ele já foi enviado para o seu Gerador de Currículo na última etapa.")
            st.info(resumo_gerado)

    with col2:
        dot = graphviz.Digraph()
        dot.attr(bgcolor='transparent')
        dot.node('A', 'Paixão'); dot.node('B', 'Missão'); dot.node('C', 'Vocação'); dot.node('D', 'Profissão')
        dot.edge('A', 'B'); dot.edge('B', 'C'); dot.edge('C', 'D'); dot.edge('D', 'A')
        dot.node('I', 'IKIGAI', shape='doublecircle', style='filled', fillcolor='#ffeb3b')
        dot.edge('A', 'I'); dot.edge('B', 'I'); dot.edge('C', 'I'); dot.edge('D', 'I')
        st.graphviz_chart(dot)

def modulo_ficha_cadastral(cad: Dict[str, str], arquivos_adicionais: list) -> None:
    with st.container(border=True):
        col_avatar, col_info = st.columns([1, 5])
        with col_avatar: st.markdown("# 🎓")
        with col_info:
            st.markdown(f"### {cad.get('NOME COMPLETO')}")
            st.markdown(f"**ID LATTES:** {cad.get('ID LATTES')}")
            st.caption(f"Última atualização: {cad.get('DATA ATUALIZAÇÃO')}")
        
        # Mostra as evidências extras que o usuário subiu
        if arquivos_adicionais:
            st.success(f"📎 {len(arquivos_adicionais)} evidência(s) extras (Certificados/Portfólio) anexadas ao seu perfil localmente.")
        
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

def modulo_formacao(df_form: pd.DataFrame, df_compl: pd.DataFrame) -> None:
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown("**Acadêmica**")
        if not df_form.empty: st.dataframe(df_form, use_container_width=True, hide_index=True)
    with c2: 
        st.markdown("**Complementar**")
        if not df_compl.empty: st.dataframe(df_compl, use_container_width=True, hide_index=True)

def modulo_dashboard(df_prod: pd.DataFrame, ano_inicio: int) -> None:
    """Dashboard de Produção com filtros visuais ampliados."""
    st.subheader(f"📊 Produção e Evolução")
    if not df_prod.empty:
        # Filtros visuais
        filtros_col, _ = st.columns([2, 1])
        cats_disponiveis = df_prod['Macro Categoria'].unique().tolist()
        cats_selecionadas = filtros_col.multiselect("Filtrar por Categoria Lattes:", cats_disponiveis, default=cats_disponiveis)
        
        df_filtro = df_prod[(df_prod['Ano'] >= ano_inicio) & (df_prod['Macro Categoria'].isin(cats_selecionadas))]
        
        if df_filtro.empty:
            st.warning("Nenhum dado encontrado para os filtros aplicados.")
            return

        k1, k2 = st.columns(2)
        with k1: 
            df_bar = df_filtro.groupby(['Ano', 'Macro Categoria']).size().reset_index(name='Q')
            fig_bar = px.bar(df_bar, x='Ano', y='Q', color='Macro Categoria', title="Evolução Anual", text_auto=True)
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
        with k2: 
            fig_sun = px.sunburst(df_filtro, path=['Macro Categoria', 'Tipo'], title="Distribuição do Portfólio")
            fig_sun.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, l=0, r=0, b=0))
            st.plotly_chart(fig_sun, use_container_width=True)

def mostra_skills(df_comp: pd.DataFrame, st_obj: Any) -> None:
    """Painel de Skills aprimorado com Top Skills em Barras."""
    st_obj.subheader(f"🧠 Inteligência de Skills")
    if df_comp.empty:
        st_obj.info("Competências não identificadas no arquivo.")
        return
    options_list = sorted(df_comp['Tipo'].unique())
    selected_types = st_obj.multiselect("Filtrar Área de Competência:", options=options_list, default=options_list)
    
    df_filtered = df_comp[df_comp['Tipo'].isin(selected_types)].copy()
    df_cleaned = df_filtered[df_filtered['Ano'] > 0].drop_duplicates()
    
    if df_cleaned.empty:
        st_obj.warning("Sem dados válidos para o filtro selecionado.")
        return
        
    col_bar, col_radar = st_obj.columns([1.5, 1])
    with col_bar:
        df_top = df_cleaned['Competencia'].value_counts().head(10).reset_index()
        df_top.columns = ['Competencia', 'Frequência']
        fig_top = px.bar(df_top, x='Frequência', y='Competencia', orientation='h', title="Top 10 Habilidades Extraídas", color='Frequência', color_continuous_scale='Teal')
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st_obj.plotly_chart(fig_top, use_container_width=True)
    with col_radar:
        df_radar = df_cleaned['Tipo'].value_counts().reset_index(name='Q')
        df_radar.columns = ['Tipo', 'Q']
        fig_radar = px.line_polar(df_radar, r='Q', theta='Tipo', line_close=True, title="Radar de Macro-Perfil")
        fig_radar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st_obj.plotly_chart(fig_radar, use_container_width=True)
        
    with st_obj.expander("Ver Matriz de Calor (Heatmap) de Skills por Ano"):
        df_heatmap = df_cleaned.groupby(['Ano', 'Tipo']).size().reset_index(name='V')
        fig_heatmap = px.density_heatmap(df_heatmap, x='Ano', y='Tipo', z='V', color_continuous_scale='Magma')
        st_obj.plotly_chart(fig_heatmap, use_container_width=True)

def modulo_trilha_dinamica(cad: Dict[str, str], vibe: str) -> None:
    """Grafo de Trilha (DAG) com escalas de avaliação e Modo Foco."""
    col_obj, col_foco = st.columns([3, 1])
    col_obj.markdown("### 🎯 Trilha de Letramento: Especialista em Dados")
    modo_foco = col_foco.toggle("⚡ MODO FOCO", value=False, help="Oculta a jornada completa e foca no agora.")

    if modo_foco:
        st.warning("🌫️ **Névoa do Futuro ativada:** Sua carga cognitiva foi reduzida.")
        with st.container(border=True):
            st.markdown("#### 🔵 NÓ ATUAL: Lógica de Extração com Python (30 min)")
            st.progress(0.2, "Micro-sprint em andamento...")
            
            st.markdown("**Checklist do Sprint:**")
            st.checkbox("Ler documentação do BeautifulSoup")
            st.checkbox("Montar o primeiro script de parser")
            st.checkbox("Lidar com exceções (try/except)")
            
            st.markdown("---")
            st.slider("Em uma escala de 1 a 5, qual o seu domínio atual neste tópico?", min_value=1, max_value=5, value=2, help="Isto ajudará a IAG a ajustar a complexidade da trilha.")
            
            st.button("🚀 CONCLUIR MICRO-SPRINT", use_container_width=True, type="primary")
            
        st.markdown("- **Próximo Passo:** Persistência em Banco de Dados SQL (20 min)")
    else:
        st.progress(0.45, text="Progresso Consolidado da Trilha: 45% (Faltam ~4 semanas no ritmo atual)")
        
        st.markdown("#### Seu Mapa de Jornada")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("✔️ **Concluído**\n\nFundamentos de Algoritmos\n\n*Autoavaliação: 4.5/5*")
        with c2:
            st.success("🔵 **Nó Atual**\n\nLógica de Extração Python\n\n*Em andamento*")
            st.slider("Avalie seu domínio parcial (1-5):", 1, 5, 2, key="slider_trilha")
        with c3:
            st.markdown("<div style='opacity: 0.5; border: 1px dashed gray; padding: 10px; border-radius: 5px;'>⚪ <b>Próximo Passo</b><br><br>Persistência em Bancos SQL</div>", unsafe_allow_html=True)

        st.caption("🌫️ *Névoa do Futuro: Pipelines ETL e Dashboards (Desbloqueia em breve)*")
        st.info("💡 A Trilha Dinâmica é re-calculada automaticamente cada vez que o seu perfil é validado pelo sistema.")
        
    st.divider()
    st.subheader(f"💬 Mentor IAG ueUP")
    st.markdown("Relate sentimentos, dúvidas sobre a competência atual ou peça para pivotar sua carreira.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])

    nome_usuario = cad.get('NOME COMPLETO', 'Visitante').split()[0]
    if prompt := st.chat_input(f"Como foi o sprint anterior, {nome_usuario}? Travou em algo?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        toms = {
            "Profissional/Sério": f"Avaliando seu input ({prompt}...), recomendo uma revisão estratégica focada em resultados.",
            "Entusiasta/Motivacional": f"Incrível! Todo o progresso em '{prompt}' constrói a sua base de sucesso. Vamos em frente!",
            "Acadêmico/Crítico": f"Do ponto de vista cognitivo, a dificuldade em '{prompt}' é um estágio de assimilação necessário.",
            "Divertido/Descontraído": f"Tranquilo! Aprender sobre '{prompt}' dá um nó na cabeça no começo. Vamos juntos.",
            "Tecnológico/Direto": f"Input recebido: '{prompt}'. Analisando gaps. Recomendação: Iterar o processo de estudo em blocos curtos.",
            "Mentor Filosófico": f"O desafio em '{prompt}' nos questiona: o que realmente significa dominar uma habilidade? Reflita sobre os fundamentos."
        }
        res = toms.get(vibe, "Recebido! Como posso auxiliar melhor?")
        st.session_state.messages.append({"role": "assistant", "content": res})
        with st.chat_message("assistant"): st.markdown(res)

def modulo_match_vagas() -> None:
    st.markdown("Analise se o seu perfil Lattes + Evidências Extras está aderente a uma vaga de mercado.")
    vaga_text = st.text_area("Cole a descrição da vaga alvo (Job Description):", height=150)
    if st.button("Analisar Aderência à Vaga"):
        if vaga_text:
            st.metric("Score de Aderência", "82%", "+15% (Bom fit)")
            st.progress(0.82)
            c1, c2 = st.columns(2)
            with c1: st.success("**Gaps Positivos:**\n- Sólida experiência em pesquisa e ensino.\n- Forte base analítica identificada.")
            with c2: st.warning("**Gaps a Desenvolver:**\n- Falta evidência explícita em Cloud (AWS/Azure).\n- Experiência comercial precisa de maior destaque.")
        else:
            st.warning("Cole o texto da vaga primeiro.")

def gerar_curriculo_base(cad: Dict[str, str], df_form: pd.DataFrame, df_compl: pd.DataFrame, df_atuacao: pd.DataFrame, df_projetos: pd.DataFrame, df_skills: pd.DataFrame) -> None:
    st.markdown("> **Mentoria de Carreira:** A IAG gerará um currículo Markdown focado na vaga escolhida. Edite as seções brutas abaixo se necessário.")
    
    selecoes = {'form': pd.DataFrame(), 'compl': pd.DataFrame(), 'tech': [], 'soft': [], 'lang': [], 'jobs': pd.DataFrame(), 'projs': pd.DataFrame()}
    tabs = st.tabs(["1. Cabeçalho & Resumo", "2. Experiência", "3. Projetos", "4. Skills & Idiomas", "5. Educação"])
    
    with tabs[0]:
        st.markdown("#### Informações de Contato")
        role_target = st.text_input("Objetivo / Cargo Alvo (Headline)", placeholder="Ex: Analista de Dados Pleno")
        c_mail, c_phone = st.columns(2)
        email = c_mail.text_input("E-mail", "seu.email@exemplo.com")
        phone = c_phone.text_input("Telefone/WhatsApp", "(XX) 99999-9999")
        c_lnk, c_port = st.columns(2)
        linkd = c_lnk.text_input("LinkedIn", "linkedin.com/in/voce")
        portf = c_port.text_input("Portfólio / Github", "github.com/voce")
        st.divider()
        resumo_padrao = st.session_state.get('resumo_ikigai', cad.get('RESUMO', ''))[:1000]
        resumo_final = st.text_area("Texto do Resumo (Editável)", value=resumo_padrao, height=200)

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
            st.markdown("**Idiomas e Soft Skills**")
            idiomas_detectados = [x for x in todas if classificar_competencia(x) == 'Idiomas'] if not df_skills.empty else []
            opcoes_idiomas = list(set(idiomas_detectados + ['Inglês', 'Espanhol', 'Francês']))
            selecoes['lang'] = st.multiselect("Idiomas:", options=opcoes_idiomas, default=[i for i in opcoes_idiomas if 'Inglês' in i])
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
    st.subheader("👁️ Visualização Final do Currículo")
    md = f"# {cad.get('NOME COMPLETO', 'Seu Nome Aqui')}\n"
    if role_target: md += f"### {role_target}\n"
    contacts = []
    if cad.get('CIDADE/UF'): contacts.append(f"📍 {cad.get('CIDADE/UF')}")
    if email: contacts.append(f"📧 {email}")
    if phone: contacts.append(f"📱 {phone}")
    if contacts: md += " | ".join(contacts) + "\n\n"
    
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

    st.text_area("Código Markdown Bruto (ATS Friendly):", value=md, height=300)
    col_dwn, col_info = st.columns([1, 4])
    with col_dwn:
        st.download_button(label="📥 Baixar CV (.md)", data=md, file_name="cv_ueup.md", mime="text/markdown", use_container_width=True)
    with col_info:
        st.info("Utilize este arquivo `.md` em conversores ATS ou ferramentas como o Obsidian.")

# ==============================================================================
# 6. ORQUESTRADOR PRINCIPAL (MAIN E ROTEAMENTO MESTRE)
# ==============================================================================

def main() -> None:
    LOGO_PATH = "logo_ueup.jpeg"

    try:
        st.set_page_config(page_title=UiConfig.PAGE_TITLE, layout=UiConfig.LAYOUT, page_icon=LOGO_PATH)
    except Exception:
        st.set_page_config(page_title=UiConfig.PAGE_TITLE, layout=UiConfig.LAYOUT, page_icon=UiConfig.PAGE_ICON)
    
    col_logo, col_title = st.columns([1, 10])
    with col_logo:
        try: st.image(LOGO_PATH, width=70) 
        except Exception: st.markdown(f"<h1>{UiConfig.PAGE_ICON}</h1>", unsafe_allow_html=True)
    with col_title:
        st.title(UiConfig.HEADER_TITLE)

    with st.sidebar:
        try: st.image(LOGO_PATH, use_container_width=True)
        except Exception: pass
            
        st.header(UiConfig.SIDEBAR_TITLE_1)
        opcoes_humor = {
            "🚀 Motivado e focado": "motivado",
            "🤔 Reflexivo, buscando clareza": "reflexivo",
            "🤯 Sobrecarregado, preciso de direção": "sobrecarregado",
            "😴 Cansado, prefiro algo direto": "cansado",
            "🤩 Empolgado e criativo": "empolgado",
            "🧘 Zen, num ritmo calmo": "zen"
        }
        humor_estado = opcoes_humor[st.selectbox("Como se sente hoje?", list(opcoes_humor.keys()))]
        st.session_state['humor_usuario'] = humor_estado
        
        opcoes_vibe = {
            "👔 Profissional/Sério": "Profissional/Sério",
            "🔥 Entusiasta/Motivacional": "Entusiasta/Motivacional",
            "🧐 Acadêmico/Crítico": "Acadêmico/Crítico",
            "😎 Divertido/Descontraído": "Divertido/Descontraído",
            "🤖 Tecnológico/Direto": "Tecnológico/Direto",
            "🧠 Mentor Filosófico": "Mentor Filosófico"
        }
        vibe_estado = opcoes_vibe[st.selectbox("Personalidade da IA:", list(opcoes_vibe.keys()))]
        
        st.divider()
        st.header(UiConfig.SIDEBAR_TITLE_2)
        menu = st.radio("Jornada ueUP", [
            UiConfig.SEC_ONBOARDING,
            UiConfig.SEC_INGESTAO,
            UiConfig.SEC_TRILHA,
            UiConfig.SEC_CV_GEN
        ])
        
        st.divider()
        st.header(UiConfig.SIDEBAR_TITLE_3)
        st.caption("A base principal do seu perfil")
        arquivo = st.file_uploader("Carregar Lattes (XML/PDF)", type=['xml', 'pdf'])
        ano_inicio = st.number_input("Ano Base (Filtro Gráficos)", min_value=1970, max_value=datetime.now().year + 1, value=2018)
        
        st.caption("Evidências Extras")
        arquivos_adicionais = st.file_uploader("Certificados, Portfólio (PDF/Imagens)", accept_multiple_files=True)

    # Injeção Global de CSS e Cor da Barra de Energia
    h_color = aplicar_estilo_dinamico(vibe_estado, humor_estado)
    st.markdown(f"<div style='height: 5px; width: 100%; background-color: {h_color}; border-radius: 5px; margin-top: -15px; margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # Processamento de Dados Lattes
    cad, df_form, df_compl, df_prod, df_skills, df_atuacao, df_projetos = {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    if arquivo:
        with st.spinner("Motor de Dados ueUP trabalhando..."):
            dados = carregar_dados_cacheado(arquivo)
            if dados[0] is None:
                st.error(dados[-1])
                st.stop()
            cad, df_form, df_compl, df_prod, df_skills, df_atuacao, df_projetos, msg = dados

    # ==========================================================================
    # ROTEAMENTO E RENDERIZAÇÃO DOS MÓDULOS 
    # ==========================================================================

    if menu == UiConfig.SEC_ONBOARDING:
        modulo_ikigai_onboarding(df_skills)

    elif menu == UiConfig.SEC_INGESTAO:
        st.subheader(f"📊 {UiConfig.SEC_INGESTAO}")
        if arquivo and cad:
            modulo_ficha_cadastral(cad, arquivos_adicionais)
            st.divider()
            modulo_dashboard(df_prod, ano_inicio)
            st.divider()
            st.subheader(f"🎓 Formação Extraída")
            modulo_formacao(df_form, df_compl)
            st.divider()
            mostra_skills(df_skills, st)
            with st.expander("Ver Tabela Completa de Produção Lattes"):
                st.dataframe(df_prod, use_container_width=True)
        else:
            st.info("👈 Faça a ingestão (Upload) do seu Currículo Lattes na barra lateral para habilitar a inteligência de dados analítica.")

    elif menu == UiConfig.SEC_TRILHA:
        modulo_trilha_dinamica(cad, vibe_estado)

    elif menu == UiConfig.SEC_CV_GEN:
        st.subheader(f"💼 {UiConfig.SEC_CV_GEN}")
        if arquivo and cad:
            modulo_match_vagas()
            st.divider()
            gerar_curriculo_base(cad, df_form, df_compl, df_atuacao, df_projetos, df_skills)
        else:
            st.warning("👈 A Inteligência do Gerador de Currículos e Match de Vagas exige que seu perfil base esteja carregado no painel à esquerda.")

if __name__ == "__main__":
    main()
