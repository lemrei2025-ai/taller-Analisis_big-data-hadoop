-- ===========================================================================
-- Base de datos multimodal de clientes - Café Andino S.A.S. (caso de ejemplo)
-- Compatible con PostgreSQL. Para MySQL, reemplazar BOOLEAN por TINYINT(1)
-- y TEXT por LONGTEXT donde se requiera.
-- ===========================================================================

CREATE TABLE sucursal (
    id_sucursal     VARCHAR(5)   PRIMARY KEY,
    nombre          VARCHAR(80)  NOT NULL,
    ciudad          VARCHAR(50)  NOT NULL,
    tipo            VARCHAR(20)  NOT NULL CHECK (tipo IN ('tienda', 'digital'))
);

CREATE TABLE producto (
    id_producto     VARCHAR(5)   PRIMARY KEY,
    nombre          VARCHAR(80)  NOT NULL,
    categoria       VARCHAR(40)  NOT NULL,
    precio          INTEGER      NOT NULL CHECK (precio > 0)
);

CREATE TABLE cliente (
    id_cliente      VARCHAR(10)  PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    genero          CHAR(1),
    edad            SMALLINT     CHECK (edad BETWEEN 14 AND 110),
    ciudad          VARCHAR(50),
    segmento        VARCHAR(30),
    fecha_registro  DATE,
    canal_preferido VARCHAR(20),
    acepta_marketing BOOLEAN     DEFAULT FALSE
);

-- --------------------------- Datos estructurados ---------------------------
CREATE TABLE transaccion (
    id_transaccion  VARCHAR(12)  PRIMARY KEY,
    id_cliente      VARCHAR(10)  NOT NULL REFERENCES cliente(id_cliente),
    id_sucursal     VARCHAR(5)   NOT NULL REFERENCES sucursal(id_sucursal),
    id_producto     VARCHAR(5)   NOT NULL REFERENCES producto(id_producto),
    fecha_hora      TIMESTAMP    NOT NULL,
    cantidad        SMALLINT     NOT NULL CHECK (cantidad > 0),
    valor_total     INTEGER      NOT NULL,
    medio_pago      VARCHAR(30)
);

-- --------------------------------- TEXTO -----------------------------------
CREATE TABLE resena (
    id_resena       VARCHAR(10)  PRIMARY KEY,
    id_cliente      VARCHAR(10)  NOT NULL REFERENCES cliente(id_cliente),
    id_sucursal     VARCHAR(5)   NOT NULL REFERENCES sucursal(id_sucursal),
    fecha           DATE         NOT NULL,
    canal           VARCHAR(30),
    calificacion    SMALLINT     CHECK (calificacion BETWEEN 1 AND 5),
    texto           TEXT         NOT NULL
);

-- --------------------------------- IMAGEN ----------------------------------
CREATE TABLE imagen (
    id_imagen       VARCHAR(10)  PRIMARY KEY,
    id_cliente      VARCHAR(10)  REFERENCES cliente(id_cliente),
    id_sucursal     VARCHAR(5)   REFERENCES sucursal(id_sucursal),
    fecha           DATE,
    origen          VARCHAR(30),
    ruta_hdfs       VARCHAR(255) NOT NULL,      -- archivo original en el data lake
    formato         VARCHAR(10),
    ancho           INTEGER,
    alto            INTEGER,
    tamano_kb       INTEGER,
    menciona_marca  BOOLEAN,
    sentimiento_visual NUMERIC(4,2) CHECK (sentimiento_visual BETWEEN -1 AND 1)
);

CREATE TABLE imagen_etiqueta (
    id_imagen       VARCHAR(10)  REFERENCES imagen(id_imagen),
    etiqueta        VARCHAR(40),
    PRIMARY KEY (id_imagen, etiqueta)
);

-- --------------------------------- VIDEO -----------------------------------
CREATE TABLE campana (
    nombre          VARCHAR(80)  PRIMARY KEY,
    objetivo        VARCHAR(200)
);

CREATE TABLE video (
    id_video        VARCHAR(10)  PRIMARY KEY,
    campana         VARCHAR(80)  REFERENCES campana(nombre),
    plataforma      VARCHAR(20),
    fecha_publicacion DATE,
    ruta_hdfs       VARCHAR(255) NOT NULL,
    duracion_seg    INTEGER,
    resolucion      VARCHAR(10),
    reproducciones  INTEGER,
    me_gusta        INTEGER,
    comentarios     INTEGER,
    compartidos     INTEGER,
    porcentaje_visto NUMERIC(4,2),
    transcripcion   TEXT
);

-- ---------------------------------- VOZ ------------------------------------
CREATE TABLE llamada (
    id_llamada      VARCHAR(10)  PRIMARY KEY,
    id_cliente      VARCHAR(10)  REFERENCES cliente(id_cliente),
    id_sucursal     VARCHAR(5)   REFERENCES sucursal(id_sucursal),
    fecha_hora      TIMESTAMP,
    ruta_audio      VARCHAR(255) NOT NULL,
    duracion_seg    INTEGER,
    motivo          VARCHAR(40),
    resuelta        BOOLEAN,
    transcripcion   TEXT
);

-- Índices sugeridos para consultas frecuentes
CREATE INDEX idx_transaccion_fecha    ON transaccion (fecha_hora);
CREATE INDEX idx_transaccion_sucursal ON transaccion (id_sucursal);
CREATE INDEX idx_resena_sucursal      ON resena (id_sucursal);
CREATE INDEX idx_llamada_motivo       ON llamada (motivo);
