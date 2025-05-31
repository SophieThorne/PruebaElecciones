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

    st.markdown("### 🎛️ Filtros")

    cols_filtrar = [
        "Circuito", "Distrito", "Circunscripcion", "Nombre",
        "Sexo", "Grado máximo de estudios", "Número de Lista", "Especialidad"
    ]

    columnas = st.columns(len(cols_filtrar))
    for i, col in enumerate(cols_filtrar):
        if col in df.columns:
            valores = sorted(df[col].dropna().unique())
            seleccion = columnas[i].selectbox(f"{col}", ["Todos"] + valores, key=f"filtro_{col}")
            if seleccion != "Todos":
                df = df[df[col] == seleccion]

    st.download_button("📅 Descargar datos filtrados", data=df.to_csv(index=False).encode("utf-8"), file_name="candidatos_filtrados.csv", mime="text/csv")

    cols_esenciales = ["Nombre", "Número de Lista", "Sexo", "Especialidad", "Circuito", "Distrito"]
    cols_esenciales = [col for col in cols_esenciales if col in df.columns]
    orden_cols = cols_esenciales + [col for col in df.columns if col not in cols_esenciales]

    st.markdown("### 🗂️ Resultados (haz clic en un nombre para ver más detalles)")
    for idx, row in df[orden_cols].iterrows():
        nombre = row.get("Nombre", f"Candidato/a {idx+1}")
        numero = row.get("Número de Lista", "")
        with st.expander(f"👤 {nombre} — Lista: {numero}"):
            for col, val in row.items():
                st.markdown(f"**{col}:** {val}")

except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

# --- Análisis de palabras en textos largos ---
st.markdown("### 🔍 Buscar una palabra clave en las propuestas")

# Entrada personalizada
palabra_input = st.text_input("Escribe una palabra para buscarla en las propuestas y visiones")
columnas_texto = [
    "¿Porqué me pustulé para el cargo?", "Visión de la función Jurisdiccional",
    "Visión de la Justicia", "Propuesta 1", "Propuesta 2", "Propuesta 3",
    "Cursos y Especializaciones"
]

if palabra_input:
    palabra_input = palabra_input.strip().lower()
    resultado = df[
        df[columnas_texto].apply(
            lambda fila: any(palabra_input in str(valor).lower() for valor in fila if pd.notna(valor)),
            axis=1
        )
    ]
    st.markdown(f"Se encontraron **{len(resultado)}** personas que mencionan la palabra: *{palabra_input}*")
    for _, row in resultado.iterrows():
        nombre = str(row.get("Nombre", "Candidato/a"))
        with st.expander(f"👤 {nombre}"):
            for col in row.index:
                st.markdown(f"**{col}:** {row[col]}")

# --- Tendencias temáticas ---
st.markdown("### 📌 Temas comunes en propuestas y visiones")

columnas_texto = [
    "¿Porqué me pustulé para el cargo?", "Visión de la función Jurisdiccional",
    "Visión de la Justicia", "Propuesta 1", "Propuesta 2", "Propuesta 3",
    "Cursos y Especializaciones"
]

texto_total = " ".join(df[col].dropna().astype(str).str.lower().str.cat(sep=" ") for col in columnas_texto if col in df.columns)

# Filtrado básico de palabras sin valor analítico
stopwords = set(["para", "esta", "entre", "como", "que", "con", "los", "las", "una", "por", "del", "más", "sus", "han", "este", "cada", "desde", "pero", "solo", "todo"])

palabras = re.findall(r'\b\w{4,}\b', texto_total)
conteo = Counter(p for p in palabras if p not in stopwords)
palabras_comunes = [palabra for palabra, _ in conteo.most_common(30)]

st.markdown("Selecciona una palabra para ver las candidaturas que la mencionan:")
colpal = st.columns(6)
for i, palabra in enumerate(palabras_comunes):
    if colpal[i % 6].button(palabra):
        resultado = df[
            df[columnas_texto].apply(
                lambda fila: any(palabra in str(valor).lower() for valor in fila if pd.notna(valor)),
                axis=1
            )
        ]
        st.markdown(f"Se encontraron **{len(resultado)}** personas que mencionan la palabra: *{palabra}*")
        for _, row in resultado.iterrows():
            nombre = str(row.get("Nombre", "Candidato/a"))
            numero = str(row.get("Número de Lista", ""))
            with st.expander(f"👤 {nombre} — Lista: {numero}"):
                for col in row.index:
                    st.markdown(f"**{col}:** {row[col]}")