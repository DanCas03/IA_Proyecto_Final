# Clasificador Semántico de Textos Clásicos

Sistema de Inteligencia Artificial para clasificar fragmentos de textos clásicos en tres categorías temáticas:
- **Areté**: Excelencia y virtud moral
- **Política y Poder**: Reflexiones sobre gobierno y autoridad
- **Relación Dioses-Humanos**: Interacciones entre lo divino y lo mortal

## Requisitos

- Python 3.9+
- MongoDB Atlas (cluster activo)
- 8GB RAM mínimo para entrenamiento

## Instalación

1. **Clonar el repositorio:**
```bash
git clone <url-repositorio>
cd proyecto2
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# En Linux/Mac: source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar MongoDB:**

Copia el archivo `.env.example` como `.env` y completa con tus credenciales:
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

Edita `.env` con tu información de MongoDB Atlas:
```
MONGO_URI=mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=textos_clasicos
```

> ⚠️ **IMPORTANTE**: Nunca subas el archivo `.env` a Git. Ya está incluido en `.gitignore`.

## Uso

### Pipeline Completo (Recomendado)

Ejecutar todo el pipeline de una vez:
```bash
python run_pipeline.py
```

### Ejecución por Pasos

1. **ETL (Extracción de datos):**
```bash
python run_pipeline.py --step etl
```

2. **Preprocesamiento:**
```bash
python run_pipeline.py --step preprocess
```

3. **Entrenamiento:**
```bash
python run_pipeline.py --step train
```

4. **Evaluación:**
```bash
python run_pipeline.py --step evaluate
```

### Aplicación Web

Una vez entrenado el modelo:
```bash
streamlit run src/app/streamlit_app.py
```

## Estructura del Proyecto

```
proyecto2/
├── Dataset/                    # Archivos Excel con datos
├── src/
│   ├── config.py              # Configuración centralizada
│   ├── data/
│   │   ├── db.py              # Conexión MongoDB
│   │   └── etl.py             # Pipeline de extracción
│   ├── model/
│   │   ├── preprocessing.py   # Preprocesamiento y balanceo
│   │   ├── train.py           # Entrenamiento del modelo
│   │   ├── evaluate.py        # Evaluación y métricas
│   │   └── inference.py       # Inferencia en tiempo real
│   └── app/
│       └── streamlit_app.py   # Interfaz de usuario
├── scripts/                    # Scripts de ejecución paso a paso
│   ├── 01_test_connection.py
│   ├── 02_run_etl.py
│   ├── 03_preprocess.py
│   ├── 04_train.py
│   ├── 05_evaluate.py
│   └── 06_run_app.py
├── models/                     # Modelos entrenados (ignorado en git)
├── reports/                    # Reportes de evaluación
├── notebooks/                  # Notebooks de exploración
├── requirements.txt
├── run_pipeline.py             # Script principal (ejecuta todo)
└── README.md
```

## Tecnologías Utilizadas

- **Python 3.9+**
- **MongoDB Atlas**: Base de datos NoSQL
- **Hugging Face Transformers**: Modelos de lenguaje
- **BETO**: BERT pre-entrenado en español
- **Streamlit**: Interfaz de usuario
- **scikit-learn**: Métricas y evaluación

## Características del Sistema ETL

### 🔍 Detección Inteligente de Datos

El sistema ETL implementa estrategias avanzadas para manejar la heterogeneidad de los datos:

1. **Detección Difusa de Categorías**: 
   - Maneja variaciones: "Areté", "arete", "etiqueta areté"
   - Soporta abreviaciones: "H. y D." → "Humanos y Dioses"
   - Normaliza automáticamente acentos y espacios

2. **Detección de Múltiples Formatos**:
   - **Formato Normal**: Una categoría por hoja (mayoría de archivos)
   - **Formato Multi-Tabla**: Múltiples categorías en paralelo (archivo 4.xlsx)

3. **Búsqueda Inteligente de Encabezados**:
   - Escanea hasta 20 filas para encontrar headers
   - Maneja tablas que no empiezan en A1
   - Detecta columnas: "Canto", "Versos", "Cita" con fuzzy matching

### 📊 Resultados de Extracción

- **123 documentos** extraídos de 7 archivos Excel
- Distribución balanceada:
  - Areté: 42 registros (34%)
  - Política y Poder: 38 registros (31%)
  - Relación Dioses-Humanos: 43 registros (35%)

## Métricas

El modelo debe alcanzar un **F1-Score ≥ 0.80** en el conjunto de prueba para considerarse viable.

## Publicación en Git

### Antes de hacer commit:

1. **Verifica que `.env` NO esté incluido:**
```bash
git status
# .env NO debe aparecer en la lista
```

2. **Archivos que SÍ debes subir:**
   - Todo el código fuente (`src/`, `run_pipeline.py`)
   - `requirements.txt`
   - `README.md`, `.gitignore`
   - `.env.example` (plantilla sin credenciales)
   - Dataset (si es de uso público)
   - Estructura de carpetas (`models/.gitkeep`, etc.)

3. **Archivos que NO debes subir (ya ignorados):**
   - `.env` (contiene credenciales)
   - `venv/` (entorno virtual)
   - `models/` (modelos entrenados son muy pesados)
   - `reports/` (pueden regenerarse)
   - `__pycache__/` (archivos compilados de Python)


## Notas Importantes

- **Modelos entrenados**: Los modelos son muy grandes (>500MB) y no se suben a Git. Cada usuario debe entrenar su propio modelo localmente.
- **Dataset**: Si el dataset es privado o tiene derechos de autor, considera no subirlo y documentar dónde obtenerlo.
- **Credenciales**: NUNCA subas archivos `.env` con credenciales reales.

## Autor

Desarrollado como proyecto académico de IA.
