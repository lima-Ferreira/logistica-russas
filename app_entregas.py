import streamlit as st
import pandas as pd
import unicodedata

# --- COLOQUE O SEU LINK DO "PUBLICAR NA WEB" AQUI ---
URL_PLANILHA = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQIcW3eGNnVmZA8TCbXqwrzhFWkMHG2-W-Tc9Aghs4bg9rKXBBdXzhmhoM2U-galWkbaKhw89ZaMomX/pub?output=csv"

st.set_page_config(page_title="Logística Russas", page_icon="🚛")

# --- FUNÇÃO MÁGICA PARA IGNORAR ACENTOS E MAIÚSCULAS ---
def normalizar(texto):
    if not texto: return ""
    # Transforma "São" em "Sao", "INGAR" em "ingar"
    nfkd_form = unicodedata.normalize('NFKD', str(texto))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().strip()

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        return pd.read_csv(URL_PLANILHA)
    except:
        return pd.DataFrame()

df = carregar_dados()

st.title("🚛 Logística Russas-CE")

if not df.empty:
    st.header("🔍 Consulta Inteligente")
    busca_usuario = st.text_input("Para onde é a entrega? (Ex: Ingar, ingá, INGAR)")
    
    # Limpamos o que o usuário digitou
    busca_limpa = normalizar(busca_usuario)

    if busca_limpa:
        # CRIAMOS A BUSCA INTELIGENTE:
        # O Pandas vai "limpar" a coluna 'Localidade' da planilha só para comparar
        df_busca = df.copy()
        df_busca['busca_temp'] = df_busca['Localidade'].apply(normalizar)
        
        # Comparamos o "limpo" com o "limpo"
        resultado = df_busca[df_busca['busca_temp'] == busca_limpa]
        
        if not resultado.empty:
            # Pegamos o nome ORIGINAL (bonito) da planilha para exibir
            item = resultado.iloc[0]
            st.markdown(f"### 📍 {item['Localidade'].upper()}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🚚 **Rota:**\n\n{item['Rota']}")
            with col2:
                st.success(f"🗓️ **Dias de Saída:**\n\n{item['Dias']}")
        else:
            st.error(f"❌ '{busca_usuario}' não encontrado no sistema.")

    with st.expander("📋 Ver Tabela Completa"):
        st.dataframe(df, hide_index=True)

    if st.button("🔄 Sincronizar Agora"):
        st.cache_data.clear()
        st.rerun()
else:
    st.error("⚠️ Não consegui ler os dados. Verifique o link da planilha!")
