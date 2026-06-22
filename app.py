import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# ⚙️ CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Natación", layout="wide", page_icon="🏊‍♂️")

st.title("🏊‍♂️ Panel de Rendimiento y Biomecánica")
st.markdown("Análisis detallado de la sesión de natación. Uso exclusivo para revisión técnica.")

# ==========================================
# 📥 CARGA DE DATOS (Backend)
# ==========================================
@st.cache_data
def load_data():
    # Lee el archivo que limpiamos en Google Colab
    df = pd.read_csv("20260622_limpio.csv") 
    # Filtramos para analizar solo los largos donde estuviste nadando (excluye descansos)
    df_nado = df[df['Estado'] == 'Nado'].copy()
    return df_nado

df = load_data()

# ==========================================
# 🎛️ PANEL LATERAL (Filtros)
# ==========================================
st.sidebar.header("Filtros de Análisis")
bloques_disponibles = df['Bloque_Rutina'].unique()
bloques_seleccionados = st.sidebar.multiselect(
    "Seleccionar Bloques a visualizar:", 
    bloques_disponibles, 
    default=bloques_disponibles
)

# Aplicar el filtro a todo el dataframe
df_filtrado = df[df['Bloque_Rutina'].isin(bloques_seleccionados)]

# ==========================================
# 📊 TARJETAS DE MÉTRICAS GLOBALES
# ==========================================
st.subheader("Resumen de la Selección")
col1, col2, col3 = st.columns(3)

# Evitamos errores matemáticos si no hay nada seleccionado
if not df_filtrado.empty:
    metros_totales = len(df_filtrado) * 25
    swolf_prom = round(df_filtrado['SWOLF'].mean(), 1)
    brazadas_prom = round(df_filtrado['Brazadas'].mean(), 1)
else:
    metros_totales, swolf_prom, brazadas_prom = 0, 0, 0

col1.metric("Distancia Analizada", f"{metros_totales} m")
col2.metric("SWOLF Promedio", swolf_prom)
col3.metric("Brazadas x Largo (Prom)", brazadas_prom)

st.divider()

# Validamos que haya datos antes de intentar graficar
if not df_filtrado.empty:
    
    # ==========================================
    # 📈 GRÁFICO 1: MAPA DE FATIGA (SWOLF)
    # ==========================================
    st.subheader("📈 Mapa de Fatiga Global (SWOLF vs Distancia)")
    st.markdown("*Mide la pérdida de eficiencia. Si la curva sube, estás requiriendo más esfuerzo para avanzar lo mismo.*")
    
    fig_swolf = px.line(df_filtrado, x='Distancia_Acumulada', y='SWOLF', markers=True, 
                        color='Bloque_Rutina', template="plotly_white")
    fig_swolf.update_traces(line=dict(width=3), marker=dict(size=6))
    fig_swolf.update_xaxes(title="Distancia Acumulada (Metros)")
    st.plotly_chart(fig_swolf, use_container_width=True)

    # ==========================================
    # ⏱️ GRÁFICO 2: ESTABILIDAD DE RITMO
    # ==========================================
    st.subheader("⏱️ Estabilidad de Ritmo por Bloque")
    st.markdown("*Las 'cajas' estiradas hacia arriba indican que te costó mantener el paso y fuiste irregular.*")
    
    fig_ritmo = px.box(df_filtrado, x='Bloque_Rutina', y='Duracion_Seg', 
                       color='Bloque_Rutina', template="plotly_white")
    fig_ritmo.update_yaxes(title="Tiempo por largo (Segundos)")
    fig_ritmo.update_xaxes(title="")
    st.plotly_chart(fig_ritmo, use_container_width=True)

    st.divider()

    # ==========================================
    # 🦋 GRÁFICO 3: MICROSCOPIO - MARIPOSA
    # ==========================================
