# Diagrama entidad–relación de la base de datos multimodal de clientes

El modelo gira alrededor de la entidad **CLIENTE**. Cada modalidad de dato (texto, imagen, video, voz) se representa con una entidad propia que guarda los **metadatos y la representación analizable**, mientras que el archivo original se referencia mediante su ruta en HDFS (`ruta_hdfs` / `ruta_audio`).

```mermaid
erDiagram
    CLIENTE ||--o{ TRANSACCION : realiza
    CLIENTE ||--o{ RESENA : escribe
    CLIENTE ||--o{ IMAGEN : publica
    CLIENTE ||--o{ LLAMADA : realiza
    SUCURSAL ||--o{ TRANSACCION : registra
    SUCURSAL ||--o{ RESENA : recibe
    SUCURSAL ||--o{ IMAGEN : aparece_en
    SUCURSAL ||--o{ LLAMADA : asociada_a
    PRODUCTO ||--o{ TRANSACCION : incluye
    CAMPANA ||--o{ VIDEO : agrupa
    IMAGEN ||--o{ IMAGEN_ETIQUETA : tiene

    CLIENTE {
        varchar id_cliente PK
        varchar nombre
        char genero
        int edad
        varchar ciudad
        varchar segmento
        date fecha_registro
        varchar canal_preferido
        boolean acepta_marketing
    }
    SUCURSAL {
        varchar id_sucursal PK
        varchar nombre
        varchar ciudad
        varchar tipo
    }
    PRODUCTO {
        varchar id_producto PK
        varchar nombre
        varchar categoria
        int precio
    }
    TRANSACCION {
        varchar id_transaccion PK
        varchar id_cliente FK
        varchar id_sucursal FK
        varchar id_producto FK
        timestamp fecha_hora
        int cantidad
        int valor_total
        varchar medio_pago
    }
    RESENA {
        varchar id_resena PK
        varchar id_cliente FK
        varchar id_sucursal FK
        date fecha
        varchar canal
        int calificacion
        text texto
    }
    IMAGEN {
        varchar id_imagen PK
        varchar id_cliente FK
        varchar id_sucursal FK
        date fecha
        varchar origen
        varchar ruta_hdfs
        varchar formato
        int ancho
        int alto
        int tamano_kb
        boolean menciona_marca
        decimal sentimiento_visual
    }
    IMAGEN_ETIQUETA {
        varchar id_imagen FK
        varchar etiqueta
    }
    CAMPANA {
        varchar nombre PK
        varchar objetivo
    }
    VIDEO {
        varchar id_video PK
        varchar campana FK
        varchar plataforma
        date fecha_publicacion
        varchar ruta_hdfs
        int duracion_seg
        varchar resolucion
        int reproducciones
        int me_gusta
        int comentarios
        int compartidos
        decimal porcentaje_visto
        text transcripcion
    }
    LLAMADA {
        varchar id_llamada PK
        varchar id_cliente FK
        varchar id_sucursal FK
        timestamp fecha_hora
        varchar ruta_audio
        int duracion_seg
        varchar motivo
        boolean resuelta
        text transcripcion
    }
```

## Modelo relacional vs. modelo en el data lake

| Aspecto | Base de datos relacional (diseño lógico) | Data lake en HDFS (implementación) |
|---|---|---|
| Esquema | Se define antes de cargar (*schema-on-write*) | Se interpreta al leer (*schema-on-read*) |
| Formato | Tablas normalizadas | CSV y JSON Lines (un registro por línea) |
| Relaciones | Llaves foráneas | Identificadores compartidos (`id_cliente`, `id_sucursal`) |
| Desnormalización | Se evita | Se acepta para facilitar el procesamiento (ej. `ciudad` dentro de `transacciones.csv` y de `resenas.jsonl`) |
| Listas | Tabla intermedia (`IMAGEN_ETIQUETA`) | Arreglo dentro del JSON (`"etiquetas": [...]`) |
| Archivos binarios | Ruta o BLOB | Archivo original en `/datalake/raw/multimedia/` |

El archivo [`esquema_relacional.sql`](esquema_relacional.sql) contiene el DDL completo para PostgreSQL/MySQL, útil si la empresa ya opera con una base de datos transaccional desde la cual se extraerían los datos hacia Hadoop.
