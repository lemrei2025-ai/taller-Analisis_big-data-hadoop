<#
.SYNOPSIS
    CAPA 2 - ALMACENAMIENTO. Crea la estructura del data lake en HDFS y carga
    los datos recopilados.
.EXAMPLE
    .\scripts\01_cargar_hdfs.ps1
#>
. (Join-Path $PSScriptRoot "comun.ps1")

Write-Host @"

=====================================================================
 CAPA 2 - ALMACENAMIENTO EN HDFS
=====================================================================
 Este script:
   1. Crea en HDFS las zonas del data lake: raw (datos crudos),
      staged (datos depurados) y curated (resultados).
   2. Copia cada archivo de datos\raw (en Windows) a su carpeta en
      HDFS con 'hdfs dfs -put'. HDFS lo divide en bloques y los
      guarda en el DataNode (C:\hadoop\data\dfs\datanode).
   3. Muestra el contenido, el espacio usado y los bloques del
      archivo de transacciones.
 Para verlo gráficamente: http://localhost:9870 > Utilities >
 Browse the file system > /datalake
=====================================================================
"@ -ForegroundColor Yellow

Titulo "Creando zonas del data lake"
hdfs.cmd dfs -mkdir -p /datalake/raw /datalake/staged $Config.zona_curada `
    /datalake/raw/multimedia/imagenes /datalake/raw/multimedia/videos /datalake/raw/multimedia/audios
Comprobar "crear carpetas en HDFS (¿está iniciado Hadoop?)"

Titulo "Cargando datos en la zona raw"
foreach ($e in $Config.entradas.PSObject.Properties) {
    $origen = Join-Path $Raiz "datos\raw\$($e.Value.archivo)"
    $destino = $e.Value.hdfs
    if (-not (Test-Path $origen)) { Write-Host "  (omitido) no existe $origen"; continue }
    hdfs.cmd dfs -mkdir -p $destino
    hdfs.cmd dfs -put -f (Q $origen) "$destino/"
    Comprobar "cargar $origen"
    Write-Host ("  {0,-28} ->  {1}" -f $e.Value.archivo, $destino)
}

# Archivos multimedia reales (opcional): datos\multimedia\{imagenes,videos,audios}
foreach ($tipo in "imagenes", "videos", "audios") {
    $carpeta = Join-Path $Raiz "datos\multimedia\$tipo"
    if ((Test-Path $carpeta) -and (Get-ChildItem $carpeta -File)) {
        foreach ($f in Get-ChildItem $carpeta -File) {
            hdfs.cmd dfs -put -f (Q $f.FullName) "/datalake/raw/multimedia/$tipo/"
        }
        Write-Host "  datos\multimedia\$tipo  ->  /datalake/raw/multimedia/$tipo"
    }
}

Titulo "Contenido del data lake"
hdfs.cmd dfs -ls -R /datalake/raw

Titulo "Espacio utilizado"
hdfs.cmd dfs -du -h /datalake/raw

Titulo "Bloques y réplicas del archivo de transacciones"
hdfs.cmd fsck $Config.entradas.transacciones.hdfs -files -blocks 2>$null |
    Select-String "blocks|Total|replica|len="
