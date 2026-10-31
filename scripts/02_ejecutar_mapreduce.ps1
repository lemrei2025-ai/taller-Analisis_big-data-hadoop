<#
.SYNOPSIS
    CAPA 3 - ANÁLISIS Y PROCESAMIENTO. Ejecuta los trabajos MapReduce con
    Hadoop Streaming.
.PARAMETER Trabajo
    Nombre(s) de los trabajos a ejecutar (ver scripts\trabajos.json). Si se omite, se ejecutan todos.
.PARAMETER Modo
    yarn  (por defecto): el trabajo se envía al clúster (ResourceManager/NodeManager).
    local: MapReduce se ejecuta dentro del mismo proceso, leyendo y escribiendo en HDFS.
           Útil si YARN presenta problemas en el equipo.
.EXAMPLE
    .\scripts\02_ejecutar_mapreduce.ps1
    .\scripts\02_ejecutar_mapreduce.ps1 -Trabajo ventas_mes
    .\scripts\02_ejecutar_mapreduce.ps1 -Trabajo ventas_mes,llamadas_motivo -Modo local
#>
param(
    [string[]]$Trabajo = @(),
    [ValidateSet("yarn", "local")][string]$Modo = "yarn"
)
. (Join-Path $PSScriptRoot "comun.ps1")

Write-Host @"

=====================================================================
 CAPA 3 - PROCESAMIENTO CON MAPREDUCE (Hadoop Streaming)
=====================================================================
 Para cada trabajo este script:
   1. Borra la carpeta de salida en HDFS si existía (MapReduce exige
      que la salida no exista).
   2. Envía a Hadoop los scripts mapper.py y reducer.py (opción -files).
   3. Hadoop divide la entrada en bloques; cada bloque lo procesa una
      tarea MAP que ejecuta 'python mapper.py' y emite pares clave->valor.
   4. SHUFFLE & SORT: Hadoop agrupa y ordena los pares por clave.
   5. Una tarea REDUCE ejecuta 'python reducer.py' y calcula los totales
      de cada clave.
   6. El resultado queda en HDFS: /datalake/curated/<trabajo>/part-00000
 Mientras corre, el avance se puede ver en http://localhost:8088
 Modo de ejecución: $Modo
=====================================================================
"@ -ForegroundColor Yellow

$jar = Get-ChildItem "$env:HADOOP_HOME\share\hadoop\tools\lib\hadoop-streaming-*.jar" | Select-Object -First 1
if (-not $jar) { Write-Host "[X] No se encontró hadoop-streaming-*.jar" -ForegroundColor Red; exit 1 }

# Hadoop recibe las rutas de los scripts relativas a la carpeta mapreduce
Push-Location (Join-Path $Raiz "mapreduce")
try {
    foreach ($t in $Config.trabajos) {
        if ($Trabajo.Count -gt 0 -and $Trabajo -notcontains $t.nombre) { continue }

        $salida = "$($Config.zona_curada)/$($t.nombre)"
        hdfs.cmd dfs -rm -r -f -skipTrash $salida *> $null

        $archivos = @("$($t.job)/mapper.py", "$($t.job)/reducer.py") + $Config.auxiliares
        $argumentos = @(
            "jar", $jar.FullName,
            "-D", (Q "mapreduce.job.name=taller-$($t.nombre)"),
            "-D", (Q "mapreduce.job.reduces=1")
        )
        if ($Modo -eq "local") { $argumentos += @("-D", (Q "mapreduce.framework.name=local")) }
        $argumentos += @(
            "-files",   (Q ($archivos -join ",")),
            "-mapper",  (Q "python mapper.py"),
            "-reducer", (Q "python reducer.py")
        )
        if ($t.combiner) { $argumentos += @("-combiner", (Q "python reducer.py")) }
        $argumentos += @("-cmdenv", (Q "PYTHONIOENCODING=utf-8"))
        foreach ($v in $t.variables.PSObject.Properties) {
            $argumentos += @("-cmdenv", (Q "$($v.Name)=$($v.Value)"))
        }
        foreach ($e in $t.entradas) { $argumentos += @("-input", $Config.entradas.$e.hdfs) }
        $argumentos += @("-output", $salida)

        Write-Host ("`n" + "=" * 70) -ForegroundColor Cyan
        Write-Host " Trabajo : $($t.nombre)" -ForegroundColor Cyan
        Write-Host ("=" * 70) -ForegroundColor Cyan
        Write-Host " Qué hace: $($t.descripcion)"
        Write-Host " Entrada : $(($t.entradas | ForEach-Object { $Config.entradas.$_.hdfs }) -join ', ')"
        Write-Host " Código  : mapreduce\$($t.job)\mapper.py  y  reducer.py"
        $vars = ($t.variables.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ", "
        if ($vars) { Write-Host " Variables: $vars" }
        Write-Host " Salida  : $salida"
        Write-Host " Comando : hadoop $($argumentos -join ' ')" -ForegroundColor DarkGray
        Write-Host " (A continuación aparece el registro de Hadoop: progreso 'map X% reduce Y%' y contadores)" -ForegroundColor DarkGray

        $inicio = Get-Date
        & hadoop.cmd @argumentos
        Comprobar "trabajo $($t.nombre)"
        Write-Host (">> {0} terminado en {1:N0} s -> {2}" -f $t.nombre, ((Get-Date) - $inicio).TotalSeconds, $salida) -ForegroundColor Green
        Write-Host "   Primeras líneas del resultado (clave <TAB> valores):" -ForegroundColor Green
        hdfs.cmd dfs -cat "$salida/part-00000" 2>$null | Select-Object -First 5 | ForEach-Object { Write-Host "     $_" }
    }
} finally {
    Pop-Location
}

Titulo "Zona curada (resultados en HDFS)"
hdfs.cmd dfs -ls $Config.zona_curada
