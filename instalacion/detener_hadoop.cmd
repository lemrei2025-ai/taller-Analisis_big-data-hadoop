@echo off
REM Detiene todos los servicios de Hadoop iniciados con iniciar_hadoop.cmd
call "%HADOOP_HOME%\sbin\stop-yarn.cmd"
call "%HADOOP_HOME%\sbin\stop-dfs.cmd"
taskkill /FI "WINDOWTITLE eq Hadoop JobHistory*" /T /F >nul 2>&1
echo Servicios de Hadoop detenidos.
