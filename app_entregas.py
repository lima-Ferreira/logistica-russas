import streamlit as st
import pandas as pd
import unicodedata

# --- CONFIGURAÇÃO DA PÁGINA (Foco no Mobile) ---
st.set_page_config(page_title="Logística Russas", page_icon="🚛", layout="centered")

# CSS para remover espaços em branco no topo e deixar visual limpo
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Esconde o botão de 'Manage App' do Streamlit Cloud */
    .stAppDeployButton {display:none;}
    div[data-testid="stStatusWidget"] {display:none;}
    .viewerBadge_container__1QS1n {display:none !important;}
    
    /* Ajustes para mobile */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1 { font-size: 1.6rem !important; margin-bottom: 0.5rem; }
    .stTextInput { margin-top: -1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- LINK DA PLANILHA (Mantenha o seu link de 'Publicar na Web') ---
URL_PLANILHA = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQIcW3eGNnVmZA8TCbXqwrzhFWkMHG2-W-Tc9Aghs4bg9rKXBBdXzhmhoM2U-galWkbaKhw89ZaMomX/pub?output=csv"

def normalizar(texto):
    if not texto: return ""
    nfkd_form = unicodedata.normalize('NFKD', str(texto))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().strip()

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        return pd.read_csv(URL_PLANILHA)
    except:
        return pd.DataFrame()

df = carregar_dados()

# --- INTERFACE ENXUTA ---
st.title("🚛 Logística Russas")

if not df.empty:
    # Campo de busca com ícone
    busca_usuario = st.text_input("", placeholder="🔍 Digite o bairro ou sítio...")
    busca_limpa = normalizar(busca_usuario)

    if busca_limpa:
        df_busca = df.copy()
        df_busca['temp'] = df_busca['Localidade'].apply(normalizar)
        res = df_busca[df_busca['temp'] == busca_limpa]
        
        if not res.empty:
            item = res.iloc[0] # Pega a primeira linha
            
            # Resultado em destaque
            st.subheader(f"📍 {item['Localidade'].upper()}")
            
            # Cards de informação
            st.info(f"**ROTA:** {item['Rota']}")
            st.success(f"**ENTREGAS:** {item['Dias']}")
        else:
            st.error(f"❌ '{busca_usuario}' não encontrado.")

    # Menu secundário compacto
    with st.expander("📋 Ver Tabela Completa"):
        st.dataframe(df, hide_index=True, use_container_width=True)
    
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
else:
    st.warning("⚠️ Aguardando dados da planilha...")

st.caption("v1.0 - Sistema Interno")

