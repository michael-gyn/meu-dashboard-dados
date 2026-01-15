import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard PO - Dados", layout="wide")

# 2. O Link (COLE O LINK QUE FAZ DOWNLOAD AUTOMÁTICO AQUI)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpleIWJqucqHpRsU3ERKNAmE_shgQS89UsAVBXwrm9Gjyk1rrEuAhiV4ysUE9tFwQOE0INJFghTfkJ/pub?gid=0&single=true&output=csv"

@st.cache_data
def carregar_dados(url):
    try:
        # Lendo o CSV e forçando os nomes das colunas para evitar erros de digitação
        df = pd.read_csv(url)
        # Padronizando nomes para minúsculo para facilitar
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return None

# Chamada da função
df = carregar_dados(URL_CSV)

# 3. Interface e Lógica
if df is not None:
    st.title("📊 Gestão de Dados (Notion Hub)")
    
    # Verificação de Colunas (O que você definiu: ID, descrição, categoria, valor)
    colunas_esperadas = ['id', 'descrição', 'categoria', 'valor']
    if all(col in df.columns for col in colunas_esperadas):
        
        # Filtros rápidos na barra lateral
        st.sidebar.header("Filtros")
        cat_selecionada = st.sidebar.multiselect(
            "Selecione a Categoria", 
            options=df['categoria'].unique(),
            default=df['categoria'].unique()
        )
        
        df_filtrado = df[df['categoria'].isin(cat_selecionada)]

        # KPIs (Métricas)
        c1, c2 = st.columns(2)
        c1.metric("Soma Total (R$)", f"{df_filtrado['valor'].sum():,.2f}")
        c2.metric("Total de Itens", len(df_filtrado))

        # Gráfico
        fig = px.pie(df_filtrado, values='valor', names='categoria', hole=.3, title="Mix por Categoria")
        st.plotly_chart(fig, use_container_width=True)

        # Tabela formatada
        st.subheader("Lista de Registros")
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning(f"Sua planilha precisa ter as colunas: {colunas_esperadas}. Colunas atuais: {list(df.columns)}")
else:
    st.info("Aguardando conexão com os dados do Google Sheets...")