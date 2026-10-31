# Binarios nativos de Hadoop 3.3.6 para Windows

| Archivo | Función |
|---|---|
| `winutils.exe` | Utilidades que Hadoop usa en Windows para permisos de archivos, enlaces y procesos |
| `hadoop.dll` | Librería nativa (acceso a archivos locales, `NativeIO`) |

Compilados a partir del código fuente de Apache Hadoop 3.3.6 (licencia Apache 2.0) y
publicados en el repositorio comunitario https://github.com/cdarlint/winutils
(carpeta `hadoop-3.3.6/bin`). Se incluyen aquí para que la instalación no dependa de
descargarlos desde GitHub.

El script `instalar_hadoop_windows.ps1` los copia automáticamente en `C:\hadoop\bin`.
Para instalarlos a mano, basta con copiar ambos archivos en esa carpeta.
