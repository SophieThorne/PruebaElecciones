import streamlit as st
import pandasai as pai
import pandas as pd

# Configura tu API key de PandasAI
pai.api_key.set(st.secrets["pandasai_api_key"])

# Config general
st.set_page_config(page_title="Explora las elecciones del PJ 📊", layout="wide")
st.title("🧠 Superdatada: Explora las bases del Poder Judicial")

st.markdown("""
Bienvenida/o a este espacio de exploración de datos.  
Consulta las bases de personas candidatas a cargos en el Poder Judicial  
y haz preguntas en lenguaje natural directamente sobre los datos del INE.
""")

# Selección de base
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

try:
    df = pd.read_excel(archivos[opcion])
    sdf = pai.DataFrame(df)

    st.subheader(f"📋 Datos de: {opcion}")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 💬 Haz una pregunta sobre esta base de datos")
    pregunta = st.text_input("Por ejemplo: ¿Cuál es la especialidad con más personas candidatas?")

    if pregunta:
        with st.spinner("Pensando..."):
            respuesta = sdf.chat(pregunta)
        st.success("✅ Respuesta:")
        st.write(respuesta)
except Exception as e:
    st.error(f"Ocurrió un error al procesar la base: {e}")
