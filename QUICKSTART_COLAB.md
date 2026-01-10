# ⚡ Quick Start - Google Colab

Entrena tu modelo en **25-30 minutos** usando GPU gratuita.

## 🚀 Pasos Rápidos

### 1. Preparación (5 min)

```bash
# En tu computadora local
cd proyecto2
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/proyecto2.git
git push -u origin main
```

### 2. Abrir en Colab (1 min)

1. Ve a https://colab.research.google.com/
2. **File → Open notebook → GitHub**
3. Pega: `https://github.com/TU_USUARIO/proyecto2`
4. Abre: `colab_setup.ipynb`

### 3. Activar GPU (30 seg)

**Runtime → Change runtime type → GPU → Save**

### 4. Configurar Secrets (2 min)

1. Click en 🔑 (panel izquierdo)
2. Agregar:
   - `MONGO_URI` = tu URI de MongoDB
   - `MONGO_DB_NAME` = `textos_clasicos`
3. Activar acceso

### 5. Ejecutar Todo (25 min)

**Runtime → Run all** ⏯️

O ejecuta celda por celda:
- ✅ Setup (2 min)
- ✅ ETL (1 min)
- ✅ Preprocesamiento (30 seg)
- ✅ **Entrenamiento (20 min)** ⚡
- ✅ Evaluación (2 min)

### 6. Descargar Modelo (1 min)

Ejecuta la última celda para descargar `modelo_entrenado.zip`

---

## 💡 Tips

- Mantén la pestaña abierta durante el entrenamiento
- Descarga el modelo antes de cerrar (se borra al cerrar)
- Los datos quedan en MongoDB (no se borran)

---

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| No GPU | Runtime → Change runtime type → GPU |
| Out of Memory | Reduce batch_size en `src/config.py` |
| Desconexión | Mantén pestaña abierta, usa keep_alive script |

---

## 📊 Tiempos Esperados

| Fase | Tiempo |
|------|--------|
| Setup | 2 min |
| ETL | 1 min |
| Preprocesamiento | 30 seg |
| **Entrenamiento** | **20 min** ⚡ |
| Evaluación | 2 min |
| **TOTAL** | **~25 min** |

vs **2-3 horas en CPU local** 🐌

---

¡Listo! 🎉
