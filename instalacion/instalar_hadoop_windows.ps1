<#
.SYNOPSIS
    Instalador de Apache Hadoop 3.3.6 para Windows 10/11 (nodo único).

.DESCRIPTION
    Automatiza los pasos de instalación de Hadoop en Windows:
      1. Verifica Java (JDK 8 u 11) y Python 3, instalados previamente con sus instaladores.
      2. Descarga Hadoop 3.3.6 desde el archivo oficial de Apache y lo extrae en C:\hadoop.
      3. Descarga los binarios nativos para Windows (winutils.exe y hadoop.dll).
      4. Copia la configuración del taller (core, hdfs, mapred y yarn-site.xml).
      5. Define las variables de entorno JAVA_HOME, HADOOP_HOME y PATH.
      6. Crea las carpetas de datos y formatea el NameNode.

    Debe ejecutarse en PowerShell COMO ADMINISTRADOR, desde la raíz del repositorio:

        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
        .\instalacion\instalar_hadoop_windows.ps1

.PARAMETER HadoopHome
    Carpeta de instalación (sin espacios ni tildes). Por defecto C:\hadoop.

.PARAMETER CarpetaWinutils
    Carpeta donde ya están winutils.exe y hadoop.dll descargados manualmente
    (por ejemplo, si la red bloquea GitHub). Por defecto se buscan también en
    instalacion\winutils\ del repositorio.

.PARAMETER Archivo
    Ruta a un hadoop-3.3.6.tar.gz ya descargado (útil en salas con conexión lenta:
    el docente descarga una vez y lo comparte por USB o red local).
#>
param(
    [string]$HadoopHome = "C:\hadoop",
    [string]$Archivo = "",
    [string]$CarpetaWinutils = ""
)

# "Continue": los programas de Hadoop escriben su registro en stderr y no debe tratarse como error.
$ErrorActionPreference = "Continue"
$Version = "3.3.6"
$UrlHadoop = "https://archive.apache.org/dist/hadoop/common/hadoop-$Version/hadoop-$Version.tar.gz"
# Varias direcciones del mismo archivo, por si la red bloquea alguna
$UrlsWinutils = @(
    "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-$Version/bin",
    "https://github.com/cdarlint/winutils/raw/master/hadoop-$Version/bin",
    "https://cdn.jsdelivr.net/gh/cdarlint/winutils@master/hadoop-$Version/bin"
)

function Paso($texto) { Write-Host "`n==> $texto" -ForegroundColor Cyan }
function Ok($texto)   { Write-Host "    [OK] $texto" -ForegroundColor Green }
function Aviso($texto){ Write-Host "    [!]  $texto" -ForegroundColor Yellow }
function Falla($texto){ Write-Host "    [X]  $texto" -ForegroundColor Red; exit 1 }

function Descargar([string]$url, [string]$destino) {
    # Intenta con curl.exe; si falla (p. ej. antivirus o proxy que impiden validar
    # la revocación del certificado), reintenta con --ssl-no-revoke y luego con
    # Invoke-WebRequest. Devuelve $true si el archivo quedó descargado.
    Remove-Item $destino -Force -ErrorAction SilentlyContinue
    foreach ($extra in @(@(), @("--ssl-no-revoke"))) {
        $salida = & curl.exe -L --fail --retry 2 -sS @extra -o $destino $url 2>&1
        if ($LASTEXITCODE -eq 0 -and (Test-Path $destino) -and (Get-Item $destino).Length -gt 0) { return $true }
        Write-Host "      curl: $salida" -ForegroundColor DarkGray
    }
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $destino -UseBasicParsing -ErrorAction Stop
        if ((Get-Item $destino).Length -gt 0) { return $true }
    } catch {
        Write-Host "      Invoke-WebRequest: $($_.Exception.Message)" -ForegroundColor DarkGray
    }
    Remove-Item $destino -Force -ErrorAction SilentlyContinue
    return $false
}

function RutaCorta([string]$ruta) {
    # Hadoop para Windows falla si JAVA_HOME contiene espacios (ej. "C:\Program Files\...").
    # Se usa el nombre corto 8.3 (ej. C:\PROGRA~1\...) cuando es necesario.
    if ($ruta -notmatch " ") { return $ruta }
    $fso = New-Object -ComObject Scripting.FileSystemObject
    $corta = $fso.GetFolder($ruta).ShortPath
    if ($corta -match " ") { Falla "JAVA_HOME contiene espacios y no fue posible obtener la ruta corta. Reinstale el JDK en C:\Java\jdk8" }
    return $corta
}

# ---------------------------------------------------------------------------
Paso "Verificando permisos de administrador"
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) { Falla "Abra PowerShell con clic derecho > 'Ejecutar como administrador' y vuelva a ejecutar el script." }
Ok "PowerShell se ejecuta como administrador"

if ($HadoopHome -match "[ áéíóúñÁÉÍÓÚÑ]") { Falla "La ruta de instalación no debe contener espacios ni tildes: $HadoopHome" }
$RepoRaiz = Split-Path -Parent $PSScriptRoot
if ($RepoRaiz -match "[ áéíóúñÁÉÍÓÚÑ]") {
    Aviso "El repositorio está en una ruta con espacios o tildes ($RepoRaiz)."
    Aviso "Se recomienda moverlo a una ruta simple, por ejemplo C:\taller-big-data-hadoop"
}

# ---------------------------------------------------------------------------
Paso "Verificando Java (JDK)"
$javaHome = [Environment]::GetEnvironmentVariable("JAVA_HOME", "Machine")
if (-not $javaHome) { $javaHome = [Environment]::GetEnvironmentVariable("JAVA_HOME", "User") }
if (-not $javaHome) {
    $java = Get-Command java -ErrorAction SilentlyContinue
    if ($java) { $javaHome = Split-Path -Parent (Split-Path -Parent $java.Source) }
}
if (-not $javaHome -or -not (Test-Path "$javaHome\bin\java.exe")) {
    Falla "No se encontró un JDK. Instale Eclipse Temurin JDK 8 (https://adoptium.net) y vuelva a ejecutar este script."
}
$javaHome = RutaCorta $javaHome.TrimEnd("\")
$versionJava = (& cmd /c "`"$javaHome\bin\java.exe`" -version 2>&1") -join " "
if ($versionJava -match 'version "(1\.8|11)\.') { Ok "Java encontrado en $javaHome" }
else { Aviso "Versión de Java no probada con Hadoop $Version ($versionJava). Se recomienda JDK 8 u 11." }

# ---------------------------------------------------------------------------
Paso "Verificando Python 3"
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py -or $py.Source -match "WindowsApps") {
    Falla "No se encontró Python. Instálelo desde https://www.python.org marcando 'Add python.exe to PATH'."
}
Ok ((& python --version) + " en " + $py.Source)

# ---------------------------------------------------------------------------
Paso "Instalando Hadoop $Version en $HadoopHome"
$padre = Split-Path -Parent $HadoopHome
$extraido = Join-Path $padre "hadoop-$Version"

# Archivos que deben existir para considerar completa una instalación
$Clave = @(
    "bin\hdfs.cmd",
    "libexec\hadoop-config.cmd",
    "share\hadoop\common\hadoop-common-$Version.jar",
    "share\hadoop\hdfs\hadoop-hdfs-$Version.jar",
    "share\hadoop\mapreduce\hadoop-mapreduce-client-core-$Version.jar",
    "share\hadoop\yarn\hadoop-yarn-server-nodemanager-$Version.jar",
    "share\hadoop\tools\lib\hadoop-streaming-$Version.jar"
)
function Faltantes([string]$base) { $Clave | Where-Object { -not (Test-Path (Join-Path $base $_)) } }

function ArchivoValido([string]$ruta) {
    # Compara el SHA-512 del .tar.gz con el publicado por Apache (detecta descargas incompletas)
    if (-not (Test-Path $ruta)) { return $false }
    $sha = Join-Path $env:TEMP "hadoop-$Version.tar.gz.sha512"
    if (-not (Descargar "$UrlHadoop.sha512" $sha)) {
        Aviso "No se pudo obtener el SHA-512 oficial; se omite la verificación del archivo."
        return $true
    }
    $esperado = ([regex]::Match((Get-Content $sha -Raw), "[0-9a-fA-F]{128}")).Value.ToLower()
    Write-Host "    Verificando la integridad de $ruta ..."
    $real = (Get-FileHash $ruta -Algorithm SHA512).Hash.ToLower()
    return ($esperado -and $esperado -eq $real)
}

$faltan = @(Faltantes $HadoopHome)
if ($faltan.Count -eq 0) {
    Ok "Hadoop ya está instalado completo en $HadoopHome (se omite la descarga)"
} else {
    if (Test-Path "$HadoopHome\bin") {
        Aviso "La instalación en $HadoopHome está incompleta. Faltan, entre otros:"
        $faltan | Select-Object -First 3 | ForEach-Object { Aviso "  $_" }
        Aviso "Se reparará con una extracción nueva."
    }

    # 1) Archivo .tar.gz verificado
    if (-not $Archivo) { $Archivo = Join-Path $env:TEMP "hadoop-$Version.tar.gz" }
    if (-not (ArchivoValido $Archivo)) {
        if (Test-Path $Archivo) { Aviso "El archivo $Archivo está dañado o incompleto; se descargará de nuevo." }
        Write-Host "    Descargando $UrlHadoop (~700 MB, puede tardar varios minutos)..."
        if (-not (Descargar $UrlHadoop $Archivo)) { Falla "No se pudo descargar Hadoop. Descárguelo manualmente y use -Archivo <ruta>." }
        if (-not (ArchivoValido $Archivo)) { Falla "El archivo descargado no coincide con el SHA-512 oficial. Intente de nuevo o use otra red." }
    }
    Ok "Archivo verificado: $Archivo"

    # 2) Extracción limpia
    if (Test-Path $extraido) { Remove-Item $extraido -Recurse -Force -ErrorAction SilentlyContinue }
    Write-Host "    Extrayendo en $padre (2 a 5 minutos)..."
    $log = Join-Path $env:TEMP "hadoop-extraccion.log"
    # Los avisos sobre enlaces simbólicos de librerías de Linux (lib\native\*.so) no afectan a Windows.
    & "$env:SystemRoot\System32\tar.exe" -xzf $Archivo -C $padre 2> $log
    $faltan = @(Faltantes $extraido)
    if ($faltan.Count -gt 0) {
        Get-Content $log -Tail 5 | ForEach-Object { Write-Host "      $_" -ForegroundColor DarkGray }
        Falla "La extracción quedó incompleta (falta $($faltan[0])). Revise el espacio libre en $padre y el antivirus. Registro: $log"
    }

    # 3) Ubicar los archivos en $HadoopHome (se conserva data\ si ya existía)
    if (-not (Test-Path $HadoopHome)) {
        Rename-Item $extraido (Split-Path -Leaf $HadoopHome)
    } else {
        Write-Host "    Copiando los archivos a $HadoopHome ..."
        & robocopy.exe $extraido $HadoopHome /E /MOVE /IS /IT /NFL /NDL /NJH /NJS /NP | Out-Null
        if ($LASTEXITCODE -ge 8) { Falla "No se pudieron copiar los archivos a $HadoopHome (código robocopy $LASTEXITCODE). Cierre ventanas o programas que usen esa carpeta." }
        Remove-Item $extraido -Recurse -Force -ErrorAction SilentlyContinue
    }
    $faltan = @(Faltantes $HadoopHome)
    if ($faltan.Count -gt 0) { Falla "Hadoop no quedó completo en $HadoopHome (falta $($faltan[0]))." }
    Ok "Hadoop instalado completo en $HadoopHome"
}

# Variables de otras instalaciones (por ejemplo de Spark) pueden apuntar a otra carpeta
foreach ($v in "HADOOP_COMMON_HOME", "HADOOP_HDFS_HOME", "HADOOP_YARN_HOME", "HADOOP_MAPRED_HOME", "HADOOP_CLASSPATH") {
    foreach ($ambito in "Machine", "User") {
        $valor = [Environment]::GetEnvironmentVariable($v, $ambito)
        if ($valor) {
            Aviso "Se elimina la variable $v=$valor ($ambito), que puede confundir a Hadoop."
            [Environment]::SetEnvironmentVariable($v, $null, $ambito)
        }
    }
    Remove-Item "Env:$v" -ErrorAction SilentlyContinue
}

# Los scripts sin extensión de bin\ (hadoop, hdfs, mapred, yarn) son para Linux.
# Se eliminan para que PowerShell ejecute siempre las versiones .cmd.
foreach ($s in "hadoop", "hdfs", "mapred", "yarn") {
    Remove-Item "$HadoopHome\bin\$s" -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------------------
Paso "Instalando binarios nativos para Windows (winutils.exe, hadoop.dll)"
$locales = @($CarpetaWinutils, (Join-Path $PSScriptRoot "winutils")) | Where-Object { $_ }
foreach ($binario in @("winutils.exe", "hadoop.dll")) {
    $destino = "$HadoopHome\bin\$binario"
    if ((Test-Path $destino) -and (Get-Item $destino).Length -gt 0) { Ok "$binario (ya presente)"; continue }

    # 1) Copia local (descarga manual)
    $local = $locales | ForEach-Object { Join-Path $_ $binario } | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($local) { Copy-Item $local $destino -Force; Ok "$binario copiado desde $local"; continue }

    # 2) Descarga desde Internet, probando varias direcciones
    $listo = $false
    foreach ($base in $UrlsWinutils) {
        Write-Host "    Descargando $binario desde $base ..."
        if (Descargar "$base/$binario" $destino) { $listo = $true; break }
    }
    if (-not $listo) {
        Falla @"
No se pudo descargar $binario (la red puede estar bloqueando GitHub).
         Solución manual:
         1. En otro equipo o red, descargar winutils.exe y hadoop.dll de
            https://github.com/cdarlint/winutils/tree/master/hadoop-$Version/bin
            (abrir cada archivo y pulsar 'Download raw file').
         2. Copiarlos en la carpeta  $(Join-Path $PSScriptRoot "winutils")
         3. Ejecutar de nuevo este script.
"@
    }
    Ok "$binario"
}

# ---------------------------------------------------------------------------
Paso "Copiando la configuración del taller"
$conf = "$HadoopHome\etc\hadoop"
$rutaDatos = ($HadoopHome -replace "\\", "/")             # C:/hadoop
foreach ($xml in Get-ChildItem "$PSScriptRoot\conf\*.xml") {
    $contenido = (Get-Content $xml.FullName -Raw) -replace "C:/hadoop", $rutaDatos
    Set-Content -Path "$conf\$($xml.Name)" -Value $contenido -Encoding ASCII
    Ok $xml.Name
}
$envCmd = "$conf\hadoop-env.cmd"
(Get-Content $envCmd) -replace '^set JAVA_HOME=.*$', "set JAVA_HOME=$javaHome" | Set-Content $envCmd -Encoding ASCII
Ok "hadoop-env.cmd -> JAVA_HOME=$javaHome"

# ---------------------------------------------------------------------------
Paso "Definiendo variables de entorno del sistema"
[Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome, "Machine")
[Environment]::SetEnvironmentVariable("HADOOP_HOME", $HadoopHome, "Machine")
[Environment]::SetEnvironmentVariable("HADOOP_CONF_DIR", $conf, "Machine")
$pathMaquina = [Environment]::GetEnvironmentVariable("Path", "Machine")
foreach ($p in @("$HadoopHome\bin", "$HadoopHome\sbin", "$javaHome\bin")) {
    if (($pathMaquina -split ";") -notcontains $p) { $pathMaquina = "$pathMaquina;$p" }
}
[Environment]::SetEnvironmentVariable("Path", $pathMaquina, "Machine")
$env:JAVA_HOME = $javaHome; $env:HADOOP_HOME = $HadoopHome; $env:HADOOP_CONF_DIR = $conf
$env:Path = "$env:Path;$HadoopHome\bin;$HadoopHome\sbin;$javaHome\bin"
Ok "JAVA_HOME, HADOOP_HOME, HADOOP_CONF_DIR y Path actualizados"

# ---------------------------------------------------------------------------
Paso "Creando carpetas de datos y formateando el NameNode"
foreach ($d in @("data\dfs\namenode", "data\dfs\datanode", "data\tmp", "data\yarn\local", "data\yarn\logs")) {
    New-Item -ItemType Directory -Force -Path "$HadoopHome\$d" | Out-Null
}
if (Test-Path "$HadoopHome\data\dfs\namenode\current") {
    Ok "El NameNode ya estaba formateado (no se borra HDFS)"
} else {
    & "$HadoopHome\bin\hdfs.cmd" namenode -format -force -nonInteractive 2>&1 | Select-String "successfully formatted|ERROR" | ForEach-Object { Write-Host "    $_" }
    if (-not (Test-Path "$HadoopHome\data\dfs\namenode\current")) { Falla "No se pudo formatear el NameNode. Ejecute:  hdfs namenode -format   en una terminal nueva de administrador y revise el mensaje." }
    Ok "NameNode formateado"
}

# ---------------------------------------------------------------------------
Paso "Verificación final"
& "$HadoopHome\bin\hadoop.cmd" version | Select-Object -First 1 | ForEach-Object { Ok $_ }
$nativo = (& "$HadoopHome\bin\hadoop.cmd" checknative 2>&1) -join "`n"
if ($nativo -match "hadoop:\s+true") { Ok "Librería nativa hadoop.dll cargada" }
else { Aviso "hadoop.dll no se cargó. Instale 'Microsoft Visual C++ Redistributable' (x64) y vuelva a verificar con: hadoop checknative" }

Write-Host @"

Instalación terminada.
IMPORTANTE: cierre esta ventana y abra una NUEVA terminal como administrador
para que las variables de entorno tomen efecto. Luego ejecute:

    .\instalacion\iniciar_hadoop.cmd

y verifique en el navegador:
    HDFS: http://localhost:9870      YARN: http://localhost:8088
"@ -ForegroundColor Green
