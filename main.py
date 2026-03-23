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
# 1. CONSTANTES, CONFIGURAÇÕES E TEMATIZAÇÃO DINÂMICA
# ==============================================================================

class UiConfig:
    PAGE_TITLE = "ueUP AI - Mentoria Lattes"
    PAGE_ICON = "🚀"
    LAYOUT = "wide"
    HEADER_TITLE = "🚀 ueUP AI: Lattes, Ikigai & Career Match v3.5"
    
    # Nomes das Seções
    SEC_HOME = "Ficha Cadastral"
    SEC_EDU = "Formação"
    SEC_DASH = "Analytics"
    SEC_SKILLS = "Inteligência de Skills"
    SEC_IKIGAI = "Mentoria Ikigai"
    SEC_MATCH = "Match de Vagas"
    SEC_CV_GEN = "Gerador de Currículo"

def aplicar_estilo_dinamico(vibe):
    """Injeta CSS baseado no humor selecionado."""
    temas = {
        "Profissional/Sério": {"primary": "#004080", "bg": "#f0f2f6", "text": "#1a1a1a"},
        "Entusiasta/Motivacional": {"primary": "#ff4b4b", "bg": "#fff5f5", "text": "#333333"},
        "Acadêmico/Crítico": {"primary": "#2e7d32", "bg": "#f1f8e9", "text": "#212121"},
        "Divertido/Descontraído": {"primary": "#7b1fa2", "bg": "#f3e5f5", "text": "#000000"}
    }
    t = temas.get(vibe, temas["Profissional/Sério"])
    
    style = f"""
    <style>
        .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
        .stButton>button {{ border-radius: 20px; border: 2px solid {t['primary']}; color: {t['primary']}; }}
        .stSidebar {{ background-color: #ffffff; border-right: 1px solid #ddd; }}
        h1, h2, h3 {{ color: {t['primary']} !important; }}
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)

class XmlTags:
    ROOT_ID, UPDATE_DATE, SYSTEM_ORIGIN = 'NUMERO-IDENTIFICADOR', 'DATA-ATUALIZACAO', 'SISTEMA-ORIGEM-XML'
    GENERAL_DATA, NAME, NATIONALITY = 'DADOS-GERAIS', 'NOME-COMPLETO', 'NACIONALIDADE'
    BIRTH_COUNTRY, BIRTH_CITY, BIRTH_STATE = 'PAIS-DE-NASCIMENTO', 'CIDADE-NASCIMENTO', 'UF-NASCIMENTO'
    CPF, ORCID, GENDER, BIRTH_DATE, RACE = 'CPF', 'ORCID-ID', 'SEXO', 'DATA-NASCIMENTO', 'RACA-OU-COR'
    PASSPORT, ID_CARD, ID_AGENCY, ID_STATE = 'NUMERO-DO-PASSAPORTE', 'NUMERO-IDENTIDADE', 'ORGAO-EMISSOR', 'UF-ORGAO-EMISSOR'
    MOTHER, FATHER, SUMMARY_CV, SUMMARY_TEXT = 'NOME-DA-MAE', 'NOME-DO-PAI', 'RESUMO-CV', 'TEXTO-RESUMO-CV-RH'
    PROF_ADDRESS, INSTITUTION = 'ENDERECO-PROFISSIONAL', 'NOME-INSTITUICAO-EMPRESA'
    ACADEMIC_EDU, OTHER_EDU, COMPL_EDU = 'FORMACAO-ACADEMICA-TITULACAO', 'OUTRA-FORMACAO', 'FORMACAO-COMPLEMENTAR'
    PROFESSIONAL_HIST, PROFESSIONAL_ITEM, JOB_LINKS = 'ATUACOES-PROFISSIONAIS', 'ATUACAO-PROFISSIONAL', 'VINCULOS'

MAPA_COMPETENCIAS = {
    'Tecnologia': ['python', 'sql', 'java', 'dados', 'data', 'analise', 'bi', 'dashboard', 'sistema', 'dev', 'iot', 'arduino', 'software', 'machine learning', 'artificial', 'excel', 'vba', 'power bi', 'tableau', 'steam', 'robotica', 'maker', 'programação', 'api', 'aws', 'cloud', 'azure', 'docker', 'git', 'linux', 'react', 'node', 'html', 'css', 'kubernetes', 'spark', 'hadoop', 'scikit', 'tensorflow'],
    'Gestão': ['gestão', 'liderança', 'coordenação', 'scrum', 'agile', 'projeto', 'planejamento', 'direção', 'negócios', 'marketing', 'estratégia', 'administração', 'pmbok', 'kanban', 'empreendedorismo', 'inovação', 'processos', 'produto', 'stakeholders'],
    'Acadêmico': ['docência', 'pesquisa', 'ensino', 'metodologia', 'didática', 'pedagogia', 'orientação', 'banca', 'tcc', 'artigo', 'publicação', 'congresso', 'anais', 'científica', 'educação', 'avaliador'],
    'Engenharia/Ind': ['engenharia', 'processos', 'manutenção', 'industrial', 'automação', 'eletrônica', 'civil', 'mecânica', 'produção', 'elétrica'],
    'Idiomas': ['inglês', 'espanhol', 'francês', 'alemão', 'italiano', 'mandarim']
}

SOFTSKILLS_LISTA = ["Comunicação Eficaz", "Trabalho em Equipe", "Liderança", "Resolução de Problemas", "Pensamento Crítico", "Adaptabilidade", "Gestão de Tempo", "Inteligência Emocional", "Criatividade", "Negociação", "Mentoria", "Proatividade", "Visão de Negócio"]

# ==============================================================================
# 2. FUNÇÕES DE PARSING (CONSOLIDADAS DO APP.PY)
# ==============================================================================

def limpar_texto(texto: str) -> str:
    return " ".join(texto.split()) if texto else ""

def formatar_data_br(data_str: str) -> str:
    return f"{data_str[:2]}/{data_str[2:4]}/{data_str[4:]}" if data_str and len(data_str) == 8 else data_str

def extrair_cadastro(root: ET.Element) -> Dict[str, str]:
    dados = {'NOME COMPLETO': 'Desconhecido', 'ID LATTES': '', 'DATA ATUALIZAÇÃO': '', 'RESUMO': 'Não informado', 'CIDADE/UF': '', 'CPF': '', 'SEXO': ''}
    if XmlTags.ROOT_ID in root.attrib: dados['ID LATTES'] = root.attrib.get(XmlTags.ROOT_ID, '')
    if XmlTags.UPDATE_DATE in root.attrib: dados['DATA ATUALIZAÇÃO'] = formatar_data_br(root.attrib.get(XmlTags.UPDATE_DATE, ''))
    dg = root.find(XmlTags.GENERAL_DATA)
    if dg is not None:
        dados['NOME COMPLETO'] = dg.get(XmlTags.NAME, 'Desconhecido').upper()
        res_tag = dg.find(XmlTags.SUMMARY_CV)
        if res_tag is not None: dados['RESUMO'] = limpar_texto(res_tag.get(XmlTags.SUMMARY_TEXT, ''))
        dados['CIDADE/UF'] = f"{dg.get(XmlTags.BIRTH_CITY, '')} / {dg.get(XmlTags.BIRTH_STATE, '')}"
        dados['CPF'] = dg.get(XmlTags.CPF, '')
        dados['SEXO'] = dg.get(XmlTags.GENDER, '')
    return dados

def extrair_atuacao_detalhada(root: ET.Element) -> pd.DataFrame:
    lista = []
    dg = root.find(XmlTags.GENERAL_DATA)
    if dg is not None:
        atuacoes = dg.find(XmlTags.PROFESSIONAL_HIST)
        if atuacoes is not None:
            for at in atuacoes.findall(XmlTags.PROFESSIONAL_ITEM):
                empresa = at.get(XmlTags.INSTITUTION)
                for vinculo in at.findall(XmlTags.JOB_LINKS):
                    cargo = vinculo.get('OUTRO-VINCULO-INFORMADO') or vinculo.get('TIPO-DE-VINCULO')
                    inicio = vinculo.get('ANO-INICIO')
                    fim = vinculo.get('ANO-FIM') or "Atual"
                    lista.append({'Empresa': empresa, 'Cargo': cargo, 'Periodo': f"{inicio} - {fim}", 'Inicio': inicio})
    return pd.DataFrame(lista).sort_values(by='Inicio', ascending=False) if lista else pd.DataFrame()

def extrair_skills_lattes(root: ET.Element) -> pd.DataFrame:
    competencias = []
    for k in root.findall('.//PALAVRAS-CHAVE'):
        for v in k.attrib.values():
            if v:
                cat = "Outros"
                for c, termos in MAPA_COMPETENCIAS.items():
                    if any(t in v.lower() for t in termos): cat = c; break
                competencias.append({'Competencia': v.title(), 'Tipo': cat})
    return pd.DataFrame(competencias).drop_duplicates() if competencias else pd.DataFrame()

# ==============================================================================
# 3. MÓDULOS DE INTELIGÊNCIA E MENTORIA
# ==============================================================================

def modulo_ikigai(df_skills, cad):
    st.header(f"🎡 {UiConfig.SEC_IKIGAI}")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Refine seu Propósito")
        love = st.text_area("1. O que você ama?", "Ex: Criar soluções de IoT e ensinar.")
        
        skills_detected = df_skills['Competencia'].tolist() if not df_skills.empty else []
        good_at = st.multiselect("2. No que você é bom? (Extraído do Lattes)", 
                                 options=list(set(SOFTSKILLS_LISTA + skills_detected)),
                                 default=skills_detected[:5] if skills_detected else None)
        
        needs = st.text_input("3. O que o mundo precisa?", "Ex: Inovação tecnológica na educação.")
        paid_for = st.text_input("4. Pelo que você pode ser pago?", "Ex: Professor de TI, Consultor de Transformação Digital.")

    with col2:
        st.markdown("### Visualização Ikigai")
        dot = graphviz.Digraph()
        dot.attr(rankdir='LR')
        for p in ['Paixão', 'Missão', 'Profissão', 'Vocação']: dot.node(p)
        dot.node('I', 'IKIGAI', shape='doublecircle', color='red', style='filled', fillcolor='yellow')
        dot.edge('Paixão', 'I'); dot.edge('Missão', 'I'); dot.edge('Profissão', 'I'); dot.edge('Vocação', 'I')
        st.graphviz_chart(dot)

def modulo_match_vagas(cad):
    st.header(f"🎯 {UiConfig.SEC_MATCH}")
    vaga_text = st.text_area("Cole aqui a descrição da vaga alvo:", height=200)
    if vaga_text:
        match = 82 # Simulação
        st.metric("Score de Match ueUP", f"{match}%")
        st.progress(match/100)
        c1, c2 = st.columns(2)
        with c1: st.success("**Ganhos:** Experiência com IoT e Docência.")
        with c2: st.warning("**Atenção:** Vaga pede Inglês C1, seu Lattes não especifica nível.")

# ==============================================================================
# 4. INTERFACE PRINCIPAL (UI/UX)
# ==============================================================================

def main():
    st.set_page_config(page_title=UiConfig.PAGE_TITLE, layout=UiConfig.LAYOUT, page_icon=UiConfig.PAGE_ICON)
    
    with st.sidebar:
        st.title("⚙️ Painel de Controle")
        vibe = st.select_slider("Humor da Mentoria:", options=["Profissional/Sério", "Entusiasta/Motivacional", "Acadêmico/Crítico", "Divertido/Descontraído"])
        aplicar_estilo_dinamico(vibe)
        
        foto = st.file_uploader("Upload de Perfil", type=['jpg', 'png'])
        if foto: st.image(foto, width=80)
        
        st.divider()
        arquivo = st.file_uploader("Carregar Lattes (XML ou PDF)", type=['xml', 'pdf'])

    if arquivo:
        # Processamento Principal (Rigor do app (2).py)
        if arquivo.name.endswith('.xml'):
            tree = ET.parse(arquivo)
            root = tree.getroot()
            cad = extrair_cadastro(root)
            df_atuacao = extrair_atuacao_detalhada(root)
            df_skills = extrair_skills_lattes(root)
        else:
            # Fallback PDF (Simplificado para o exemplo)
            cad = {"NOME COMPLETO": "Usuário PDF", "RESUMO": "Extração via PDF ativa."}
            df_atuacao = pd.DataFrame()
            df_skills = pd.DataFrame()

        st.title(f"Bem-vindo à sua mentoria, {cad['NOME COMPLETO'].split()[0]}")
        
        t1, t2, t3, t4, t5 = st.tabs([UiConfig.SEC_HOME, UiConfig.SEC_SKILLS, UiConfig.SEC_IKIGAI, UiConfig.SEC_MATCH, "💬 Chat Mentor"])
        
        with t1:
            st.subheader("Sua Trajetória")
            st.info(cad['RESUMO'])
            if not df_atuacao.empty:
                st.markdown("#### Histórico Profissional")
                st.table(df_atuacao[['Cargo', 'Empresa', 'Periodo']])

        with t2:
            st.subheader("Mapa de Competências")
            if not df_skills.empty:
                fig = px.pie(df_skills, names='Tipo', title="Distribuição de Skills")
                st.plotly_chart(fig)
                st.dataframe(df_skills, use_container_width=True)
            else:
                st.warning("Nenhuma skill detectada automaticamente.")

        with t3:
            modulo_ikigai(df_skills, cad)

        with t4:
            modulo_match_vagas(cad)

        with t5:
            st.subheader("💬 Chat Mentor ueUP")
            if "msgs" not in st.session_state: st.session_state.msgs = []
            for m in st.session_state.msgs:
                with st.chat_message(m["role"]): st.markdown(m["content"])
            
            if prompt := st.chat_input("Dúvidas sobre sua carreira?"):
                st.session_state.msgs.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.markdown(prompt)
                
                # Lógica de Tom Dinâmico
                res = f"[{vibe}] Como especialista em IA, vejo que sua experiência em {df_skills['Competencia'].iloc[0] if not df_skills.empty else 'sua área'} é um diferencial competitivo."
                st.session_state.msgs.append({"role": "assistant", "content": res})
                with st.chat_message("assistant"): st.markdown(res)
    else:
        st.warning("Arraste seu arquivo Lattes para o menu lateral para iniciar a análise.")

if __name__ == "__main__":
    main()main()
