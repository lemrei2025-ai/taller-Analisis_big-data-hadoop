@echo off
REM ==========================================================================
REM  Inicia HDFS (NameNode, DataNode), YARN (ResourceManager, NodeManager)
REM  y el servidor de historial de MapReduce.
REM  Ejecutar en una terminal COMO ADMINISTRADOR (YARN necesita crear enlaces
REM  simbolicos), o activar el "Modo para desarrolladores" de Windows.
REM ==========================================================================
net session >nul 2>&1
if errorlevel 1 (
  echo [!] La terminal no es de administrador. HDFS funcionara, pero los trabajos
  echo     en YARN pueden fallar con el error "CreateSymbolicLink error 1314".
  echo.
)
if not defined HADOOP_HOME (
  echo [X] La variable HADOOP_HOME no esta definida. Ejecute primero instalar_hadoop_windows.ps1
  exit /b 1
)

echo == Iniciando HDFS ==
call "%HADOOP_HOME%\sbin\start-dfs.cmd"
timeout /t 15 /nobreak >nul

echo == Iniciando YARN ==
call "%HADOOP_HOME%\sbin\start-yarn.cmd"

echo == Iniciando JobHistory Server ==
start "Hadoop JobHistory" "%HADOOP_HOME%\bin\mapred.cmd" historyserver

echo == Esperando a que HDFS salga de modo seguro ==
call "%HADOOP_HOME%\bin\hdfs.cmd" dfsadmin -safemode wait

timeout /t 10 /nobreak >nul
echo.
echo == Procesos Java activos (deben aparecer NameNode, DataNode, ResourceManager,
echo    NodeManager y JobHistoryServer) ==
jps
echo.
echo HDFS:      http://localhost:9870
echo YARN:      http://localhost:8088
echo Historial: http://localhost:19888
echo.
echo No cierre las ventanas negras que se abrieron: cada una es un servicio de Hadoop.
