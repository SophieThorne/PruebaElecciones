import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Explora las elecciones del PJ 📊", layout="wide")
st.title("🧠 Superdatada: Explora las bases del Poder Judicial")

st.markdown("""
Bienvenida/o a este espacio de exploración de datos.  
Aquí puedes consultar las bases de personas candidatas a cargos en el Poder Judicial  
y hacer preguntas en lenguaje natural para obtener insights.  
""")

# --- CARGA DE ARCHIVOS DISPONIBLES ---
st.sidebar.header("📂 Bases disponibles")

archivos = {
    "Magistraturas de Circuito": "data/Candidatos_MC_Integradas_especialidad_limpia.xlsx",
    "Juzgados de Distrito": "data/Candidatos_JD_Integradas_especialidad_limpia.xlsx",
    # Puedes agregar más aquí si lo deseas
}

opcion = st.sidebar.selectbox("Selecciona una base de datos:", list(archivos.keys()))

# --- CARGA DEL DATAFRAME SELECCIONADO ---
archivo = archivos[opcion]
df = pd.read_excel(archivo)
st.subheader(f"📋 Datos de: {opcion}")
st.dataframe(df, use_container_width=True)

# --- PREGUNTAS EN LENGUAJE NATURAL ---
st.markdown("### 💬 Haz una pregunta sobre esta base de datos")

pregunta = st.text_input("Por ejemplo: ¿Cuál es la especialidad con más personas candidatas?")

if pregunta:
    with st.spinner("Pensando..."):
        # Usa tu API Key desde el archivo .streamlit/secrets.toml
        llm = OpenAI(api_token=st.secrets["openai_api_key"])
        sdf = SmartDataframe(df, config={"llm": llm})
        respuesta = sdf.chat(pregunta)

    st.success("✅ Respuesta:")
    st.write(respuesta)
