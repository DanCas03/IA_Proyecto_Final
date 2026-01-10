# 📚 Índice de Documentación

Guía completa de todos los documentos del proyecto.

---

## 🚀 Para Empezar

### Nuevos Usuarios
1. **[README.md](README.md)** - Guía principal paso a paso (Local)
2. **[QUICKSTART_COLAB.md](QUICKSTART_COLAB.md)** - Inicio rápido en Google Colab ⚡
3. **[COMPARATIVA_OPCIONES.md](COMPARATIVA_OPCIONES.md)** - ¿Local o Colab?

### Usuarios de Google Colab
1. **[QUICKSTART_COLAB.md](QUICKSTART_COLAB.md)** - Quick start (5 min)
2. **[GUIA_COLAB.md](GUIA_COLAB.md)** - Guía completa y detallada
3. **[colab_setup.ipynb](colab_setup.ipynb)** - Notebook ejecutable

---

## 📖 Documentación por Tema

### Configuración Inicial
- **[README.md#configuración-inicial](README.md#-fase-1-configuración-inicial)** - Setup local
- **[GUIA_COLAB.md#preparación](GUIA_COLAB.md#1-preparación-5-min)** - Setup Colab

### Extracción de Datos (ETL)
- **[README.md#migración-de-datos](README.md#-fase-2-migración-de-datos-etl)** - Pipeline ETL
- **[Notas.md#características-del-sistema-etl](Notas.md)** - Detalles técnicos

### Entrenamiento
- **[README.md#entrenamiento-del-modelo](README.md#-fase-4-entrenamiento-del-modelo)** - Local
- **[GUIA_COLAB.md#entrenamiento](GUIA_COLAB.md)** - Con GPU en Colab

### Evaluación
- **[README.md#evaluación](README.md#-fase-5-evaluación)** - Métricas y reportes

### Aplicación Web
- **[README.md#aplicación-web](README.md#-fase-6-aplicación-web)** - Streamlit

### Solución de Problemas
- **[README.md#solución-de-problemas](README.md#-solución-de-problemas)** - Troubleshooting local
- **[GUIA_COLAB.md#solución-de-problemas](GUIA_COLAB.md#-solución-de-problemas-en-colab)** - Troubleshooting Colab

---

## 🎯 Por Objetivo

### "Quiero entrenar lo más rápido posible"
→ **[QUICKSTART_COLAB.md](QUICKSTART_COLAB.md)** (25 min)

### "Quiero entender todo el proceso"
→ **[README.md](README.md)** + **[GUIA_COLAB.md](GUIA_COLAB.md)**

### "¿Qué opción me conviene?"
→ **[COMPARATIVA_OPCIONES.md](COMPARATIVA_OPCIONES.md)**

### "Quiero ver el código"
→ **[src/](src/)** + **[scripts/](scripts/)**

### "Necesito un resumen ejecutivo"
→ **[RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)**

---

## 📁 Archivos Técnicos

### Código Fuente
```
src/
├── config.py              # Configuración
├── data/
│   ├── db.py             # MongoDB
│   └── etl.py            # ETL
├── model/
│   ├── preprocessing.py  # Preprocesamiento
│   ├── train.py          # Entrenamiento
│   ├── evaluate.py       # Evaluación
│   └── inference.py      # Predicción
└── app/
    └── streamlit_app.py  # UI
```

### Scripts
```
scripts/
├── 01_test_connection.py  # Test MongoDB
├── 02_run_etl.py          # ETL
├── 03_preprocess.py       # Preprocesar
├── 04_train.py            # Entrenar
├── 05_evaluate.py         # Evaluar
└── 06_run_app.py          # App
```

### Notebooks
- **[colab_setup.ipynb](colab_setup.ipynb)** - Pipeline completo en Colab

---

## 🔧 Configuración

### Archivos de Configuración
- **[requirements.txt](requirements.txt)** - Dependencias Python
- **[.env.example](.env.example)** - Plantilla de variables de entorno
- **[.gitignore](.gitignore)** - Archivos ignorados por Git
- **[.gitattributes](.gitattributes)** - Configuración Git LFS

### Archivos de Proyecto
- **[proyecto.txt](proyecto.txt)** - Especificaciones originales
- **[Notas.md](Notas.md)** - Información técnica adicional

---

## 📊 Reportes y Resultados

### Generados Automáticamente
```
reports/
├── confusion_matrix.png      # Matriz de confusión
├── metrics_by_class.png      # Métricas por clase
└── evaluation_report.json    # Reporte completo
```

---

## 🎓 Por Nivel de Experiencia

### Principiante
1. **[QUICKSTART_COLAB.md](QUICKSTART_COLAB.md)** - Más fácil
2. **[GUIA_COLAB.md](GUIA_COLAB.md)** - Paso a paso
3. **[colab_setup.ipynb](colab_setup.ipynb)** - Ejecutar

### Intermedio
1. **[README.md](README.md)** - Setup local
2. **[COMPARATIVA_OPCIONES.md](COMPARATIVA_OPCIONES.md)** - Decidir
3. **[Código fuente](src/)** - Explorar

### Avanzado
1. **[src/](src/)** - Código completo
2. **[src/config.py](src/config.py)** - Configuración
3. **[RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)** - Overview técnico

---

## 🔍 Búsqueda Rápida

### Por Palabra Clave

**MongoDB**
- Setup: [README.md#configurar-mongodb](README.md)
- Conexión: [src/data/db.py](src/data/db.py)
- Troubleshooting: [README.md#error-de-conexión](README.md)

**ETL**
- Guía: [README.md#fase-2](README.md)
- Código: [src/data/etl.py](src/data/etl.py)
- Script: [scripts/02_run_etl.py](scripts/02_run_etl.py)

**Entrenamiento**
- Local: [README.md#fase-4](README.md)
- Colab: [GUIA_COLAB.md](GUIA_COLAB.md)
- Código: [src/model/train.py](src/model/train.py)

**GPU / Colab**
- Quick Start: [QUICKSTART_COLAB.md](QUICKSTART_COLAB.md)
- Guía completa: [GUIA_COLAB.md](GUIA_COLAB.md)
- Notebook: [colab_setup.ipynb](colab_setup.ipynb)

**Streamlit / App**
- Guía: [README.md#fase-6](README.md)
- Código: [src/app/streamlit_app.py](src/app/streamlit_app.py)
- Script: [scripts/06_run_app.py](scripts/06_run_app.py)

---

## 📞 Ayuda

### ¿No encuentras algo?
1. Usa Ctrl+F en este documento
2. Revisa el [README.md](README.md)
3. Consulta [RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)

### ¿Tienes un error?
1. [README.md#solución-de-problemas](README.md#-solución-de-problemas)
2. [GUIA_COLAB.md#solución-de-problemas](GUIA_COLAB.md#-solución-de-problemas-en-colab)

---

## 🗺️ Mapa del Proyecto

```
Documentación
├── README.md                    ⭐ Guía principal
├── QUICKSTART_COLAB.md          ⚡ Inicio rápido
├── GUIA_COLAB.md               📖 Guía Colab completa
├── COMPARATIVA_OPCIONES.md      ⚖️ Local vs Colab
├── RESUMEN_PROYECTO.md          📊 Resumen ejecutivo
├── INDICE_DOCUMENTACION.md      📚 Este archivo
└── Notas.md                     📝 Info técnica

Notebooks
└── colab_setup.ipynb            💻 Notebook Colab

Código
├── src/                         🔧 Código fuente
├── scripts/                     📜 Scripts ejecución
└── run_pipeline.py              🚀 Pipeline maestro

Configuración
├── requirements.txt             📦 Dependencias
├── .env.example                 🔐 Plantilla env
├── .gitignore                   🚫 Git ignore
└── .gitattributes              📁 Git LFS
```

---

✅ **Toda la documentación está completa y organizada**
