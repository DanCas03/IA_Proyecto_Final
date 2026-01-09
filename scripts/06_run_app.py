"""
Script 06: Lanzar la aplicación Streamlit.
Interfaz de usuario para clasificación de textos.
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("🚀 LANZANDO APLICACIÓN WEB")
    print("=" * 60)
    
    # Verificar que existe el modelo
    model_path = Path("models/clasificador_textos/final")
    if not model_path.exists():
        print(f"\n⚠️ ADVERTENCIA: No se encontró el modelo en '{model_path}'")
        print("   La app mostrará un error hasta que entrenes el modelo.")
        print("   Ejecuta: python scripts/04_train.py")
    else:
        print(f"\n✓ Modelo encontrado: {model_path}")
    
    # Lanzar Streamlit
    app_path = Path("src/app/streamlit_app.py")
    if not app_path.exists():
        print(f"\n❌ ERROR: No se encontró la app en '{app_path}'")
        sys.exit(1)
    
    print(f"\n🌐 Iniciando servidor Streamlit...")
    print("   La aplicación se abrirá en tu navegador.")
    print("   Para detener: Ctrl+C")
    print("\n" + "-" * 60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n✓ Servidor detenido.")


if __name__ == "__main__":
    main()
