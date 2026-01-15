import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Imersão", layout="wide")

# Link do CSV (o mesmo que você usou no Colab)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpleIWJqucqHpRsU3ERKNAmE_shgQS89UsAVBXwrm9Gjyk1rrEuAhiV4ysUE9tFwQOE0INJFghTfkJ/pub?gid=0&single=true&output=csv"

@st.cache_data # Faz o app carregar mais rápido
def carregar_dados():
    return pd.read_csv(URL_CSV)

df = carregar_dados()

st.title("🚀 Meu Front-end de Dados")

# Filtro na barra lateral
categorias = df['categoria'].unique()
filtro = st.sidebar.multiselect("Filtrar por Categoria", categorias, default=categorias)

df_filtrado = df[df['categoria'].isin(filtro)]

# Exibindo Métricas
col1, col2 = st.columns(2)
col1.metric("Soma dos Valores", f"R$ {df_filtrado['valor'].sum():,.2f}")
col2.metric("Itens Listados", len(df_filtrado))

# Gráfico de Storytelling
st.subheader("Análise Visual")
fig = px.bar(df_filtrado, x='descrição', y='valor', color='categoria', barmode='group')
st.plotly_chart(fig, use_container_width=True)

# Tabela
st.dataframe(df_filtrado, use_container_width=True)
