# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# PyInstaller injects SPECPATH (directory containing this spec)
project_root = Path(SPECPATH).resolve()

# Collect package data/binaries/hidden imports
# NOTE: Streamlit has good hook support via pyinstaller-hooks-contrib;
# collecting *all* submodules may trigger optional deps (e.g., langchain).
streamlit_datas = collect_data_files("streamlit")
streamlit_binaries = []
streamlit_hidden = []

transformers_datas, transformers_binaries, transformers_hidden = collect_all("transformers")
torch_datas, torch_binaries, torch_hidden = collect_all("torch")

datas = []
binaries = []
hiddenimports = []

for d in (streamlit_datas + transformers_datas + torch_datas):
    datas.append(d)
for b in (streamlit_binaries + transformers_binaries + torch_binaries):
    binaries.append(b)
for h in (streamlit_hidden + transformers_hidden + torch_hidden):
    hiddenimports.append(h)

# Bundle your Streamlit script and local model folder as data
# NOTE: This makes the EXE self-contained, but size will be large due to torch.
datas += [
    (str(project_root / "src" / "app" / "streamlit_app.py"), str(Path("src") / "app")),
]

model_dir = project_root / "models" / "clasificador_textos"
if model_dir.exists():
    datas.append((str(model_dir), str(Path("models") / "clasificador_textos")))

analysis = Analysis(
    [str(project_root / "scripts" / "06_run_app.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    [],
    name="ClasificadorTextos",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
