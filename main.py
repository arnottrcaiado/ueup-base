import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Mentoria ueUP", layout="wide", initial_sidebar_state="collapsed")

# 2. INICIALIZAÇÃO DO ESTADO (STATE)
themes_config = {
    "standard": {"bg": "#F8F9FA", "primary": "#2E4053", "text": "#333", "label": "Padrão"},
    "calm": {"bg": "#E8F4F8", "primary": "#5DADE2", "text": "#1B4F72", "label": "Calmo"},
    "focused": {"bg": "#FEF9E7", "primary": "#F4D03F", "text": "#7D6608", "label": "Foco"},
    "energetic": {"bg": "#FDEDEC", "primary": "#E74C3C", "text": "#78281F", "label": "Energético"}
}
theme_keys = list(themes_config.keys())

if "theme_idx" not in st.session_state:
    st.session_state.theme_idx = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ikigai_focus" not in st.session_state:
    st.session_state.ikigai_focus = None

# --- LÓGICA DE ATALHOS DE TECLADO (JS INVISÍVEL) ---
# Este componente captura as teclas e simula o clique nos botões de troca
components.html(
    """
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        if (e.key.toLowerCase() === 'q') {
            const btnNext = doc.querySelector('button[kind="secondary"]:nth-child(1)'); 
            // Buscamos os botões de navegação por IDs ou posições se necessário
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'next', key: 'kbd'}, '*');
        } else if (e.key.toLowerCase() === 'a') {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'prev', key: 'kbd'}, '*');
        }
    });
    </script>
    """,
    height=0,
)

# 3. FUNÇÃO DE ESTILO DINÂMICO (HTML/CSS)
def apply_custom_style():
    current_key = theme_keys[st.session_state.theme_idx]
    t = themes_config[current_key]
    
    style = f"""
    <style>
    .stApp {{ 
        background-color: {t['bg']}; 
        color: {t['text']}; 
        transition: background-color 0.5s ease, color 0.5s ease; 
    }}
    .stButton>button {{
        border-radius: 12px;
        transition: all 0.3s;
        border: 1px solid {t['primary']};
    }}
    .stButton>button:hover {{
        background-color: {t['primary']};
        color: white !important;
    }}
    [data-testid="stMetricValue"] {{ color: {t['primary']}; }}
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)

apply_custom_style()

# 4. FUNÇÕES DE SUPORTE
def next_theme():
    st.session_state.theme_idx = (st.session_state.theme_idx + 1) % len(theme_keys)

def prev_theme():
    st.session_state.theme_idx = (st.session_state.theme_idx - 1) % len(theme_keys)

def analyze_intent(user_text):
    text = user_text.lower()
    if any(word in text for word in ["triste", "cansado", "ajuda", "mal"]):
        st.session_state.theme_idx = theme_keys.index("calm")
    elif any(word in text for word in ["foco", "estudar", "meta", "objetivo"]):
        st.session_state.theme_idx = theme_keys.index("focused")
    elif any(word in text for word in ["feliz", "animado", "vamos", "bora"]):
        st.session_state.theme_idx = theme_keys.index("energetic")

# 5. LAYOUT DE TRÊS COLUNAS
col_interacao, col_ikigai, col_acao = st.columns([1.2, 2, 0.8], gap="medium")

# --- COLUNA ESQUERDA: INTERAÇÃO ---
with col_interacao:
    st.subheader("💬 Mentoria Dialógica")
    
    # Navegação rápida (também serve como feedback para os atalhos Q e A)
    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("⬅️ [A] Anterior", use_container_width=True):
            prev_theme()
            st.rerun()
    with c_nav2:
        if st.button("Próximo [Q] ➡️", use_container_width=True):
            next_theme()
            st.rerun()

    with st.container(border=True):
        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).write(msg["content"])
            
    if prompt := st.chat_input("Como você está se sentindo?"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        analyze_intent(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": "Entendi. Como isso se conecta ao seu propósito hoje?"})
        st.rerun()

    st.divider()
    st.write("📸 Captura de Imagem / Reações")
    st.button("Capturar Sentimento (Câmera)")
    st.slider("Nível de Energia", 0, 100, 50)

# --- COLUNA CENTRAL: IKIGAI ---
with col_ikigai:
    current_theme_label = themes_config[theme_keys[st.session_state.theme_idx]]["label"]
    st.markdown(f"<h2 style='text-align: center;'>Sua Jornada ueUP</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; opacity: 0.7;'>Ambiente atual: <b>{current_theme_label}</b></p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("❤️ O QUE EU AMO", use_container_width=True): st.session_state.ikigai_focus = "love"
        if st.button("🛠️ O QUE SOU BOM", use_container_width=True): st.session_state.ikigai_focus = "skills"
    with c2:
        if st.button("🌍 O QUE O MUNDO PRECISA", use_container_width=True): st.session_state.ikigai_focus = "needs"
        if st.button("💰 PELO QUE SOU PAGO", use_container_width=True): st.session_state.ikigai_focus = "career"

    st.markdown("---")
    if st.session_state.ikigai_focus:
        st.info(f"Editando: {st.session_state.ikigai_focus.upper()}")
        st.text_area("Descreva aqui suas reflexões...", height=150, key="ikigai_input")
        st.button("Salvar Progresso")
    else:
        st.write("Clique em um elemento acima para detalhar seu propósito.")

# --- COLUNA DIREITA: AÇÕES ---
with col_acao:
    st.subheader("👤 Perfil & Ação")
    with st.expander("Acesso"):
        st.text_input("Email")
     ##   st.password("Senha")
        st.button("Entrar / Registrar")
    
    st.divider()
    st.subheader("🛣️ Trilhas de Carreira")
    st.progress(40, text="Trilha Researcher")
    st.progress(10, text="Trilha Deeptech Founder")
    
    if st.button("📄 Gerar Currículo Inteligente", use_container_width=True):
        st.balloons()
        st.success("Gerando...")

# 6. RODAPÉ
st.markdown("<br><hr><center><small>ueUP v1.1 | Use 'A' e 'Q' para navegar nos temas</small></center>", unsafe_allow_html=True)