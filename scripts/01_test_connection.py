"""
Script 01: Prueba de conexión a MongoDB Atlas.
Ejecutar primero para verificar que la configuración es correcta.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.db import test_connection, init_database, get_database

def main():
    print("=" * 60)
    print("🔌 PRUEBA DE CONEXIÓN A MONGODB ATLAS")
    print("=" * 60)
    
    # Test 1: Conexión básica
    print("\n[1/3] Probando conexión...")
    if not test_connection():
        print("\n❌ FALLO: No se pudo conectar a MongoDB")
        print("   Verifica tu archivo .env con MONGO_URI correcto")
        sys.exit(1)
    
    # Test 2: Inicializar base de datos
    print("\n[2/3] Inicializando base de datos y colecciones...")
    try:
        info = init_database()
        print(f"   ✓ Base de datos: {info['database']}")
        print(f"   ✓ Colecciones creadas: {info['created_collections']}")
        print(f"   ✓ Colecciones existentes: {info['existing_collections']}")
    except Exception as e:
        print(f"\n❌ FALLO al inicializar: {e}")
        sys.exit(1)
    
    # Test 3: Verificar acceso
    print("\n[3/3] Verificando permisos de escritura...")
    try:
        db = get_database()
        # Intentar insertar y eliminar un documento de prueba
        test_col = db["_test_connection"]
        test_col.insert_one({"test": True})
        test_col.delete_many({})
        db.drop_collection("_test_connection")
        print("   ✓ Permisos de lectura/escritura: OK")
    except Exception as e:
        print(f"\n❌ FALLO en permisos: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS PASARON - CONEXIÓN EXITOSA")
    print("=" * 60)
    print("\nPuedes continuar con: python scripts/02_run_etl.py")


if __name__ == "__main__":
    main()
