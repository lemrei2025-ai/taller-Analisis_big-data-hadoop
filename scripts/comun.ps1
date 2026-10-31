# ---------------------------------------------------------------------------
# Funciones comunes para los scripts del taller (se cargan con: . .\scripts\comun.ps1)
# ---------------------------------------------------------------------------
$ErrorActionPreference = "Continue"
$Raiz = Split-Path -Parent $PSScriptRoot
$Config = Get-Content (Join-Path $PSScriptRoot "trabajos.json") -Raw -Encoding UTF8 | ConvertFrom-Json

if (-not $env:HADOOP_HOME) {
    Write-Host "[X] HADOOP_HOME no está definida. Ejecute instalacion\instalar_hadoop_windows.ps1 y abra una nueva terminal." -ForegroundColor Red
    exit 1
}

# Los .cmd de Hadoop separan los argumentos en '=' y ','. Por eso los valores que
# contienen esos caracteres (o espacios) se envían entre comillas dobles.
function Q([string]$texto) { return '"' + $texto + '"' }

function Titulo([string]$texto) { Write-Host "`n== $texto ==" -ForegroundColor Cyan }

function Comprobar([string]$accion) {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[X] Falló: $accion (código $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
