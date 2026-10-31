# Capa 5. Análisis de la información obtenida

**Propósito:** interpretar los resultados del procesamiento, cruzar las distintas modalidades de datos y transformar los hallazgos en recomendaciones para la empresa.

**Duración estimada:** 3 horas.

---

## 5.1 Método de análisis

El análisis sigue cuatro pasos para cada pregunta de negocio:

| Paso | Pregunta guía |
|---|---|
| 1. **Describir** | ¿Qué muestran los datos? (cifras concretas, comparaciones, tendencias) |
| 2. **Explicar** | ¿Por qué ocurre? ¿Qué otra fuente de datos lo confirma o lo contradice? |
| 3. **Validar** | ¿El resultado puede estar sesgado por la forma en que se recopilaron o procesaron los datos? |
| 4. **Recomendar** | ¿Qué decisión concreta debería tomar la empresa y cómo se mediría su efecto? |

El valor del Big Data multimodal aparece en el paso 2: un hallazgo es más sólido cuando **varias modalidades independientes apuntan a la misma conclusión** (triangulación).

## 5.2 Ejemplo de análisis resuelto: Café Andino S.A.S.

Las cifras corresponden a la ejecución con los parámetros por defecto (`--semilla 2025 --escala 1`).

### Hallazgo 1. Andino El Prado (Barranquilla) concentra la peor experiencia del cliente

**Describir.** Es la única sucursal con índice neto de sentimiento negativo en reseñas (**−0,34**), frente a **+0,76** de Andino El Poblado (Medellín). En la fuente de voz también registra el índice más bajo (−0,80) y el puntaje promedio más negativo de todas las sucursales (−1,91).

**Explicar (triangulación).**

| Modalidad | Evidencia |
|---|---|
| Texto | Los bigramas más frecuentes en reseñas de 1–2 estrellas son *aire acondicionado*, *funcionaba calor*, *demora entrega* y *entrega excesiva* |
| Voz | `pedido_tardio` es el motivo de llamada más frecuente de toda la empresa (466 llamadas, 54,9 horas de atención) |
| Imagen | Barranquilla tiene el sentimiento visual más bajo en fotos con bebidas frías (0,16 frente a 0,42 en Medellín) |
| Estructurado | Las ventas de la sucursal se mantienen (79 millones COP, similar a Cali y Medellín): el problema aún no se refleja en los ingresos, pero es una alerta temprana |

**Validar.** El volumen de reseñas de la sucursal (891) es comparable al de las demás tiendas, por lo que el resultado no se explica por una muestra pequeña.

**Recomendar.** Revisar el sistema de climatización y los tiempos de entrega del domicilio en Barranquilla. Indicador de seguimiento: índice neto de sentimiento mensual de la sucursal, con meta ≥ 0,30 en tres meses.

### Hallazgo 2. La aplicación móvil genera los casos más difíciles de resolver

**Describir.** `falla_aplicacion` es el motivo con la **menor tasa de resolución (48,6 %)** y una de las mayores duraciones medias (478 s). Le sigue `cobro_incorrecto` (53,5 %).

**Explicar.** En las quejas escritas aparecen con alta frecuencia los bigramas *aplicacion fallo* y *momento pagar*; el canal en línea (Andino Online) presenta un índice de sentimiento en reseñas de solo +0,26, por debajo de las tiendas físicas excepto Andino Centro y El Prado.

**Recomendar.** Priorizar la corrección del módulo de pagos de la app y habilitar en el centro de contacto un procedimiento de pago alternativo para cerrar el caso en la primera llamada.

### Hallazgo 3. Diciembre es el mes de mayor venta, impulsado por el café empacado

**Describir.** Las ventas de diciembre (**67,1 millones COP**) superan en cerca de un **33 %** al promedio de enero a noviembre (~50,4 millones), y el ticket promedio sube de ~20.000 a **26.390 COP**.

**Explicar.** El aumento del ticket promedio sugiere que en diciembre se compran productos de mayor valor. La hipótesis es que se trata de café empacado para regalo (el producto más costoso del portafolio). Para confirmarla, el estudiante crea una nueva dimensión `mes_categoria` en el Job 1 y compara las unidades de café empacado de diciembre con las de los demás meses.

**Recomendar.** Preparar inventario de café empacado y una campaña de regalos corporativos para el último trimestre.

### Hallazgo 4. Las bebidas frías dominan en ciudades cálidas

**Describir.** En Barranquilla y Cali las bebidas frías representan cerca del **42 %** de las ventas de la ciudad, frente a 12–19 % en Bogotá, Medellín y Bucaramanga.

**Explicar.** Las imágenes de clientes lo confirman: la etiqueta `bebida_fria` aparece en 284 fotos de Barranquilla y 261 de Cali, frente a 75–102 en las demás ciudades.

**Recomendar.** Diferenciar el menú y las campañas por clima: la promoción de bebidas frías debería concentrarse en la región Caribe y el Valle del Cauca.

### Hallazgo 5. La campaña "Origen del grano" logra la mejor combinación de interacción y retención

**Describir.** Registra la mayor tasa de *engagement* (9,0 %) y una retención promedio de **75 %**, frente a 37 % de "Promo 2x1 frías", que en cambio obtiene el mayor número de reproducciones (sobre todo en TikTok).

**Explicar.** El contenido de marca (historia del café) retiene a la audiencia; las promociones generan alcance pero poca permanencia.

**Recomendar.** Usar las promociones para alcance y el contenido de origen para fidelización; medir la conversión de cada campaña cruzando los videos con las ventas posteriores.

### Validación crítica: una lectura que puede engañar

En la tabla de ventas por ciudad y categoría, **Bogotá** aparece con el **62 %** de sus ventas en café empacado, muy por encima de las demás ciudades. Un análisis apresurado concluiría que los bogotanos compran más café para la casa. Sin embargo, al revisar el modelo de datos se observa que el **canal en línea (S07) está registrado con ciudad = Bogotá**, y es el canal donde más se vende café empacado. El resultado refleja una **decisión de modelado**, no un comportamiento de los clientes de la ciudad.

**Corrección propuesta:** ejecutar el Job 1 con `DIMENSION=sucursal` (o crear una dimensión `canal`) y separar las ventas en línea antes de comparar ciudades.

> Este tipo de verificación es obligatorio en el informe: el estudiante debe identificar **al menos una limitación o posible sesgo** en sus propios resultados.

### Otras limitaciones del caso

- El léxico de sentimiento es pequeño y no maneja ironía ni palabras ambiguas (por ejemplo, *frío*).
- Las llamadas tienen sentimiento negativo en todas las sucursales porque los clientes llaman mayoritariamente para reclamar; la comparación válida es **entre sucursales** dentro de la misma fuente, no entre fuentes.
- Las etiquetas y el sentimiento de las imágenes dependen de la precisión del modelo de visión utilizado.
- Los datos son sintéticos: las conclusiones ilustran el método, no la realidad de una empresa.

## 5.3 Matriz de hallazgos y decisiones

El estudiante resume su análisis en una matriz como la siguiente:

| # | Hallazgo | Fuentes que lo soportan | Decisión recomendada | Indicador de seguimiento | Prioridad |
|---|---|---|---|---|---|
| 1 | El Prado con sentimiento negativo por calor y demoras | Texto, voz, imagen | Mantenimiento del aire acondicionado; revisar logística de domicilios | Índice neto mensual ≥ 0,30 | Alta |
| 2 | Fallas de pago en la app con baja resolución | Voz, texto | Corregir módulo de pagos; protocolo alterno en call center | % resolución de `falla_aplicacion` ≥ 75 % | Alta |
| 3 | Pico de ventas en diciembre por café empacado | Estructurado | Plan de inventario y campaña de regalos | Ventas del 4.º trimestre | Media |
| 4 | Bebidas frías en ciudades cálidas | Estructurado, imagen | Menú y promociones regionales | Participación de bebidas frías por ciudad | Media |
| 5 | Contenido de origen retiene más | Video | Calendario de contenido mixto | Retención y engagement por campaña | Media |

## 5.4 Actividad del estudiante

Con los resultados de **su propia empresa**, el estudiante:

1. Responde cada pregunta de negocio planteada en la ficha de la empresa siguiendo los cuatro pasos (describir, explicar, validar, recomendar).
2. Presenta **al menos un hallazgo triangulado** con tres o más modalidades de datos.
3. Identifica **al menos una limitación o sesgo** y propone cómo corregirlo.
4. Construye la matriz de hallazgos y decisiones.
5. Reflexiona sobre la arquitectura: ¿qué cambiaría si la empresa tuviera 1.000 veces más datos? ¿Qué parte del proceso se podría automatizar o ejecutar en tiempo real?

Todo se consigna en [`plantillas/informe_final.md`](../plantillas/informe_final.md).

---
[← 4. Acceso y comunicación](04_acceso_comunicacion.md) | Siguiente: [6. Entregables y rúbrica →](06_entregables_rubrica.md)
