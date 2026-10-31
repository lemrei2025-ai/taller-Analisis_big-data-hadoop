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

Todos los comandos se ejecutan en **PowerShell como administrador**, desde la carpeta del repositorio.

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
