import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from sklearn.linear_model import LinearRegression
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="PO Dashboard & AI", layout="wide")

# 1. CONEXÃO (Substitua pelo seu link CSV que termina em ?output=csv)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpleIWJqucqHpRsU3ERKNAmE_shgQS89UsAVBXwrm9Gjyk1rrEuAhiV4ysUE9tFwQOE0INJFghTfkJ/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=600)
def load_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            # Limpeza Ninja: Remove espaços, acentos e coloca tudo em minúsculo
            df.columns = df.columns.str.strip().str.lower().str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('utf-8')
            
            # Conversão de Tipos
            if 'valor' in df.columns:
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
            if 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
                df = df.dropna(subset=['data']) # Remove linhas sem data
            return df
        return None
    except:
        return None

df = load_data(URL_CSV)

# 2. INTERFACE E STORYTELLING
if df is not None and not df.empty:
    st.title("📈 Inteligência de Dados: Previsão e Performance")
    
    # Sidebar com filtros
    st.sidebar.header("Configurações")
    meses_previsao = st.sidebar.slider("Meses para prever", 1, 24, 6)

    # Verificação de colunas essenciais
    if 'valor' in df.columns and 'data' in df.columns:
        # Preparação para Machine Learning
        # Agrupando por mês para ver a tendência
        df_temp = df.set_index('data').resample('M')['valor'].sum().reset_index()
        df_temp['ordinal_date'] = df_temp['data'].map(datetime.toordinal)

        # Treinando o Modelo (Regressão Linear)
        X = df_temp[['ordinal_date']].values
        y = df_temp['valor'].values
        
        modelo = LinearRegression()
        modelo.fit(X, y)

        # Gerando Datas Futuras para Previsão
        ultima_data = df_temp['data'].max()
        datas_futuras = pd.date_range(start=ultima_data, periods=meses_previsao + 1, freq='M')[1:]
        ordinais_futuros = datas_futuras.map(datetime.toordinal).values.reshape(-1, 1)
        previsoes = modelo.predict(ordinais_futuros)

        # Plotando o Storytelling
        st.subheader("🔮 Previsão de Tendência (Machine Learning)")
        
        df_pred = pd.DataFrame({'data': datas_futuras, 'valor': previsoes, 'tipo': 'Previsão'})
        df_real = df_temp[['data', 'valor']].copy()
        df_real['tipo'] = 'Histórico'
        
        df_final = pd.concat([df_real, df_pred])
        
        fig = px.line(df_final, x='data', y='valor', color='tipo', 
                      title="Análise de Tendência de Aportes/Gastos",
                      line_dash='tipo', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Métricas de PO
        c1, c2, c3 = st.columns(3)
        c1.metric("Média Mensal Atual", f"R$ {df_real['valor'].mean():,.2f}")
        c2.metric("Projeção Próximo Mês", f"R$ {previsoes[0]:,.2f}")
        c3.metric("Total em {meses_previsao} Meses", f"R$ {previsoes.sum():,.2f}")

    else:
        st.warning("Para ver a previsão, sua planilha precisa das colunas: 'data' e 'valor'.")
        st.write("Colunas lidas atualmente:", list(df.columns))

else:
    st.error("Erro ao carregar dados. Verifique o link e se a planilha está publicada na web.")