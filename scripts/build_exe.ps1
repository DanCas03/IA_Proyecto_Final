$ErrorActionPreference = 'Stop'

Write-Host "== Build EXE (Streamlit) ==" -ForegroundColor Cyan

# Go to project root (this script lives in scripts/)
$projectRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $projectRoot

python -m pip install --upgrade pip | Out-Host
python -m pip install --upgrade pyinstaller | Out-Host

# Build using the spec (handles bundling app + model + common hidden imports)
pyinstaller --noconfirm --clean ClasificadorTextos.spec | Out-Host

Write-Host "\nBuild output:" -ForegroundColor Green
Write-Host "- dist/ClasificadorTextos/ClasificadorTextos.exe" -ForegroundColor Green
Write-Host "\nRun it with:" -ForegroundColor Yellow
Write-Host "- .\\dist\\ClasificadorTextos\\ClasificadorTextos.exe" -ForegroundColor Yellow
