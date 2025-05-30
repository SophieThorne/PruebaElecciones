import streamlit as st
import pandas as pd
import pandasai as pai

# Configuración general
st.set_page_config(page_title="Explora las elecciones del PJ 📊", layout="wide")
st.title("🧠 Superdatada: Explora las bases del Poder Judicial")

st.markdown("""
Bienvenida/o a este espacio de exploración de datos.  
Aquí puedes consultar las bases de personas candidatas a cargos en el Poder Judicial  
y hacer preguntas en lenguaje natural para obtener insights directamente desde los datos proporcionados por el INE.
""")

# Carga de archivos
st.sidebar.header("📂 Bases disponibles")
archivos = {
    "Magistraturas de Circuito": "data/Candidatos_MC_Integradas.xlsx",
    "Juzgados de Distrito": "data/Candidatos_JD_Integradas.xlsx",
    "Magistraturas de Sala Regional del Tribunal Electoral": "data/Candidatos_MSRTEPJF_Integradas.xlsx",
    "Magistraturas de Sala Superior del Tribunal Electoral": "data/Candidatos_MSSTEPJF_Integradas.xlsx",
    "Magistraturas Tribunal de Justicia": "data/Candidatos_MTDJ_Integradas.xlsx",
    "Ministros de la Suprema Corte de Justicia": "data/Candidaturas_SCJN_Integradas.xlsx",
}

opcion = st.sidebar.selectbox("Selecciona una base de datos:", list(archivos.keys()))
archivo = archivos[opcion]

try:
    df = pd.read_excel(archivo)

    # Filtros en la barra lateral
    if 'Circuito' in df.columns:
        circuito_sel = st.sidebar.multiselect("Filtra por circuito", sorted(df['Circuito'].dropna().unique()))
        if circuito_sel:
            df = df[df['Circuito'].isin(circuito_sel)]

    if 'Distrito' in df.columns:
        distrito_sel = st.sidebar.multiselect("Filtra por distrito", sorted(df['Distrito'].dropna().unique()))
        if distrito_sel:
            df = df[df['Distrito'].isin(distrito_sel)]

    if 'Especialidad' in df.columns:
        espec_sel = st.sidebar.multiselect("Filtra por especialidad", sorted(df['Especialidad'].dropna().unique()))
        if espec_sel:
            df = df[df['Especialidad'].isin(espec_sel)]

    if 'Sexo' in df.columns:
        sexo_sel = st.sidebar.multiselect("Filtra por sexo", sorted(df['Sexo'].dropna().unique()))
        if sexo_sel:
            df = df[df['Sexo'].isin(sexo_sel)]

    # Búsqueda por nombre
    nombre_query = st.text_input("🔍 Buscar persona candidata por nombre")
    if nombre_query:
        df = df[df['Nombre'].str.contains(nombre_query, case=False, na=False)]

    # Mostrar fichas
    st.subheader(f"📋 Resultados: {len(df)} personas candidatas")
    for _, row in df.iterrows():
        with st.expander(f"{row.get('Nombre', 'Sin nombre')} - {row.get('Cargo', 'Sin cargo')}"):
            st.write({col: row[col] for col in df.columns if pd.notnull(row[col])})

except Exception as e:
    st.error(f"Ocurrió un error al procesar la base: {e}")
    st.stop()

# Sección de IA con PandasAI
st.markdown("""
---
### 💬 Haz una pregunta sobre esta base de datos
""")

pregunta = st.text_input("Por ejemplo: ¿Cuál es la especialidad con más personas candidatas?")

if pregunta:
    try:
        pai.api_key.set(st.secrets["pandasai_api_key"])
        pai_df = pai.DataFrame(df)
        with st.spinner("Pensando..."):
            respuesta = pai_df.chat(pregunta)
        st.success("✅ Respuesta:")
        st.write(respuesta)
    except Exception as e:
        st.error(f"Ocurrió un error procesando tu pregunta: {e}")
