"""
Configuración centralizada del proyecto.
"""

from pathlib import Path

# ============================================
# RUTAS DEL PROYECTO
# ============================================
PROJECT_ROOT = Path(__file__).parent.parent
DATASET_DIR = PROJECT_ROOT / "Dataset"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# ============================================
# CONFIGURACIÓN DEL MODELO
# ============================================
MODEL_CONFIG = {
    # Modelo base (BETO - BERT en español)
    "model_name": "dccuchile/bert-base-spanish-wwm-cased",
    
    # Alternativas:
    # "model_name": "bert-base-multilingual-cased",  # Multilingüe
    # "model_name": "xlm-roberta-base",  # XLM-RoBERTa
    
    # Hiperparámetros de entrenamiento
    "num_epochs": 5,
    "batch_size_gpu": 8,
    "batch_size_cpu": 4,
    "learning_rate": 2e-5,
    "warmup_steps": 100,
    "weight_decay": 0.01,
    "max_length": 512,
    
    # Early stopping
    "early_stopping_patience": 2,
    
    # Directorio de salida
    "output_dir": str(MODELS_DIR / "clasificador_textos"),
}

# ============================================
# CONFIGURACIÓN DE DATOS
# ============================================
DATA_CONFIG = {
    # Estrategia de balanceo: "undersample" o "oversample"
    "balance_strategy": "undersample",
    
    # Proporciones de split
    "test_size": 0.15,
    "val_size": 0.15,
    
    # Semilla para reproducibilidad
    "random_state": 42,
}

# ============================================
# CATEGORÍAS
# ============================================
CATEGORIES = {
    "arete": {
        "id": 0,
        "display_name": "Areté",
        "description": "Excelencia y virtud moral. La búsqueda de la perfección del carácter.",
        "color": "#50fa7b"
    },
    "politica_poder": {
        "id": 1,
        "display_name": "Política y Poder",
        "description": "Reflexiones sobre gobierno, autoridad y estructuras de poder.",
        "color": "#ff79c6"
    },
    "dioses_hombres": {
        "id": 2,
        "display_name": "Relación Dioses-Humanos",
        "description": "Interacciones entre lo divino y lo mortal, destino y piedad.",
        "color": "#8be9fd"
    }
}

# Mapeos útiles
LABEL_MAP = {cat: info["id"] for cat, info in CATEGORIES.items()}
LABEL_NAMES = {info["id"]: cat for cat, info in CATEGORIES.items()}
ID_TO_DISPLAY = {info["id"]: info["display_name"] for cat, info in CATEGORIES.items()}

# ============================================
# MONGODB
# ============================================
MONGO_CONFIG = {
    "db_name": "textos_clasicos",
    "collections": {
        "raw_texts": "raw_texts",
        "processed_texts": "processed_texts",
        "train_data": "train_data",
        "val_data": "val_data",
        "test_data": "test_data",
    }
}

# ============================================
# CRITERIO DE ACEPTACIÓN
# ============================================
ACCEPTANCE_CRITERIA = {
    "min_f1_score": 0.80,
    "metric": "f1_macro"
}
