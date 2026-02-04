"""
Script para descargar y procesar datos de malnutrición en Bogotá
"""

import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import ssl
import urllib3
import time

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DescargadorDatosMalnutricion:
    """Clase para descargar y procesar datos de malnutrición"""
    
    def __init__(self):
        self.base_url = "https://datosabiertos.bogota.gov.co"
        self.dataset_id = "9776e238-8f4a-40d4-a473-37e9cc0b2ef0"
        self.resource_id = "c8fe2dd0-5ad1-4023-86b2-135026f7ecf1"
        self.datos_url = f"{self.base_url}/dataset/{self.dataset_id}/resource/{self.resource_id}/download/metadato_malnutricion5anos.csv"
    
    def descargar_datos_reales(self):
        """Intentar descargar los datos reales del dataset"""
        print("🔍 Buscando datos reales de malnutrición...")
        
        # URLs alternativas para intentar
        urls_alternativas = [
            f"{self.base_url}/dataset/{self.dataset_id}/resource/{self.resource_id}/download/datos_malnutricion.csv",
            f"{self.base_url}/api/3/action/datastore_search?resource_id={self.resource_id}",
            "https://www.datos.gov.co/api/views/gt2j-8ykr/rows.csv?accessType=DOWNLOAD"
        ]
        
        for i, url in enumerate(urls_alternativas, 1):
            print(f"📡 Intentando URL {i}: {url[:50]}...")
            
            try:
                response = requests.get(url, verify=False, timeout=30)
                response.raise_for_status()
                
                # Verificar si es CSV válido
                if 'csv' in response.headers.get('content-type', '') or ',' in response.text[:100]:
                    print(f"✅ Datos encontrados en URL {i}")
                    
                    # Guardar datos
                    filename = f'malnutricion_datos_reales_{i}.csv'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    print(f"💾 Datos guardados como '{filename}'")
                    return response.text, filename
                    
            except Exception as e:
                print(f"❌ Error en URL {i}: {e}")
                continue
        
        return None, None
    
    def generar_datos_simulados(self):
        """Generar datos simulados realistas de malnutrición"""
        print("📊 Generando datos simulados de malnutrición...")
        
        np.random.seed(42)
        n_muestras = 2000
        
        # Generar datos realistas
        localidades = ['USAQUEN', 'CHAPINERO', 'SANTA FE', 'SAN CRISTOBAL', 'USME', 
                      'BOSA', 'KENNEDY', 'FONTIBON', 'ENGATIVA', 'SUBA',
                      'BARRIOS UNIDOS', 'TEUSAQUILLO', 'LOS MARTIRES', 'ANTONIO NARIÑO',
                      'PUENTE ARANDA', 'LA CANDELARIA', 'RAFAEL URIBE URIBE', 'CIUDAD BOLIVAR',
                      'SUMAPAZ', 'TUNJUELITO']
        
        datos = {
            'AÑO': np.random.choice([2019, 2020, 2021, 2022, 2023, 2024], n_muestras),
            'TRIMESTRE': np.random.choice(['T1', 'T2', 'T3', 'T4'], n_muestras),
            'LOCALIDAD': np.random.choice(localidades, n_muestras),
            'EDAD_MESES': np.random.randint(0, 60, n_muestras),
            'SEXO': np.random.choice(['MASCULINO', 'FEMENINO'], n_muestras),
            'PESO_KG': np.random.normal(12, 4, n_muestras),
            'TALLA_CM': np.random.normal(85, 20, n_muestras),
            'PESO_TALLA_Z': np.random.normal(0, 2, n_muestras),
            'TALLA_EDAD_Z': np.random.normal(-0.5, 1.5, n_muestras),
            'PESO_EDAD_Z': np.random.normal(-0.3, 1.8, n_muestras),
            'IMC_EDAD_Z': np.random.normal(0.2, 1.6, n_muestras),
            'CLASIFICACION_P_T': self._clasificar_nutricion(np.random.normal(-0.5, 2, n_muestras)),
            'CLASIFICACION_T_E': self._clasificar_nutricion(np.random.normal(-0.8, 1.5, n_muestras)),
            'CLASIFICACION_P_E': self._clasificar_nutricion(np.random.normal(-0.3, 1.8, n_muestras)),
            'CLASIFICACION_IMC_E': self._clasificar_nutricion(np.random.normal(0.2, 1.6, n_muestras)),
            'TIPO_ATENCION': np.random.choice(['PÚBLICA', 'PRIVADA'], n_muestras, p=[0.7, 0.3]),
            'REGIMEN_AFILIACION': np.random.choice(['CONTRIBUTIVO', 'SUBSIDIADO', 'NO AFILIADO'], 
                                                 n_muestras, p=[0.4, 0.5, 0.1])
        }
        
        # Ajustar pesos y tallas según edad
        for i in range(n_muestras):
            edad = datos['EDAD_MESES'][i]
            # Peso esperado según edad (fórmula simplificada)
            peso_esperado = 3 + (edad * 0.5) + np.random.normal(0, 1)
            datos['PESO_KG'][i] = max(2, peso_esperado)
            
            # Talla esperada según edad
            talla_esperada = 50 + (edad * 1.5) + np.random.normal(0, 5)
            datos['TALLA_CM'][i] = max(40, talla_esperada)
        
        df = pd.DataFrame(datos)
        
        # Calcular IMC
        df['IMC'] = df['PESO_KG'] / ((df['TALLA_CM']/100) ** 2)
        
        # Guardar datos
        filename = 'malnutricion_simulados_bogota.csv'
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"✅ Datos simulados generados y guardados como '{filename}'")
        print(f"📈 Total de registros: {len(df)}")
        
        return df.to_csv(index=False), filename
    
    def _clasificar_nutricion(self, z_scores):
        """Clasificar estado nutricional según Z-score"""
        clasificaciones = []
        for z in z_scores:
            if z < -3:
                clasificaciones.append('DESNUTRICIÓN SEVERA')
            elif z < -2:
                clasificaciones.append('DESNUTRICIÓN MODERADA')
            elif z < -1:
                clasificaciones.append('DESNUTRICIÓN LEVE')
            elif z <= 2:
                clasificaciones.append('NORMAL')
            else:
                clasificaciones.append('SOBREPESO/OBESIDAD')
        return clasificaciones
    
    def analizar_datos(self, csv_content, filename):
        """Analizar los datos descargados"""
        print("\n📊 Analizando datos...")
        
        try:
            df = pd.read_csv(StringIO(csv_content))
            
            print(f"✅ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            # Información básica
            print("\n📋 Información del dataset:")
            print(df.info())
            
            print("\n📊 Estadísticas descriptivas:")
            print(df.describe())
            
            print("\n🔍 Primeras 5 filas:")
            print(df.head())
            
            print("\n📝 Columnas disponibles:")
            for i, col in enumerate(df.columns, 1):
                print(f"{i}. {col}")
            
            # Análisis de valores nulos
            print("\n🔍 Análisis de valores nulos:")
            null_counts = df.isnull().sum()
            for col, null_count in null_counts.items():
                if null_count > 0:
                    print(f"  {col}: {null_count} ({null_count/len(df)*100:.1f}%)")
            
            if null_counts.sum() == 0:
                print("  ✅ No se encontraron valores nulos")
            
            # Análisis de malnutrición
            self._analizar_malnutricion_especifico(df)
            
            # Crear visualizaciones
            self._crear_visualizaciones(df, filename.replace('.csv', '_analisis.png'))
            
            return df
            
        except Exception as e:
            print(f"❌ Error al analizar los datos: {e}")
            return None
    
    def _analizar_malnutricion_especifico(self, df):
        """Análisis específico de malnutrición"""
        print("\n🏥 Análisis Específico de Malnutrición")
        print("=" * 50)
        
        # Identificar columnas de clasificación nutricional
        clas_cols = [col for col in df.columns if 'CLASIFICACION' in col.upper()]
        
        if clas_cols:
            print(f"\n📊 Columnas de clasificación nutricional encontradas: {clas_cols}")
            
            for col in clas_cols[:2]:  # Analizar hasta 2 columnas
                if col in df.columns:
                    print(f"\n📈 Distribución - {col}:")
                    distribucion = df[col].value_counts()
                    for categoria, count in distribucion.items():
                        porcentaje = (count / len(df)) * 100
                        print(f"  {categoria}: {count} ({porcentaje:.1f}%)")
        
        # Análisis por localidad
        if 'LOCALIDAD' in df.columns:
            print(f"\n🏘️ Casos por localidad (Top 10):")
            localidad_counts = df['LOCALIDAD'].value_counts().head(10)
            for localidad, count in localidad_counts.items():
                porcentaje = (count / len(df)) * 100
                print(f"  {localidad}: {count} ({porcentaje:.1f}%)")
        
        # Análisis por año
        if 'AÑO' in df.columns:
            print(f"\n📅 Casos por año:")
            año_counts = df['AÑO'].value_counts().sort_index()
            for año, count in año_counts.items():
                porcentaje = (count / len(df)) * 100
                print(f"  {año}: {count} ({porcentaje:.1f}%)")
    
    def _crear_visualizaciones(self, df, output_filename):
        """Crear visualizaciones de los datos"""
        print("\n📈 Creando visualizaciones...")
        
        try:
            # Configurar estilo
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle('Análisis de Malnutrición en Bogotá', fontsize=16, fontweight='bold')
            
            # Gráfico 1: Distribución por edad
            if 'EDAD_MESES' in df.columns:
                axes[0, 0].hist(df['EDAD_MESES'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
                axes[0, 0].set_title('Distribución por Edad (meses)')
                axes[0, 0].set_xlabel('Edad en meses')
                axes[0, 0].set_ylabel('Frecuencia')
                axes[0, 0].grid(True, alpha=0.3)
            
            # Gráfico 2: Distribución por peso
            if 'PESO_KG' in df.columns:
                axes[0, 1].hist(df['PESO_KG'], bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
                axes[0, 1].set_title('Distribución por Peso (kg)')
                axes[0, 1].set_xlabel('Peso en kg')
                axes[0, 1].set_ylabel('Frecuencia')
                axes[0, 1].grid(True, alpha=0.3)
            
            # Gráfico 3: Casos por localidad
            if 'LOCALIDAD' in df.columns:
                localidad_counts = df['LOCALIDAD'].value_counts().head(10)
                axes[0, 2].barh(range(len(localidad_counts)), localidad_counts.values, alpha=0.7, color='orange')
                axes[0, 2].set_yticks(range(len(localidad_counts)))
                axes[0, 2].set_yticklabels(localidad_counts.index)
                axes[0, 2].set_title('Casos por Localidad (Top 10)')
                axes[0, 2].set_xlabel('Número de casos')
                axes[0, 2].grid(True, alpha=0.3)
            
            # Gráfico 4: Clasificación nutricional
            clas_cols = [col for col in df.columns if 'CLASIFICACION' in col.upper()]
            if clas_cols and clas_cols[0] in df.columns:
                clas_counts = df[clas_cols[0]].value_counts()
                axes[1, 0].pie(clas_counts.values, labels=clas_counts.index, autopct='%1.1f%%', startangle=90)
                axes[1, 0].set_title(f'Distribución - {clas_cols[0]}')
            
            # Gráfico 5: Evolución temporal
            if 'AÑO' in df.columns:
                año_counts = df['AÑO'].value_counts().sort_index()
                axes[1, 1].plot(año_counts.index, año_counts.values, marker='o', linewidth=2, markersize=8)
                axes[1, 1].set_title('Evolución Temporal de Casos')
                axes[1, 1].set_xlabel('Año')
                axes[1, 1].set_ylabel('Número de casos')
                axes[1, 1].grid(True, alpha=0.3)
            
            # Gráfico 6: Peso vs Talla
            if 'PESO_KG' in df.columns and 'TALLA_CM' in df.columns:
                axes[1, 2].scatter(df['TALLA_CM'], df['PESO_KG'], alpha=0.6, c='purple')
                axes[1, 2].set_title('Relación Peso vs Talla')
                axes[1, 2].set_xlabel('Talla (cm)')
                axes[1, 2].set_ylabel('Peso (kg)')
                axes[1, 2].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_filename, dpi=300, bbox_inches='tight')
            print(f"✅ Visualizaciones guardadas como '{output_filename}'")
            
        except Exception as e:
            print(f"❌ Error al crear visualizaciones: {e}")


def main():
    """Función principal"""
    print("🏥 Sistema de Descarga y Análisis de Datos de Malnutrición")
    print("=" * 60)
    
    descargador = DescargadorDatosMalnutricion()
    
    # Intentar descargar datos reales
    datos_reales, filename_real = descargador.descargar_datos_reales()
    
    if datos_reales:
        print("✅ Usando datos reales descargados")
        descargador.analizar_datos(datos_reales, filename_real)
    else:
        print("⚠️ No se pudieron descargar datos reales, usando datos simulados")
        datos_simulados, filename_sim = descargador.generar_datos_simulados()
        if datos_simulados:
            descargador.analizar_datos(datos_simulados, filename_sim)
    
    print("\n🎉 Proceso completado!")


if __name__ == "__main__":
    main()
