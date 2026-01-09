"""
Evaluación exhaustiva del modelo entrenado.
Genera matriz de confusión y métricas detalladas.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)
import matplotlib.pyplot as plt
import seaborn as sns

from src.data.db import get_collection
from src.model.preprocessing import LABEL_MAP, LABEL_NAMES

# Configuración
MODEL_PATH = Path("models/clasificador_textos/final")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def load_model_and_tokenizer(model_path: Path = MODEL_PATH):
    """Carga el modelo entrenado y su tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    return model, tokenizer, device


def predict_batch(
    texts: List[str],
    model,
    tokenizer,
    device: str,
    batch_size: int = 16,
    max_length: int = 512
) -> Tuple[List[int], List[List[float]]]:
    """
    Realiza predicciones en lotes.
    
    Args:
        texts: Lista de textos a clasificar
        model: Modelo cargado
        tokenizer: Tokenizer
        device: Dispositivo (cuda/cpu)
        batch_size: Tamaño del lote
        max_length: Longitud máxima de tokens
    
    Returns:
        Tuple (predicciones, probabilidades)
    """
    all_predictions = []
    all_probabilities = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        
        encodings = tokenizer(
            batch_texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        
        encodings = {k: v.to(device) for k, v in encodings.items()}
        
        with torch.no_grad():
            outputs = model(**encodings)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            preds = torch.argmax(logits, dim=-1)
        
        all_predictions.extend(preds.cpu().numpy().tolist())
        all_probabilities.extend(probs.cpu().numpy().tolist())
    
    return all_predictions, all_probabilities


def plot_confusion_matrix(
    y_true: List[int],
    y_pred: List[int],
    labels: List[str],
    save_path: Path
):
    """Genera y guarda la matriz de confusión."""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        annot_kws={"size": 14}
    )
    plt.title("Matriz de Confusión", fontsize=16, fontweight="bold")
    plt.xlabel("Predicción", fontsize=12)
    plt.ylabel("Valor Real", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    print(f"   📊 Matriz de confusión guardada: {save_path}")


def plot_metrics_by_class(
    report_dict: Dict,
    labels: List[str],
    save_path: Path
):
    """Genera gráfico de métricas por clase."""
    metrics = ["precision", "recall", "f1-score"]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, metric in enumerate(metrics):
        values = [report_dict[label][metric] for label in labels]
        
        ax = axes[idx]
        bars = ax.bar(labels, values, color=["#3498db", "#e74c3c", "#2ecc71"])
        ax.set_title(f"{metric.capitalize()}", fontsize=14, fontweight="bold")
        ax.set_ylim(0, 1)
        ax.axhline(y=0.8, color="orange", linestyle="--", label="Umbral (0.8)")
        
        # Añadir valores sobre las barras
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f"{val:.3f}",
                ha="center",
                fontsize=10
            )
        
        ax.tick_params(axis="x", rotation=45)
    
    plt.suptitle("Métricas por Categoría", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    print(f"   📈 Gráfico de métricas guardado: {save_path}")


def evaluate_model(model_path: Path = MODEL_PATH) -> Dict:
    """
    Evalúa el modelo sobre el conjunto de test.
    
    Args:
        model_path: Ruta al modelo entrenado
    
    Returns:
        Diccionario con todas las métricas
    """
    print("=" * 60)
    print("📊 Evaluación del Modelo")
    print("=" * 60)
    
    # Cargar modelo
    print(f"\n🔧 Cargando modelo desde: {model_path}")
    model, tokenizer, device = load_model_and_tokenizer(model_path)
    print(f"   Dispositivo: {device}")
    
    # Cargar datos de test
    print("\n📥 Cargando datos de test desde MongoDB...")
    collection = get_collection("test_data")
    documents = list(collection.find({}))
    
    texts = [doc["texto"] for doc in documents]
    y_true = [doc["label"] for doc in documents]
    
    print(f"   Muestras de test: {len(texts)}")
    
    # Realizar predicciones
    print("\n🔮 Generando predicciones...")
    y_pred, probabilities = predict_batch(texts, model, tokenizer, device)
    
    # Calcular métricas
    print("\n📈 Calculando métricas...")
    
    accuracy = accuracy_score(y_true, y_pred)
    precision_macro = precision_score(y_true, y_pred, average="macro")
    recall_macro = recall_score(y_true, y_pred, average="macro")
    f1_macro = f1_score(y_true, y_pred, average="macro")
    f1_weighted = f1_score(y_true, y_pred, average="weighted")
    
    # Nombres de categorías
    label_names = [LABEL_NAMES[i] for i in range(len(LABEL_NAMES))]
    
    # Reporte de clasificación
    report = classification_report(
        y_true, y_pred,
        target_names=label_names,
        output_dict=True
    )
    
    report_text = classification_report(
        y_true, y_pred,
        target_names=label_names
    )
    
    # Mostrar resultados
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DE EVALUACIÓN")
    print("=" * 60)
    print(f"\n🎯 Métricas Globales:")
    print(f"   • Accuracy: {accuracy:.4f}")
    print(f"   • Precision (macro): {precision_macro:.4f}")
    print(f"   • Recall (macro): {recall_macro:.4f}")
    print(f"   • F1-Score (macro): {f1_macro:.4f}")
    print(f"   • F1-Score (weighted): {f1_weighted:.4f}")
    
    # Verificar criterio de aceptación
    print("\n" + "-" * 40)
    if f1_macro >= 0.8:
        print(f"✅ CRITERIO CUMPLIDO: F1-Score ({f1_macro:.4f}) ≥ 0.80")
    else:
        print(f"⚠️ CRITERIO NO CUMPLIDO: F1-Score ({f1_macro:.4f}) < 0.80")
    print("-" * 40)
    
    print(f"\n📋 Reporte por Clase:\n")
    print(report_text)
    
    # Generar visualizaciones
    print("\n🎨 Generando visualizaciones...")
    
    plot_confusion_matrix(
        y_true, y_pred,
        label_names,
        REPORTS_DIR / "confusion_matrix.png"
    )
    
    plot_metrics_by_class(
        report,
        label_names,
        REPORTS_DIR / "metrics_by_class.png"
    )
    
    # Guardar reporte JSON
    results = {
        "test_samples": len(texts),
        "accuracy": accuracy,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "meets_criteria": f1_macro >= 0.8,
        "classification_report": report
    }
    
    report_path = REPORTS_DIR / "evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado: {report_path}")
    
    print("\n" + "=" * 60)
    print("✅ Evaluación completada")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    results = evaluate_model()
