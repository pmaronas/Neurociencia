import streamlit as st
import pandas as pd

st.title("Contador de Parpadeos Tobii")
st.write("Sube tu archivo Excel para analizar las métricas.")

# Este es el botón "Examinar" que querías
archivo_subido = st.file_uploader("Elige un archivo Excel", type=["xlsx"])

if archivo_subido is not None:
    df = pd.read_excel(archivo_subido)
    st.success("¡Archivo cargado con éxito!")
    st.write("Aquí tienes una vista previa de tus datos:")
    st.dataframe(df.head())

    try:
        # Leer el Excel
        df = pd.read_excel(archivo_subido)
        
        # Verificar que las columnas existen
        if 'Recording timestamp' in df.columns and 'Eye movement type' in df.columns:
            
            tiempos = df['Recording timestamp'].tolist()
            tipos_movimiento = df['Eye movement type'].tolist()
            
            resultados = []
            num_evento = 1
            i = 0
            etiquetas_validas = ['EyesNotFound', 'Unclassified']
            
            # 2. Lógica de detección
            while i < len(tipos_movimiento):
                if tipos_movimiento[i] in etiquetas_validas:
                    inicio_idx = i
                    tiene_eyes_not_found = False
                    
                    while i < len(tipos_movimiento) and tipos_movimiento[i] in etiquetas_validas:
                        if tipos_movimiento[i] == 'EyesNotFound':
                            tiene_eyes_not_found = True
                        i += 1
                    
                    fin_idx = i - 1
                    longitud = fin_idx - inicio_idx + 1
                    
                    # Aplicar filtros (4-60 filas y presencia de EyesNotFound)
                    if 4 <= longitud <= 60 and tiene_eyes_not_found:
                        t_inicio = tiempos[inicio_idx] / 1000000.0
                        t_fin = tiempos[fin_idx] / 1000000.0
                        
                        resultados.append({
                            'Parpadeo': num_evento,
                            'Inicio (s)': round(t_inicio, 4),
                            'Fin (s)': round(t_fin, 4),
                            'Duración (s)': round(t_fin - t_inicio, 4),
                            'Nº de Filas': longitud
                        })
                        num_evento += 1
                else:
                    i += 1
            
            # 3. Mostrar resultados
            df_resultados = pd.DataFrame(resultados)
            
            if not df_resultados.empty:
                st.success(f"Se han detectado {len(df_resultados)} parpadeos.")
                
                # Mostrar tabla en la web
                st.dataframe(df_resultados, use_container_width=True)
                
                # Botón para descargar los resultados en Excel
                @st.cache_data
                def convertir_df(df):
                    return df.to_csv(index=False).encode('utf-8')

                csv = convertir_df(df_resultados)
                st.download_button(
                    label="📥 Descargar resultados en CSV",
                    data=csv,
                    file_name='resultados_parpadeos.csv',
                    mime='text/csv',
                )
                
                st.divider() 
                col1, col2 = st.columns(2)

                # 1. Cálculo de Frecuencia (usando el primer y último timestamp del Excel)
                duracion_total_grabacion = (tiempos[-1] - tiempos[0]) / 1000000.0
                frecuencia = (len(df_resultados) / duracion_total_grabacion)*60

                # 2. Cálculo de Duración Media en ms
                duracion_media_ms = round(df_resultados['Duración (s)'].mean() * 1000)

                with col1:
                    st.metric(label="Frecuencia de parpadeo", value=f"{frecuencia:.0f} parpadeos/min")
            
                with col2:
                    st.metric(label="Duración media", value=f"{duracion_media_ms} ms")
            
                st.divider()
            
            else:
                st.warning("No se detectaron patrones con los criterios actuales.")
        else:
            st.error("El archivo no tiene las columnas necesarias: 'Recording timestamp' y 'Eye movement type'")
            
    except Exception as e:
        st.error(f"Hubo un error al procesar el archivo: {e}")

else:
    st.info("A la espera de un archivo Excel para comenzar el análisis...")
    
    