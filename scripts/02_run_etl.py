"""
Script 02: Extracción y carga de datos (ETL).
Migra los datos de los archivos Excel a MongoDB.

Uso:
    python scripts/02_run_etl.py          # Normal
    python scripts/02_run_etl.py --debug  # Con información de debugging
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

from src.data.etl import run_etl_pipeline

def main():
    # Verificar si se pasó el flag de debug
    debug = "--debug" in sys.argv
    
    print("=" * 60)
    print("📊 EXTRACCIÓN Y CARGA DE DATOS (ETL)")
    if debug:
        print("   [MODO DEBUG ACTIVADO]")
    print("=" * 60)
    
    # Verificar que existe el directorio Dataset
    dataset_path = Path("Dataset")
    if not dataset_path.exists():
        print(f"\n❌ ERROR: No se encontró el directorio '{dataset_path}'")
        print("   Asegúrate de que los archivos Excel estén en ./Dataset/")
        sys.exit(1)
    
    # Contar archivos
    excel_files = sorted(list(dataset_path.glob("*.xlsx")))
    print(f"\n📁 Archivos Excel encontrados: {len(excel_files)}")
    for f in excel_files:
        print(f"   • {f.name}")
    
    if not excel_files:
        print("\n❌ ERROR: No hay archivos .xlsx en el directorio Dataset/")
        sys.exit(1)
    
    # Ejecutar ETL
    print("\n🚀 Iniciando proceso de extracción...")
    try:
        stats = run_etl_pipeline(dataset_path=str(dataset_path), clear_existing=True, debug=debug)
        
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
