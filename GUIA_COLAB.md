# 🚀 Guía para Usar Google Colab

Esta guía te explica cómo entrenar el modelo usando la **GPU gratuita de Google Colab**, ideal si no tienes una GPU potente en tu computadora local.

## 🎯 Ventajas de Usar Colab

- ✅ **GPU gratuita** (Tesla T4 o similar)
- ✅ **Entrenamiento 10-20x más rápido** que en CPU
- ✅ **No consume recursos locales**
- ✅ **Sin instalación** de dependencias pesadas
- ✅ **Acceso desde cualquier lugar**

---

## 📋 Requisitos Previos

1. **Cuenta de Google** (Gmail)
2. **Repositorio en GitHub** con tu código
3. **MongoDB Atlas** configurado (cluster activo)
4. **Datos en el repositorio** (carpeta `Dataset/`)

---

## 🚀 Método 1: Usar el Notebook Completo (Recomendado)

### Paso 1: Subir el Código a GitHub

```powershell
# En tu computadora local
cd C:\Users\danie\Documents\code\Proyects\IA\proyecto2

# Inicializar git (si no lo has hecho)
git init
git add .
git commit -m "Initial commit"

# Conectar con GitHub
git remote add origin https://github.com/TU_USUARIO/proyecto2.git
git push -u origin main
```

### Paso 2: Abrir el Notebook en Colab

1. Ve a [Google Colab](https://colab.research.google.com/)
2. Haz clic en **File → Open notebook**
3. Selecciona la pestaña **GitHub**
4. Pega la URL de tu repositorio: `https://github.com/TU_USUARIO/proyecto2`
5. Selecciona el archivo `colab_setup.ipynb`

### Paso 3: Activar GPU

1. En Colab, ve a **Runtime → Change runtime type**
2. En **Hardware accelerator**, selecciona **GPU**
3. Haz clic en **Save**

### Paso 4: Configurar Credenciales (Seguro)

1. Haz clic en el ícono de **🔑 (llave)** en el panel izquierdo
2. Agrega dos secretos:
   - **Nombre:** `MONGO_URI`
   - **Valor:** Tu URI completa de MongoDB Atlas
   
   - **Nombre:** `MONGO_DB_NAME`
   - **Valor:** `textos_clasicos`

3. Activa el **notebook access** para cada secreto

### Paso 5: Ejecutar el Pipeline

Ejecuta las celdas **una por una** en orden:

1. ✅ Verificar GPU
2. ✅ Clonar repositorio
3. ✅ Instalar dependencias
4. ✅ Configurar credenciales
5. ✅ Test de conexión
6. ✅ ETL (1-2 min)
7. ✅ Preprocesamiento (30 seg)
8. ✅ **Entrenamiento (15-30 min con GPU)** ⚡
9. ✅ Evaluación (2-3 min)
10. ✅ Probar el modelo

### Paso 6: Descargar el Modelo

Al final del notebook, ejecuta la celda de descarga:

```python
!zip -r modelo_entrenado.zip models/clasificador_textos/final/
from google.colab import files
files.download('modelo_entrenado.zip')
```

Descomprime el archivo en tu carpeta `models/` local para usar la app Streamlit.

---

## 🔧 Método 2: Ejecutar Scripts Individuales

Si prefieres más control, puedes ejecutar cada script por separado:

### Setup Inicial

```python
# Celda 1: Verificar GPU
!nvidia-smi

# Celda 2: Clonar repo
!git clone https://github.com/TU_USUARIO/proyecto2.git
%cd proyecto2

# Celda 3: Instalar dependencias
!pip install -q -r requirements.txt

# Celda 4: Configurar credenciales
from google.colab import userdata
import os

os.environ['MONGO_URI'] = userdata.get('MONGO_URI')
os.environ['MONGO_DB_NAME'] = userdata.get('MONGO_DB_NAME')

with open('.env', 'w') as f:
    f.write(f"MONGO_URI={os.environ['MONGO_URI']}\\n")
    f.write(f"MONGO_DB_NAME={os.environ['MONGO_DB_NAME']}\\n")
```

### Pipeline

```python
# Test conexión
!python scripts/01_test_connection.py

# ETL
!python scripts/02_run_etl.py

# Preprocesamiento
!python scripts/03_preprocess.py

# Entrenamiento (con GPU)
!python scripts/04_train.py

# Evaluación
!python scripts/05_evaluate.py
```

---

## 📊 Comparación de Tiempos

| Fase | CPU Local | GPU Colab | Diferencia |
|------|-----------|-----------|------------|
| ETL | 1-2 min | 1-2 min | Igual |
| Preprocesamiento | 30 seg | 30 seg | Igual |
| **Entrenamiento** | **1-3 horas** | **15-30 min** | **10-20x más rápido** ⚡ |
| Evaluación | 2-3 min | 1-2 min | 2x más rápido |
| **TOTAL** | **~2 horas** | **~25 min** | **5x más rápido** |

---

## 🎨 Usar la App Streamlit Después

Una vez descargado el modelo:

1. Descomprime `modelo_entrenado.zip` en tu carpeta `models/` local
2. Ejecuta la app:

```powershell
streamlit run src/app/streamlit_app.py
```

---

## ⚠️ Limitaciones de Colab

1. **Tiempo de sesión**: ~12 horas máximo
2. **Desconexión por inactividad**: ~90 minutos
3. **Archivos temporales**: Se borran al cerrar la sesión
4. **Solución**: Descarga el modelo antes de cerrar

---

## 💡 Consejos y Trucos

### 1. Mantener la Sesión Activa

Ejecuta este código en una celda para evitar desconexiones:

```python
import time
from IPython.display import Javascript

def keep_alive():
    display(Javascript('''
        function KeepClicking(){
            console.log("Clicking");
            document.querySelector("colab-toolbar-button#connect").click()
        }
        setInterval(KeepClicking, 60000)
    '''))

keep_alive()
```

### 2. Monitorear el Uso de GPU

```python
# Ver uso de memoria GPU
!nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

### 3. Guardar Checkpoints en Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')

# Copiar modelo a Drive
!cp -r models/clasificador_textos/final /content/drive/MyDrive/modelo_textos_clasicos
```

### 4. Reanudar Entrenamiento Interrumpido

Si se desconecta durante el entrenamiento:

1. Vuelve a ejecutar las celdas de setup
2. El modelo guardará checkpoints automáticamente
3. Continúa desde donde se quedó

---

## 🐛 Solución de Problemas en Colab

### Problema: "No GPU available"

**Solución:**
- Runtime → Change runtime type → GPU → Save
- Si sigue sin funcionar, espera unos minutos (límite de uso alcanzado)

### Problema: "Out of Memory"

**Solución:**
```python
# Reducir batch size en src/config.py
"batch_size_gpu": 4,  # Reducir de 8 a 4
```

### Problema: Desconexión durante entrenamiento

**Solución:**
- Usa el script de keep_alive
- Mantén la pestaña abierta
- Guarda checkpoints en Drive

### Problema: "Module not found"

**Solución:**
```python
!pip install -q [nombre_del_modulo]
```

---

## 📝 Checklist de Ejecución en Colab

- [ ] Código subido a GitHub
- [ ] GPU activada en Colab
- [ ] Credenciales configuradas en Secrets
- [ ] Repositorio clonado
- [ ] Dependencias instaladas
- [ ] Conexión a MongoDB verificada
- [ ] ETL ejecutado (123 docs)
- [ ] Preprocesamiento completado
- [ ] Entrenamiento finalizado (F1 ≥ 0.80)
- [ ] Evaluación generada
- [ ] Modelo descargado
- [ ] Modelo descomprimido localmente

---

## 🎓 Recursos Adicionales

- [Documentación de Google Colab](https://colab.research.google.com/notebooks/intro.ipynb)
- [Límites y Restricciones de Colab](https://research.google.com/colaboratory/faq.html)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [MongoDB Atlas](https://docs.atlas.mongodb.com/)

---

## 🎉 ¡Listo!

Ahora puedes entrenar tu modelo de forma rápida y gratuita usando Google Colab. El proceso completo toma aproximadamente **25-30 minutos** en lugar de 2-3 horas en CPU local.

¡Disfruta de la velocidad de la GPU! ⚡
