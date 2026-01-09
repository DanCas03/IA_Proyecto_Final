"""
Script principal para ejecutar el pipeline completo.
Desde extracción de datos hasta entrenamiento y evaluación.
"""

import argparse
import sys
from pathlib import Path

def run_etl():
    """Ejecuta el pipeline ETL."""
    print("\n" + "=" * 70)
    print("FASE 1: EXTRACCIÓN Y CARGA DE DATOS (ETL)")
    print("=" * 70)
    
    from src.data.db import test_connection, init_database
    from src.data.etl import run_etl_pipeline
    
    # Verificar conexión
    if not test_connection():
        print("❌ No se pudo conectar a MongoDB. Verifica tu archivo .env")
        sys.exit(1)
    
    # Inicializar base de datos
    init_database()
    
    # Ejecutar ETL
    stats = run_etl_pipeline()
    return stats


def run_preprocessing():
    """Ejecuta preprocesamiento y balanceo."""
    print("\n" + "=" * 70)
    print("FASE 2: PREPROCESAMIENTO Y BALANCEO")
    print("=" * 70)
    
    from src.model.preprocessing import preprocess_and_balance
    
    stats = preprocess_and_balance(balance_strategy="undersample")
    return stats


def run_training():
    """Ejecuta el entrenamiento del modelo."""
    print("\n" + "=" * 70)
    print("FASE 3: ENTRENAMIENTO DEL MODELO")
    print("=" * 70)
    
    from src.model.train import train_model
    
    stats = train_model(
        num_epochs=5,
        batch_size=8,
        learning_rate=2e-5
    )
    return stats


def run_evaluation():
    """Ejecuta la evaluación del modelo."""
    print("\n" + "=" * 70)
    print("FASE 4: EVALUACIÓN")
    print("=" * 70)
    
    from src.model.evaluate import evaluate_model
    
    results = evaluate_model()
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de Clasificación de Textos Clásicos"
    )
    parser.add_argument(
        "--step",
        choices=["etl", "preprocess", "train", "evaluate", "all"],
        default="all",
        help="Paso del pipeline a ejecutar (default: all)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "🏛️" * 20)
    print("   CLASIFICADOR DE TEXTOS CLÁSICOS")
    print("   Pipeline de Procesamiento y Entrenamiento")
    print("🏛️" * 20)
    
    if args.step in ["etl", "all"]:
        run_etl()
    
    if args.step in ["preprocess", "all"]:
        run_preprocessing()
    
    if args.step in ["train", "all"]:
        run_training()
    
    if args.step in ["evaluate", "all"]:
        run_evaluation()
    
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print("\nPara iniciar la aplicación web:")
    print("  streamlit run src/app/streamlit_app.py")
    print()


if __name__ == "__main__":
    main()
