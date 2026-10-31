<#
.SYNOPSIS
    CAPA 4 - ACCESO. Descarga los resultados de la zona curada de HDFS a la
    carpeta resultados\hadoop del repositorio.
.EXAMPLE
    .\scripts\03_exportar_resultados.ps1
#>
. (Join-Path $PSScriptRoot "comun.ps1")

Write-Host @"

=====================================================================
 CAPA 4 - EXPORTAR RESULTADOS DESDE HDFS
=====================================================================
 Para cada trabajo terminado (carpeta con el archivo _SUCCESS),
 'hdfs dfs -getmerge' une los archivos part-* de HDFS en un solo
 archivo .tsv en resultados\hadoop (en Windows). Esos archivos los
 usan después cargar_sqlite.py, api_resultados.py y generar_reporte.py.
=====================================================================
"@ -ForegroundColor Yellow

$destino = Join-Path $Raiz "resultados\hadoop"
New-Item -ItemType Directory -Force -Path $destino | Out-Null

foreach ($t in $Config.trabajos) {
    $origen = "$($Config.zona_curada)/$($t.nombre)"
    hdfs.cmd dfs -test -e "$origen/_SUCCESS" 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "  (omitido) $($t.nombre) no tiene resultados en HDFS"; continue }

    $archivo = Join-Path $destino "$($t.nombre).tsv"
    Remove-Item $archivo, (Join-Path $destino ".$($t.nombre).tsv.crc") -Force -ErrorAction SilentlyContinue
    hdfs.cmd dfs -getmerge $origen (Q $archivo)
    Comprobar "exportar $origen"
    Remove-Item (Join-Path $destino ".$($t.nombre).tsv.crc") -Force -ErrorAction SilentlyContinue
    $filas = (Get-Content $archivo | Measure-Object -Line).Lines
    Write-Host ("  {0,-40} -> resultados\hadoop\{1}.tsv ({2} filas)" -f $origen, $t.nombre, $filas)
}
