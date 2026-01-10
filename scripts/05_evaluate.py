"""
Script 05: Evaluación del modelo.
Genera matriz de confusión y métricas detalladas.
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

def main():
    print("=" * 60)
    print("📊 EVALUACIÓN DEL MODELO")
    print("=" * 60)
    
    # Verificar que existe el modelo
    model_path = Path("models/clasificador_textos/final")
    if not model_path.exists():
        print(f"\n❌ ERROR: No se encontró el modelo en '{model_path}'")
        print("   Ejecuta primero: python scripts/04_train.py")
        sys.exit(1)
    
    print(f"\n✓ Modelo encontrado: {model_path}")
    
    # Ejecutar evaluación
    try:
        from src.model.evaluate import evaluate_model
        
        results = evaluate_model(model_path=model_path)
        
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE EVALUACIÓN")
        print("=" * 60)
        
        # Criterio de aceptación
        f1 = results['f1_macro']
        if results['meets_criteria']:
            print(f"\n🎉 ¡PROYECTO EXITOSO!")
            print(f"   F1-Score: {f1:.4f} >= 0.80 ✓")
        else:
            print(f"\n⚠️ CRITERIO NO CUMPLIDO")
            print(f"   F1-Score: {f1:.4f} < 0.80")
            print("\n   Sugerencias:")
            print("   1. Revisa la calidad de los datos")
            print("   2. Aumenta el número de épocas")
            print("   3. Prueba con oversampling en lugar de undersampling")
            print("   4. Ajusta el learning rate")
        
        print(f"\n📁 Reportes generados en: reports/")
        print("   • confusion_matrix.png")
        print("   • metrics_by_class.png")
        print("   • evaluation_report.json")
        
        print("\nPuedes iniciar la app: streamlit run src/app/streamlit_app.py")
        
    except Exception as e:
        print(f"\n❌ ERROR durante evaluación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
