<#
.SYNOPSIS
    CAPA 4 - ACCESO. Ejemplos de consulta a HDFS mediante la API REST WebHDFS,
    usando solo PowerShell (no requiere clientes de Hadoop).
.EXAMPLE
    .\scripts\webhdfs_ejemplos.ps1
#>
param([string]$Servidor = "localhost:9870")
$api = "http://$Servidor/webhdfs/v1"

Write-Host "`n1) Listar la zona curada" -ForegroundColor Cyan
(Invoke-RestMethod "$api/datalake/curated?op=LISTSTATUS").FileStatuses.FileStatus |
    Select-Object pathSuffix, type, modificationTime | Format-Table -AutoSize

Write-Host "2) Resumen de espacio de la zona raw" -ForegroundColor Cyan
(Invoke-RestMethod "$api/datalake/raw?op=GETCONTENTSUMMARY").ContentSummary | Format-List

Write-Host "3) Leer el resultado de ventas por mes (el NameNode redirige al DataNode)" -ForegroundColor Cyan
$respuesta = Invoke-WebRequest "$api/datalake/curated/ventas_mes/part-00000?op=OPEN" -UseBasicParsing
[Text.Encoding]::UTF8.GetString($respuesta.RawContentStream.ToArray())

Write-Host "4) Metadatos de un archivo" -ForegroundColor Cyan
(Invoke-RestMethod "$api/datalake/raw/estructurados/transacciones/transacciones.csv?op=GETFILESTATUS").FileStatus | Format-List
