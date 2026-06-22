import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Natación", layout="wide", page_icon="🏊‍♂️")

st.title("🏊‍♂️ Panel de Rendimiento - Natación")
st.markdown("Análisis biomecánico y aeróbico de la sesión.")

# 1. Cargar los datos
@st.cache_data
def load_data():
    # Asegurate de que este nombre coincida con el CSV que subiste
    df = pd.read_csv("20260622_limpio.csv") 
    df_nado = df[df['Estado'] == 'Nado'].copy()
    return df_nado

df = load_data()

# 2. Panel lateral (Filtros para la profe)
st.sidebar.header("Filtros de Análisis")
bloques = df['Bloque_Rutina'].unique()
bloques_seleccionados = st.sidebar.multiselect("Seleccionar Bloques:", bloques, default=bloques)

# Aplicar filtro
df_filtrado = df[df['Bloque_Rutina'].isin(bloques_seleccionados)]

# 3. Tarjetas de Resumen Rápido (Métricas)
col1, col2, col3 = st.columns(3)
col1.metric("Metros Analizados", f"{len(df_filtrado) * 25} m")
col2.metric("SWOLF Promedio", round(df_filtrado['SWOLF'].mean(), 1))
col3.metric("Brazadas x Largo (Prom)", round(df_filtrado['Brazadas'].mean(), 1))

st.divider()

# 4. Gráfico 1: Desgaste Técnico (SWOLF)
st.subheader("📈 Evolución de la Eficiencia (SWOLF vs Distancia)")
st.markdown("*A menor SWOLF, mejor técnica y deslizamiento.*")
fig_swolf = px.line(df_filtrado, x='Distancia_Acumulada', y='SWOLF', markers=True, 
                    color='Bloque_Rutina', template="plotly_white")
fig_swolf.update_traces(line=dict(width=3), marker=dict(size=8))
st.plotly_chart(fig_swolf, use_container_width=True)

# 5. Gráfico 2: Consistencia del Ritmo
st.subheader("⏱️ Estabilidad de Ritmo por Bloque")
st.markdown("*Cajas más pequeñas indican un ritmo constante. Cajas alargadas indican irregularidad por fatiga.*")
fig_ritmo = px.box(df_filtrado, x='Bloque_Rutina', y='Duracion_Seg', 
                   color='Bloque_Rutina', template="plotly_white")
fig_ritmo.update_yaxes(title="Segundos por largo (25m)")
st.plotly_chart(fig_ritmo, use_container_width=True)
