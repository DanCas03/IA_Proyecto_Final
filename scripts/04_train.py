"""
Script 04: Entrenamiento del modelo.
Fine-tuning de BETO para clasificación de textos.

⚠️ NOTA: Este proceso puede tardar varias horas en CPU.
"""

import sys
import os
from pathlib import Path

# Configurar UTF-8 para Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from src.data.db import get_collection

def check_prerequisites():
    """Verifica que hay datos para entrenar."""
    print("\n[1/3] Verificando prerrequisitos...")
    
    # Verificar datos de entrenamiento
    train_col = get_collection("train_data")
    train_count = train_col.count_documents({})
    
    val_col = get_collection("val_data")
    val_count = val_col.count_documents({})
    
    if train_count == 0 or val_count == 0:
        print("\n❌ ERROR: No hay datos de entrenamiento/validación")
        print("   Ejecuta primero: python scripts/03_preprocess.py")
        sys.exit(1)
    
    print(f"   ✓ Datos de entrenamiento: {train_count}")
    print(f"   ✓ Datos de validación: {val_count}")
    
    # Verificar hardware
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"   ✓ Dispositivo: {device}")
    
    if device == "cpu":
        print("\n   ⚠️ ADVERTENCIA: Entrenando en CPU")
        print("   El proceso puede tardar 1-3 horas dependiendo de tu hardware.")
        print("   Considera usar Google Colab con GPU si tienes problemas.")
    
    return train_count, val_count, device


def main():
    print("=" * 60)
    print("🤖 ENTRENAMIENTO DEL MODELO")
    print("=" * 60)
    
    # Verificar prerrequisitos
    train_count, val_count, device = check_prerequisites()
    
    # Configuración
    print("\n[2/3] Configuración de entrenamiento:")
    config = {
        "model_name": "dccuchile/bert-base-spanish-wwm-cased",
        "num_epochs": 5,
        "batch_size": 4 if device == "cpu" else 8,
        "learning_rate": 2e-5,
        "output_dir": "models/clasificador_textos"
    }
    
    for key, value in config.items():
        print(f"   • {key}: {value}")
    
    # Entrenar
    print("\n[3/3] Iniciando entrenamiento...")
    print("-" * 40)
    
    try:
        from src.model.train import train_model
        
        stats = train_model(
            model_name=config["model_name"],
            output_dir=config["output_dir"],
            num_epochs=config["num_epochs"],
            batch_size=config["batch_size"],
            learning_rate=config["learning_rate"]
        )
        
        print("\n" + "=" * 60)
        print("✅ ENTRENAMIENTO COMPLETADO")
        print("=" * 60)
        print(f"\n📈 Resultados:")
        print(f"   • Loss final: {stats['train_loss']:.4f}")
        print(f"   • Accuracy (val): {stats['eval_accuracy']:.4f}")
        print(f"   • F1 Macro (val): {stats['eval_f1_macro']:.4f}")
        print(f"   • Modelo guardado en: {stats['model_path']}")
        
        # Verificar criterio
        if stats['eval_f1_macro'] >= 0.8:
            print(f"\n🎉 ¡CRITERIO CUMPLIDO! F1 = {stats['eval_f1_macro']:.4f} >= 0.80")
        else:
            print(f"\n⚠️ F1 = {stats['eval_f1_macro']:.4f} < 0.80")
            print("   Considera ajustar hiperparámetros o revisar los datos.")
        
        print("\nPuedes continuar con: python scripts/05_evaluate.py")
        
    except Exception as e:
        print(f"\n❌ ERROR durante entrenamiento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
