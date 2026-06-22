import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==========================================
# ⚙️ CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Revisión Técnica - Natación", layout="wide", page_icon="🏊‍♂️")

# ==========================================
# 📥 CARGA DE DATOS
# ==========================================
@st.cache_data
def load_data():
    df_raw = pd.read_csv("20260620_limpio.csv") 
    df_nado = df_raw[df_raw['Estado'] == 'Nado'].copy()
    
    # Extraer la fecha real del entrenamiento
    if 'Hora_Inicio' in df_nado.columns:
        fecha_str = pd.to_datetime(df_nado['Hora_Inicio'].iloc[0]).strftime('%d/%m/%Y')
    else:
        fecha_str = "Fecha Desconocida"
        
    return df_nado, fecha_str

df, fecha_sesion = load_data()

# Título Dinámico
st.title(f"🏊‍♂️ Reporte de Rendimiento: {fecha_sesion}")
st.markdown("Análisis biomecánico y fisiológico de la sesión.")

# ==========================================
# 🎛️ PANEL LATERAL (Filtros)
# ==========================================
st.sidebar.header("⚙️ Configuración")
bloques_disponibles = df['Bloque_Rutina'].unique()
bloques_seleccionados = st.sidebar.multiselect(
    "Seleccionar Bloques a visualizar:", 
    bloques_disponibles, 
    default=bloques_disponibles
)

df_filtrado = df[df['Bloque_Rutina'].isin(bloques_seleccionados)]
colores_paleta = px.colors.qualitative.Set1 

# ==========================================
# 📊 TARJETAS DE MÉTRICAS GLOBALES
# ==========================================
st.subheader("📋 Resumen de la Selección")
col1, col2, col3, col4 = st.columns(4)

if not df_filtrado.empty:
    metros_totales = len(df_filtrado) * 25
    swolf_prom = round(df_filtrado['SWOLF'].mean(), 1)
    brazadas_prom = round(df_filtrado['Brazadas'].mean(), 1)
    ppm_prom = round(df_filtrado['PPM'].mean(), 0) if 'PPM' in df_filtrado.columns else "N/A"
else:
    metros_totales, swolf_prom, brazadas_prom, ppm_prom = 0, 0, 0, 0

col1.metric("Distancia Efectiva", f"{metros_totales} m")
col2.metric("SWOLF Promedio", swolf_prom)
col3.metric("Brazadas x 25m", brazadas_prom)
col4.metric("Pulso Promedio", f"{ppm_prom} PPM")

st.divider()

if not df_filtrado.empty:
    
    # ==========================================
    # NIVEL 1: 📈 MAPA DE EFICIENCIA MECÁNICA
    # ==========================================
    st.subheader("📈 1. Tracción y Fatiga Mecánica (Brazadas vs Distancia)")
    st.markdown("*Líneas punteadas indican el promedio de brazadas de cada bloque.*")
    
    fig_traccion = go.Figure()

    # Fondo gris global para SWOLF
    fig_traccion.add_trace(go.Scatter(
        x=df_filtrado['Distancia_Acumulada'], y=df_filtrado['SWOLF'],
        fill='tozeroy', mode='none', name='SWOLF Global',
        fillcolor='rgba(230, 230, 230, 0.4)', yaxis='y2'
    ))

    # Iterar por bloques para dar color
    for i, bloque in enumerate(bloques_seleccionados):
        df_b = df_filtrado[df_filtrado['Bloque_Rutina'] == bloque]
        if df_b.empty: continue
        color_b = colores_paleta[i % len(colores_paleta)]
        
        # Línea de nado
        fig_traccion.add_trace(go.Scatter(
            x=df_b['Distancia_Acumulada'], y=df_b['Brazadas'],
            mode='lines+markers', name=bloque,
            line=dict(color=color_b, width=3), marker=dict(size=6)
        ))
        
        # Línea de promedio de brazadas
        promedio = df_b['Brazadas'].mean()
        fig_traccion.add_trace(go.Scatter(
            x=[df_b['Distancia_Acumulada'].min(), df_b['Distancia_Acumulada'].max()], 
            y=[promedio, promedio], mode='lines',
            line=dict(color=color_b, width=2, dash='dash'),
            showlegend=False, hoverinfo='skip'
        ))

    fig_traccion.update_layout(
        xaxis=dict(title=dict(text='Distancia Acumulada (m)')),
        yaxis=dict(title=dict(text='Brazadas x Largo'), range=[df_filtrado['Brazadas'].min()-2, df_filtrado['Brazadas'].max()+2]),
        yaxis2=dict(title=dict(text='SWOLF (Fondo Gris)'), overlaying='y', side='right', showgrid=False),
        template='plotly_white', hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_traccion, use_container_width=True)

    # ==========================================
    # NIVEL 2: ❤️ DESACOPLE AERÓBICO POR BLOQUE
    # ==========================================
    st.subheader("❤️ 2. Estrés Cardiovascular (Ritmo vs PPM Segmentado)")
    st.markdown("*Compara cómo varió tu tiempo (línea sólida) frente al costo cardíaco promedio de cada bloque (línea punteada).*")

    df_cardio = df_filtrado.dropna(subset=['PPM', 'Duracion_Seg'])
    
    if not df_cardio.empty:
        fig_cardio = go.Figure()
        
        # Fondo gris global para la "forma" del pulso
        fig_cardio.add_trace(go.Scatter(
            x=df_cardio['Distancia_Acumulada'], y=df_cardio['PPM'],
            fill='tozeroy', mode='none', name='PPM Curva Global',
            fillcolor='rgba(230, 230, 230, 0.3)', yaxis='y2'
        ))

        # Iterar por bloques
        for i, bloque in enumerate(bloques_seleccionados):
            df_b = df_cardio[df_cardio['Bloque_Rutina'] == bloque]
            if df_b.empty: continue
            color_b = colores_paleta[i % len(colores_paleta)]
            
            # Ritmo (Velocidad)
            fig_cardio.add_trace(go.Scatter(
                x=df_b['Distancia_Acumulada'], y=df_b['Duracion_Seg'],
                mode='lines+markers', name=f'Ritmo: {bloque}',
                line=dict(color=color_b, width=3), marker=dict(size=6)
            ))
            
            # Línea de Promedio Cardíaco por bloque
            prom_ppm = df_b['PPM'].mean()
            fig_cardio.add_trace(go.Scatter(
                x=[df_b['Distancia_Acumulada'].min(), df_b['Distancia_Acumulada'].max()], 
                y=[prom_ppm, prom_ppm], mode='lines',
                line=dict(color=color_b, width=3, dash='dot'),
                yaxis='y2', showlegend=False, name=f'Promedio PPM {bloque}'
            ))

        fig_cardio.update_layout(
            xaxis=dict(title=dict(text='Distancia Acumulada (m)')),
            yaxis=dict(title=dict(text='Ritmo (Segundos)')),
            yaxis2=dict(title=dict(text='Frecuencia Cardíaca (PPM)'), overlaying='y', side='right', range=[90, 190]),
            template='plotly_white', hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_cardio, use_container_width=True)
    
    # ==========================================
    # NIVEL 3: 🎯 MATRIZ DE CONSISTENCIA (NUEVO)
    # ==========================================
    st.subheader("🎯 3. Matriz de Consistencia Técnica")
    st.markdown("*Cada punto es un largo. Grupos compactos = Nado sólido. Puntos dispersos = Nado inestable.*")
    
    fig_scatter = px.scatter(
        df_filtrado, x='Duracion_Seg', y='Brazadas', color='Bloque_Rutina',
        size='SWOLF', hover_data=['Distancia_Acumulada', 'Estilo'],
        color_discrete_sequence=colores_paleta, template='plotly_white'
    )
    fig_scatter.update_layout(
        xaxis=dict(title=dict(text='Ritmo (Segundos)')),
        yaxis=dict(title=dict(text='Agarre (Brazadas)')),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # ==========================================
    # 🧠 MOTOR DE DIAGNÓSTICO (CONCLUSIONES AUTOMÁTICAS)
    # ==========================================
    st.subheader("🧠 Diagnóstico de la Sesión")
    
    # Cálculos
    bloque_peor_tecnica = df_filtrado.groupby('Bloque_Rutina')['SWOLF'].mean().idxmax()
    bloque_mayor_esfuerzo = df_cardio.groupby('Bloque_Rutina')['PPM'].mean().idxmax() if not df_cardio.empty else "N/A"
    bloque_mas_inestable = df_filtrado.groupby('Bloque_Rutina')['Duracion_Seg'].std().idxmax()
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.error(f"**Pérdida de Tracción:**\n\nEl bloque con el SWOLF más alto (peor deslizamiento) fue **{bloque_peor_tecnica}**. Aquí los músculos fallaron mecánicamente.")
        
    with c2:
        st.warning(f"**Pico de Estrés Cardíaco:**\n\nTu motor trabajó a máximas revoluciones durante **{bloque_mayor_esfuerzo}**. Si el ritmo bajó acá, sufriste desacople aeróbico.")
        
    with c3:
        st.info(f"**Inestabilidad de Ritmo:**\n\nEl bloque con más saltos de tiempo (mayor desvío estándar) fue **{bloque_mas_inestable}**. Te costó mantener un paso constante.")

else:
    st.warning("⚠️ Seleccioná al menos un bloque para ver el análisis.")
