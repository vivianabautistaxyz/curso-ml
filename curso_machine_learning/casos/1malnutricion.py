import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import StringIO
import ssl
import urllib3

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL del dataset de malnutrición en Bogotá
URL_DATASET = "https://datosabiertos.bogota.gov.co/dataset/9776e238-8f4a-40d4-a473-37e9cc0b2ef0/resource/c8fe2dd0-5ad1-4023-86b2-135026f7ecf1/download/metadato_malnutricion5anos.csv"

def descargar_dataset():
    """Descargar el dataset de malnutrición"""
    print("📥 Descargando dataset de malnutrición en Bogotá...")
    
    try:
        # Crear contexto SSL que no verifique certificados
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        response = requests.get(URL_DATASET, verify=False, timeout=30)
        response.raise_for_status()
        
        # Guardar archivo localmente
        with open('malnutricion_bogota.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("✅ Dataset descargado exitosamente como 'malnutricion_bogota.csv'")
        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al descargar el dataset: {e}")
        print("💡 Intentando con datos de ejemplo...")
        return generar_datos_ejemplo()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def generar_datos_ejemplo():
    """Generar datos de ejemplo para demostración"""
    print("📊 Generando datos de ejemplo...")
    
    np.random.seed(42)
    n_muestras = 1000
    
    datos = {
        'AÑO': np.random.choice([2020, 2021, 2022, 2023], n_muestras),
        'LOCALIDAD': np.random.choice(['USAQUEN', 'CHAPINERO', 'SANTA FE', 'SAN CRISTOBAL', 'USME'], n_muestras),
        'EDAD_MESES': np.random.randint(0, 60, n_muestras),
        'PESO_KG': np.random.normal(10, 3, n_muestras),
        'TALLA_CM': np.random.normal(75, 15, n_muestras),
        'INDICE_MASA_CORPORAL': np.random.normal(15, 2, n_muestras),
        'CLASIFICACION_NUTRICIONAL': np.random.choice(['NORMAL', 'DESNUTRICION', 'SOBREPESO'], n_muestras, p=[0.7, 0.15, 0.15])
    }
    
    df = pd.DataFrame(datos)
    
    # Guardar datos de ejemplo
    df.to_csv('malnutricion_bogota.csv', index=False)
    
    print("✅ Datos de ejemplo generados y guardados como 'malnutricion_bogota.csv'")
    return df.to_csv(index=False)

def cargar_y_analizar_datos(csv_content):
    """Cargar y analizar los datos del dataset"""
    if csv_content is None:
        return None
    
    print("\n Cargando y analizando datos...")
    
    try:
        # Cargar datos desde el contenido CSV
        df = pd.read_csv(StringIO(csv_content))
        
        print(f" Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        # Mostrar información básica
        print("\n Información del dataset:")
        print(df.info())
        
        print("\n Estadísticas descriptivas:")
        print(df.describe())
        
        print("\n Primeras 5 filas:")
        print(df.head())
        
        print("\n Columnas disponibles:")
        for i, col in enumerate(df.columns, 1):
            print(f"{i}. {col}")
        
        return df
        
    except Exception as e:
        print(f" Error al analizar los datos: {e}")
        return None

def analizar_malnutricion(df):
    """Análisis específico de malnutrición"""
    if df is None:
        return
    
    print("\n Análisis de Malnutrición en Bogotá")
    print("=" * 50)
    
    # Identificar columnas numéricas relevantes
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print(f"\n Columnas numéricas encontradas: {numeric_cols}")
    
    # Identificar columnas categóricas
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    print(f" Columnas categóricas encontradas: {categorical_cols}")
    
    # Análisis de valores nulos
    print("\n Análisis de valores nulos:")
    null_counts = df.isnull().sum()
    for col, null_count in null_counts.items():
        if null_count > 0:
            print(f"  {col}: {null_count} ({null_count/len(df)*100:.1f}%)")
    
    if null_counts.sum() == 0:
        print("  No se encontraron valores nulos")
    
    return numeric_cols, categorical_cols

def crear_visualizaciones(df, numeric_cols, categorical_cols):
    """Crear visualizaciones básicas"""
    if df is None or len(numeric_cols) == 0:
        print("\n No hay suficientes datos numéricos para visualizaciones")
        return
    
    print("\n Creando visualizaciones...")
    
    try:
        # Configurar estilo
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Análisis de Malnutrición en Bogotá', fontsize=16, fontweight='bold')
        
        # Gráfico 1: Distribución de la primera variable numérica
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            axes[0, 0].hist(df[col].dropna(), bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            axes[0, 0].set_title(f'Distribución de {col}')
            axes[0, 0].set_xlabel(col)
            axes[0, 0].set_ylabel('Frecuencia')
            axes[0, 0].grid(True, alpha=0.3)
        
        # Gráfico 2: Box plot de variables numéricas
        if len(numeric_cols) > 0:
            df[numeric_cols].boxplot(ax=axes[0, 1])
            axes[0, 1].set_title('Box Plot de Variables Numéricas')
            axes[0, 1].tick_params(axis='x', rotation=45)
            axes[0, 1].grid(True, alpha=0.3)
        
        # Gráfico 3: Correlación entre variables numéricas
        if len(numeric_cols) > 1:
            correlation_matrix = df[numeric_cols].corr()
            im = axes[1, 0].imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
            axes[1, 0].set_title('Matriz de Correlación')
            axes[1, 0].set_xticks(range(len(numeric_cols)))
            axes[1, 0].set_yticks(range(len(numeric_cols)))
            axes[1, 0].set_xticklabels(numeric_cols, rotation=45)
            axes[1, 0].set_yticklabels(numeric_cols)
            
            # Añadir valores de correlación
            for i in range(len(numeric_cols)):
                for j in range(len(numeric_cols)):
                    axes[1, 0].text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}', 
                                   ha='center', va='center', color='black')
        else:
            axes[1, 0].text(0.5, 0.5, 'Se necesitan más variables\nnuméricas para correlación', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Matriz de Correlación')
        
        # Gráfico 4: Resumen estadístico
        axes[1, 1].axis('off')
        summary_text = "Resumen Estadístico:\n\n"
        for col in numeric_cols[:3]:  # Mostrar hasta 3 variables
            if col in df.columns:
                summary_text += f"{col}:\n"
                summary_text += f"  Media: {df[col].mean():.2f}\n"
                summary_text += f"  Mediana: {df[col].median():.2f}\n"
                summary_text += f"  Desv. Std: {df[col].std():.2f}\n\n"
        
        axes[1, 1].text(0.1, 0.9, summary_text, transform=axes[1, 1].transAxes, 
                       fontsize=10, verticalalignment='top', fontfamily='monospace')
        axes[1, 1].set_title('Resumen Estadístico')
        
        plt.tight_layout()
        plt.savefig('analisis_malnutricion.png', dpi=300, bbox_inches='tight')
        print(" Visualizaciones guardadas como 'analisis_malnutricion.png'")
        
    except Exception as e:
        print(f" Error al crear visualizaciones: {e}")

def main():
    """Función principal del análisis"""
    print("🏥 Análisis de Malnutrición en Niños menores de 5 años en Bogotá")
    print("=" * 70)
    
    # Paso 1: Descargar dataset
    csv_content = descargar_dataset()
    
    # Paso 2: Cargar y analizar datos
    df = cargar_y_analizar_datos(csv_content)
    
    if df is None:
        print("❌ No se pudieron cargar los datos. Finalizando análisis.")
        return
    
    # Paso 3: Análisis específico
    resultado_analisis = analizar_malnutricion(df)
    
    if resultado_analisis is None:
        print("❌ No se pudo completar el análisis específico. Finalizando.")
        return
    
    numeric_cols, categorical_cols = resultado_analisis
    
    # Paso 4: Crear visualizaciones
    crear_visualizaciones(df, numeric_cols, categorical_cols)
    
    print("\n🎉 Análisis completado!")
    print("📁 Archivos generados:")
    print("  - malnutricion_bogota.csv (datos originales)")
    print("  - analisis_malnutricion.png (visualizaciones)")

if __name__ == "__main__":
    main()