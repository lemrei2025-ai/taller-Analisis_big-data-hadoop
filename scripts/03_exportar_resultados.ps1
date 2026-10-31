<#
.SYNOPSIS
    CAPA 4 - ACCESO. Descarga los resultados de la zona curada de HDFS a la
    carpeta resultados\hadoop del repositorio.
.DESCRIPTION
    Usa la API REST WebHDFS de Hadoop (la misma de webhdfs_ejemplos.ps1), de modo
    que los archivos se copian byte a byte, sin problemas de codificación ni de
    rutas de Windows. Para cada trabajo equivale a:
        hdfs dfs -getmerge /datalake/curated/<trabajo> resultados\hadoop\<trabajo>.tsv
.EXAMPLE
    .\scripts\03_exportar_resultados.ps1
#>
param([string]$Servidor = "localhost:9870")
. (Join-Path $PSScriptRoot "comun.ps1")

Write-Host @"

=====================================================================
 CAPA 4 - EXPORTAR RESULTADOS DESDE HDFS
=====================================================================
 Para cada trabajo terminado (carpeta de HDFS con el archivo _SUCCESS)
 se descargan sus archivos part-* y se unen en un solo archivo .tsv en
 resultados\hadoop (en Windows). Es lo mismo que hace el comando
 'hdfs dfs -getmerge'. Esos archivos los usan después cargar_sqlite.py,
 api_resultados.py y generar_reporte.py.
=====================================================================
"@ -ForegroundColor Yellow

$api = "http://$Servidor/webhdfs/v1"

function Listar([string]$ruta) {
    # Devuelve la lista de archivos de una carpeta de HDFS, o $null si no existe.
    try {
        return (Invoke-RestMethod "$api$($ruta)?op=LISTSTATUS" -ErrorAction Stop).FileStatuses.FileStatus
    } catch {
        $codigo = 0
        if ($_.Exception.Response) { $codigo = [int]$_.Exception.Response.StatusCode }
        if ($codigo -eq 404) { return $null }
        Write-Host "[X] No hay conexión con HDFS en http://$Servidor ($($_.Exception.Message))" -ForegroundColor Red
        Write-Host "    Verifique que Hadoop esté iniciado: .\instalacion\iniciar_hadoop.cmd" -ForegroundColor Red
        exit 1
    }
}

# 1) ¿Existe la zona curada?
if ($null -eq (Listar $Config.zona_curada)) {
    Write-Host "[X] No existe $($Config.zona_curada) en HDFS." -ForegroundColor Red
    Write-Host "    Primero deben ejecutarse los trabajos MapReduce: .\scripts\02_ejecutar_mapreduce.ps1" -ForegroundColor Red
    exit 1
}

$destino = Join-Path $Raiz "resultados\hadoop"
New-Item -ItemType Directory -Force -Path $destino | Out-Null
$exportados = 0
$pendientes = @()

foreach ($t in $Config.trabajos) {
    $origen = "$($Config.zona_curada)/$($t.nombre)"
    $archivos = Listar $origen

    if ($null -eq $archivos) {
        Write-Host ("  (falta)      {0,-26} no se ha ejecutado" -f $t.nombre) -ForegroundColor Yellow
        $pendientes += $t.nombre; continue
    }
    if (-not ($archivos | Where-Object { $_.pathSuffix -eq "_SUCCESS" })) {
        Write-Host ("  (incompleto) {0,-26} el trabajo falló o no terminó" -f $t.nombre) -ForegroundColor Yellow
        $pendientes += $t.nombre; continue
    }

    # 2) Descargar y unir los archivos part-* (normalmente uno solo: part-00000)
    $salida = Join-Path $destino "$($t.nombre).tsv"
    $bytes = New-Object System.Collections.Generic.List[byte]
    foreach ($parte in ($archivos | Where-Object { $_.pathSuffix -like "part-*" } | Sort-Object pathSuffix)) {
        $tmp = [IO.Path]::GetTempFileName()
        Invoke-WebRequest "$api$origen/$($parte.pathSuffix)?op=OPEN" -OutFile $tmp -UseBasicParsing
        $bytes.AddRange([IO.File]::ReadAllBytes($tmp))
        Remove-Item $tmp -Force
    }
    [IO.File]::WriteAllBytes($salida, $bytes.ToArray())

    $filas = ([IO.File]::ReadAllLines($salida)).Count
    Write-Host ("  (exportado)  {0,-26} -> resultados\hadoop\{0}.tsv  ({1} filas)" -f $t.nombre, $filas) -ForegroundColor Green
    $exportados++
}

Titulo "Resumen"
Write-Host "  Exportados: $exportados de $($Config.trabajos.Count)  ->  $destino"
if ($pendientes.Count -gt 0) {
    Write-Host "  Pendientes: $($pendientes -join ', ')" -ForegroundColor Yellow
    Write-Host "  Para ejecutarlos:  .\scripts\02_ejecutar_mapreduce.ps1 -Trabajo $($pendientes -join ',')" -ForegroundColor Yellow
    Write-Host "  (si YARN falla, agregar:  -Modo local)" -ForegroundColor Yellow
}
