# Instalación de las herramientas en Windows

**Propósito:** dejar el equipo listo para el taller con todas las herramientas instaladas de forma nativa en Windows 10/11 (64 bits).

**Duración estimada:** 45–60 minutos (la mayor parte es descarga).

> **Recomendación para el docente:** realizar esta instalación en una sesión previa o enviarla como tarea, y verificar los equipos de la sala con `instalacion\verificar_instalacion.ps1` antes de la primera clase práctica.

---

## Resumen

| # | Herramienta | Descarga | Indicaciones durante la instalación |
|---|---|---|---|
| 1 | **Eclipse Temurin JDK 8** (x64, `.msi`) | https://adoptium.net/temurin/releases/?version=8&os=windows | Cambiar la carpeta a `C:\Java\jdk8\` y activar **Set JAVA_HOME variable** |
| 2 | **Python 3.11+** (x64) | https://www.python.org/downloads/windows/ | Marcar **Add python.exe to PATH** |
| 3 | **Microsoft Visual C++ Redistributable** 2015–2022 x64 | https://aka.ms/vs/17/release/vc_redist.x64.exe | Instalación por defecto |
| 4 | **Git for Windows** | https://git-scm.com/download/win | Instalación por defecto |
| 5 | **Apache Hadoop 3.3.6 + winutils** | Script `instalacion\instalar_hadoop_windows.ps1` | Ver paso 5 |
| 6 | **DB Browser for SQLite** | https://sqlitebrowser.org/dl/ | Instalación por defecto (se usa en la capa 4) |
| 7 | Visual Studio Code (opcional) | https://code.visualstudio.com | Instalación por defecto |

### Alternativa: instalación con `winget`

En Windows 10/11 actualizados, los pasos 1 a 4 y 6 se pueden hacer desde PowerShell como administrador:

```powershell
winget install EclipseAdoptium.Temurin.8.JDK
winget install Python.Python.3.12
winget install Microsoft.VCRedist.2015+.x64
winget install Git.Git
winget install DBBrowserForSQLite.DBBrowserForSQLite
```

Con `winget`, el JDK queda en `C:\Program Files\...` (ruta con espacios). El instalador de Hadoop lo detecta y lo resuelve automáticamente usando la ruta corta de Windows.

---

## Paso 1. Java (JDK 8)

Hadoop 3.3.6 funciona con Java 8 y Java 11; el taller usa **Java 8**, la versión con mayor compatibilidad en Windows.

1. Descargar el instalador `.msi` de **Temurin 8 – JDK – Windows x64**.
2. En la pantalla **Custom Setup**:
   - Activar **Set JAVA_HOME variable** (opción *Will be installed on local hard drive*).
   - Pulsar **Browse** y cambiar la carpeta a `C:\Java\jdk8\`.

   > Hadoop para Windows **no admite espacios** en `JAVA_HOME` (por ejemplo `C:\Program Files\...`). Por eso se instala en `C:\Java\jdk8`.

3. Verificar en una **nueva** ventana de PowerShell:

   ```powershell
   java -version
   echo $env:JAVA_HOME
   ```

   Resultado esperado: `openjdk version "1.8.0_..."` y `C:\Java\jdk8\`.

## Paso 2. Python

1. Descargar el instalador de Python 3 para Windows (64 bits).
2. En la primera pantalla marcar **Add python.exe to PATH** y luego **Install Now**.
3. Al final, si aparece la opción **Disable path length limit**, pulsarla.
4. Verificar:

   ```powershell
   python --version
   pip --version
   ```

> Si `python` abre la Microsoft Store, desactivar los alias en **Configuración → Aplicaciones → Configuración avanzada de aplicaciones → Alias de ejecución de aplicaciones** (apagar `python.exe` y `python3.exe`).

## Paso 3. Visual C++ Redistributable

Instalar `vc_redist.x64.exe` con las opciones por defecto. Lo requiere la librería nativa `hadoop.dll`.

## Paso 4. Git y obtención del repositorio

1. Instalar Git for Windows con las opciones por defecto.
2. Abrir **PowerShell como administrador** (clic derecho en Inicio → *Terminal (administrador)* o *Windows PowerShell (administrador)*) y clonar el repositorio en una ruta **sin espacios ni tildes**:

   ```powershell
   cd C:\
   git clone https://github.com/<usuario>/taller-big-data-hadoop.git
   cd C:\taller-big-data-hadoop
   ```

   > Si no se usa Git, descargar el repositorio con **Code → Download ZIP** y descomprimirlo en `C:\taller-big-data-hadoop`.

3. Permitir la ejecución de los scripts del taller (solo la primera vez) e instalar las librerías de Python:

   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   Unblock-File -Path .\instalacion\*.ps1, .\scripts\*.ps1
   pip install -r requirements.txt
   ```

## Paso 5. Apache Hadoop 3.3.6

Hadoop no tiene un instalador `.msi` oficial: se distribuye como un archivo comprimido y en Windows necesita, además, dos binarios nativos (`winutils.exe` y `hadoop.dll`). El repositorio incluye un **script instalador** que realiza todo el proceso.

### 5.1 Instalación con el script (recomendada)

En PowerShell **como administrador**, desde `C:\taller-big-data-hadoop`:

```powershell
.\instalacion\instalar_hadoop_windows.ps1
```

El script:

1. Verifica Java y Python.
2. Descarga `hadoop-3.3.6.tar.gz` (~700 MB) desde el archivo oficial de Apache y lo extrae en `C:\hadoop`.
3. Descarga `winutils.exe` y `hadoop.dll` para Hadoop 3.3.6 (repositorio comunitario `cdarlint/winutils` en GitHub).
4. Copia la configuración del taller (`instalacion\conf\*.xml`) en `C:\hadoop\etc\hadoop` y ajusta `hadoop-env.cmd`.
5. Define las variables de entorno `JAVA_HOME`, `HADOOP_HOME`, `HADOOP_CONF_DIR` y agrega `C:\hadoop\bin` y `C:\hadoop\sbin` al `Path`.
6. Crea las carpetas de datos en `C:\hadoop\data` y formatea el NameNode.

Salida esperada (final):

```text
==> Verificación final
    [OK] Hadoop 3.3.6
    [OK] Librería nativa hadoop.dll cargada

Instalación terminada.
```

> **Salas con conexión lenta:** el docente descarga una sola vez `hadoop-3.3.6.tar.gz` desde https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/ , lo comparte por la red local o USB, y cada estudiante ejecuta:
> `.\instalacion\instalar_hadoop_windows.ps1 -Archivo D:\hadoop-3.3.6.tar.gz`

**Cerrar PowerShell y abrir una nueva ventana como administrador** para que las variables de entorno tomen efecto.

### 5.2 Instalación manual (para comprender cada paso)

Si el docente prefiere que los estudiantes realicen la instalación paso a paso, o si el script falla:

1. **Descargar** `hadoop-3.3.6.tar.gz` desde https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/
2. **Extraer** como administrador con 7-Zip (dos veces: `.gz` y luego `.tar`) o con el comando `tar -xzf hadoop-3.3.6.tar.gz -C C:\`. Renombrar la carpeta resultante a `C:\hadoop`. Los avisos sobre enlaces simbólicos (`lib\native\*.so`) pueden ignorarse.
3. **Copiar** `winutils.exe` y `hadoop.dll` de la carpeta `hadoop-3.3.6/bin` del repositorio https://github.com/cdarlint/winutils en `C:\hadoop\bin`.
4. **Configurar** copiando los cuatro archivos de `instalacion\conf\` del taller en `C:\hadoop\etc\hadoop\`.
5. **Editar** `C:\hadoop\etc\hadoop\hadoop-env.cmd` y cambiar la línea `set JAVA_HOME=%JAVA_HOME%` por `set JAVA_HOME=C:\Java\jdk8`.
6. **Variables de entorno**: *Panel de control → Sistema → Configuración avanzada del sistema → Variables de entorno → Variables del sistema*:

   | Variable | Valor |
   |---|---|
   | `JAVA_HOME` | `C:\Java\jdk8` |
   | `HADOOP_HOME` | `C:\hadoop` |
   | `HADOOP_CONF_DIR` | `C:\hadoop\etc\hadoop` |
   | `Path` (agregar) | `C:\hadoop\bin` y `C:\hadoop\sbin` |

7. **Crear** las carpetas `C:\hadoop\data\dfs\namenode`, `C:\hadoop\data\dfs\datanode`, `C:\hadoop\data\tmp`, `C:\hadoop\data\yarn\local` y `C:\hadoop\data\yarn\logs`.
8. **Eliminar** de `C:\hadoop\bin` los archivos sin extensión `hadoop`, `hdfs`, `mapred` y `yarn` (son para Linux y confunden a PowerShell).
9. **Formatear** el NameNode en una nueva ventana de administrador:

   ```powershell
   hdfs namenode -format
   ```

   Debe aparecer `Storage directory C:\hadoop\data\dfs\namenode has been successfully formatted`.

## Paso 6. Primer arranque y verificación

En PowerShell **como administrador**:

```powershell
cd C:\taller-big-data-hadoop
.\instalacion\iniciar_hadoop.cmd
```

Se abren varias ventanas negras (una por servicio: NameNode, DataNode, ResourceManager, NodeManager y JobHistory). **No se deben cerrar** mientras se trabaja. Si el Firewall de Windows lo solicita, permitir el acceso de *Java(TM) Platform SE binary* en redes privadas.

Luego:

```powershell
.\instalacion\verificar_instalacion.ps1
```

Resultado esperado:

```text
== Herramientas ==
[OK] Java (JDK)                   openjdk version "1.8.0_..."
[OK] JAVA_HOME                    C:\Java\jdk8
[OK] Python                       Python 3.12.x
[OK] HADOOP_HOME                  C:\hadoop
[OK] Hadoop                       Hadoop 3.3.6
[OK] winutils.exe                 presente
[OK] hadoop.dll nativa            cargada
[OK] matplotlib                   matplotlib 3.x

== Servicios de Hadoop ==
[OK] NameNode                     en ejecución
[OK] DataNode                     en ejecución
[OK] ResourceManager              en ejecución
[OK] NodeManager                  en ejecución
[OK] JobHistoryServer             en ejecución
[OK] HDFS web (9870)              http://localhost:9870
[OK] YARN web (8088)              http://localhost:8088
[OK] Historial (19888)            http://localhost:19888
```

Finalmente, abrir en el navegador http://localhost:9870 (debe mostrar 1 DataNode *In Service*) y http://localhost:8088 (debe mostrar 1 nodo *RUNNING*).

Para detener Hadoop al terminar cada sesión:

```powershell
.\instalacion\detener_hadoop.cmd
```

## ¿Por qué ejecutar como administrador?

Cuando YARN ejecuta una tarea, crea **enlaces simbólicos** hacia los archivos del trabajo (scripts, léxicos). En Windows esa operación requiere privilegios de administrador; sin ellos aparece el error `CreateSymbolicLink error (1314): A required privilege is not held by the client`. Hay dos alternativas:

- Abrir siempre la terminal **como administrador** (recomendado), o
- Activar el **Modo para desarrolladores** en *Configuración → Privacidad y seguridad → Para programadores*, que permite crear enlaces simbólicos sin ser administrador.

---
Siguiente: [0. Introducción →](00_introduccion.md)
