<#
.SYNOPSIS
    Verifica que las herramientas del taller estén instaladas y que Hadoop esté en ejecución.
    Uso:  .\instalacion\verificar_instalacion.ps1
#>
function Revisar($nombre, [scriptblock]$prueba, $ayuda) {
    try { $r = & $prueba } catch { $r = $null }
    if ($r) { Write-Host ("[OK] {0,-28} {1}" -f $nombre, $r) -ForegroundColor Green }
    else    { Write-Host ("[X]  {0,-28} {1}" -f $nombre, $ayuda) -ForegroundColor Red }
}

Write-Host "`n== Herramientas ==" -ForegroundColor Cyan
Revisar "Java (JDK)"        { (cmd /c "java -version 2>&1" | Select-Object -First 1) } "Instalar Eclipse Temurin JDK 8"
Revisar "JAVA_HOME"         { if ($env:JAVA_HOME -and $env:JAVA_HOME -notmatch " ") { $env:JAVA_HOME } } "Definir JAVA_HOME sin espacios"
Revisar "Python"            { (python --version 2>&1) } "Instalar Python 3 con 'Add python.exe to PATH'"
Revisar "Git"               { (git --version) } "Instalar Git for Windows (opcional)"
Revisar "HADOOP_HOME"       { if (Test-Path "$env:HADOOP_HOME\bin\hdfs.cmd") { $env:HADOOP_HOME } } "Ejecutar instalar_hadoop_windows.ps1"
Revisar "Hadoop"            { (hadoop.cmd version | Select-Object -First 1) } "Revisar Path (debe incluir %HADOOP_HOME%\bin)"
Revisar "winutils.exe"      { if (Test-Path "$env:HADOOP_HOME\bin\winutils.exe") { "presente" } } "Copiar winutils.exe en %HADOOP_HOME%\bin"
Revisar "hadoop.dll nativa" { if ((hadoop.cmd checknative 2>&1) -match "hadoop:\s+true") { "cargada" } } "Instalar Visual C++ Redistributable x64"
Revisar "matplotlib"        { (python -c "import matplotlib; print('matplotlib', matplotlib.__version__)") } "pip install -r requirements.txt"

Write-Host "`n== Servicios de Hadoop ==" -ForegroundColor Cyan
$procesos = (jps 2>$null) -join " "
foreach ($s in "NameNode", "DataNode", "ResourceManager", "NodeManager", "JobHistoryServer") {
    Revisar $s { if ($procesos -match "\b$s\b") { "en ejecución" } } "No iniciado (ejecutar instalacion\iniciar_hadoop.cmd)"
}
foreach ($p in @(@{n="HDFS web (9870)";p=9870}, @{n="YARN web (8088)";p=8088}, @{n="Historial (19888)";p=19888})) {
    Revisar $p.n { if ((Test-NetConnection localhost -Port $p.p -WarningAction SilentlyContinue).TcpTestSucceeded) { "http://localhost:$($p.p)" } } "Puerto cerrado"
}
