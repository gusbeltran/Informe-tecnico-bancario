import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página y estilos CSS adaptables (Modo Claro / Modo Oscuro)
st.set_page_config(
    page_title="Dashboard de Marketing Bancario",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    /* Tarjetas de métricas adaptables a Modo Claro y Modo Oscuro */
    div[data-testid="stMetric"] {
        background-color: var(--background-secondary-color, #f8f9fa);
        border: 1px solid var(--border-color, #e9ecef);
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
    }
    
    /* Asegurar visibilidad de textos y números en ambos modos */
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--text-color, #31333F) !important;
    }
    
    /* Efecto hover interactivo */
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border-color: #1f4e79;
    }

    /* Efecto hover para botones */
    .stButton > button {
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border-color: #1f4e79;
    }

    /* Ajuste de padding contenedor */
    .block-container {
        padding-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Mapa de colores global unificado para "Sí" y "No"
COLOR_MAP = {"Sí": "#2ca02c", "No": "#d62728"}

# Caché de datos
@st.cache_data(show_spinner="Cargando datos…")
def load_data():
    df = pd.read_excel("bank-additional-full.xlsx")

    # Limpieza de espacios en texto
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Diccionarios de traducción
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

    dic_estado_civil = {
        "married": "Casado/a",
        "single": "Soltero/a",
        "divorced": "Divorciado/a",
        "unknown": "Desconocido",
    }

    dic_sino_desconocido = {
        "yes": "Sí",
        "no": "No",
        "unknown": "Desconocido",
    }

    # Aplicar traducciones
    df["job"] = df["job"].map(dic_trabajos).fillna(df["job"])
    df["contact"] = df["contact"].map(dic_contacto).fillna(df["contact"])
    df["y"] = df["y"].map(dic_respuesta).fillna(df["y"])

    if "marital" in df.columns:
        df["marital"] = df["marital"].map(dic_estado_civil).fillna(df["marital"])
    if "default" in df.columns:
        df["default"] = df["default"].map(dic_sino_desconocido).fillna(df["default"])
    if "housing" in df.columns:
        df["housing"] = df["housing"].map(dic_sino_desconocido).fillna(df["housing"])
    if "loan" in df.columns:
        df["loan"] = df["loan"].map(dic_sino_desconocido).fillna(df["loan"])
    if "poutcome" in df.columns:
        df["poutcome"] = df["poutcome"].map(dic_resultado).fillna(df["poutcome"])
    if "education" in df.columns:
        df["education"] = df["education"].map(dic_educacion).fillna(df["education"])

    return df

df = load_data()

# Título principal
st.title("📊 Dashboard Analítico: Campañas de Marketing Bancario")
st.markdown(
    "Este tablero interactivo analiza los resultados de las campañas de telemercadeo de una institución bancaria para predecir y entender la suscripción de depósitos a plazo fijo."
)

# Sidebar: Filtros Globales
st.sidebar.header("Filtros de Datos")

min_age, max_age = int(df["age"].min()), int(df["age"].max())
if min_age == max_age:
    max_age += 1

jobs = sorted(df["job"].unique().tolist())
contacts = sorted(df["contact"].unique().tolist())

# Session state
if "age_range" not in st.session_state:
    st.session_state.age_range = (min_age, max_age)
if "selected_jobs" not in st.session_state:
    st.session_state.selected_jobs = jobs
if "selected_contacts" not in st.session_state:
    st.session_state.selected_contacts = contacts

def reset_filters():
    st.session_state.age_range = (min_age, max_age)
    st.session_state.selected_jobs = jobs
    st.session_state.selected_contacts = contacts
    st.toast("Filtros restablecidos correctamente", icon="🔄")

selected_age = st.sidebar.slider(
    "Rango de Edad", min_age, max_age, key="age_range"
)

selected_jobs = st.sidebar.multiselect(
    "Ocupación", jobs, key="selected_jobs"
)

selected_contacts = st.sidebar.multiselect(
    "Método de Contacto", contacts, key="selected_contacts"
)

filtered_df = df[
    (df["age"] >= selected_age[0])
    & (df["age"] <= selected_age[1])
    & (df["job"].isin(selected_jobs))
    & (df["contact"].isin(selected_contacts))
]

total_clients = len(filtered_df)
has_data = total_clients > 0

st.sidebar.markdown("---")
st.sidebar.caption(f"*{total_clients:,}* de *{len(df):,}* registros")

if st.sidebar.button("🔄 Restablecer filtros", on_click=reset_filters):
    pass

# Pestañas principales
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📈 Resumen Ejecutivo",
        "👥 Análisis Demográfico",
        "📞 Canales y Campañas",
        "🔍 Datos Detallados",
        "💼 Sobre los Creadores",
    ]
)

with tab1:
    st.header("Indicadores Clave de Rendimiento (KPIs)")

    if has_data:
        conversions = (filtered_df["y"] == "Sí").sum()
        conversion_rate = (conversions / total_clients) * 100
        avg_duration = filtered_df["duration"].mean()
        euribor_mean = filtered_df["euribor3m"].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Total Clientes Analizados", f"{total_clients:,}")
        col2.metric("✅ Tasa de Conversión", f"{conversion_rate:.2f}%")
        col3.metric(
            "📞 Duración media (post-llamada)",
            f"{avg_duration:.1f} seg",
            help="Variable descriptiva post-llamada: solo se conoce tras finalizar la interacción.",
        )
        col4.metric("💹 Euribor Promedio (3m)", f"{euribor_mean:.2f}%")

        st.markdown("---")

        col_a, col_b = st.columns(2)

        with col_a:
            with st.container(border=True):
                st.subheader("Distribución de Conversión (Depósito Sí/No)")
                fig_conv = px.pie(
                    filtered_df,
                    names="y",
                    title="Proporción de Suscripciones",
                    color="y",
                    color_discrete_map=COLOR_MAP,
                    hole=0.45,
                )
                fig_conv.update_traces(textinfo="percent+label")
                st.plotly_chart(fig_conv, use_container_width=True)

        with col_b:
            with st.container(border=True):
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
                    text_auto=".2f"
                )
                st.plotly_chart(fig_job, use_container_width=True)
    else:
        st.warning(
            "No hay datos disponibles para los filtros seleccionados. Intenta ampliar los rangos."
        )

with tab2:
    st.header("Análisis Demográfico y Socioeconómico")

    if has_data:
        col_c, col_d = st.columns(2)

        with col_c:
            with st.container(border=True):
                st.subheader("Distribución de Edades y Conversión")
                fig_age = px.histogram(
                    filtered_df,
                    x="age",
                    color="y",
                    nbins=30,
                    title="Histograma de Edades según Suscripción",
                    barmode="overlay",
                    color_discrete_map=COLOR_MAP,
                )
                st.plotly_chart(fig_age, use_container_width=True)

        with col_d:
            with st.container(border=True):
                st.subheader("Nivel Educativo vs. Conversión")
                if "education" in filtered_df.columns:
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
                        color_discrete_map=COLOR_MAP,
                        text_auto=True,
                    )
                    st.plotly_chart(fig_edu, use_container_width=True)
                else:
                    st.info("Columna 'education' no disponible en el dataset.")
    else:
        st.warning("Selecciona al menos un filtro con datos.")

with tab3:
    st.header("Efectividad de Canales e Historial de Campaña")

    if has_data:
        col_e, col_f = st.columns(2)

        with col_e:
            with st.container(border=True):
                st.subheader("Resultado de Campaña Anterior")
                if "poutcome" in filtered_df.columns:
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
                        color_discrete_map=COLOR_MAP,
                        text_auto=True,
                    )
                    st.plotly_chart(fig_pout, use_container_width=True)
                else:
                    st.info("Columna 'poutcome' no disponible en el dataset.")

        with col_f:
            with st.container(border=True):
                st.subheader("Tipo de Contacto y Conversión")
                if "contact" in filtered_df.columns:
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
                        color_discrete_map=COLOR_MAP,
                        text_auto=True,
                    )
                    st.plotly_chart(fig_cont, use_container_width=True)
                else:
                    st.info("Columna 'contact' no disponible en el dataset.")
    else:
        st.warning("Selecciona datos válidos.")

with tab4:
    st.header("Explorador de Datos Filtrados")
    st.markdown("Visualiza las primeras filas del dataset en base a tu selección:")
    
    st.dataframe(
        filtered_df.head(100),
        use_container_width=True,
        hide_index=True,
        column_config={
            "age": st.column_config.NumberColumn("Edad", format="%d años"),
            "job": "Ocupación",
            "marital": "Estado Civil",
            "education": "Nivel Educativo",
            "default": "Crédito Incumplido",
            "housing": "Préstamo Vivienda",
            "loan": "Préstamo Personal",
            "contact": "Tipo de Contacto",
            "month": "Mes",
            "day_of_week": "Día de la Semana",
            "duration": st.column_config.NumberColumn("Duración", format="%d seg"),
            "euribor3m": st.column_config.NumberColumn("Euribor 3m", format="%.2f %%"),
            "y": "Suscripción"
        }
    )
    st.caption(f"Mostrando 100 de {total_clients:,} filas filtradas.")

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar datos filtrados como CSV",
        data=csv,
        file_name="datos_banco_filtrados.csv",
        mime="text/csv",
    )

with tab5:
    st.header("💼 Sobre el Equipo y Nuestros Servicios")
    st.markdown("Transformamos datos complejos en decisiones estratégicas claras a través de herramientas interactivas de alta gama.")

    col_serv1, col_serv2 = st.columns(2)

    with col_serv1:
        with st.container(border=True):
            st.subheader("🚀 ¿Quiénes Somos?")
            st.markdown("""
            Somos especialistas en **Ciencia de Datos, Business Intelligence y Desarrollo de Software Analítico**. 
            Ayudamos a las organizaciones a potenciar el valor de su información mediante tableros modernos, intuitivos y de alto rendimiento.
            """)
            st.markdown("**Tecnologías Principales:** Python, Streamlit, Pandas, Plotly, SQL y Machine Learning aplicado.")
            
            st.markdown("---")
            st.markdown("### 👥 Creadores del Proyecto")
            st.markdown("* **Gustavo De Mey** — 📱 [Chat por WhatsApp](https://wa.me/5491122657342)")
            st.markdown("* **Gonzalo Fleitas** — 📱 [Chat por WhatsApp](https://wa.me/5491162248149)")

    with col_serv2:
        with st.container(border=True):
            st.subheader("🛠️ Nuestros Servicios Profesionales")
            st.markdown("""
            * **Desarrollo de Dashboards a Medida:** Paneles interactivos adaptados a las necesidades operativas de tu empresa.
            * **Modelos Predictivos y de Marketing:** Segmentación de clientes, optimización de campañas de telemercadeo y análisis de conversión.
            * **Optimización y Automatización:** Integración de pipelines de datos y reportes automáticos en tiempo real.
            """)

    st.markdown("---")
    st.info("💡 **¿Interesado en implementar una solución similar en tu empresa o proyecto?** Contáctanos directamente vía WhatsApp para potenciar tus datos.")

# Pie de página
st.markdown("---")
st.caption("Fuente: UCI Bank Marketing Dataset · Dashboard educativo")
#streamlit run app4.py para correrlo
