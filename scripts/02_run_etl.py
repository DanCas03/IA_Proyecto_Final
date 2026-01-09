"""
Script 02: Extracción y carga de datos (ETL).
Migra los datos de los archivos Excel a MongoDB.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.etl import run_etl_pipeline

def main():
    print("=" * 60)
    print("📊 EXTRACCIÓN Y CARGA DE DATOS (ETL)")
    print("=" * 60)
    
    # Verificar que existe el directorio Dataset
    dataset_path = Path("Dataset")
    if not dataset_path.exists():
        print(f"\n❌ ERROR: No se encontró el directorio '{dataset_path}'")
        print("   Asegúrate de que los archivos Excel estén en ./Dataset/")
        sys.exit(1)
    
    # Contar archivos
    excel_files = list(dataset_path.glob("*.xlsx"))
    print(f"\n📁 Archivos Excel encontrados: {len(excel_files)}")
    for f in excel_files:
        print(f"   • {f.name}")
    
    if not excel_files:
        print("\n❌ ERROR: No hay archivos .xlsx en el directorio Dataset/")
        sys.exit(1)
    
    # Ejecutar ETL
    print("\n🚀 Iniciando proceso de extracción...")
    try:
        stats = run_etl_pipeline(dataset_path=str(dataset_path), clear_existing=True)
        
        print("\n" + "=" * 60)
        print("✅ ETL COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\n📈 Resumen:")
        print(f"   • Total documentos: {stats['total_inserted']}")
        print(f"   • Por categoría:")
        for cat, count in stats['by_category'].items():
            print(f"      - {cat}: {count}")
        
        print("\nPuedes continuar con: python scripts/03_preprocess.py")
        
    except Exception as e:
        print(f"\n❌ ERROR durante ETL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
