# Anexo. Solución de problemas frecuentes en Windows

## Instalación

| Síntoma | Causa probable | Solución |
|---|---|---|
| `... no se puede cargar porque la ejecución de scripts está deshabilitada en este sistema` | Política de ejecución de PowerShell | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` y `Unblock-File .\instalacion\*.ps1, .\scripts\*.ps1` |
| `python` abre la Microsoft Store o no se reconoce | Python no está en el `Path` | Reinstalar Python marcando *Add python.exe to PATH*; desactivar los alias de `python.exe` en *Alias de ejecución de aplicaciones* |
| `Files\Eclipse was unexpected at this time` o `JAVA_HOME is incorrectly set` | `JAVA_HOME` contiene espacios | Reinstalar el JDK en `C:\Java\jdk8` o volver a ejecutar `instalar_hadoop_windows.ps1` (usa la ruta corta). Revisar la línea `set JAVA_HOME=` en `C:\hadoop\etc\hadoop\hadoop-env.cmd` |
| `'hdfs' no se reconoce como un comando` | Terminal abierta antes de definir las variables | Cerrar y abrir una nueva terminal. Verificar con `echo $env:HADOOP_HOME` |
| Al escribir `hdfs` o `hadoop`, Windows pregunta con qué programa abrir el archivo | Existen en `C:\hadoop\bin` los scripts de Linux sin extensión | Eliminar `C:\hadoop\bin\hadoop`, `hdfs`, `mapred` y `yarn` (sin extensión); conservar los `.cmd` |
| `Could not locate executable null\bin\winutils.exe` | `HADOOP_HOME` no definida o falta winutils | Verificar `HADOOP_HOME=C:\hadoop` y la existencia de `C:\hadoop\bin\winutils.exe` |
| `UnsatisfiedLinkError: ...NativeIO$Windows.access0` | `hadoop.dll` no se carga | Copiar `hadoop.dll` en `C:\hadoop\bin`, instalar Visual C++ Redistributable x64 y reiniciar Hadoop. Como último recurso, copiar `hadoop.dll` también en `C:\Windows\System32` |
| `hadoop checknative` muestra `hadoop: false` | Ídem | Ídem |
| La descarga de Hadoop es muy lenta o falla | Conexión de la sala | Descargar una vez el `.tar.gz`, compartirlo y usar `instalar_hadoop_windows.ps1 -Archivo <ruta>` |

## Inicio de los servicios

| Síntoma | Causa probable | Solución |
|---|---|---|
| La ventana del DataNode se cierra o `jps` no lo muestra; en el registro aparece `Incompatible clusterIDs` | El NameNode se formateó de nuevo y el DataNode conserva el identificador anterior | Detener Hadoop, borrar la carpeta `C:\hadoop\data\dfs\datanode` y volver a iniciar |
| El NameNode no inicia: `NameNode is not formatted` | Falta el formateo inicial | `hdfs namenode -format` |
| `Name node is in safe mode` | HDFS está iniciando | Esperar un minuto o ejecutar `hdfs dfsadmin -safemode leave` |
| `Address already in use` / `BindException` | Otro programa usa los puertos 9000, 9870, 8088 o 19888 | Detener Hadoop con `detener_hadoop.cmd`; cerrar procesos `java.exe` restantes en el Administrador de tareas; identificar el puerto con `netstat -ano \| findstr :9870` |
| El NodeManager aparece como *UNHEALTHY* en http://localhost:8088 | El disco C: tiene más del 98 % ocupado | Liberar espacio en el disco |
| El Firewall de Windows muestra una alerta | Java abre puertos de red | Permitir el acceso en redes privadas |

## Ejecución de MapReduce

| Síntoma | Causa probable | Solución |
|---|---|---|
| `CreateSymbolicLink error (1314): A required privilege is not held by the client` | YARN necesita crear enlaces simbólicos | Iniciar Hadoop y ejecutar los scripts desde una terminal **como administrador**, o activar el *Modo para desarrolladores* de Windows |
| El trabajo queda en estado *ACCEPTED* sin avanzar | El NodeManager no está activo o no tiene memoria suficiente | Verificar con `jps` y en http://localhost:8088 → *Nodes*. Cerrar programas pesados |
| YARN sigue fallando después de revisar lo anterior | Restricciones del equipo (antivirus, políticas corporativas) | Ejecutar en modo local, que también lee y escribe en HDFS: `.\scripts\02_ejecutar_mapreduce.ps1 -Modo local` |
| `PipeMapRed.waitOutputThreads(): subprocess failed with code 1` | Error de Python dentro del mapper o reducer | Probar con `python scripts\probar_local.py <trabajo>`; revisar el detalle en http://localhost:19888 → trabajo → tarea fallida → *logs* (stderr) |
| `Cannot run program "python"` | Las tareas de YARN no encuentran Python | Verificar que `python` funcione en una terminal nueva y reiniciar Hadoop (el NodeManager toma el `Path` al iniciar) |
| `ModuleNotFoundError: texto_utils` | No se envió el módulo con `-files` | Agregar `comun/texto_utils.py` a la lista de `-files` |
| `Output directory ... already exists` | La carpeta de salida ya existe | `hdfs dfs -rm -r /datalake/curated/<nombre>` (el script 02 lo hace automáticamente) |
| `Unrecognized option` o `Missing required options: input, output` en una ejecución manual | `hadoop.cmd` dividió un argumento en `=` o `,` | Encerrar los valores entre comillas: `-D '"clave=valor"'`, `-files '"a.py,b.py"'` (ver sección 3.5) |
| `Container killed ... beyond physical memory limits` | La tarea usa más memoria de la asignada | Agregar `-D '"mapreduce.map.memory.mb=1024"'` |
| Caracteres extraños (`BogotÃ¡`) en los resultados | Archivo guardado con otra codificación | Guardar los datos en UTF-8 (sin usar `>` de PowerShell 5 para generar archivos) y abrir los resultados como UTF-8 |

## Comandos de diagnóstico útiles

```powershell
.\instalacion\verificar_instalacion.ps1          # verificación integral
jps                                               # servicios Java activos
hdfs dfsadmin -report                             # estado de HDFS y DataNodes
yarn node -list                                   # nodos de YARN
yarn application -list -appStates ALL             # trabajos enviados
yarn logs -applicationId <id>                     # registros de un trabajo
hadoop checknative                                # librerías nativas de Windows
Get-ChildItem C:\hadoop\logs                      # archivos de registro de los servicios
```

## Reinicio completo del entorno (borra HDFS)

```powershell
.\instalacion\detener_hadoop.cmd
Remove-Item -Recurse -Force C:\hadoop\data
.\instalacion\instalar_hadoop_windows.ps1        # recrea carpetas y formatea el NameNode
#  -> abrir una nueva terminal como administrador
.\instalacion\iniciar_hadoop.cmd
python recopilacion\generar_datos.py
.\scripts\01_cargar_hdfs.ps1
```
