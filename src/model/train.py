"""
Entrenamiento del modelo de clasificación basado en BERT/BETO.
Optimizado para CPU con configuraciones conservadoras.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
from sklearn.metrics import accuracy_score, f1_score
import numpy as np

from src.data.db import get_collection
from src.model.preprocessing import LABEL_MAP, LABEL_NAMES

# Configuración del modelo
MODEL_NAME = "dccuchile/bert-base-spanish-wwm-cased"  # BETO
NUM_LABELS = 3
MAX_LENGTH = 512

# Directorio para guardar modelos
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)


class TextClassificationDataset(Dataset):
    """Dataset personalizado para clasificación de texto."""
    
    def __init__(self, texts, labels, tokenizer, max_length=MAX_LENGTH):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long)
        }


def load_data_from_mongo(collection_name: str):
    """Carga datos de una colección de MongoDB."""
    collection = get_collection(collection_name)
    documents = list(collection.find({}))
    
    texts = [doc["texto"] for doc in documents]
    labels = [doc["label"] for doc in documents]
    
    return texts, labels


def compute_metrics(eval_pred):
    """Calcula métricas de evaluación."""
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    accuracy = accuracy_score(labels, predictions)
    f1_macro = f1_score(labels, predictions, average="macro")
    f1_weighted = f1_score(labels, predictions, average="weighted")
    
    return {
        "accuracy": accuracy,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted
    }


def train_model(
    model_name: str = MODEL_NAME,
    output_dir: str = "models/clasificador_textos",
    num_epochs: int = 5,
    batch_size: int = 8,
    learning_rate: float = 2e-5,
    warmup_steps: int = 100,
    weight_decay: float = 0.01,
    early_stopping_patience: int = 2
) -> Dict:
    """
    Entrena el modelo de clasificación.
    
    Args:
        model_name: Nombre del modelo pre-entrenado (Hugging Face)
        output_dir: Directorio para guardar el modelo
        num_epochs: Número de épocas de entrenamiento
        batch_size: Tamaño del batch
        learning_rate: Tasa de aprendizaje
        warmup_steps: Pasos de warmup
        weight_decay: Decaimiento de pesos
        early_stopping_patience: Épocas sin mejora antes de parar
    
    Returns:
        Diccionario con métricas de entrenamiento
    """
    print("=" * 60)
    print("🤖 Iniciando Entrenamiento del Modelo")
    print("=" * 60)
    
    # Verificar dispositivo
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n💻 Dispositivo: {device}")
    
    if device == "cpu":
        print("   ⚠️ Entrenando en CPU - esto puede tomar tiempo")
        # Reducir configuración para CPU
        batch_size = min(batch_size, 4)
        print(f"   Batch size ajustado a: {batch_size}")
    
    # Cargar datos
    print("\n📥 Cargando datos de MongoDB...")
    train_texts, train_labels = load_data_from_mongo("train_data")
    val_texts, val_labels = load_data_from_mongo("val_data")
    
    print(f"   • Train samples: {len(train_texts)}")
    print(f"   • Val samples: {len(val_texts)}")
    
    # Cargar tokenizer y modelo
    print(f"\n🔧 Cargando modelo: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=NUM_LABELS,
        id2label=LABEL_NAMES,
        label2id=LABEL_MAP
    )
    
    # Crear datasets
    print("\n📦 Preparando datasets...")
    train_dataset = TextClassificationDataset(train_texts, train_labels, tokenizer)
    val_dataset = TextClassificationDataset(val_texts, val_labels, tokenizer)
    
    # Configurar entrenamiento
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        warmup_steps=warmup_steps,
        weight_decay=weight_decay,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        save_total_limit=2,
        report_to="none",  # Desactivar wandb/tensorboard por defecto
        fp16=False,  # Desactivar para CPU
        dataloader_num_workers=0,  # Evitar problemas en Windows
    )
    
    # Crear trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=early_stopping_patience)]
    )
    
    # Entrenar
    print("\n🏋️ Iniciando entrenamiento...")
    print("-" * 40)
    
    train_result = trainer.train()
    
    print("-" * 40)
    print("✅ Entrenamiento completado")
    
    # Evaluar en validación
    print("\n📊 Evaluando modelo...")
    eval_results = trainer.evaluate()
    
    print(f"\n📈 Resultados de validación:")
    print(f"   • Accuracy: {eval_results['eval_accuracy']:.4f}")
    print(f"   • F1 Macro: {eval_results['eval_f1_macro']:.4f}")
    print(f"   • F1 Weighted: {eval_results['eval_f1_weighted']:.4f}")
    
    # Guardar modelo final
    final_model_path = Path(output_dir) / "final"
    print(f"\n💾 Guardando modelo en: {final_model_path}")
    trainer.save_model(str(final_model_path))
    tokenizer.save_pretrained(str(final_model_path))
    
    # Estadísticas
    stats = {
        "model_name": model_name,
        "device": device,
        "train_samples": len(train_texts),
        "val_samples": len(val_texts),
        "num_epochs": num_epochs,
        "batch_size": batch_size,
        "train_loss": train_result.training_loss,
        "eval_accuracy": eval_results["eval_accuracy"],
        "eval_f1_macro": eval_results["eval_f1_macro"],
        "eval_f1_weighted": eval_results["eval_f1_weighted"],
        "model_path": str(final_model_path)
    }
    
    print("\n" + "=" * 60)
    print("✅ Modelo guardado exitosamente")
    print("=" * 60)
    
    return stats


if __name__ == "__main__":
    stats = train_model()
    print(f"\nF1-Score obtenido: {stats['eval_f1_macro']:.4f}")
