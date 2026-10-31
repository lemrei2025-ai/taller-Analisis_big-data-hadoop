# Taller guiado: Modelo de capas de Big Data con Hadoop y MapReduce en Windows

Taller práctico en el que cada estudiante selecciona una empresa de su contexto, diseña una base de datos de clientes que integra **datos multimodales** (estructurados, texto, imágenes, video y voz) e implementa, de principio a fin, el **modelo de capas de Big Data** sobre **Windows 10/11**, con herramientas instaladas de forma nativa:

| Capa | Actividad | Herramienta en el taller |
|---|---|---|
| 1. Recopilación de datos | Identificar fuentes y obtener los datos de clientes | Python (generador sintético / extracción de metadatos) |
| 2. Almacenamiento | Organizar un *data lake* distribuido | **Apache Hadoop 3.3.6 – HDFS** |
| 3. Análisis y procesamiento | Transformar y agregar los datos en paralelo | **Hadoop MapReduce** (Streaming con Python) sobre YARN |
| 4. Acceso y comunicación | Exponer los resultados a usuarios y aplicaciones | WebHDFS, SQLite + DB Browser, API REST, reporte con gráficos |
| 5. Análisis de la información | Interpretar resultados y proponer decisiones | Informe analítico |

El repositorio incluye un **caso resuelto de ejemplo** con la empresa ficticia **Café Andino S.A.S.**, una cadena de tiendas de café con presencia en varias ciudades de Colombia. El estudiante lo ejecuta primero para comprender el flujo completo y luego lo adapta a la empresa que haya elegido.

---

## Objetivos de aprendizaje

Al finalizar el taller, el estudiante estará en capacidad de:

1. Caracterizar una empresa real desde la perspectiva de sus datos de clientes y las *5 V* del Big Data.
2. Diseñar un modelo de datos que combine información estructurada y no estructurada (texto, imagen, video, voz).
3. Instalar y configurar Hadoop en Windows, organizar un *data lake* por zonas y operar HDFS por línea de comandos y web.
4. Programar trabajos MapReduce (mapper, combiner, reducer) y ejecutarlos sobre YARN.
5. Publicar los resultados mediante distintos mecanismos de acceso (WebHDFS, SQL, API REST, reporte).
6. Interpretar los resultados y transformarlos en recomendaciones para la empresa.

---

## Herramientas que se instalan

Todas se instalan con su instalador para Windows; Hadoop se instala con el script incluido en el repositorio. El paso a paso está en [`docs/instalacion_windows.md`](docs/instalacion_windows.md).

| Herramienta | Versión recomendada | Uso en el taller |
|---|---|---|
| Eclipse Temurin JDK | 8 (LTS), 64 bits | Requisito de Hadoop |
| Python | 3.11 o superior, 64 bits | Generador de datos, MapReduce, acceso |
| Microsoft Visual C++ Redistributable | 2015–2022, x64 | Requisito de `hadoop.dll` |
| Git for Windows | Última | Clonar el repositorio y versionar el trabajo |
| Apache Hadoop + winutils | 3.3.6 | HDFS, YARN y MapReduce |
| DB Browser for SQLite | Última | Consultar la base de datos de resultados |
| Visual Studio Code (opcional) | Última | Editar el código |

**Requisitos del equipo:** Windows 10 u 11 de 64 bits, 8 GB de RAM (mínimo), 6 GB libres en el disco C: y permisos de administrador.

---

## Estructura del repositorio

```text
taller-big-data-hadoop\
├── README.md                        ← este documento
├── requirements.txt                 ← librerías de Python
├── docs\                            ← GUÍA DEL TALLER (leer en orden)
│   ├── instalacion_windows.md       ← instalación de todas las herramientas
│   ├── 00_introduccion.md
│   ├── 01_recopilacion.md
│   ├── 02_almacenamiento_hadoop.md
│   ├── 03_procesamiento_mapreduce.md
│   ├── 04_acceso_comunicacion.md
│   ├── 05_analisis_resultados.md
│   ├── 06_entregables_rubrica.md
│   ├── anexo_solucion_problemas.md
│   └── img\
├── instalacion\                     ← instalador y configuración de Hadoop para Windows
│   ├── instalar_hadoop_windows.ps1
│   ├── verificar_instalacion.ps1
│   ├── diagnostico_hadoop.ps1
│   ├── winutils\                    (winutils.exe y hadoop.dll para Windows)
│   ├── iniciar_hadoop.cmd
│   ├── detener_hadoop.cmd
│   └── conf\                        (core, hdfs, mapred y yarn-site.xml)
├── empresa_ejemplo\                 ← ficha del caso Café Andino S.A.S.
├── modelo_datos\                    ← diseño de la base de datos multimodal
├── recopilacion\                    ← CAPA 1
├── datos\raw\                       ← datos generados (no se versionan)
├── mapreduce\                       ← CAPA 3: seis trabajos MapReduce en Python
├── scripts\                         ← automatización de las capas 2, 3 y 4 (PowerShell)
│   ├── trabajos.json                (definición de entradas y trabajos)
│   ├── probar_local.py              (prueba de MapReduce sin Hadoop)
│   ├── 01_cargar_hdfs.ps1
│   ├── 02_ejecutar_mapreduce.ps1
│   ├── 03_exportar_resultados.ps1
│   └── webhdfs_ejemplos.ps1
├── acceso\                          ← CAPA 4: SQLite, API REST y reporte
├── plantillas\                      ← plantillas para el estudiante
├── evidencias\                      ← capturas de pantalla del estudiante
└── resultados\                      ← salidas de MapReduce y reportes (no se versionan)
```

---

## Inicio rápido (caso de ejemplo)

Resumen de los comandos en orden. Todos se ejecutan en **PowerShell como administrador**, desde la carpeta del repositorio. La explicación detallada de cada uno está en la [Guía de comandos](#guía-de-comandos-qué-hace-cada-uno).

```powershell
# 0. Obtener el repositorio en una ruta SIN espacios ni tildes
cd C:\
git clone https://github.com/<usuario>/taller-big-data-hadoop.git
cd C:\taller-big-data-hadoop
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned   # solo la primera vez
pip install -r requirements.txt

# Instalar Hadoop (una sola vez; requiere JDK y Python ya instalados)
.\instalacion\instalar_hadoop_windows.ps1
#   -> cerrar PowerShell y abrir una nueva ventana como administrador

# 1. RECOPILACIÓN: generar los datos multimodales de Café Andino S.A.S.
python recopilacion\generar_datos.py
python scripts\probar_local.py              # (opcional) prueba de MapReduce sin Hadoop

# 2. ALMACENAMIENTO: iniciar Hadoop y cargar el data lake en HDFS
.\instalacion\iniciar_hadoop.cmd
.\instalacion\verificar_instalacion.ps1
.\scripts\01_cargar_hdfs.ps1

# 3. PROCESAMIENTO: ejecutar los trabajos MapReduce en YARN
.\scripts\02_ejecutar_mapreduce.ps1

# 4. ACCESO Y COMUNICACIÓN
.\scripts\03_exportar_resultados.ps1
.\scripts\webhdfs_ejemplos.ps1
python acceso\cargar_sqlite.py
python acceso\generar_reporte.py
python acceso\api_resultados.py             # http://localhost:8000  (Ctrl+C para detener)

# 5. ANÁLISIS: leer resultados\reporte_resultados.md y completar plantillas\informe_final.md

# Al terminar la sesión
.\instalacion\detener_hadoop.cmd
```

Interfaces web disponibles mientras Hadoop está en ejecución:

| Servicio | URL |
|---|---|
| HDFS (NameNode) | http://localhost:9870 |
| YARN (ResourceManager) | http://localhost:8088 |
| Historial de trabajos MapReduce | http://localhost:19888 |
| API de resultados | http://localhost:8000 |

---

## Guía de comandos: qué hace cada uno

Esta sección explica, en orden de uso, **qué hace internamente** cada comando del taller, **qué se debe observar** en pantalla y dónde está la **documentación oficial** de cada herramienta. Se recomienda leerla antes de ejecutar cada paso.

> **Convenciones.** Los comandos se escriben en **PowerShell como administrador**, ubicados en la carpeta del repositorio (`cd C:\taller-big-data-hadoop`). `.\` significa "en la carpeta actual". En las rutas de **Windows** se usa `\` (`datos\raw\clientes.csv`); en las rutas de **HDFS** se usa `/` (`/datalake/raw`). Las líneas de Hadoop marcadas como `INFO` o `WARN` son normales; los fallos aparecen como `ERROR` o `Exception`.

### Preparación del equipo (una sola vez)

| Comando | Qué hace |
|---|---|
| `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` | Permite que PowerShell ejecute scripts `.ps1` creados localmente o desbloqueados. Por seguridad, Windows los bloquea por defecto. |
| `Unblock-File .\instalacion\*.ps1, .\scripts\*.ps1` | Quita la marca de "descargado de Internet" que Windows pone a los archivos que vienen en un ZIP, para que puedan ejecutarse. |
| `pip install -r requirements.txt` | Instala las librerías de Python que usa el taller: `matplotlib` (gráficos) y `Pillow` (lectura de imágenes). `pip` es el gestor de paquetes de Python. |
| `.\instalacion\instalar_hadoop_windows.ps1` | Instala Hadoop: verifica Java y Python; descarga Hadoop 3.3.6 y comprueba que el archivo esté completo (SHA-512); lo extrae en `C:\hadoop`; copia `winutils.exe` y `hadoop.dll` (necesarios para que Hadoop funcione en Windows); copia la configuración del taller (`instalacion\conf\*.xml`) a `C:\hadoop\etc\hadoop`; define `JAVA_HOME`, `HADOOP_HOME` y `Path`; crea `C:\hadoop\data` y **formatea el NameNode**, es decir, crea un sistema de archivos HDFS vacío. Al terminar se debe abrir una terminal nueva. |
| `.\instalacion\verificar_instalacion.ps1` | Revisa, sin cambiar nada, que cada herramienta responda y que los cinco servicios de Hadoop estén en ejecución. Muestra `[OK]` o `[X]` con la solución sugerida. |
| `.\instalacion\diagnostico_hadoop.ps1` | Si algo falla, reúne variables de entorno, versión de Java, contenido de `C:\hadoop` y el error completo en `diagnostico_hadoop.txt` para pedir ayuda. |

### Encender y apagar Hadoop (cada sesión)

| Comando | Qué hace |
|---|---|
| `.\instalacion\iniciar_hadoop.cmd` | Ejecuta `start-dfs.cmd` (inicia **NameNode** y **DataNode**, los servicios de HDFS) y `start-yarn.cmd` (inicia **ResourceManager** y **NodeManager**, los servicios de YARN que ejecutan los trabajos); luego inicia el **JobHistory Server** (historial de trabajos). Cada servicio abre su propia ventana negra, que **no debe cerrarse**. Por último espera a que HDFS salga del "modo seguro" y lista los procesos con `jps`. |
| `jps` | Herramienta de Java que lista los procesos Java en ejecución. Deben aparecer `NameNode`, `DataNode`, `ResourceManager`, `NodeManager` y `JobHistoryServer`. |
| `.\instalacion\detener_hadoop.cmd` | Detiene YARN, HDFS y el historial. Los datos guardados en HDFS **se conservan** para la siguiente sesión. |

### Capa 1 · Recopilación

| Comando | Qué hace |
|---|---|
| `python recopilacion\generar_datos.py` | Crea en `datos\raw\` los datos de la empresa de ejemplo: clientes, sucursales, productos y transacciones (CSV, datos estructurados); reseñas (texto); metadatos de fotos (imagen); métricas y transcripciones de videos (video); y llamadas transcritas (voz), en formato JSON Lines, un registro por línea. Siempre genera los mismos datos (semilla fija), de modo que todos los estudiantes obtienen los mismos resultados. |
| `python recopilacion\generar_datos.py --escala 20` | Genera 20 veces más registros (~110 MB de transacciones), para observar cómo HDFS divide un archivo en varios bloques y cómo MapReduce lanza varias tareas map. |
| `python recopilacion\extraer_metadatos_multimedia.py imagenes <carpeta> <salida.jsonl>` | (Opcional) Lee fotos, videos o audios **reales** de una carpeta y extrae sus metadatos (formato, dimensiones, duración, tamaño) al mismo formato JSON que usan los trabajos MapReduce. |
| `python scripts\probar_local.py` | **Simula MapReduce sin Hadoop**: para cada trabajo pasa los datos por `mapper.py`, ordena los pares por clave (como el *shuffle & sort* de Hadoop) y entrega el resultado a `reducer.py`. Guarda las salidas en `resultados\local\`. Sirve para encontrar errores de Python antes de usar el clúster. Variantes: `--ver-map ventas_mes` muestra lo que emite el mapper; `ventas_mes DIMENSION=medio_pago` cambia una variable. |

### Capa 2 · Almacenamiento (HDFS)

**`.\scripts\01_cargar_hdfs.ps1`** construye el data lake. Internamente ejecuta:

1. `hdfs dfs -mkdir -p /datalake/raw /datalake/staged /datalake/curated ...` → crea las zonas del data lake en HDFS.
2. `hdfs dfs -put -f datos\raw\<archivo> /datalake/raw/<zona>/` → copia cada archivo de Windows a HDFS (`-f` sobrescribe si ya existe). HDFS lo parte en bloques de 32 MB y los guarda en el DataNode (`C:\hadoop\data\dfs\datanode`). Las rutas de destino están en `scripts\trabajos.json`.
3. `hdfs dfs -ls -R /datalake/raw` → lista todo lo cargado.
4. `hdfs dfs -du -h /datalake/raw` → muestra el espacio ocupado.
5. `hdfs fsck <ruta> -files -blocks` → muestra en cuántos bloques quedó cada archivo y sus réplicas.

*Qué observar:* las carpetas en http://localhost:9870 → *Utilities* → *Browse the file system*.

Comandos de HDFS para practicar manualmente:

| Comando | Qué hace |
|---|---|
| `hdfs dfs -ls /datalake/raw` | Lista una carpeta de HDFS |
| `hdfs dfs -cat /datalake/raw/estructurados/sucursales/sucursales.csv` | Muestra el contenido de un archivo |
| `hdfs dfs -put <local> <hdfs>` / `hdfs dfs -get <hdfs> <local>` | Sube un archivo de Windows a HDFS / lo descarga |
| `hdfs dfs -mkdir -p <ruta>` / `hdfs dfs -rm -r <ruta>` | Crea / elimina carpetas |
| `hdfs dfs -du -h <ruta>` | Tamaño ocupado |
| `hdfs dfsadmin -report` | Estado del clúster: capacidad, DataNodes vivos, espacio libre |
| `hdfs fsck <ruta> -files -blocks -locations` | Bloques, réplicas y en qué DataNode está cada bloque |

### Capa 3 · Procesamiento (MapReduce)

**`.\scripts\02_ejecutar_mapreduce.ps1`** ejecuta los 11 trabajos definidos en `scripts\trabajos.json`. Antes de cada trabajo muestra en pantalla qué hace, sus entradas, su salida y el comando exacto. Para cada trabajo:

1. `hdfs dfs -rm -r -f /datalake/curated/<trabajo>` → borra la salida anterior (MapReduce no sobrescribe resultados).
2. Lanza **Hadoop Streaming**, la herramienta que permite escribir el mapper y el reducer en Python:

   ```text
   hadoop jar hadoop-streaming-3.3.6.jar            ← programa de Hadoop que ejecuta el trabajo
     -D mapreduce.job.name=taller-<trabajo>         ← nombre visible en http://localhost:8088
     -D mapreduce.job.reduces=1                     ← un solo reducer → un solo archivo de salida
     -files job1_ventas/mapper.py,...               ← archivos que Hadoop copia a cada tarea
     -mapper  "python mapper.py"                    ← programa que ejecuta cada tarea MAP
     -reducer "python reducer.py"                   ← programa que ejecuta la tarea REDUCE
     -combiner "python reducer.py"                  ← (algunos trabajos) pre-suma dentro de cada map
     -cmdenv DIMENSION=mes                          ← variable de entorno que lee el script
     -input  /datalake/raw/...                      ← carpeta(s) de entrada en HDFS
     -output /datalake/curated/<trabajo>            ← carpeta de salida en HDFS
   ```

3. Hadoop ejecuta el trabajo:
   - **Map:** cada bloque de entrada se procesa con `python mapper.py`, que lee línea por línea y escribe pares `clave<TAB>valor`.
   - **Shuffle & Sort:** Hadoop agrupa y ordena todos los pares por clave.
   - **Reduce:** `python reducer.py` recibe los pares ordenados y calcula totales, promedios o conteos por clave.
4. Muestra las primeras líneas del resultado (`/datalake/curated/<trabajo>/part-00000`).

*Qué observar en la consola:*

| Línea en pantalla | Significado |
|---|---|
| `Running job: job_17..._0001` | El trabajo fue aceptado por YARN y recibió un identificador |
| `map 0% reduce 0%` … `map 100% reduce 100%` | Avance de las fases map y reduce |
| `Job job_... completed successfully` | El trabajo terminó bien |
| `Map input records=30001` | Líneas leídas de la entrada |
| `Map output records=30000` | Pares clave–valor emitidos por el mapper |
| `Reduce input groups=12` | Claves distintas (por ejemplo, 12 meses) |
| `Reduce output records=12` | Líneas del resultado |
| `Output directory ... already exists` / `subprocess failed with code 1` | Errores: ver `docs\anexo_solucion_problemas.md` |

*Qué observar en el navegador:* http://localhost:8088 muestra los trabajos en curso y terminados; http://localhost:19888 muestra el historial, la duración de cada tarea y los registros de error de Python.

Variantes:

| Comando | Qué hace |
|---|---|
| `.\scripts\02_ejecutar_mapreduce.ps1 -Trabajo ventas_mes` | Ejecuta solo uno (o varios separados por coma) |
| `.\scripts\02_ejecutar_mapreduce.ps1 -Modo local` | Ejecuta MapReduce en un solo proceso, sin YARN, pero leyendo y escribiendo en HDFS. Plan alternativo si YARN falla. |

Los 11 trabajos que se ejecutan:

| Trabajo | Modalidad | Qué calcula |
|---|---|---|
| `ventas_ciudad_categoria` | Estructurado | Ventas, unidades y ticket promedio por ciudad y categoría |
| `ventas_mes` | Estructurado | Totales por mes (estacionalidad) |
| `ventas_sucursal` | Estructurado | Totales por sucursal |
| `sentimiento_sucursal` | Texto + Voz | Reseñas y llamadas positivas, negativas y neutras por sucursal |
| `palabras_frecuentes` | Texto + Voz + Video | Frecuencia de cada palabra |
| `bigramas_quejas` | Texto | Pares de palabras más comunes en reseñas de 1–2 estrellas |
| `imagenes_etiquetas` | Imagen | Fotos por etiqueta detectada y sentimiento visual |
| `imagenes_ciudad_etiqueta` | Imagen | Lo mismo, por ciudad |
| `videos_campanas` | Video | Reproducciones, engagement y retención por campaña y plataforma |
| `llamadas_motivo` | Voz | Llamadas, duración media y % resuelto por motivo |
| `llamadas_sucursal` | Voz | Lo mismo, por sucursal |

### Capa 4 · Acceso y comunicación

| Comando | Qué hace |
|---|---|
| `.\scripts\03_exportar_resultados.ps1` | Para cada trabajo terminado (carpeta con el archivo `_SUCCESS`) ejecuta `hdfs dfs -getmerge`, que une los archivos `part-*` de HDFS en un solo `.tsv` en `resultados\hadoop\` (en Windows). |
| `.\scripts\webhdfs_ejemplos.ps1` | Consulta HDFS **por HTTP** (API REST WebHDFS), sin usar comandos de Hadoop: lista la zona curada (`op=LISTSTATUS`), resume el espacio (`op=GETCONTENTSUMMARY`), lee un resultado (`op=OPEN`) y muestra metadatos de un archivo (`op=GETFILESTATUS`). Así es como otra aplicación accedería a los datos. |
| `python acceso\cargar_sqlite.py` | Crea la base de datos `resultados\analitica.db` (SQLite) con una tabla por resultado y la vista `v_tablero_sucursal`, que une ventas, reseñas y llamadas por sucursal. Usa `resultados\hadoop\` si existe; si no, `resultados\local\`. |
| **DB Browser for SQLite** → *Abrir base de datos* → `resultados\analitica.db` → *Ejecutar SQL* | Permite consultar los resultados con SQL de forma gráfica. |
| `python acceso\api_resultados.py` | Inicia un servidor web en http://localhost:8000 que entrega los resultados en formato JSON (`/tablero`, `/resultados/<tabla>?orden=...&limite=...`). Simula cómo una app o un tablero consumiría los datos. Se detiene con `Ctrl+C`. |
| `python acceso\generar_reporte.py` | Lee los resultados, dibuja 7 gráficos (`resultados\graficos\*.png`) y escribe `resultados\reporte_resultados.md` con tablas y gráficos, que es el insumo de la capa 5. |

### Capa 5 · Análisis

No requiere comandos: se interpreta `resultados\reporte_resultados.md` siguiendo [`docs/05_analisis_resultados.md`](docs/05_analisis_resultados.md) y se completa [`plantillas/informe_final.md`](plantillas/informe_final.md).

---

## Documentación de referencia

### Apache Hadoop 3.3.6 (documentación oficial)

| Tema | Enlace |
|---|---|
| Instalación de un nodo único (*pseudo-distributed*) | https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-common/SingleCluster.html |
| Arquitectura de HDFS (NameNode, DataNode, bloques, réplicas) | https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html |
| Comandos `hdfs dfs` (ls, put, get, cat, du, rm…) | https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-common/FileSystemShell.html |
| Comandos de administración (`dfsadmin`, `fsck`, `namenode -format`) | https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html |
| Guía de usuario de HDFS | https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html |
| Tutorial de MapReduce (map, combiner, reduce, contadores) | https://hadoop.apache.org/docs/r3.3.6/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html |
| Hadoop Streaming (`-mapper`, `-reducer`, `-files`, `-cmdenv`) | https://hadoop.apache.org/docs/r3.3.6/hadoop-streaming/HadoopStreaming.html |
| Arquitectura de YARN (ResourceManager, NodeManager) | https://hadoop.apache.org/docs/r3.3.6/hadoop-yarn/hadoop-yarn-site/YARN.html |
| Comandos de YARN (`yarn application`, `yarn logs`) | https://hadoop.apache.org/docs/r3.3.6/hadoop-yarn/hadoop-yarn-site/YarnCommands.html |
| API REST WebHDFS | https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/WebHDFS.html |
| Manual general de comandos (`hadoop jar`, `-D`, `-files`) | https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-common/CommandsManual.html |
| Problemas de Hadoop en Windows (winutils) | https://cwiki.apache.org/confluence/display/HADOOP2/WindowsProblems |
| Binarios `winutils.exe` / `hadoop.dll` | https://github.com/cdarlint/winutils |

### Artículos fundacionales

- Dean, J. y Ghemawat, S. (2004). *MapReduce: Simplified Data Processing on Large Clusters*. OSDI. https://research.google/pubs/pub62/
- Ghemawat, S., Gobioff, H. y Leung, S.-T. (2003). *The Google File System*. SOSP. https://doi.org/10.1145/945445.945450
- Shvachko, K., Kuang, H., Radia, S. y Chansler, R. (2010). *The Hadoop Distributed File System*. IEEE MSST. https://doi.org/10.1109/MSST.2010.5496972

### Otras herramientas

| Herramienta | Enlace |
|---|---|
| Eclipse Temurin (Java) | https://adoptium.net/es/ |
| Python: lectura de entrada estándar, `csv`, `json` | https://docs.python.org/es/3/library/sys.html · https://docs.python.org/es/3/library/csv.html · https://docs.python.org/es/3/library/json.html |
| Python: `sqlite3` y `http.server` | https://docs.python.org/es/3/library/sqlite3.html · https://docs.python.org/es/3/library/http.server.html |
| SQLite (lenguaje SQL) | https://www.sqlite.org/lang.html |
| DB Browser for SQLite | https://sqlitebrowser.org/ |
| Matplotlib | https://matplotlib.org/stable/ |
| PowerShell: políticas de ejecución | https://learn.microsoft.com/es-es/powershell/module/microsoft.powershell.core/about/about_execution_policies |
| PowerShell: `Invoke-RestMethod` | https://learn.microsoft.com/es-es/powershell/module/microsoft.powershell.utility/invoke-restmethod |
| Formato JSON Lines | https://jsonlines.org/ |
| Ley 1581 de 2012 (protección de datos personales, Colombia) | http://www.secretariasenado.gov.co/senado/basedoc/ley_1581_2012.html |

---

## Ruta de trabajo sugerida

| Sesión | Contenido | Guía |
|---|---|---|
| 0 (previa) | Instalación de las herramientas | [Instalación en Windows](docs/instalacion_windows.md) |
| 1 | Conceptos, selección de la empresa y diseño del modelo de datos | [00](docs/00_introduccion.md), [01](docs/01_recopilacion.md) |
| 2 | Inicio de Hadoop y construcción del data lake | [02](docs/02_almacenamiento_hadoop.md) |
| 3 | Programación y ejecución de MapReduce | [03](docs/03_procesamiento_mapreduce.md) |
| 4 | Acceso a los datos y comunicación de resultados | [04](docs/04_acceso_comunicacion.md) |
| 5 | Análisis, informe y sustentación | [05](docs/05_analisis_resultados.md), [06](docs/06_entregables_rubrica.md) |

---

## Entregables

1. Repositorio propio (*fork*) con el caso adaptado a la empresa seleccionada.
2. Modelo de datos multimodal (diagrama E-R, diccionario de datos y organización del data lake).
3. Evidencias de ejecución en Hadoop (capturas de HDFS, YARN y JobHistory).
4. Código de los trabajos MapReduce (al menos uno nuevo, diseñado por el estudiante).
5. Informe final de análisis usando [`plantillas/informe_final.md`](plantillas/informe_final.md).

Los criterios de evaluación se encuentran en [`docs/06_entregables_rubrica.md`](docs/06_entregables_rubrica.md). Ante cualquier error, consultar [`docs/anexo_solucion_problemas.md`](docs/anexo_solucion_problemas.md).

---

## Licencia

Material educativo distribuido bajo licencia MIT (ver [`LICENSE`](LICENSE)). Los datos de Café Andino S.A.S. son completamente sintéticos; cualquier parecido con una empresa real es coincidencia.
