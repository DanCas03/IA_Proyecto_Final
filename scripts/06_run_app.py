"""
Script 06: Lanzar la aplicación Streamlit.
Interfaz de usuario para clasificación de textos.
"""

import sys
import os
import subprocess
from pathlib import Path

# Configurar UTF-8 para Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

def main():
    print("=" * 60)
    print("🚀 LANZANDO APLICACIÓN WEB")
    print("=" * 60)
    
    # Base dir del proyecto (normal) o del bundle (PyInstaller)
    meipass = getattr(sys, "_MEIPASS", None)
    if getattr(sys, "frozen", False) and meipass:
        base_dir = Path(meipass)
    else:
        base_dir = Path(__file__).resolve().parents[1]

    # Verificar que existe el modelo
    model_path = base_dir / "models" / "clasificador_textos" / "final"
    if not model_path.exists():
        print(f"\n⚠️ ADVERTENCIA: No se encontró el modelo en '{model_path}'")
        print("   La app mostrará un error hasta que entrenes el modelo.")
        print("   Ejecuta: python scripts/04_train.py")
    else:
        print(f"\n✓ Modelo encontrado: {model_path}")
    
    # Lanzar Streamlit
    app_path = base_dir / "src" / "app" / "streamlit_app.py"
    if not app_path.exists():
        print(f"\n❌ ERROR: No se encontró la app en '{app_path}'")
        sys.exit(1)
    
    print("\n🌐 Iniciando servidor Streamlit...")
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
