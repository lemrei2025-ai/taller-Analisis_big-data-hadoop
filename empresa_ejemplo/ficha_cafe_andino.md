# Ficha de la empresa de ejemplo: Café Andino S.A.S.

> Empresa ficticia creada con fines educativos.

## 1. Descripción general

| Campo | Descripción |
|---|---|
| Razón social | Café Andino S.A.S. |
| Sector | Alimentos y bebidas – cadena de tiendas de café especial |
| Presencia | Bogotá (2 tiendas), Medellín, Cali, Barranquilla, Bucaramanga y canal en línea (app y web) |
| Clientes | Estudiantes, profesionales, familias, turistas y empresas (pedidos corporativos) |
| Productos | Bebidas calientes y frías, panadería, postres y café empacado |
| Canales de contacto | Tiendas físicas, aplicación móvil, sitio web, redes sociales, centro de contacto telefónico |

## 2. Problema de negocio

La gerencia percibe que la satisfacción de los clientes no es homogénea entre sucursales y que las campañas en redes sociales tienen resultados desiguales, pero no tiene una visión integrada porque la información está dispersa en el sistema de ventas, las reseñas de la app y Google Maps, las publicaciones en Instagram y TikTok y las grabaciones del centro de contacto.

## 3. Preguntas de negocio

1. ¿Qué sucursales y categorías generan más ventas y cuál es su ticket promedio?
2. ¿Existe estacionalidad en las ventas?
3. ¿Cómo varía el sentimiento de los clientes entre sucursales según reseñas (texto) y llamadas (voz)?
4. ¿Cuáles son los temas recurrentes en las quejas?
5. ¿Qué elementos aparecen en las fotografías que publican los clientes (imagen)?
6. ¿Qué campañas de video logran mayor interacción y retención?
7. ¿Cuáles son los motivos de llamada más frecuentes y cuáles se resuelven peor?

## 4. Fuentes de datos (inventario multimodal)

| Fuente | Tipo de dato | Formato original | Representación analizable | Volumen (escala 1) |
|---|---|---|---|---|
| Sistema POS / e-commerce | Estructurado | Tablas SQL | `transacciones.csv` | 30.000 |
| CRM | Estructurado | Tablas SQL | `clientes.csv` | 2.000 |
| App, Google Maps, Instagram | Texto | Texto libre | `resenas.jsonl` | 6.000 |
| Publicaciones de clientes | Imagen | JPG / PNG / HEIC | `imagenes.jsonl` (metadatos + etiquetas) | 2.500 |
| Campañas en TikTok, Instagram, YouTube | Video | MP4 | `videos.jsonl` (métricas + transcripción) | 400 |
| Centro de contacto | Voz | WAV | `llamadas.jsonl` (metadatos + transcripción) | 1.500 |

## 5. Indicadores esperados

- Ventas totales, unidades y ticket promedio por ciudad, categoría, sucursal y mes.
- Índice neto de sentimiento por sucursal y fuente (texto y voz).
- Frecuencia de palabras y bigramas en quejas.
- Etiquetas de imagen más frecuentes y su sentimiento visual.
- Tasa de *engagement* y retención por campaña y plataforma.
- Volumen, duración media y porcentaje de resolución de llamadas por motivo y por sucursal.
