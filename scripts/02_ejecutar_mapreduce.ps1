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
        Write-Host " Trabajo: $($t.nombre)   ($($t.job))   modo: $Modo" -ForegroundColor Cyan
        Write-Host ("=" * 70) -ForegroundColor Cyan
        $inicio = Get-Date
        & hadoop.cmd @argumentos
        Comprobar "trabajo $($t.nombre)"
        Write-Host (">> {0} terminado en {1:N0} s -> {2}" -f $t.nombre, ((Get-Date) - $inicio).TotalSeconds, $salida) -ForegroundColor Green
    }
} finally {
    Pop-Location
}

Titulo "Zona curada"
hdfs.cmd dfs -ls $Config.zona_curada
