"""
Script 03: Preprocesamiento y balanceo de datos.
Limpia textos, balancea clases y divide en train/val/test.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model.preprocessing import preprocess_and_balance, get_category_distribution

def main():
    print("=" * 60)
    print("🔄 PREPROCESAMIENTO Y BALANCEO DE DATOS")
    print("=" * 60)
    
    # Verificar que hay datos en MongoDB
    print("\n[1/2] Verificando datos en MongoDB...")
    try:
        dist = get_category_distribution()
        total = sum(dist.values())
        
        if total == 0:
            print("\n❌ ERROR: No hay datos en la colección 'raw_texts'")
            print("   Ejecuta primero: python scripts/02_run_etl.py")
            sys.exit(1)
        
        print(f"   ✓ Total de documentos: {total}")
        print(f"   ✓ Distribución actual:")
        for cat, count in dist.items():
            pct = (count / total) * 100
            print(f"      - {cat}: {count} ({pct:.1f}%)")
            
    except Exception as e:
        print(f"\n❌ ERROR al verificar datos: {e}")
        sys.exit(1)
    
    # Ejecutar preprocesamiento
    print("\n[2/2] Ejecutando preprocesamiento y balanceo...")
    try:
        stats = preprocess_and_balance(
            balance_strategy="undersample",  # Usa undersampling para evitar overfitting
            test_size=0.15,
            val_size=0.15,
            random_state=42
        )
        
        print("\n" + "=" * 60)
        print("✅ PREPROCESAMIENTO COMPLETADO")
        print("=" * 60)
        print(f"\n📈 Resumen:")
        print(f"   • Estrategia: {stats['balance_strategy']}")
        print(f"   • Documentos originales: {stats['initial_count']}")
        print(f"   • Documentos balanceados: {stats['balanced_count']}")
        print(f"   • Train: {stats['train_count']}")
        print(f"   • Val: {stats['val_count']}")
        print(f"   • Test: {stats['test_count']}")
        print(f"\n📝 Justificación: {stats['justification']}")
        
        print("\nPuedes continuar con: python scripts/04_train.py")
        
    except Exception as e:
        print(f"\n❌ ERROR durante preprocesamiento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
