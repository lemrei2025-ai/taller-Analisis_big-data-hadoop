# Capa 1. Recopilación de datos

**Propósito:** identificar las fuentes de datos de clientes de la empresa, diseñar la base de datos multimodal y obtener los datos que alimentarán el data lake.

**Duración estimada:** 2 horas.

---

## 1.1 Inventario de fuentes

El estudiante identifica, para la empresa seleccionada, de dónde provienen los datos de sus clientes y en qué formato se encuentran. Para cada fuente se registra:

| Pregunta | Ejemplo (Café Andino) |
|---|---|
| ¿Qué sistema o canal la genera? | Aplicación móvil |
| ¿Qué tipo de dato es? | Texto (reseñas) |
| ¿En qué formato se obtiene? | JSON exportado de la API de la app |
| ¿Con qué frecuencia se genera? | Continua, ~500 reseñas por mes |
| ¿Qué pregunta de negocio ayuda a responder? | Satisfacción por sucursal, temas de queja |
| ¿Cómo se convierte en un dato analizable? | Directamente (texto) |

La tabla completa del caso de ejemplo está en [`empresa_ejemplo/ficha_cafe_andino.md`](../empresa_ejemplo/ficha_cafe_andino.md), sección 4.

## 1.2 Diseño de la base de datos multimodal

A partir del inventario, el estudiante diseña el modelo de datos de clientes. El caso de ejemplo incluye:

- [`modelo_datos/diagrama_er.md`](../modelo_datos/diagrama_er.md): diagrama entidad–relación (Mermaid, se visualiza directamente en GitHub).
- [`modelo_datos/esquema_relacional.sql`](../modelo_datos/esquema_relacional.sql): DDL de las tablas.
- [`modelo_datos/diccionario_datos.md`](../modelo_datos/diccionario_datos.md): descripción de cada campo.
- [`modelo_datos/organizacion_data_lake.md`](../modelo_datos/organizacion_data_lake.md): cómo se ubican los datos en HDFS.

Principios que debe cumplir el diseño:

1. **Entidad central CLIENTE** con un identificador seudonimizado (nunca el número de documento).
2. **Una entidad por modalidad** (texto, imagen, video, voz) que guarde los metadatos y la representación analizable, y una referencia (`ruta_hdfs`) al archivo original.
3. **Llaves compartidas** (`id_cliente`, `id_sucursal`, etc.) para poder relacionar fuentes durante el análisis.
4. **Campos de tiempo** en todas las entidades, para analizar tendencias.

## 1.3 Generación de los datos del caso de ejemplo

Como los datos reales de clientes son confidenciales, el taller utiliza un **generador de datos sintéticos** que reproduce patrones realistas (estacionalidad, diferencias entre sucursales, quejas recurrentes, campañas con desempeño distinto). Esos patrones están ocultos en los datos y es tarea del estudiante **descubrirlos** con MapReduce.

```powershell
python recopilacion\generar_datos.py
```

Salida esperada:

```text
Datos generados para Café Andino S.A.S. en '.../datos/raw':
  clientes.csv               2,000 registros
  transacciones.csv         30,000 registros
  resenas.jsonl              6,000 registros
  imagenes.jsonl             2,500 registros
  videos.jsonl                 400 registros
  llamadas.jsonl             1,500 registros
```

Para trabajar con mayor volumen (y observar la división en bloques y la ejecución de varios *mappers* en Hadoop) se usa el parámetro `--escala`:

```powershell
python recopilacion\generar_datos.py --escala 20     # ~600.000 transacciones (~110 MB)
```

### Exploración inicial de los datos

```powershell
Get-Content datos\raw\transacciones.csv -TotalCount 3 -Encoding UTF8
Get-Content datos\raw\resenas.jsonl -TotalCount 2 -Encoding UTF8
Get-Content datos\raw\imagenes.jsonl -TotalCount 1 -Encoding UTF8 | ConvertFrom-Json
Get-ChildItem datos\raw | Select-Object Name, @{n="KB";e={[math]::Round($_.Length/1KB)}}
```

> También pueden abrirse con Visual Studio Code o con el Bloc de notas. No se recomienda abrir `transacciones.csv` con Excel y guardarlo, porque Excel puede cambiar el separador y la codificación.

**Preguntas de control** (responder en el informe):

1. ¿Por qué las reseñas se guardan en formato JSON Lines y no en un único arreglo JSON?
2. ¿Qué campos de `imagenes.jsonl` provienen del archivo y cuáles de un modelo de inteligencia artificial?
3. ¿Qué ventaja tiene incluir `ciudad` dentro de `transacciones.csv` aunque ya exista en `sucursales.csv`?

## 1.4 Adaptación a la empresa seleccionada

El estudiante edita el bloque `CONFIGURACIÓN DE LA EMPRESA` al inicio de [`recopilacion/generar_datos.py`](../recopilacion/generar_datos.py) (con Visual Studio Code o el Bloc de notas, guardando en UTF-8):

| Variable | Qué se debe ajustar |
|---|---|
| `EMPRESA` | Nombre de la empresa seleccionada |
| `SUCURSALES`, `CALIDAD_SUCURSAL` | Sedes, puntos de atención o canales |
| `PRODUCTOS` | Productos o servicios con su categoría y precio |
| `SEGMENTOS`, `CANALES`, `MEDIOS_PAGO` | Tipología de clientes de la empresa |
| `FRASES_POSITIVAS`, `FRASES_NEGATIVAS`, `FRASES_NEUTRAS`, `PROBLEMA_SUCURSAL` | Vocabulario real del sector (se recomienda tomar ideas de reseñas públicas en Google Maps) |
| `ETIQUETAS_IMAGEN` | Objetos que aparecerían en fotos de clientes |
| `CAMPANAS_VIDEO` | Campañas reales o plausibles de la empresa |
| `MOTIVOS_LLAMADA`, `FRASES_LLAMADA` | Motivos de contacto al centro de atención |

> **Ejemplo:** para una clínica odontológica, `PRODUCTOS` serían servicios (limpieza, ortodoncia, blanqueamiento), `ETIQUETAS_IMAGEN` podrían ser `sonrisa`, `consultorio`, `antes_despues`, y `MOTIVOS_LLAMADA` serían `agendar_cita`, `cancelar_cita`, `cobro_incorrecto`, `urgencia`.

Si se modifican los campos de los archivos (no solo sus valores), también se deben actualizar los *mappers* correspondientes en la capa 3.

### Uso de datos multimedia reales (opcional, recomendado)

Si el estudiante dispone de imágenes, videos o audios propios (por ejemplo, fotos públicas de la empresa o grabaciones simuladas por el grupo), los ubica en `datos\multimedia\imagenes`, `datos\multimedia\videos` o `datos\multimedia\audios` y extrae sus metadatos:

```powershell
python recopilacion\extraer_metadatos_multimedia.py imagenes datos\multimedia\imagenes datos\raw\imagenes_reales.jsonl
```

El script `01_cargar_hdfs.ps1` sube automáticamente esos archivos binarios a `/datalake/raw/multimedia/`. El archivo de metadatos resultante se agrega a la misma carpeta de HDFS que los datos sintéticos, de modo que los trabajos MapReduce lo procesen junto con ellos:

```powershell
hdfs dfs -put -f datos\raw\imagenes_reales.jsonl /datalake/raw/imagen/metadatos/
```

## Evidencias de esta capa

- [ ] Ficha de la empresa diligenciada (`plantillas/ficha_empresa.md`).
- [ ] Inventario de fuentes multimodales (mínimo cuatro tipos de dato).
- [ ] Diagrama E-R y diccionario de datos adaptados.
- [ ] Generador configurado y salida de `generar_datos.py` con los conteos de registros.

---
[← Introducción](00_introduccion.md) | Siguiente: [2. Almacenamiento con Hadoop →](02_almacenamiento_hadoop.md)
