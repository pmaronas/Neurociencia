import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTADO INICIAL
st.set_page_config(page_title="Tobii Metrics", layout="wide")

# Inicializamos los valores por defecto si no existen
if 'min_filas' not in st.session_state:
    st.session_state.min_filas = 4
if 'max_filas' not in st.session_state:
    st.session_state.max_filas = 60
if 'req_sacada' not in st.session_state:
    st.session_state.req_sacada = False

st.title("Análisis de Métricas Oculares")

# 2. CREACIÓN DEL MENÚ DE PESTAÑAS
tab_contador, tab_ajustes, tab_guia = st.tabs(["Parpadeos", "Ajustes", "Guía"])


# --- PESTAÑA DE GUÍA
with tab_guia:
    st.header("Guía de Usuario: Extracción y Carga de Datos")
    st.write("Sigue estos pasos para exportar correctamente los datos desde Tobii Pro Lab.")

    # PASO 1
    st.subheader("Paso 1: Selección del proyecto en Tobii Pro Lab")
    st.write("""
    Nada más abrir el programa aparece un menú para seleccionar el proyecto que se quiere abrir. Si no se ha creado ningún proyecto todavía, 
    se selecciona Create new Project, en caso contrario, se selecciona aquel proyecto que se quiera estudiar, como se ve en la imagen.
    """)
    # Para que funcione, guarda la imagen en la misma carpeta que tu código
    st.image("paso1.png", caption="Interfaz de selección de proyectos de Tobii") 
    

    st.divider()

    # PASO 2
    st.subheader("Paso 2: Selección de la grabación")
    st.write("""
    Un proyecto puede estar formado por varias grabaciones. Habrá que seleccionar aquella que queramos analizar en el Excel y hacer clic en Data Export. 
    Si el proyecto es nuevo, no aparecerán grabaciones disponibles, habrá que pulsar el botón ‘import’ y buscar la carpeta en la que se encuentre la grabación de las Tobii.
    """)
    st.image("paso2.png", caption="Selección de grabación en Tobii Pro Lab")
    

    st.divider()

    # PASO 3
    st.subheader("Paso 3: Configuración del archivo Excel")
    st.write("Una vez seleccionada la grabación, se hace clic en el botón Data Export. Aparecerá una interfaz con la configuración del archivo que se quiere descargar." \
    " En el menú de la derecha 'Settings' se debe escoger el formato 'Single Excel File' para exportar." \
    " A continuación, se escogen las variables que se desean extraer de la grabación. Serán únicamente necesarias 'Gaze direction', 'Eye movement type' y 'Pupil diameter'. " \
    "Haciendo clic en el botón azul ‘Export 1 file’ y se descargará el archivo Excel con los datos.")
    st.image("paso3.png", caption="Configuración del Excel en Tobii Pro Lab")
    

    st.divider()

    # PASO 4
    st.subheader("Paso 4: Importar el archivo Excel al programa")
    st.write(""" Finalmente, se deberá importar el archivo Excel descargado a la página prinicpal de este programa.
    Una vez detectado, el programa comenzará a analizar el archivo Excel y mostrará su análisis.
    """)
    st.image("paso4.png", caption="Importación del Excel al programa")
    



# --- PESTAÑA DE AJUSTES ---
with tab_ajustes:
    st.header("Configuración del Algoritmo")
    st.write("Define las condiciones para identificar un parpadeo.")
    
    st.subheader("Duración del parpadeo (filas de Excel, cada fila equivale a 10 ms)")
    
    # Creamos dos columnas para los inputs numéricos
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.min_filas = st.number_input(
            "Mínimo de filas:", 
            min_value=1, 
            value=st.session_state.min_filas,
            help="Menos de este número de filas no se contará como parpadeo."
        )
    with c2:
        st.session_state.max_filas = st.number_input(
            "Máximo de filas:", 
            min_value=1, 
            value=st.session_state.max_filas,
            help="Más de este número de filas se considerará pérdida de señal larga, no parpadeo."
        )

    st.info(f"Configuración actual: Bloques de {st.session_state.min_filas} a {st.session_state.max_filas} filas.")

    st.subheader("Validación Biomecánica")
    # AQUÍ ESTÁ LA NUEVA CASILLA
    st.session_state.req_sacada = st.checkbox(
        "Considerar sacada antes del parpadeo", 
        value=st.session_state.req_sacada,
        help="Si se activa, solo se contará como parpadeo si el bloque viene precedido por un movimiento de tipo 'Saccade'."
    )
    
    if st.session_state.req_sacada:
        st.warning("⚠️ Se ignorarán los parpadeos que no tengan una sacada previa registrada.")

# --- PESTAÑA DEL CONTADOR ---
with tab_contador:
    archivo_subido = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

    if archivo_subido is not None:
        try:
            df = pd.read_excel(archivo_subido)
            if 'Recording timestamp' in df.columns and 'Eye movement type' in df.columns:
                tiempos = df['Recording timestamp'].tolist()
                tipos_movimiento = df['Eye movement type'].tolist()
                
                resultados = []
                num_evento = 1
                i = 0
                etiquetas_validas = ['EyesNotFound', 'Unclassified']
                
                while i < len(tipos_movimiento):
                    if tipos_movimiento[i] in etiquetas_validas:
                        inicio_idx = i
                        tiene_eyes_not_found = False
                        
                        # Miramos qué había JUSTO ANTES del bloque
                        sacada_previa = False
                        if inicio_idx > 0:
                            if tipos_movimiento[inicio_idx - 1] == 'Saccade':
                                sacada_previa = True
                        
                        while i < len(tipos_movimiento) and tipos_movimiento[i] in etiquetas_validas:
                            if tipos_movimiento[i] == 'EyesNotFound':
                                tiene_eyes_not_found = True
                            i += 1
                        
                        fin_idx = i - 1
                        longitud = fin_idx - inicio_idx + 1
                        
                        # --- LÓGICA DE FILTRADO ---
                        cumple_duracion = st.session_state.min_filas <= longitud <= st.session_state.max_filas
                        cumple_sacada = True # Por defecto es True si la opción está desactivada
                        
                        if st.session_state.req_sacada:
                            cumple_sacada = sacada_previa

                        if cumple_duracion and tiene_eyes_not_found and cumple_sacada:
                            t_inicio = tiempos[inicio_idx] / 1000000.0
                            t_fin = tiempos[fin_idx] / 1000000.0
                            resultados.append({
                                'Parpadeo': num_evento,
                                'Inicio (s)': round(t_inicio, 4),
                                'Fin (s)': round(t_fin, 4),
                                'Duración (s)': round(t_fin - t_inicio, 4),
                                'Nº de Filas': longitud,
                                'Sacada Previa': "Sí" if sacada_previa else "No"
                            })
                            num_evento += 1
                    else:
                        i += 1
                
                df_resultados = pd.DataFrame(resultados)
                if not df_resultados.empty:
                    st.success(f"Se han detectado {len(df_resultados)} parpadeos.")
                    df_resultados.index = df_resultados.index + 1
                    st.dataframe(df_resultados, use_container_width=True)
                    
                    # MÉTRICAS Y TIEMPOS
                    st.divider()
                
                    col_m1, col_m2 = st.columns(2)
                    
                    duracion_total_seg = (tiempos[-1] - tiempos[0]) / 1000000.0
                    frecuencia_min = (len(df_resultados) / duracion_total_seg) * 60
                    duracion_media_ms = round(df_resultados['Duración (s)'].mean() * 1000)
                    with col_m1:
                        st.metric("Frecuencia media de parpadeo", f"{frecuencia_min:.0f} parpadeos/min")
                    with col_m2:
                        st.metric("Duración media del parpadeo", f"{duracion_media_ms} ms")

                    c_meta1, c_meta2 = st.columns(2)
                    with c_meta1:
                        st.metric("Total de filas procesadas", f"{len(df):,}".replace(',', '.'))
                    with c_meta2:
                        total_seg = (tiempos[-1] - tiempos[0]) / 1000000.0
                        h, m, s = int(total_seg//3600), int((total_seg%3600)//60), int(total_seg%60)
                        st.metric("Duración de la grabación", f"{h:02d}:{m:02d}:{s:02d}")
                else:
                    st.warning("No se detectaron eventos con los ajustes actuales.")
            else:
                st.error("Columnas necesarias no encontradas.")
        except Exception as e:
            st.error(f"Error: {e}")
