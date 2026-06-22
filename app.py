import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# ⚙️ CONFIGURACIÓN DE PÁGINA (Alto Rendimiento)
# ==========================================
st.set_page_config(page_title="Revisión Técnica - Natación", layout="wide", page_icon="🏊‍♂️")

st.title("🏊‍♂️ Panel de Rendimiento y Biomecánica")
st.markdown("Análisis detallado de la sesión de natación. Uso exclusivo para revisión técnica.")

# ==========================================
# 📥 CARGA DE DATOS (Backend Blindado)
# ==========================================
@st.cache_data
def load_data():
    # Asegurate de que este nombre coincida con el CSV que subiste
    df = pd.read_csv("20260620_limpio.csv") 
    # Analizamos solo los largos donde estuviste nadando (excluye descansos)
    df_nado = df[df['Estado'] == 'Nado'].copy()
    return df_nado

df = load_data()

# ==========================================
# 🎛️ PANEL LATERAL (Filtros Tácticos)
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
    # NIVEL 1: 📈 MAPA DE EFICIENCIA MECÁNICA (ECONOMÍA DE NADO)
    # ==========================================
    st.subheader("📈 Mapa de Eficiencia Mecánica (Brazadas vs Distancia)")
    st.markdown("*Mide la tracción. Si la línea sube progresivamente, estás perdiendo 'agarre' en el agua y patinando.*")
    
    fig_traccion = go.Figure()

    # Línea principal: Brazadas
    fig_traccion.add_trace(go.Scatter(
        x=df_filtrado['Distancia_Acumulada'], 
        y=df_filtrado['Brazadas'],
        mode='lines+markers',
        name='Brazadas x 25m',
        line=dict(color='rgb(55, 128, 191)', width=3),
        marker=dict(size=6)
    ))

    # Área de fondo para el SWOLF (tendencia global)
    fig_traccion.add_trace(go.Scatter(
        x=df_filtrado['Distancia_Acumulada'], 
        y=df_filtrado['SWOLF'],
        fill='tozeroy',
        mode='none', 
        name='SWOLF',
        fillcolor='rgba(230, 230, 230, 0.5)',
        yaxis='y2'
    ))

    fig_traccion.update_layout(
        xaxis=dict(title='Distancia Acumulada (Metros)'),
        yaxis=dict(title='Brazadas - MÁS BAJO ES MEJOR', titlefont=dict(color='rgb(55, 128, 191)'), tickfont=dict(color='rgb(55, 128, 191)')),
        yaxis2=dict(title='Métrica SWOLF', overlaying='y', side='right', range=[30, 70]),
        template='plotly_white',
        hovermode='x unified'
    )
    st.plotly_chart(fig_traccion, use_container_width=True)

    st.divider()

    # ==========================================
    # NIVEL 2: ❤️ REVISIÓN FISIOLÓGICA (DESACOPLE AERÓBICO)
    # ==========================================
    st.subheader("❤️ Desacople Aeróbico (Ritmo vs Frecuencia Cardíaca)")
    st.markdown("*Detector de fatiga por pre-fatiga. Si el Corazón (Área Azul) sube y el Ritmo (Línea Roja) empeora, tu motor cardiovascular colapsó.*")

    # Filtramos nulos por si el reloj perdió señal
    df_cardio = df_filtrado.dropna(subset=['PPM', 'Duracion_Seg'])

    if not df_cardio.empty:
        fig_cardio = go.Figure()

        # Fondo (Área azul): Pulsaciones (PPM)
        fig_cardio.add_trace(go.Scatter(
            x=df_cardio['Distancia_Acumulada'], 
            y=df_cardio['PPM'],
            fill='tozeroy',
            mode='none',
            name='Corazón (PPM)',
            fillcolor='rgba(55, 128, 191, 0.2)',
            yaxis='y2'
        ))

        # Frente (Línea roja gruesa): Tiempo por largo (Ritmo)
        fig_cardio.add_trace(go.Scatter(
            x=df_cardio['Distancia_Acumulada'], 
            y=df_cardio['Duracion_Seg'],
            mode='lines+markers',
            name='Tiempo x 25m (Seg)',
            line=dict(color='firebrick', width=3),
            marker=dict(size=6)
        ))

        fig_cardio.update_layout(
            xaxis=dict(title='Distancia Acumulada (Metros)'),
            yaxis=dict(title='Ritmo (Segundos) - MÁS BAJO ES MEJOR', titlefont=dict(color='firebrick'), tickfont=dict(color='firebrick')),
            yaxis2=dict(title='Pulsaciones (PPM)', titlefont=dict(color='blue'), tickfont=dict(color='blue'), overlaying='y', side='right'),
            template='plotly_white',
            hovermode='x unified'
        )

        st.plotly_chart(fig_cardio, use_container_width=True)
    else:
        st.info("No hay datos de Frecuencia Cardíaca disponibles en esta selección.")

    st.divider()

    # ==========================================
    # NIVEL 3: 🦋 MICROSCOPIO BIOMECÁNICO - BLOQUE COMBINADO
    # ==========================================
    st.subheader("🦋 Análisis de Tolerancia a Lactato (Combinados Mariposa/Crol)")
    st.markdown("*Aislamiento de los sprints de 25m. Buscamos consistencia en segundos y brazadas entre la pasada 1 y la 8.*")

    # Aislamos específicamente la mariposa dentro del bloque seleccionado
    df_combinado = df_filtrado[df_filtrado['Bloque_Rutina'].str.contains('Combinados', case=False, na=False)]
    
    if not df_combinado.empty:
        # Gráfico comparativo de Tiempo y SWOLF por estilo
        fig_comp_comb = px.bar(df_combinado, x='Distancia_Acumulada', y='Duracion_Seg', color='Estilo',
                              text='SWOLF', barmode='group',
                              template='plotly_white', color_discrete_map={'butterfly': 'firebrick', 'freestyle': 'rgb(55, 128, 191)'})
        
        fig_comp_comb.update_layout(
            xaxis=dict(title='Distancia Acumulada del Sprint'),
            yaxis=dict(title='Segundos por Pasada (25m)'),
            legend=dict(title='Estilo', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_comp_comb, use_container_width=True)
    else:
        st.info("💡 Para ver este análisis biomecánico, asegurate de tener seleccionado el bloque 'Combinados' en el panel lateral.")

else:
    st.warning("⚠️ No hay datos para mostrar. Por favor, seleccioná al menos un bloque en el panel lateral.")
