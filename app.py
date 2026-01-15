import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Configuração de Layout para o Notion
st.set_page_config(page_title="PO Dashboard", layout="wide")

# 1. ENDEREÇO DOS DADOS (Substitua pelo seu link CSV aqui)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpleIWJqucqHpRsU3ERKNAmE_shgQS89UsAVBXwrm9Gjyk1rrEuAhiV4ysUE9tFwQOE0INJFghTfkJ/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=600) # Atualiza a cada 10 minutos
def load_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Transforma o texto recebido em um arquivo que o Pandas entende
            dados_brutos = StringIO(response.text)
            df = pd.read_csv(dados_brutos)
            
            # Limpeza de colunas (converte para minúsculo e remove espaços)
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
        else:
            st.error(f"Erro ao acessar planilha. Status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Falha crítica na conexão: {e}")
        return None

# Execução
df = load_data(URL_CSV)

# 2. INTERFACE (O que aparecerá no Notion)
if df is not None:
    st.title("📊 Monitor de Performance")
    
    # Validação das colunas (ID, descrição, categoria, valor)
    colunas_foco = ['id', 'descrição', 'categoria', 'valor']
    
    if all(c in df.columns for c in colunas_foco):
        # Filtro de Categoria
        categorias = df['categoria'].unique()
        selecao = st.sidebar.multiselect("Filtrar Categoria", categorias, default=categorias)
        
        df_filtrado = df[df['categoria'].isin(selecao)]

        # Métricas de Negócio
        m1, m2, m3 = st.columns(3)
        m1.metric("Valor Total", f"R$ {df_filtrado['valor'].sum():,.2f}")
        m2.metric("Média por Item", f"R$ {df_filtrado['valor'].mean():,.2f}")
        m3.metric("Qtd Itens", len(df_filtrado))

        # Tabela e Gráfico
        st.divider()
        st.subheader("Visualização de Dados")
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning(f"Atenção PO: Verifique se os nomes das colunas na Planilha são: {colunas_foco}")