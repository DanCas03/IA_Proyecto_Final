"""
Preprocesamiento y balanceo de datos para entrenamiento.
Lee datos de MongoDB y genera conjuntos balanceados.
"""

import re
from typing import Dict, List, Tuple
from collections import Counter
import random
from sklearn.model_selection import train_test_split
from src.data.db import get_collection, clear_collection

# Mapeo de categorías a IDs numéricos
LABEL_MAP = {
    "arete": 0,
    "politica_poder": 1,
    "dioses_hombres": 2
}

LABEL_NAMES = {v: k for k, v in LABEL_MAP.items()}


def clean_text(text: str) -> str:
    """
    Limpia y normaliza el texto para el modelo.
    
    Args:
        text: Texto crudo
    
    Returns:
        Texto limpio
    """
    if not isinstance(text, str):
        return ""
    
    # Eliminar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar caracteres de control
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Trim
    text = text.strip()
    
    return text


def get_category_distribution() -> Dict[str, int]:
    """Obtiene la distribución de categorías en raw_texts."""
    collection = get_collection("raw_texts")
    pipeline = [
        {"$group": {"_id": "$categoria", "count": {"$sum": 1}}}
    ]
    result = list(collection.aggregate(pipeline))
    return {item["_id"]: item["count"] for item in result}


def balance_by_undersampling(documents: List[Dict]) -> List[Dict]:
    """
    Balancea las clases mediante subsampling de la clase mayoritaria.
    
    Args:
        documents: Lista de documentos con campo 'categoria'
    
    Returns:
        Lista balanceada de documentos
    """
    # Agrupar por categoría
    by_category = {}
    for doc in documents:
        cat = doc["categoria"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(doc)
    
    # Encontrar el mínimo
    min_count = min(len(docs) for docs in by_category.values())
    
    # Subsamplear cada categoría
    balanced = []
    for cat, docs in by_category.items():
        sampled = random.sample(docs, min_count)
        balanced.extend(sampled)
    
    # Mezclar
    random.shuffle(balanced)
    
    return balanced


def balance_by_oversampling(documents: List[Dict]) -> List[Dict]:
    """
    Balancea las clases mediante oversampling de las clases minoritarias.
    
    Args:
        documents: Lista de documentos con campo 'categoria'
    
    Returns:
        Lista balanceada de documentos
    """
    # Agrupar por categoría
    by_category = {}
    for doc in documents:
        cat = doc["categoria"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(doc)
    
    # Encontrar el máximo
    max_count = max(len(docs) for docs in by_category.values())
    
    # Oversamplear cada categoría
    balanced = []
    for cat, docs in by_category.items():
        if len(docs) < max_count:
            # Duplicar documentos hasta alcanzar max_count
            oversampled = docs.copy()
            while len(oversampled) < max_count:
                oversampled.extend(random.sample(docs, min(len(docs), max_count - len(oversampled))))
            balanced.extend(oversampled[:max_count])
        else:
            balanced.extend(docs)
    
    # Mezclar
    random.shuffle(balanced)
    
    return balanced


def preprocess_and_balance(
    balance_strategy: str = "undersample",
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42
) -> Dict:
    """
    Pipeline completo de preprocesamiento y balanceo.
    
    Args:
        balance_strategy: "undersample" o "oversample"
        test_size: Proporción para conjunto de prueba
        val_size: Proporción para conjunto de validación
        random_state: Semilla para reproducibilidad
    
    Returns:
        Estadísticas del proceso
    """
    random.seed(random_state)
    
    print("=" * 60)
    print("🔄 Iniciando Preprocesamiento y Balanceo")
    print("=" * 60)
    
    # Obtener datos crudos
    raw_collection = get_collection("raw_texts")
    documents = list(raw_collection.find({}))
    
    print(f"\n📥 Documentos cargados: {len(documents)}")
    
    # Distribución inicial
    initial_dist = Counter(doc["categoria"] for doc in documents)
    print(f"\n📊 Distribución inicial:")
    for cat, count in initial_dist.items():
        print(f"   • {cat}: {count}")
    
    # Limpiar textos
    print("\n🧹 Limpiando textos...")
    for doc in documents:
        doc["texto_limpio"] = clean_text(doc["texto"])
    
    # Filtrar documentos sin texto válido
    documents = [d for d in documents if len(d["texto_limpio"]) > 10]
    print(f"   Documentos válidos después de limpieza: {len(documents)}")
    
    # Balancear
    print(f"\n⚖️ Aplicando estrategia de balanceo: {balance_strategy}")
    if balance_strategy == "undersample":
        balanced_docs = balance_by_undersampling(documents)
        justification = (
            "Se eligió undersampling para evitar overfitting en clases minoritarias "
            "y mantener la diversidad natural de los datos."
        )
    else:
        balanced_docs = balance_by_oversampling(documents)
        justification = (
            "Se eligió oversampling para maximizar la cantidad de datos de entrenamiento "
            "sin perder información de ninguna clase."
        )
    
    balanced_dist = Counter(doc["categoria"] for doc in balanced_docs)
    print(f"\n📊 Distribución después de balanceo:")
    for cat, count in balanced_dist.items():
        print(f"   • {cat}: {count}")
    print(f"\n📝 Justificación: {justification}")
    
    # Preparar datos para split
    texts = [doc["texto_limpio"] for doc in balanced_docs]
    labels = [LABEL_MAP[doc["categoria"]] for doc in balanced_docs]
    
    # Split estratificado
    print(f"\n✂️ Dividiendo datos (train={1-test_size-val_size:.0%}, val={val_size:.0%}, test={test_size:.0%})...")
    
    # Primero separar test
    X_temp, X_test, y_temp, y_test = train_test_split(
        texts, labels, 
        test_size=test_size, 
        stratify=labels, 
        random_state=random_state
    )
    
    # Luego separar validation del resto
    val_ratio = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=val_ratio,
        stratify=y_temp,
        random_state=random_state
    )
    
    print(f"   • Train: {len(X_train)} samples")
    print(f"   • Val: {len(X_val)} samples")
    print(f"   • Test: {len(X_test)} samples")
    
    # Guardar en MongoDB
    print("\n💾 Guardando conjuntos en MongoDB...")
    
    # Limpiar colecciones existentes
    for col_name in ["processed_texts", "train_data", "val_data", "test_data"]:
        clear_collection(col_name)
    
    # Guardar datos procesados completos
    processed_collection = get_collection("processed_texts")
    processed_docs = [
        {"texto": t, "label": l, "categoria": LABEL_NAMES[l]}
        for t, l in zip(texts, labels)
    ]
    processed_collection.insert_many(processed_docs)
    
    # Guardar splits
    def save_split(collection_name: str, X: List[str], y: List[int]):
        collection = get_collection(collection_name)
        docs = [
            {"texto": t, "label": l, "categoria": LABEL_NAMES[l]}
            for t, l in zip(X, y)
        ]
        if docs:
            collection.insert_many(docs)
    
    save_split("train_data", X_train, y_train)
    save_split("val_data", X_val, y_val)
    save_split("test_data", X_test, y_test)
    
    print("   ✓ Datos guardados exitosamente")
    
    # Estadísticas finales
    stats = {
        "initial_count": len(documents),
        "initial_distribution": dict(initial_dist),
        "balanced_count": len(balanced_docs),
        "balanced_distribution": dict(balanced_dist),
        "balance_strategy": balance_strategy,
        "justification": justification,
        "train_count": len(X_train),
        "val_count": len(X_val),
        "test_count": len(X_test)
    }
    
    print("\n" + "=" * 60)
    print("✅ Preprocesamiento completado")
    print("=" * 60)
    
    return stats


if __name__ == "__main__":
    stats = preprocess_and_balance(balance_strategy="undersample")
