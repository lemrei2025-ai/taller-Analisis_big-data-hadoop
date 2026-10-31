# 6. Entregables y rúbrica de evaluación

## 6.1 Modalidad de entrega

1. Cada grupo (o estudiante) realiza un **fork** de este repositorio en su cuenta de GitHub.
2. Todo el trabajo se versiona en el fork, con *commits* frecuentes y descriptivos (por ejemplo, `Capa 3: job7 ventas por franja horaria`).
3. Las evidencias (capturas de pantalla) se guardan en la carpeta `evidencias/`, nombradas por capa: `capa2_datanodes.png`, `capa3_yarn_trabajos.png`, etc.
4. El informe final se entrega como `informe_final.md` en la raíz del repositorio, a partir de la plantilla.
5. Se envía al docente el enlace del repositorio antes de la fecha límite.

> No se deben subir datos personales reales ni archivos de más de 50 MB. Los datos generados (`datos/raw/`) y los resultados (`resultados/`) ya están excluidos en `.gitignore`; el docente los reproduce ejecutando los scripts.

> Antes de subir cambios, verificar con `git status` que no se incluyan archivos de `datos\` ni de `resultados\`.

## 6.2 Lista de entregables

| Capa | Entregable | Ubicación en el repositorio |
|---|---|---|
| 1 | Ficha de la empresa e inventario de fuentes | `informe_final.md` (sección 1) |
| 1 | Modelo de datos adaptado (E-R, diccionario, data lake) | `modelo_datos/` |
| 1 | Generador configurado para la empresa | `recopilacion/generar_datos.py` |
| 2 | Evidencias del clúster y del data lake | `evidencias/` |
| 3 | Trabajos MapReduce adaptados + al menos un trabajo propio | `mapreduce/` |
| 3 | Evidencias de ejecución en YARN | `evidencias/` |
| 4 | Base de datos, API y reporte funcionando | `acceso/`, evidencias |
| 5 | Informe de análisis con matriz de decisiones | `informe_final.md` |
| — | Sustentación oral (10–15 minutos) | Presencial / virtual |

## 6.3 Rúbrica

| Criterio | Peso | Excelente (4.5–5.0) | Aceptable (3.0–4.4) | Insuficiente (0–2.9) |
|---|---|---|---|---|
| **1. Contexto y recopilación** | 15 % | Empresa bien caracterizada; preguntas de negocio claras; ≥ 4 modalidades de datos justificadas; generador adaptado con vocabulario propio del sector | Empresa descrita; 3–4 modalidades; adaptación parcial del generador | Empresa genérica; menos de 3 modalidades; se usan los datos de ejemplo sin cambios |
| **2. Diseño de la base de datos** | 15 % | Modelo E-R coherente, entidades por modalidad, diccionario completo, organización del data lake justificada | Modelo correcto con omisiones menores | Modelo incompleto o incoherente con los datos |
| **3. Almacenamiento con Hadoop** | 15 % | Hadoop instalado y operativo en Windows; data lake por zonas; experimento de bloques analizado; preguntas de control respondidas con fundamento | Clúster operativo y datos cargados; análisis superficial | Clúster no operativo o datos fuera de HDFS |
| **4. Procesamiento con MapReduce** | 20 % | Todos los trabajos ejecutados en YARN; trabajo propio original y correcto; ejercicio del combiner analizado; al menos un reto resuelto | Trabajos ejecutados; trabajo propio sencillo | Solo prueba local o trabajos con errores |
| **5. Acceso y comunicación** | 10 % | WebHDFS, SQL, API y reporte funcionando; consultas propias; propuesta de seguridad | Al menos tres mecanismos funcionando | Un solo mecanismo o ninguno |
| **6. Análisis de resultados** | 20 % | Hallazgos triangulados entre modalidades; validación crítica de sesgos; recomendaciones accionables con indicadores | Hallazgos descriptivos correctos con recomendaciones generales | Se presentan cifras sin interpretación |
| **7. Repositorio y sustentación** | 5 % | Repositorio ordenado, *commits* frecuentes, README actualizado; sustentación clara y dominio del tema | Repositorio funcional; sustentación aceptable | Repositorio desordenado o sin historial; no sustenta |

## 6.4 Lista de verificación previa a la entrega

- [ ] `.\instalacion\verificar_instalacion.ps1` muestra todas las herramientas y servicios en `[OK]`.
- [ ] `python recopilacion\generar_datos.py` se ejecuta sin errores y genera los datos de la empresa seleccionada.
- [ ] `python scripts\probar_local.py` se ejecuta sin errores.
- [ ] Los scripts `01_cargar_hdfs.ps1`, `02_ejecutar_mapreduce.ps1` y `03_exportar_resultados.ps1` se ejecutan en orden sin errores.
- [ ] `python acceso\generar_reporte.py` produce el reporte y los gráficos.
- [ ] El README describe la empresa seleccionada y los cambios realizados.
- [ ] `informe_final.md` está completo y las evidencias están en `evidencias\`.

---
[← 5. Análisis de resultados](05_analisis_resultados.md) | [Volver al inicio](../README.md)
