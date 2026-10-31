# Diccionario de datos

Formato de los archivos producidos por la capa de recopilación (`datos/raw/`).

## clientes.csv — estructurado

| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| id_cliente | texto | Identificador único (seudónimo, no documento de identidad) | C000123 |
| nombre | texto | Nombre sintético | Laura Gómez |
| genero | F / M | Género declarado | F |
| edad | entero | Edad en años | 27 |
| ciudad | texto | Ciudad de residencia | Medellín |
| segmento | texto | estudiante, profesional, familia, turista, empresa | profesional |
| fecha_registro | fecha ISO | Fecha de afiliación | 2023-05-14 |
| canal_preferido | texto | tienda, app, web | app |
| acepta_marketing | si / no | Autorización de tratamiento para mercadeo | si |

## sucursales.csv y productos.csv — catálogos

| Archivo | Campos |
|---|---|
| sucursales.csv | id_sucursal, nombre, ciudad, tipo (tienda / digital) |
| productos.csv | id_producto, nombre, categoria, precio (COP) |

## transacciones.csv — estructurado

| Campo | Tipo | Descripción |
|---|---|---|
| id_transaccion | texto | Identificador de la línea de venta |
| id_cliente | texto | Cliente que compra |
| id_sucursal | texto | Sucursal donde se registra la venta (S07 = canal en línea) |
| ciudad | texto | Ciudad de la sucursal (desnormalizada para facilitar MapReduce) |
| fecha_hora | AAAA-MM-DD HH:MM | Momento de la venta |
| id_producto | texto | Producto vendido |
| categoria | texto | Categoría del producto (desnormalizada) |
| cantidad | entero | Unidades |
| valor_total | entero | Valor en COP (precio × cantidad) |
| medio_pago | texto | efectivo, tarjeta_debito, tarjeta_credito, billetera_digital |

## resenas.jsonl — TEXTO

Un objeto JSON por línea.

| Campo | Tipo | Descripción |
|---|---|---|
| id_resena | texto | Identificador |
| id_cliente, id_sucursal, ciudad | texto | Relación con cliente y sucursal |
| fecha | fecha ISO | Fecha de publicación |
| canal | texto | app, google_maps, instagram, web |
| calificacion | entero 1–5 | Estrellas otorgadas |
| texto | texto libre | Contenido de la reseña |

## imagenes.jsonl — IMAGEN

| Campo | Tipo | Descripción |
|---|---|---|
| id_imagen | texto | Identificador |
| id_cliente, id_sucursal | texto | Autor y sucursal asociada |
| fecha, origen | texto | Fecha y red/canal de publicación |
| ruta_hdfs | texto | Ubicación del archivo original en el data lake |
| formato, ancho, alto, tamano_kb | metadatos técnicos | Extraídos del archivo (EXIF / encabezado) |
| etiquetas | lista de texto | Objetos detectados por un modelo de visión (ej. `taza`, `latte_art`, `logo_marca`) |
| menciona_marca | booleano | Si la imagen muestra o etiqueta la marca |
| sentimiento_visual | decimal −1 a 1 | Puntaje estimado por un modelo de análisis de imagen |

## videos.jsonl — VIDEO

| Campo | Tipo | Descripción |
|---|---|---|
| id_video | texto | Identificador |
| campana | texto | Campaña de mercadeo a la que pertenece |
| plataforma | texto | tiktok, instagram, youtube |
| fecha_publicacion | fecha ISO | Fecha de publicación |
| ruta_hdfs | texto | Archivo MP4 original |
| duracion_seg, resolucion | metadatos técnicos | Extraídos con ffprobe |
| reproducciones, me_gusta, comentarios, compartidos | enteros | Métricas de la plataforma |
| porcentaje_visto | decimal 0–1 | Retención promedio |
| transcripcion | texto | Audio del video convertido a texto |

## llamadas.jsonl — VOZ

| Campo | Tipo | Descripción |
|---|---|---|
| id_llamada | texto | Identificador |
| id_cliente, id_sucursal | texto | Cliente y sucursal relacionada con el pedido |
| fecha_hora | AAAA-MM-DD HH:MM | Inicio de la llamada |
| ruta_audio | texto | Archivo WAV original en el data lake |
| duracion_seg | entero | Duración del audio |
| motivo | texto | Clasificación del motivo (pedido_tardio, falla_aplicacion, felicitacion, …) |
| resuelta | booleano | Si el caso se cerró en el primer contacto |
| transcripcion | texto | Conversión de voz a texto |
