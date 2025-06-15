# app.py (Dashboard de Avistamientos de OVNIs - Versión 4.2 - COMPLETA Y VERIFICADA)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import date

# --- 1. DICCIONARIO DE TEXTOS COMPLETO (ES/EN) ---
TEXTS = {
    'es': {
        'page_title': "Análisis de Avistamientos de OVNIs", 'page_icon': "🛸",
        'title': "Dashboard Interactivo de Avistamientos de OVNIs 🛸",
        'lang_button': "English",
        'dataset_selector_label': "Seleccionar Periodo de Datos:",
        'dataset_options': {"historic": "Histórico (antes de 2015)", "recent": "Reciente (2015-2025)"},
        'tab1': "🗺️ Mapa de Avistamientos", 'tab2': "✨ Análisis de Formas", 'tab3': "📈 Tendencia Temporal",
        'sidebar_title': "Panel de Control",
        'year_filter_label': "Filtrar por Rango de Años:",
        'state_filter_label': "Filtrar por Estado (Opcional):",
        'shape_filter_label': "Filtrar por Forma (Opcional):",
        'all_option': "Todos / Todas",
        'filters_header': "Filtros aplicados:",
        'filters_year': "Años", 'filters_state': "Estado", 'filters_shape': "Forma",
        'results_found': "Total de avistamientos encontrados:",
        'map_header': "Mapa de Calor de Avistamientos",
        'map_desc': "Los estados más intensos tienen más reportes en el periodo seleccionado.",
        'map_plot_title': "Avistamientos en EE.UU.",
        'map_legend': "Número de Reportes",
        'map_info': "Mostrando datos solo para {}. Para ver el mapa completo, selecciona '{}' en el filtro de estado.",
        'shape_header': "Formas de OVNIs Más Reportadas",
        'shape_desc': "Conteo de las formas más comunes según los filtros aplicados.",
        'shape_plot_title': "Top 15 Formas Reportadas",
        'shape_axis_x': "Número de Avistamientos",
        'shape_axis_y': "Forma Reportada",
        'time_header': "Evolución de los Reportes a lo Largo del Tiempo",
        'time_desc': "Número de reportes anuales según los filtros aplicados.",
        'time_plot_title': "Reportes Anuales",
        'time_axis_x': "Año",
        'time_axis_y': "Número de Reportes",
        'no_data_warning': "No se encontraron datos para los filtros seleccionados."
    },
    'en': {
        'page_title': "UFO Sightings Analysis", 'page_icon': "🛸",
        'title': "Interactive UFO Sightings Dashboard 🛸",
        'lang_button': "Español",
        'dataset_selector_label': "Select Data Period:",
        'dataset_options': {"historic": "Historical (pre-2015)", "recent": "Recent (2015-2025)"},
        'tab1': "🗺️ Sightings Map", 'tab2': "✨ Shape Analysis", 'tab3': "📈 Temporal Trend",
        'sidebar_title': "Control Panel",
        'year_filter_label': "Filter by Year Range:",
        'state_filter_label': "Filter by State (Optional):",
        'shape_filter_label': "Filter by Shape (Optional):",
        'all_option': "All",
        'filters_header': "Active filters:",
        'filters_year': "Years", 'filters_state': "State", 'filters_shape': "Shape",
        'results_found': "Total sightings found:",
        'map_header': "Sightings Heatmap",
        'map_desc': "States with more intense colors have more reports in the selected period.",
        'map_plot_title': "UFO Sightings in the USA",
        'map_legend': "Number of Sightings",
        'map_info': "Showing data only for {}. To see the full map, select '{}' in the state filter.",
        'shape_header': "Most Reported UFO Shapes",
        'shape_desc': "Count of the most common shapes based on the applied filters.",
        'shape_plot_title': "Top 15 Reported Shapes",
        'shape_axis_x': "Number of Sightings",
        'shape_axis_y': "Reported Shape",
        'time_header': "Evolution of Reports Over Time",
        'time_desc': "Number of annual reports based on the applied filters.",
        'time_plot_title': "Annual Reports",
        'time_axis_x': "Year",
        'time_axis_y': "Number of Annual Reports",
        'no_data_warning': "No data found for the selected filters."
    }
}

# --- LÓGICA DE LA APP ---
st.set_page_config(
    page_title=TEXTS[st.session_state.get('lang', 'en')]['page_title'],
    page_icon="🛸",
    layout="wide"
)

if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

def toggle_language():
    st.session_state.lang = 'es' if st.session_state.lang == 'en' else 'en'

texts = TEXTS[st.session_state.lang]

DATA_URLS = {
    "historic": 'https://gist.githubusercontent.com/dezzf/039463c267b36f7881c1251978258e77/raw/958357069142274431f492b45a27814b64f5195e/ufo_scrubbed_pre2015.csv',
    "recent": 'https://gist.githubusercontent.com/dezzf/039463c267b36f7881c1251978258e77/raw/958357069142274431f492b45a27814b64f5195e/ufo_recent_2015_2025.csv'
}

@st.cache_data
def load_and_clean_data(data_period):
    url = DATA_URLS[data_period]
    df = pd.read_csv(url, low_memory=False)
    
    # --- INICIO DE LA CORRECCIÓN ROBUSTA ---
    # 1. Limpiamos TODOS los nombres de las columnas para eliminar espacios y caracteres extraños
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    
    # 2. Ahora trabajamos con nombres de columna limpios y predecibles
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    
    numeric_cols = ['duration_seconds', 'latitude', 'longitude']
    for col in numeric_cols:
        if col in df.columns: # Verificamos si la columna existe antes de intentar convertirla
            df[col] = pd.to_numeric(df[col], errors='coerce')

    cols_to_check = ['datetime', 'state', 'country', 'shape', 'latitude', 'longitude']
    df.dropna(subset=cols_to_check, inplace=True)
    
    df = df[df['country'] == 'us'].copy()
    df['year'] = df['datetime'].dt.year.astype(int)
    df['state'] = df['state'].str.upper()
    
    # Renombramos la columna 'duration_seconds' para que el código viejo siga funcionando
    if 'duration_seconds' in df.columns:
        df.rename(columns={'duration_seconds': 'duration (seconds)'}, inplace=True)
        
    return df
    # --- FIN DE LA CORRECCIÓN ROBUSTA ---

# --- INTERFAZ ---
st.button(texts['lang_button'], on_click=toggle_language)
st.title(texts['title'])

st.sidebar.title(texts['sidebar_title'])

dataset_options_keys = list(texts['dataset_options'].keys())
selected_period = st.sidebar.radio(
    texts['dataset_selector_label'],
    dataset_options_keys,
    format_func=lambda key: texts['dataset_options'][key]
)
df_clean = load_and_clean_data(selected_period)

min_year, max_year = int(df_clean['year'].min()), int(df_clean['year'].max())
selected_years = st.sidebar.slider(
    texts['year_filter_label'],
    min_year, max_year, (min_year, max_year)
)

all_states_option = texts['all_option']
state_list = [all_states_option] + sorted(df_clean['state'].unique().tolist())
selected_state = st.sidebar.selectbox(texts['state_filter_label'], state_list)

all_shapes_option = texts['all_option']
shape_list = [all_shapes_option] + sorted(df_clean['shape'].unique().tolist())
selected_shape = st.sidebar.selectbox(texts['shape_filter_label'], shape_list)

df_filtered = df_clean[(df_clean['year'] >= selected_years[0]) & (df_clean['year'] <= selected_years[1])]
if selected_state != all_states_option: df_filtered = df_filtered[df_filtered['state'] == selected_state]
if selected_shape != all_shapes_option: df_filtered = df_filtered[df_filtered['shape'] == selected_shape]

st.markdown(f"**{texts['filters_header']}** {texts['filters_year']}: `{selected_years[0]}`-`{selected_years[1]}` | {texts['filters_state']}: `{selected_state}` | {texts['filters_shape']}: `{selected_shape}`")
st.markdown(f"**{texts['results_found']}** `{len(df_filtered)}`")
st.write("---")

tab1, tab2, tab3 = st.tabs([texts['tab1'], texts['tab2'], texts['tab3']])

with tab1:
    st.header(texts['map_header']); st.write(texts['map_desc'])
    if not df_filtered.empty and selected_state == all_states_option:
        state_counts = df_filtered['state'].value_counts().reset_index(); state_counts.columns = ['state_code', 'sighting_count']
        fig = px.choropleth(data_frame=state_counts, locations='state_code', locationmode="USA-states", color='sighting_count', scope="usa", color_continuous_scale="Plasma", title=texts['map_plot_title'], labels={'sighting_count': texts['map_legend']})
        st.plotly_chart(fig, use_container_width=True)
    elif selected_state != all_states_option: st.info(texts['map_info'].format(selected_state, all_states_option))
    else: st.warning(texts['no_data_warning'])
with tab2:
    st.header(texts['shape_header']); st.write(texts['shape_desc'])
    if not df_filtered.empty:
        top_shapes = df_filtered['shape'].value_counts().nlargest(15)
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(x=top_shapes.values, y=top_shapes.index, palette='inferno', ax=ax, hue=top_shapes.index, legend=False)
        ax.set_title(texts['shape_plot_title'], fontsize=16); ax.set_xlabel(texts['shape_axis_x'], fontsize=12); ax.set_ylabel(texts['shape_axis_y'], fontsize=12)
        st.pyplot(fig)
    else: st.warning(texts['no_data_warning'])
with tab3:
    st.header(texts['time_header']); st.write(texts['time_desc'])
    if not df_filtered.empty:
        yearly_counts = df_filtered['year'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(yearly_counts.index, yearly_counts.values, marker='o', linestyle='-', color='lime')
        ax.set_facecolor('#1E1E1E'); fig.set_facecolor('#0E1117')
        ax.set_title(texts['time_plot_title'], fontsize=18, color='white'); ax.set_xlabel(texts['time_axis_x'], fontsize=14, color='white'); ax.set_ylabel(texts['time_axis_y'], fontsize=14, color='white')
        ax.tick_params(axis='x', colors='white'); ax.tick_params(axis='y', colors='white')
        ax.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig)
    else: st.warning(texts['no_data_warning'])
