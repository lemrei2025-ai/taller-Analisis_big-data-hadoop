<#
.SYNOPSIS
    Reúne la información necesaria para diagnosticar errores de instalación de Hadoop
    y la guarda en diagnostico_hadoop.txt (en la carpeta actual).
    Uso (PowerShell como administrador):  .\instalacion\diagnostico_hadoop.ps1
#>
param([string]$HadoopHome = "C:\hadoop")
$ErrorActionPreference = "Continue"
$salida = Join-Path (Get-Location) "diagnostico_hadoop.txt"

& {
    "=== Variables de entorno (sesión) ==="
    Get-ChildItem Env: | Where-Object { $_.Name -match "HADOOP|JAVA|CLASSPATH" } |
        ForEach-Object { "{0} = {1}" -f $_.Name, $_.Value }

    "`n=== Variables de entorno (sistema y usuario) ==="
    foreach ($v in "JAVA_HOME", "HADOOP_HOME", "HADOOP_CONF_DIR", "CLASSPATH", "HADOOP_CLASSPATH", "HADOOP_HDFS_HOME", "HADOOP_COMMON_HOME") {
        foreach ($a in "Machine", "User") {
            $x = [Environment]::GetEnvironmentVariable($v, $a)
            if ($x) { "{0} ({1}) = {2}" -f $v, $a, $x }
        }
    }

    "`n=== Java ==="
    cmd /c "java -version 2>&1"
    (Get-Command java -ErrorAction SilentlyContinue).Source

    "`n=== Carpeta $HadoopHome ==="
    Get-ChildItem $HadoopHome -ErrorAction SilentlyContinue | ForEach-Object Name
    "-- bin --"
    Get-ChildItem "$HadoopHome\bin" -ErrorAction SilentlyContinue | ForEach-Object Name
    "-- jar de HDFS --"
    Get-ChildItem "$HadoopHome\share\hadoop\hdfs\hadoop-hdfs-*.jar" -ErrorAction SilentlyContinue | ForEach-Object { "{0}  {1:N0} bytes" -f $_.Name, $_.Length }
    "-- número de .jar en share\hadoop --"
    (Get-ChildItem "$HadoopHome\share\hadoop" -Recurse -Filter *.jar -ErrorAction SilentlyContinue | Measure-Object).Count

    "`n=== hadoop-env.cmd (JAVA_HOME) ==="
    Select-String -Path "$HadoopHome\etc\hadoop\hadoop-env.cmd" -Pattern "JAVA_HOME" -ErrorAction SilentlyContinue | ForEach-Object Line

    "`n=== hadoop classpath ==="
    cmd /c "`"$HadoopHome\bin\hadoop.cmd`" classpath 2>&1"

    "`n=== hadoop version ==="
    cmd /c "`"$HadoopHome\bin\hadoop.cmd`" version 2>&1" | Select-Object -First 3

    "`n=== hdfs namenode -format (primeras 25 líneas) ==="
    cmd /c "`"$HadoopHome\bin\hdfs.cmd`" namenode -format -nonInteractive 2>&1" | Select-Object -First 25
} *>&1 | Out-File -FilePath $salida -Encoding UTF8

Get-Content $salida
Write-Host "`nInformación guardada en: $salida" -ForegroundColor Green
