import streamlit as st
import pandas as pd
from pandas_ai import SmartDataframe
from pandas_ai.llm import OpenAI

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Explora las elecciones del PJ 📊", layout="wide")
st.title("🧠 Superdatada: Explora las bases del Poder Judicial")

st.markdown("""
Bienvenida/o a este espacio de exploración de datos.  
Aquí puedes consultar las bases de personas candidatas a cargos en el Poder Judicial  
y hacer preguntas en lenguaje natural para obtener insights directamente desde los datos proporcionados por el INE.
""")

# --- CARGA DE ARCHIVOS DISPONIBLES ---
st.sidebar.header("📂 Bases disponibles")

archivos = {
    "Magistraturas de Circuito": "data/Candidatos_MC_Integradas.xlsx",
    "Juzgados de Distrito": "data/Candidatos_JD_Integradas.xlsx",
    "Sala Regional del Tribunal Electoral": "data/Candidatos_MSRTEPJF_Integradas.xlsx",
    "Sala Superior del Tribunal Electoral": "data/Candidatos_MSSTEPJF_Integradas.xlsx",
    "Tribunal de Justicia": "data/Candidatos_MTDJ_Integradas.xlsx",
    "Suprema Corte de Justicia": "data/Candidaturas_SCJN_Integradas.xlsx",
}

opcion = st.sidebar.selectbox("Selecciona una base de datos:", list(archivos.keys()))
archivo = archivos[opcion]

try:
    df = pd.read_excel(archivo)
    st.subheader(f"📋 Datos de: {opcion}")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

# --- PREGUNTAS EN LENGUAJE NATURAL ---
st.markdown("### 💬 Haz una pregunta sobre esta base de datos")

pregunta = st.text_input("Por ejemplo: ¿Cuál es la especialidad con más personas candidatas?")

if pregunta:
    try:
        with st.spinner("Pensando..."):
            llm = OpenAI(api_token=st.secrets["openai_api_key"])
            sdf = SmartDataframe(df, config={"llm": llm})
            respuesta = sdf.chat(pregunta)

        st.success("✅ Respuesta:")
        st.write(respuesta)
    except Exception as e:
        st.error(f"Ocurrió un error procesando tu pregunta: {e}")
