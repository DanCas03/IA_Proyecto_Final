# Clasificador Semántico de Textos Clásicos

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/cloud/atlas)
[![Transformers](https://img.shields.io/badge/🤗-Transformers-yellow.svg)](https://huggingface.co/transformers/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TU_USUARIO/proyecto2/blob/main/colab_setup.ipynb)

Sistema de Inteligencia Artificial para clasificar fragmentos de textos clásicos en tres categorías temáticas:
- **Areté**: Excelencia y virtud moral.
- **Política y Poder**: Reflexiones sobre gobierno y autoridad.
- **Relación Dioses-Humanos**: Interacciones entre lo divino y lo mortal.

> 📖 **Quick Start:** [Local](README.md#-fase-1-configuración-inicial) | [Google Colab](QUICKSTART_COLAB.md) | [Guía Completa Colab](GUIA_COLAB.md)

## 🛠️ Tecnologías Utilizadas

- **Python 3.9+**
- **MongoDB Atlas**: Base de datos NoSQL para persistencia.
- **Hugging Face Transformers**: Modelos de lenguaje avanzados.
- **BETO**: BERT pre-entrenado en español para el análisis semántico.
- **Streamlit**: Interfaz de usuario moderna y accesible.
- **scikit-learn**: Herramientas de evaluación y métricas.

## 📁 Estructura del Proyecto

```
proyecto2/
├── Dataset/                    # Archivos Excel con datos originales
├── src/
│   ├── config.py              # Configuración centralizada
│   ├── data/
│   │   ├── db.py              # Conexión y gestión de MongoDB
│   │   └── etl.py             # Pipeline de extracción (ETL)
│   ├── model/
│   │   ├── preprocessing.py   # Limpieza y balanceo de datos
│   │   ├── train.py           # Entrenamiento del modelo
│   │   ├── evaluate.py        # Evaluación y reportes
│   │   └── inference.py       # Módulo para predicciones
│   └── app/
│       └── streamlit_app.py   # Aplicación web Streamlit
├── scripts/                    # Scripts de ejecución paso a paso
│   ├── 01_test_connection.py
│   ├── 02_run_etl.py
│   ├── ...
├── models/                     # Modelos entrenados (ignorado en git)
├── reports/                    # Gráficos y reportes de métricas
└── run_pipeline.py             # Script maestro del pipeline
```

---

# 📖 Guía de Ejecución Paso a Paso

Esta guía te llevará a través de todo el proceso, desde la configuración inicial hasta tener la aplicación funcionando.

## 📋 Requisitos Previos

- ✅ Python 3.9+ instalado
- ✅ MongoDB Atlas cluster activo
- ✅ 8GB RAM mínimo
- ✅ Espacio en disco: ~2GB (modelos + datos)

> 💡 **¿No tienes GPU?** Usa [Google Colab](QUICKSTART_COLAB.md) para entrenar **10-20x más rápido** de forma gratuita.

## 🚀 Fase 1: Configuración Inicial

### 1. Preparar el Entorno

```powershell
# Navegar al directorio del proyecto

# Activar entorno virtual (ya creado)
.\venv\Scripts\Activate.ps1

# Verificar instalación de dependencias
python -c "import torch; import transformers; print('Dependencias OK')"
```

### 2. Configurar MongoDB

1. Crea un archivo `.env` en la raíz del proyecto
2. Agrega tu URI de conexión:

```
MONGO_URI=mongodb+srv://TU_USUARIO:TU_PASSWORD@TU_CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=textos_clasicos
```

3. **Importante**: Reemplaza `TU_USUARIO`, `TU_PASSWORD` y `TU_CLUSTER` con tus credenciales reales

### 3. Verificar Conexión

```powershell
python scripts/01_test_connection.py
```

**Resultado esperado:**
```
✓ Conexión exitosa a MongoDB Atlas
✓ Base de datos: textos_clasicos
✓ Permisos de lectura/escritura: OK
✅ TODAS LAS PRUEBAS PASARON
```

---

## 📊 Fase 2: Migración de Datos (ETL)

### Ejecutar ETL

```powershell
python scripts/02_run_etl.py
```

**Tiempo estimado:** 1-2 minutos

**Resultado esperado:**
- 123 documentos insertados
- Distribución por categoría:
  - Areté: 42
  - Política y Poder: 38
  - Dioses-Humanos: 43

**En caso de problemas:**
```powershell
# Ejecutar con debug para ver detalles
python scripts/02_run_etl.py --debug
```

---

## 🔄 Fase 3: Preprocesamiento

### Ejecutar Preprocesamiento y Balanceo

```powershell
python scripts/03_preprocess.py
```

**Tiempo estimado:** 30 segundos

**Qué hace:**
1. Limpia los textos (elimina caracteres especiales, normaliza espacios)
2. Balancea las clases (undersampling por defecto)
3. Divide en train (70%), validation (15%), test (15%)
4. Guarda los conjuntos en MongoDB

**Resultado esperado:**
```
✓ Documentos balanceados: ~105
✓ Train: ~73
✓ Val: ~16
✓ Test: ~16
```

---

## 🤖 Fase 4: Entrenamiento del Modelo

### Entrenar BETO

```powershell
python scripts/04_train.py
```

**⏱️ Tiempo estimado:**
- **CPU**: 1-3 horas
- **GPU**: 15-30 minutos

**Qué hace:**
1. Carga BETO (bert-base-spanish-wwm-cased)
2. Fine-tuning con tus datos
3. Guarda el mejor modelo basado en F1-Score
4. Early stopping después de 2 épocas sin mejora

**Durante el entrenamiento verás:**
```
Epoch 1/5: [████████████] loss: 0.85 | accuracy: 0.72
Epoch 2/5: [████████████] loss: 0.42 | accuracy: 0.88
...
```

**Resultado esperado:**
```
✅ ENTRENAMIENTO COMPLETADO
   • F1 Macro (val): 0.82 ✓
   • Modelo guardado en: models/clasificador_textos/final
```

### Si el F1 es < 0.80:

1. **Aumenta épocas**: Edita `src/config.py` → `num_epochs: 10`
2. **Prueba oversampling**: En `preprocessing.py` cambia a `oversample`
3. **Ajusta learning rate**: Prueba `1e-5` o `3e-5`

---

## 📈 Fase 5: Evaluación

### Generar Reportes

```powershell
python scripts/05_evaluate.py
```

**Tiempo estimado:** 2-3 minutos

**Qué genera:**
- `reports/confusion_matrix.png` - Matriz de confusión visual
- `reports/metrics_by_class.png` - Métricas por categoría
- `reports/evaluation_report.json` - Reporte completo en JSON

**Resultado esperado:**
```
📊 RESULTADOS DE EVALUACIÓN
   • Accuracy: 0.85
   • F1-Score (macro): 0.82
   ✅ CRITERIO CUMPLIDO: ≥ 0.80
```

---

## 🎨 Fase 6: Aplicación Web

### Lanzar Streamlit

```powershell
streamlit run src/app/streamlit_app.py
```

**Se abrirá automáticamente en:** http://localhost:8501

### Uso de la Aplicación:

1. **Ingresa un texto** en el área de texto
2. **Haz clic en "Analizar Texto"**
3. **Observa**:
   - Categoría predicha
   - Nivel de confianza (%)
   - Distribución de probabilidades

**Ejemplo de texto para probar:**
```
"La virtud es el camino hacia la excelencia del alma."
→ Debería clasificarse como "Areté"
```

---

## 🐛 Solución de Problemas

### Problema: Error de conexión a MongoDB

**Solución:**
1. Verifica que tu cluster esté activo en MongoDB Atlas
2. Revisa que el `.env` tenga la URI correcta
3. Verifica que tu IP esté en la whitelist de Atlas

### Problema: "Module not found"

**Solución:**
```powershell
pip install -r requirements.txt --upgrade
```

### Problema: Memoria insuficiente durante entrenamiento

**Solución:**
1. Reduce batch_size en `src/config.py`:
   ```python
   "batch_size_cpu": 2,  # Reducir de 4 a 2
   ```
2. Considera usar Google Colab con GPU gratuita

### Problema: Emojis no se muestran en terminal

**No es un error** - Los scripts ya manejan esto automáticamente. Verás caracteres extraños pero el programa funciona correctamente.

---

## ✅ Verificación Final

Revisa que todo funcione:

```powershell
# ✓ Datos en MongoDB
python -c "from src.data.db import get_collection; print(f'Datos: {get_collection(\"raw_texts\").count_documents({})}')"

# ✓ Modelo entrenado existe
python -c "from pathlib import Path; print('Modelo OK' if Path('models/clasificador_textos/final').exists() else 'Sin modelo')"

# ✓ Reportes generados
python -c "from pathlib import Path; print('Reportes OK' if Path('reports/confusion_matrix.png').exists() else 'Sin reportes')"
```

---

## 📚 Próximos Pasos

1. **Experimentar** con diferentes textos en la app
2. **Revisar** las métricas en `reports/`
3. **Ajustar** hiperparámetros si es necesario
4. **Documentar** tus resultados
5. **Publicar** en GitHub (sin `.env` ni modelos)

---

## 🔍 Características del Sistema ETL

El sistema ETL implementa estrategias avanzadas para manejar la heterogeneidad de los archivos suministrados:

1.  **Detección Difusa de Categorías**: Maneja variaciones en los nombres de las hojas (ej: "etiqueta areté", "Areté") y abreviaciones ("H. y D.").
2.  **Detección de Múltiples Formatos**: Soporta tanto hojas individuales por categoría como hojas con múltiples tablas en paralelo (formato multi-columna).
3.  **Búsqueda Inteligente de Encabezados**: Escanea automáticamente las filas para localizar los encabezados de las tablas (Canto, Versos, Cita), sin importar si la tabla empieza en la celda A1.

---

## 🚩 Publicación en Git y Notas Importantes

### Antes de hacer commit:
1.  **Verifica `.env`**: Asegúrate de que tus credenciales de MongoDB NO se suban. Ya está en el `.gitignore`.
2.  **Modelos Pesados**: Los modelos entrenados (>500MB) están ignorados; cada usuario debe entrenar el suyo localmente.
3.  **Dataset**: El dataset original está incluido en el repositorio para facilitar la primera ejecución, pero considera los derechos de autor antes de hacerlo público.

### Archivos a subir:
- Código fuente (`src/`, `run_pipeline.py`, `scripts/`).
- `requirements.txt`, `README.md`, `.gitignore`, `.env.example`.
- Carpetas de estructura con `.gitkeep` (`models/`, `reports/`).

---

## 📞 Ayuda Adicional

Si encuentras problemas:
1. Revisa esta guía
2. Ejecuta scripts con `--debug` cuando esté disponible
3. Revisa los logs de error completos
4. Consulta la documentación de las librerías (Hugging Face, PyTorch)

¡Éxito con tu proyecto! 🎉

---

## 🚀 Opción Alternativa: Google Colab

Si no tienes una GPU potente, puedes entrenar el modelo en **Google Colab** de forma gratuita.

### Ventajas:
- ✅ **GPU Tesla T4 gratuita**
- ✅ **10-20x más rápido** que CPU
- ✅ **Sin instalación local**

### Cómo usar:

1. Sube el código a GitHub
2. Abre `colab_setup.ipynb` en [Google Colab](https://colab.research.google.com/)
3. Sigue las instrucciones del notebook

📖 **Guía completa:** Ver [GUIA_COLAB.md](GUIA_COLAB.md)

---

# Autor
Daniel Castellanos  
Desarrollado como proyecto académico de IA.
