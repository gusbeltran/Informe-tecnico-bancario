import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Marketing Bancario",
    page_icon="📊",
    layout="wide",
)


# Cargar y traducir los datos directamente
def load_data():
    df = pd.read_excel("bank-additional-full.xlsx")

    # Limpieza de espacios por seguridad
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Diccionarios de traducción al español
    dic_trabajos = {
        "admin.": "Administrativo",
        "blue-collar": "Obrero / Operario",
        "entrepreneur": "Emprendedor",
        "housemaid": "Empleado Doméstico",
        "management": "Gerente / Directivo",
        "retired": "Jubilado",
        "self-employed": "Trabajador Autónomo",
        "services": "Servicios",
        "student": "Estudiante",
        "technician": "Técnico",
        "unemployed": "Desempleado",
        "unknown": "Desconocido",
    }

    dic_contacto = {
        "cellular": "Celular",
        "telephone": "Teléfono Fijo",
    }

    dic_respuesta = {
        "yes": "Sí",
        "no": "No",
    }

    dic_resultado = {
        "success": "Éxito",
        "failure": "Fracaso",
        "nonexistent": "Inexistente",
    }

    dic_educacion = {
        "basic.4y": "Primaria (4 años)",
        "basic.6y": "Primaria (6 años)",
        "basic.9y": "Secundaria Básica (9 años)",
        "high.school": "Secundaria Completa",
        "illiterate": "Analfabeto",
        "professional.course": "Curso Profesional",
        "university.degree": "Título Universitario",
        "unknown": "Desconocido",
    }

    # Aplicar traducciones en el DataFrame
    df["job"] = df["job"].map(dic_trabajos).fillna(df["job"])
    df["contact"] = df["contact"].map(dic_contacto).fillna(df["contact"])
    df["y"] = df["y"].map(dic_respuesta).fillna(df["y"])
    if "poutcome" in df.columns:
        df["poutcome"] = df["poutcome"].map(dic_resultado).fillna(df["poutcome"])
    if "education" in df.columns:
        df["education"] = (
            df["education"].map(dic_educacion).fillna(df["education"])
        )

    return df


df = load_data()

# Título principal
st.title("📊 Dashboard Analítico: Campañas de Marketing Bancario")
st.markdown(
    "Este tablero interactivo analiza los resultados de las campañas de telemercadeo de una institución bancaria para predecir y entender la suscripción de depósitos a plazo fijo."
)

# Sidebar: Filtros Globales
st.sidebar.header("Filtros de Datos")

# Filtro de Edades
min_age, max_age = int(df["age"].min()), int(df["age"].max())
selected_age = st.sidebar.slider(
    "Rango de Edad", min_age, max_age, (min_age, max_age)
)

# Filtro de Tipo de Trabajo
jobs = sorted(df["job"].unique().tolist())
selected_jobs = st.sidebar.multiselect("Ocupación", jobs, default=jobs)

# Filtro de Contacto
contacts = sorted(df["contact"].unique().tolist())
selected_contacts = st.sidebar.multiselect(
    "Método de Contacto", contacts, default=contacts
)

# Aplicar filtros al DataFrame
filtered_df = df[
    (df["age"] >= selected_age[0])
    & (df["age"] <= selected_age[1])
    & (df["job"].isin(selected_jobs))
    & (df["contact"].isin(selected_contacts))
]

# Pestañas principales
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Resumen Ejecutivo",
        "👥 Análisis Demográfico",
        "📞 Canales y Campañas",
        "🔍 Datos Detallados",
    ]
)

with tab1:
    st.header("Indicadores Clave de Rendimiento (KPIs)")

    total_clients = len(filtered_df)
    if total_clients > 0:
        conversions = (filtered_df["y"] == "Sí").sum()
        conversion_rate = (conversions / total_clients) * 100
        avg_duration = filtered_df["duration"].mean()
        euribor_mean = filtered_df["euribor3m"].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Clientes Analizados", f"{total_clients:,}")
        col2.metric("Tasa de Conversión", f"{conversion_rate:.2f}%")
        col3.metric("Duración Media de Llamada", f"{avg_duration:.1f} seg")
        col4.metric("Euribor Promedio (3m)", f"{euribor_mean:.2f}%")

        st.markdown("---")

        # Gráficos principales
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Distribución de Conversión (Depósito Sí/No)")
            fig_conv = px.pie(
                filtered_df,
                names="y",
                title="Proporción de Suscripciones",
                color_discrete_sequence=["#ff9999", "#66b3ff"],
            )
            fig_conv.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_conv, use_container_width=True)

        with col_b:
            st.subheader("Conversión por Tipo de Ocupación")
            job_conv = (
                filtered_df.groupby("job")["y"]
                .apply(lambda x: (x == "Sí").mean() * 100)
                .reset_index(name="tasa_conversion_%")
            )
            fig_job = px.bar(
                job_conv.sort_values(by="tasa_conversion_%", ascending=True),
                x="tasa_conversion_%",
                y="job",
                orientation="h",
                title="Tasa de Conversión por Ocupación (%)",
                color="tasa_conversion_%",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig_job, use_container_width=True)
    else:
        st.warning(
            "No hay datos disponibles para los filtros seleccionados. Intenta ampliar los rangos."
        )

with tab2:
    st.header("Análisis Demográfico y Socioeconómico")

    if total_clients > 0:
        col_c, col_d = st.columns(2)

        with col_c:
            st.subheader("Distribución de Edades y Conversión")
            fig_age = px.histogram(
                filtered_df,
                x="age",
                color="y",
                nbins=30,
                title="Histograma de Edades según Suscripción",
                barmode="overlay",
                color_discrete_sequence=["#ff6666", "#2ca02c"],
            )
            st.plotly_chart(fig_age, use_container_width=True)

        with col_d:
            st.subheader("Nivel Educativo vs. Conversión")
            edu_conv = (
                filtered_df.groupby(["education", "y"])
                .size()
                .reset_index(name="count")
            )
            fig_edu = px.bar(
                edu_conv,
                x="education",
                y="count",
                color="y",
                title="Educación y Éxito de la Campaña",
                barmode="group",
            )
            st.plotly_chart(fig_edu, use_container_width=True)
    else:
        st.warning("Selecciona al menos un filtro con datos.")

with tab3:
    st.header("Efectividad de Canales e Historial de Campaña")

    if total_clients > 0:
        col_e, col_f = st.columns(2)

        with col_e:
            st.subheader("Resultado de Campaña Anterior")
            pout = (
                filtered_df.groupby(["poutcome", "y"])
                .size()
                .reset_index(name="count")
            )
            fig_pout = px.bar(
                pout,
                x="poutcome",
                y="count",
                color="y",
                title="Impacto del Resultado Previo",
                barmode="stack",
            )
            st.plotly_chart(fig_pout, use_container_width=True)

        with col_f:
            st.subheader("Tipo de Contacto y Conversión")
            cont = (
                filtered_df.groupby(["contact", "y"])
                .size()
                .reset_index(name="count")
            )
            fig_cont = px.bar(
                cont,
                x="contact",
                y="count",
                color="y",
                title="Celular vs Teléfono Fijo",
                barmode="group",
            )
            st.plotly_chart(fig_cont, use_container_width=True)
    else:
        st.warning("Selecciona datos válidos.")

with tab4:
    st.header("Explorador de Datos Filtrados")
    st.markdown("Visualiza las primeras filas del dataset en base a tu selección:")
    st.dataframe(filtered_df.head(100))

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar datos filtrados como CSV",
        data=csv,
        file_name="datos_banco_filtrados.csv",
        mime="text/csv",
    )