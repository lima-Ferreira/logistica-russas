import streamlit as st
import pandas as pd
import unicodedata

# --- LINKS DAS ABAS ---
URL_LOCALIDADES = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQIcW3eGNnVmZA8TCbXqwrzhFWkMHG2-W-Tc9Aghs4bg9rKXBBdXzhmhoM2U-galWkbaKhw89ZaMomX/pub?output=csv"
URL_STATUS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQIcW3eGNnVmZA8TCbXqwrzhFWkMHG2-W-Tc9Aghs4bg9rKXBBdXzhmhoM2U-galWkbaKhw89ZaMomX/pub?gid=1161835604&single=true&output=csv"

st.set_page_config(page_title="Logística Russas", page_icon="🚛")

def normalizar(texto):
    if not texto or pd.isna(texto): return ""
    nfkd_form = unicodedata.normalize('NFKD', str(texto))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().strip()

@st.cache_data(ttl=30)
def carregar(url):
    try:
        df = pd.read_csv(url)
        # LIMPEZA DOS NOMES: remove espaços extras (ex: "Status " vira "Status")
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

df_loc = carregar(URL_LOCALIDADES)
df_status = carregar(URL_STATUS)

st.title("🚛 Logística Russas")

tab1, tab2 = st.tabs(["🔍 Consulta", "🗓️ Rotas da Semana"])

with tab1:
    busca = st.text_input("", placeholder="🔍 Digite o bairro ou sítio...")
    busca_limpa = normalizar(busca)

    if busca_limpa and not df_loc.empty:
        df_loc['temp'] = df_loc['Localidade'].apply(normalizar)
        res = df_loc[df_loc['temp'] == busca_limpa]
        
        if not res.empty:
            local_nome = res.iloc[0]['Localidade']
            rota_nome = res.iloc[0]['Rota']
            
            st.markdown(f"### 📍 {local_nome.upper()}")
            st.caption(f"Rota: {rota_nome}")

            if not df_status.empty:
                df_status['rota_temp'] = df_status['Rota'].apply(normalizar)
                info_rota = df_status[df_status['rota_temp'] == normalizar(rota_nome)]
                
                if not info_rota.empty:
                    s = info_rota.iloc[0]
                    # PROTEÇÃO: Se a coluna 'Status' não existir, ele avisa
                    try:
                        status_texto = str(s['Status'])
                        cor = "green" if "Confirmada" in status_texto else "orange"
                        if "Sem Entregas" in status_texto: cor = "red"
                        
                        st.markdown(f"#### Status: :{cor}[{status_texto}]")
                        st.info(f"🗓️ **PRÓXIMA SAÍDA:**  \n{s['Próxima Saída']}")
                    except KeyError:
                        st.error("⚠️ Coluna 'Status' não encontrada na aba Status_Rotas.")
        else:
            st.error("❌ Localidade não encontrada.")

with tab2:
    if not df_status.empty:
        st.subheader("🗓️ Cronograma Geral")
        
        # Criamos uma cópia limpa para exibição
        df_view = df_status[['Rota', 'Status', 'Próxima Saída']].copy()

        # Função de Estilo (Compatível com Versões Novas)
        def style_status(val):
            if str(val).strip() == 'Confirmado':
                return ' color: #155724; font-weight: bold;'
            elif str(val).strip() == 'Sem Entregas':
                return 'color: #721c24; font-weight: bold;'
            elif str(val).strip() == 'Em análise':
                return 'color: #856404; font-weight: bold;'
            return ''

        # Usando .map (o padrão novo do Pandas/Streamlit)
        st.dataframe(
            df_view.style.map(style_status, subset=['Status']),
            hide_index=True,
            use_container_width=True
        )
        
        st.caption("💡 Atualizado em tempo real via Google Sheets")
    else:
        st.warning("Aguardando dados da planilha...")





if st.button("🔄 Sincronizar"):
    st.cache_data.clear()
    st.rerun()
