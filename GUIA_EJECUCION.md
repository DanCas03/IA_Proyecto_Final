# Guía de Ejecución Paso a Paso

Esta guía te llevará a través de todo el proceso, desde la configuración inicial hasta tener la aplicación funcionando.

## 📋 Requisitos Previos

- ✅ Python 3.9+ instalado
- ✅ MongoDB Atlas cluster activo
- ✅ 8GB RAM mínimo
- ✅ Espacio en disco: ~2GB (modelos + datos)

## 🚀 Fase 1: Configuración Inicial

### 1. Preparar el Entorno

```powershell
# Navegar al directorio del proyecto
cd C:\Users\danie\Documents\code\Proyects\IA\proyecto2

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

## 📞 Ayuda Adicional

Si encuentras problemas:
1. Revisa esta guía
2. Ejecuta scripts con `--debug` cuando esté disponible
3. Revisa los logs de error completos
4. Consulta la documentación de las librerías (Hugging Face, PyTorch)

¡Éxito con tu proyecto! 🎉
