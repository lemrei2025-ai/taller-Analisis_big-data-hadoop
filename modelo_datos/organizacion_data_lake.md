# Organización del data lake en HDFS

El almacenamiento se organiza por **zonas**, una práctica habitual en arquitecturas de Big Data que separa los datos según su nivel de procesamiento.

```text
/datalake
├── raw/                                  ← ZONA CRUDA: datos tal como llegan (inmutables)
│   ├── estructurados/
│   │   ├── clientes/clientes.csv
│   │   ├── sucursales/sucursales.csv
│   │   ├── productos/productos.csv
│   │   └── transacciones/transacciones.csv
│   ├── texto/resenas/resenas.jsonl
│   ├── imagen/metadatos/imagenes.jsonl
│   ├── video/metadatos/videos.jsonl
│   ├── voz/llamadas/llamadas.jsonl
│   └── multimedia/                       ← archivos binarios originales
│       ├── imagenes/   (*.jpg, *.png, *.heic)
│       ├── videos/     (*.mp4)
│       └── audios/     (*.wav)
├── staged/                               ← ZONA INTERMEDIA: datos limpios / validados
└── curated/                              ← ZONA CURADA: resultados de MapReduce
    ├── ventas_ciudad_categoria/part-00000
    ├── ventas_mes/part-00000
    ├── sentimiento_sucursal/part-00000
    └── ...
```

| Zona | Propósito | ¿Quién escribe? | ¿Quién lee? |
|---|---|---|---|
| raw | Conservar la fuente original para auditoría y reprocesos | Procesos de ingesta (capa 1) | Trabajos MapReduce |
| staged | Datos depurados (duplicados eliminados, formatos homogéneos) | Trabajos de limpieza | Trabajos analíticos |
| curated | Indicadores listos para consumo | Trabajos analíticos | Capa de acceso (WebHDFS, SQL, API) |

## Decisiones de diseño a justificar en el informe

1. **Una carpeta por conjunto de datos** (y no un archivo suelto): MapReduce recibe carpetas como entrada y procesa todos los archivos que contengan, lo que permite agregar nuevos lotes sin modificar el código.
2. **Formato JSON Lines** para datos semiestructurados: cada línea es un registro independiente, de modo que HDFS puede dividir el archivo en bloques y cada *mapper* procesar una parte.
3. **Factor de replicación**: en el laboratorio es 1 (un solo DataNode); en producción se usa 3 para tolerar fallos.
4. **Tamaño de bloque**: configurado en 32 MB para que, al aumentar la escala de los datos (`--escala 10`), se observe cómo un archivo se divide en varios bloques y se lanzan varios *mappers*.
5. **Particionamiento** (mejora opcional): organizar las transacciones por fecha, por ejemplo `/transacciones/anio=2025/mes=12/`, para procesar solo el periodo de interés.
