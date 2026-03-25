import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTADO INICIAL
st.set_page_config(page_title="Tobii Metrics", layout="wide")

# --- INICIALIZACIÓN DE VARIABLES (PONER AL PRINCIPIO DEL ARCHIVO) ---
if 'min_f' not in st.session_state: 
    st.session_state.min_f = 4
if 'max_f' not in st.session_state: 
    st.session_state.max_f = 60
if 'req_sac_pre' not in st.session_state: 
    st.session_state.req_sac_pre = False
if 'req_sac_post' not in st.session_state: 
    st.session_state.req_sac_post = False
if 'min_sac_post' not in st.session_state: 
    st.session_state.min_sac_post = 1
if 'max_sac_post' not in st.session_state: 
    st.session_state.max_sac_post = 20
if 'req_vel_post' not in st.session_state: 
    st.session_state.req_vel_post = False
if 'min_vel_post' not in st.session_state: 
    st.session_state.min_vel_post = 100.0
if 'max_vel_post' not in st.session_state: 
    st.session_state.max_vel_post = 700.0
# -------------------------------------------------------------------

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
        st.session_state.min_f = st.number_input(
            "Mínimo de filas:", 
            min_value=1, 
            value=st.session_state.min_f,
            help="Menos de este número de filas no se contará como parpadeo."
        )
    with c2:
        st.session_state.max_f = st.number_input(
            "Máximo de filas:", 
            min_value=1, 
            value=st.session_state.max_f,
            help="Más de este número de filas se considerará pérdida de señal larga, no parpadeo."
        )

    # Ventana de ayuda para duración
    with st.popover("�"):
        st.write("La duración se mide en número de filas consecutivas de 'EyesNotFound'.")
        st.image("ayuda1.png", caption="Esquema de duración del parpadeo")


    st.info(f"Configuración actual: Bloques de {st.session_state.min_f} a {st.session_state.max_f} filas.")

    st.subheader("Condición anterior")
    # AQUÍ ESTÁ LA NUEVA CASILLA
    st.session_state.req_sac_pre = st.checkbox(
        "Considerar sacada antes del parpadeo", 
        value=st.session_state.req_sac_pre,
    )

    # Ventana de ayuda para duración
    with st.popover("�"):
        st.write("El algoritmo busca una etiqueta 'Saccade' justo antes del inicio del parpadeo.")
        st.image("ayuda2.png", caption="Ejemplo de sacada previa al parpadeo")
    
    if st.session_state.req_sac_pre:
        st.warning("⚠️ Se ignorarán los parpadeos que no tengan una sacada previa registrada.")

    # --- 3. CONDICIÓN POSTERIOR ---
    st.subheader("Condición Posterior")
    st.checkbox("Considerar sacada después del parpadeo", key="req_sac_post")
    
    if st.session_state.req_sac_post:
        # A. Filtro por Filas (Duración)
        st.write("Filtro por duración:")
        c3, c4 = st.columns(2)
        c3.number_input("Mínimo filas sacada:", min_value=1, key="min_sac_post")
        c4.number_input("Máximo filas sacada:", min_value=1, key="max_sac_post")

        with st.popover("�"):
            st.write("Se analiza si existe un movimiento sacádico inmediatamente después del parpadeo.")
            st.image("ayuda3.png", caption="Ejemplo de sacada posterior al parpadeo")

        
        # B. Filtro por Velocidad (NUEVO)
        st.write("Filtro por velocidad angular:")
        st.checkbox("Filtrar por velocidad angular pico (º/s)", key="req_vel_post")
        
        if st.session_state.req_vel_post:
            cv1, cv2 = st.columns(2)
            cv1.number_input("Velocidad pico mínima (º/s):", min_value=0.0, key="min_vel_post")
            cv2.number_input("Velocidad pico máxima (º/s):", min_value=0.0, key="max_vel_post")
            st.info(f"Filtro activo: La sacada debe alcanzar entre {st.session_state.min_vel_post} y {st.session_state.max_vel_post} º/s.")

            with st.popover("�"):
                st.write("Se analiza la velocidad angular máxima del ojo durante el movimiento sacádico posterior.")
                st.image("ayuda4.png", caption="Esquema del cálculo de la velocidad angular")

# --- PESTAÑA DEL CONTADOR ---
with tab_contador:
    archivo_subido = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

    if archivo_subido is not None:
        try:
            # 1. Carga de datos
            df = pd.read_excel(archivo_subido)

            import numpy as np # Asegúrate de tener el import arriba

            # --- CÁLCULO PREVIO DE VELOCIDAD ANGULAR ---
            # 1. Extraemos los vectores y el tiempo
            gzx = df['Gaze direction left X'].fillna(0).values
            gzy = df['Gaze direction left Y'].fillna(0).values
            gzz = df['Gaze direction left Z'].fillna(0).values
            t_seg = df['Recording timestamp'].values / 1000000.0
            
            # 2. Preparamos un array para las velocidades (mismo tamaño que el DF)
            velocidades = np.zeros(len(df))
            
            for k in range(1, len(df)):
                # Si hay EyesNotFound (0), la velocidad es 0
                if gzx[k] == 0 or gzx[k-1] == 0:
                    continue
                
                # Delta t
                dt = t_seg[k] - t_seg[k-1]
                if dt <= 0: continue
    
                # Vectores v1 y v2
                v1 = np.array([gzx[k-1], gzy[k-1], gzz[k-1]])
                v2 = np.array([gzx[k], gzy[k], gzz[k]])
     
                # Producto escalar y módulos
                prod_esc = np.dot(v1, v2)
                mod1 = np.linalg.norm(v1)
                mod2 = np.linalg.norm(v2)
    
                # Coseno de theta (protegido entre -1 y 1)
                cos_theta = np.clip(prod_esc / (mod1 * mod2), -1.0, 1.0)
    
                # Ángulo en grados
                theta_rad = np.arccos(cos_theta)
                theta_deg = np.degrees(theta_rad)
     
                # Velocidad angular (º/s)
                velocidades[k] = theta_deg / dt

            # Añadimos la columna al dataframe original por si la quieres consultar
            df['Velocidad Angular'] = velocidades

            
            
            # 2. Verificación de columnas
            if 'Recording timestamp' in df.columns and 'Eye movement type' in df.columns:
                tiempos = df['Recording timestamp'].tolist()
                tipos_movimiento = df['Eye movement type'].tolist()
                
                resultados = []
                num_evento = 1
                i = 0
                etiquetas_blink = ['EyesNotFound', 'Unclassified']
                
                # 3. Bucle de procesamiento (Lógica de detección)
                while i < len(tipos_movimiento):
                    if tipos_movimiento[i] in etiquetas_blink:
                        inicio_idx = i
                        tiene_eyes_not_found = False
                        
                        # A. VERIFICAR SACADA PREVIA
                        sac_pre = (inicio_idx > 0 and tipos_movimiento[inicio_idx - 1] == 'Saccade')
                        
                        # B. CONTAR BLOQUE DE PARPADEO
                        while i < len(tipos_movimiento) and tipos_movimiento[i] in etiquetas_blink:
                            if tipos_movimiento[i] == 'EyesNotFound': 
                                tiene_eyes_not_found = True
                            i += 1
                        
                        fin_idx = i - 1
                        long_blink = fin_idx - inicio_idx + 1
                        
                        # C. VERIFICAR SACADA POSTERIOR
                        long_sac_post = 0
                        vel_pico = 0.0
                        j = i
                        indices_sacada = [] # Guardaremos los índices para buscar la velocidad
                        
                        while j < len(tipos_movimiento) and tipos_movimiento[j] == 'Saccade':
                            long_sac_post += 1
                            indices_sacada.append(j)
                            j += 1
                        
                        # Si hay sacada, buscamos la velocidad máxima en esos índices
                        if indices_sacada:
                            vel_pico = df['Velocidad Angular'].iloc[indices_sacada].max()
                        
                        sac_post_valida = (st.session_state.min_sac_post <= long_sac_post <= st.session_state.max_sac_post)
                        
                     
                        # Comprobamos la velocidad pico solo si la casilla está marcada
                        vel_post_valida = True 
                        if st.session_state.req_vel_post:
                            vel_post_valida = (st.session_state.min_vel_post <= vel_pico <= st.session_state.max_vel_post)
                        
                        # D. FILTRADO FINAL SEGÚN AJUSTES
                        # --- D. FILTRADO FINAL SEGÚN AJUSTES ---
                
                        # 1. Condición de duración del parpadeo
                        cond_parp = st.session_state.min_f <= long_blink <= st.session_state.max_f
                
                        # 2. Condición de Sacada Anterior (La puerta de seguridad)
                        if st.session_state.req_sac_pre:
                            cond_pre = sac_pre # Solo será True si realmente hubo sacada
                        else:
                            cond_pre = True    # Si no está marcada la casilla, dejamos pasar todo

                            # --- SUSTITUYE LAS LÍNEAS 264 A 267 POR ESTO ---

                
                        # 3. Condición de Sacada Posterior
                        if st.session_state.req_sac_post:
                            cond_post = (long_sac_post > 0 and sac_post_valida and vel_post_valida)
                        else:
                            cond_post = True

                        if cond_parp and tiene_eyes_not_found and cond_pre and cond_post:
                            t_ini = tiempos[inicio_idx] / 1000000.0
                            t_fin = tiempos[fin_idx] / 1000000.0
                            resultados.append({
                                'Parpadeo': num_evento,
                                'Inicio (s)': round(t_ini, 4),
                                'Fin (s)': round(t_fin, 4),
                                'Duración (s)': round(t_fin - t_ini, 4),
                                'Filas Parpadeo': long_blink,
                                'Sacada Previa': "Sí" if sac_pre else "No",
                                'Filas Sacada Posterior': long_sac_post,
                                'Velocidad Pico (º/s)': round(vel_pico, 2) 
                            })
                            num_evento += 1
                    else:
                        i += 1
                
                # 4. PRESENTACIÓN DE RESULTADOS
                df_resultados = pd.DataFrame(resultados)

                if not df_resultados.empty:
                    st.success(f"Se han detectado {len(df_resultados)} parpadeos.")
                    
                    # Corrección visual del índice
                    df_resultados.index = df_resultados.index + 1
                    st.dataframe(df_resultados, use_container_width=True)

                    # --- SECCIÓN DE MÉTRICAS ---
                    st.divider()
                    col_m1, col_m2 = st.columns(2)
                    
                    duracion_total_seg = (tiempos[-1] - tiempos[0]) / 1000000.0
                    frecuencia_min = (len(df_resultados) / duracion_total_seg) * 60
                    duracion_media_ms = round(df_resultados['Duración (s)'].mean() * 1000)
                    
                    with col_m1:
                        st.metric("Frecuencia media de parpadeo", f"{frecuencia_min:.0f} parpadeos/min")
                    with col_m2:
                        st.metric("Duración media del parpadeo (ojo completamente cerrado)", f"{duracion_media_ms} ms")

                    # Metadatos del archivo
                    c_meta1, c_meta2 = st.columns(2)
                    with c_meta1:
                        st.metric("Total de filas procesadas", f"{len(df):,}".replace(',', '.'))
                    with c_meta2:
                        h = int(duracion_total_seg // 3600)
                        m = int((duracion_total_seg % 3600) // 60)
                        s = int(duracion_total_seg % 60)
                        st.metric("Duración de la grabación", f"{h:02d}:{m:02d}:{s:02d}")
                    
                    # --- GRÁFICA DE DISTRIBUCIÓN DE DURACIONES ---
                    st.divider()
                    st.subheader("Distribución de parpadeos por duración")

                    if not df_resultados.empty:
                        # 1. Calculamos la duración en ms (Filas * 10)
                        # # Usamos la columna 'Filas Parpadeo' que ya tienes en el DataFrame
                        df_resultados['ms'] = df_resultados['Filas Parpadeo'] * 10
                        
                        # 2. Agrupamos para contar cuántos parpadeos hay de cada duración
                        df_counts = df_resultados.groupby('ms').size().reset_index(name='Cantidad')
                        
                        # Aseguramos que el eje X sea tratado como número para que mantenga el orden 10, 20, 30...
                        df_counts = df_counts.sort_values('ms')
                        
                        # 3. Creamos la gráfica de barras
                        import plotly.express as px
                        
                        fig = px.bar(
                            df_counts, 
                            x='ms', 
                            y='Cantidad',
                            labels={'ms': 'Duración (ms)', 'Cantidad': 'Número de Parpadeos'},
                            text_auto=True, # Pone el número encima de cada barra
                            template="plotly_dark" # Para que pegue con el modo oscuro de VS Code/Streamlit
                        )

                        # Ajustamos el eje X para que salte de 10 en 10 si hay muchos datos
                        fig.update_xaxes(type='linear', tickmode='linear', dtick=10)
                        fig.update_layout(bargap=0.2)

                        # 4. Mostrar en la web
                        st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning("No se detectaron eventos con los ajustes actuales.")

            else:
                st.error("El archivo no tiene las columnas necesarias: 'Recording timestamp' y 'Eye movement type'.")

        except Exception as e:
            st.error(f"Hubo un error al procesar el archivo: {e}")
