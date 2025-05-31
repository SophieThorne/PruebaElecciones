import streamlit as st
import pandas as pd
import pandasai as pai
import re
from collections import Counter

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

# --- Mapeo de estados a circunscripción ---
estado_a_circunscripcion = {
    "Baja California": 1, "Baja California Sur": 1, "Chihuahua": 1, "Durango": 1,
    "Jalisco": 1, "Nayarit": 1, "Sinaloa": 1, "Sonora": 1,
    "Aguascalientes": 2, "Coahuila": 2, "Guanajuato": 2, "Nuevo León": 2,
    "Querétaro": 2, "San Luis Potosí": 2, "Tamaulipas": 2, "Zacatecas": 2,
    "Campeche": 3, "Chiapas": 3, "Oaxaca": 3, "Quintana Roo": 3,
    "Tabasco": 3, "Veracruz": 3, "Yucatán": 3,
    "Ciudad de México": 4, "CDMX": 4, "Guerrero": 4,
    "Morelos": 4, "Puebla": 4, "Tlaxcala": 4,
    "Colima": 5, "Hidalgo": 5, "Estado de México": 5, "Michoacán": 5,
}

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

# Circunscripción solo si aplica
if opcion == "Magistraturas de Sala Regional del Tribunal Electoral":
    st.sidebar.markdown("### 🧭 ¿No sabes qué circunscripción te corresponde?")
    estado_sel = st.sidebar.selectbox("📍 Selecciona tu estado", sorted(estado_a_circunscripcion.keys()))
    circ = estado_a_circunscripcion.get(estado_sel)
    st.sidebar.success(f"Tu circunscripción es: **{circ}**")

# Instrucción para obtener Circuito/Distrito si aplica
if opcion in ["Magistraturas de Circuito", "Juzgados de Distrito"]:
    st.sidebar.markdown("""
📌 **¿No sabes cuál es tu circuito o distrito judicial?**  
Entra a 👉 [https://cartografia.ine.mx/sige8/mapas/conoce-tu-nuevo-distrito](https://cartografia.ine.mx/sige8/mapas/conoce-tu-nuevo-distrito)  
y escribe tu estado y sección del INE para conocerlos.
""")

try:
    df = pd.read_excel(archivo)
    st.subheader(f"📋 Datos de: {opcion}")

    # Filtros amigables
    st.markdown("### 🎛️ Filtros")

    cols_filtrar = [
        "Circuito",
        "Distrito",
        "Circunscripción",
        "Nombre",
        "Sexo",
        "Grado máximo de estudios",
        "Número de Lista",
        "Especialidad"
    ]

    # Crear columnas horizontales (puedes ajustar el número si hay más filtros)
    columnas = st.columns(len(cols_filtrar))

    # Iterar sobre filtros y colocarlos en columnas horizontales
    for i, col in enumerate(cols_filtrar):
        if col in df.columns:
            valores = sorted(df[col].dropna().unique())
            seleccion = columnas[i].selectbox(f"{col}", ["Todos"] + valores, key=f"filtro_{col}")
            if seleccion != "Todos":
                df = df[df[col] == seleccion]

    # Botón de descarga
    st.download_button("📥 Descargar datos filtrados", data=df.to_csv(index=False).encode("utf-8"), file_name="candidatos_filtrados.csv", mime="text/csv")

    # Mostrar tabla resaltando columnas clave
    cols_esenciales = ["Nombre", "Número de lista","Sexo", "Especialidad", "Circuito", "Distrito"]
    cols_esenciales = [col for col in cols_esenciales if col in df.columns]
    orden_cols = cols_esenciales + [col for col in df.columns if col not in cols_esenciales]
    st.dataframe(df[orden_cols], use_container_width=True)


except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

    # --- Análisis de palabras en textos largos ---
st.markdown("### 🔍 Palabras más mencionadas en propuestas y visiones")

# Campos a analizar
columnas_texto = [
    "¿Porqué me pustulé para el cargo?",
    "Visión de la función Jurisdiccional",
    "Visión de la Justicia",
    "Propuesta 1", "Propuesta 2", "Propuesta 3",
    "Cursos y Especializaciones"
]

# Unir texto y limpiar
texto_total = " ".join(df[col].dropna().astype(str).str.lower().str.cat(sep=" ") for col in columnas_texto)
palabras = re.findall(r'\b\w+\b', texto_total)
stopwords = set(["para", "esta", "entre", "como", "que", "con", "los", "las", "una", "por", "del", "más", "sus", "han"])
palabras_limpias = [p for p in palabras if len(p) > 3 and p not in stopwords]

# Conteo y visualización
conteo = Counter(palabras_limpias)
palabras_comunes = [palabra for palabra, _ in conteo.most_common(30)]
palabra_clave = st.selectbox("🔎 Selecciona una palabra clave para ver quién la mencionó:", ["Ninguna"] + palabras_comunes)

if palabra_clave != "Ninguna":
    resultado = df[df[columnas_texto].apply(
        lambda fila: any(palabra_clave in str(c).lower() for c in fila if pd.notna(c)), axis=1)]

    st.markdown(f"🗂️ Se encontraron **{len(resultado)}** personas que mencionan la palabra: *{palabra_clave}*")

    for _, row in resultado.iterrows():
        nombre = str(row.get("Nombre", "Candidato/a"))
        with st.expander(f"👤 {nombre}"):
            for col in row.index:
                st.markdown(f"**{col}:** {row[col]}")

# --- PREGUNTAS EN LENGUAJE NATURAL ---
st.markdown("""
---
### 💬 Haz una pregunta sobre esta base de datos
""")

pregunta = st.text_input("Por ejemplo: ¿De los candidatos filtrados quién tiene estudios o propuestas de equidad de género?")

if pregunta:
    try:
        with st.spinner("Pensando..."):
            sdf = pai.DataFrame(df)
            respuesta = sdf.chat(pregunta)

        st.success("✅ Respuesta:")

        if isinstance(respuesta, pd.DataFrame):
            st.markdown("Haz clic en el nombre de cada candidata o candidato para ver su ficha completa.")
            if respuesta.shape[0] <= 20:
                for idx, row in respuesta.iterrows():
                    nombre = str(row.get("Nombre", f"Candidato/a {idx+1}"))
                    with st.expander(f"👤 {nombre}"):
                        for col, val in row.items():
                            st.markdown(f"**{col}:** {val}")
            else:
                st.dataframe(respuesta, use_container_width=True)
        else:
            st.write(respuesta)

    except Exception as e:
        st.error(f"Ocurrió un error procesando tu pregunta: {e}")