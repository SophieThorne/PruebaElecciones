import streamlit as st
import pandas as pd
import pandasai as pai

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Explora las elecciones del PJ 📊", layout="wide")
st.title("🧠 Superdatada: Explora las bases del Poder Judicial")

st.markdown("""
Bienvenida/o a este espacio de exploración de datos.  
Aquí puedes consultar las bases de personas candidatas a cargos en el Poder Judicial  
y hacer preguntas en lenguaje natural para obtener insights directamente desde los datos proporcionados por el INE.
""")

# --- API Key ---
pai.api_key.set(st.secrets["pandasai_api_key"])

# --- CARGA DE ARCHIVOS DISPONIBLES ---
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
    st.subheader(f"📋 Datos de: {opcion}")

    # Filtros básicos
    with st.expander("🔍 Filtros avanzados"):
        columnas_filtrables = [col for col in df.columns if df[col].dtype == object and df[col].nunique() < 100]
        filtros = {}
        for col in columnas_filtrables:
            valores = df[col].dropna().unique().tolist()
            seleccion = st.multiselect(f"Filtrar por {col}", opciones := sorted(valores), default=valores)
            filtros[col] = seleccion

        for col, vals in filtros.items():
            df = df[df[col].isin(vals)]

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
            sdf = pai.DataFrame(df)
            respuesta = sdf.chat(pregunta)

        st.success("✅ Respuesta:")

        # Si la respuesta es un DataFrame
        if isinstance(respuesta, pd.DataFrame):
            st.markdown("Haz clic en el nombre de cada candidata o candidato para ver su ficha completa.")
            if len(respuesta) <= 20:
                for _, row in respuesta.iterrows():
                    with st.expander(f"👤 {row.get('Nombre', 'Candidato/a')}"):
                        st.write(row.to_frame())
            else:
                st.dataframe(respuesta, use_container_width=True)
        else:
            st.write(respuesta)

    except Exception as e:
        st.error(f"Ocurrió un error procesando tu pregunta: {e}")
