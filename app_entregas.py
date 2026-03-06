import streamlit as st
import pandas as pd
import unicodedata

# --- CONFIGURAÇÃO DA PÁGINA (Mobile First) ---
st.set_page_config(page_title="Logística", page_icon="🚛", layout="centered")

# CSS para compactar o visual no celular
st.markdown("""
    <style>
    .main { padding-top: 0rem; }
    .stTextInput { margin-top: -2rem; }
    .stAlert { padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_status=True)

# --- LINK DA PLANILHA ---
URL_PLANILHA = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQIcW3eGNnVmZA8TCbXqwrzhFWkMHG2-W-Tc9Aghs4bg9rKXBBdXzhmhoM2U-galWkbaKhw89ZaMomX/pub?output=csv"

def normalizar(texto):
    if not texto: return ""
    nfkd_form = unicodedata.normalize('NFKD', str(texto))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().strip()

@st.cache_data(ttl=60)
def carregar_dados():
    try: return pd.read_csv(URL_PLANILHA)
    except: return pd.DataFrame()

df = carregar_dados()

# --- INTERFACE ENXUTA ---
st.subheader("🚛 Logística Russas")

if not df.empty:
    # Campo de busca mais discreto
    busca = st.text_input("", placeholder="🔍 Onde é a entrega?")
    busca_limpa = normalizar(busca)

    if busca_limpa:
        df_busca = df.copy()
        df_busca['temp'] = df_busca['Localidade'].apply(normalizar)
        res = df_busca[df_busca['temp'] == busca_limpa]
        
        if not res.empty:
            item = res.iloc[0]
            # Cards coloridos e compactos
            st.markdown(f"### 📍 {item['Localidade'].upper()}")
            
            # Usando containers para economizar espaço
            with st.container():
                st.info(f"**ROTA:** {item['Rota']}")
                st.success(f"**DIAS:** {item['Dias']}")
        else:
            st.error("❌ Não encontrado!")

    # Menu de apoio lá embaixo para não atrapalhar
    with st.expander("📋 Ver Tudo"):
        st.dataframe(df, hide_index=True)
    
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()
else:
    st.error("Erro na planilha!")
