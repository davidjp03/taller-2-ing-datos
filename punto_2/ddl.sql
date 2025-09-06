CREATE DATABASE DB_SPORTS;

CREATE TABLE Football_FactMatches (
    id SERIAL PRIMARY KEY,
    fecha_id INT,
    equipo_local_id INT,
    equipo_visitante_id INT,
    estadio_id INT,
    goles_local INT,
    goles_visitante INT,
    FOREIGN KEY (fecha_id) REFERENCES Football_DimFecha(id),
    FOREIGN KEY (equipo_local_id) REFERENCES Football_DimEquipo(id),
    FOREIGN KEY (equipo_visitante_id) REFERENCES Football_DimEquipo(id),
    FOREIGN KEY (estadio_id) REFERENCES Football_DimEstadio(id)
);

CREATE TABLE Football_DimFecha (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    temporada INT,
    dia_semana VARCHAR
);

CREATE TABLE Football_DimEquipo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    liga VARCHAR,
    pais VARCHAR
);

CREATE TABLE Football_DimJugador (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    posicion VARCHAR,
    equipo_id INT,
    FOREIGN KEY (equipo_id) REFERENCES Football_DimEquipo(id)
);

CREATE TABLE Football_DimEstadio (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    ciudad VARCHAR,
    capacidad INT
);


CREATE TABLE NBA_FactGames (
    id SERIAL PRIMARY KEY,
    fecha_id INT,
    equipo_local_id INT,
    equipo_visitante_id INT,
    arena_id INT,
    puntos_local INT,
    puntos_visitante INT,
    FOREIGN KEY (fecha_id) REFERENCES NBA_DimFecha(id),
    FOREIGN KEY (equipo_local_id) REFERENCES NBA_DimEquipo(id),
    FOREIGN KEY (equipo_visitante_id) REFERENCES NBA_DimEquipo(id),
    FOREIGN KEY (arena_id) REFERENCES NBA_DimArena(id)
);

CREATE TABLE NBA_DimFecha (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    temporada VARCHAR
);

CREATE TABLE NBA_DimEquipo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    conferencia VARCHAR,
    division VARCHAR
);

CREATE TABLE NBA_DimJugador (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    posicion VARCHAR,
    altura FLOAT,
    peso FLOAT,
    equipo_id INT,
    FOREIGN KEY (equipo_id) REFERENCES NBA_DimEquipo(id)
);

CREATE TABLE NBA_DimArena (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    ciudad VARCHAR,
    capacidad INT
);


CREATE TABLE F1_FactRaces (
    id SERIAL PRIMARY KEY,
    fecha_id INT,
    piloto_id INT,
    equipo_id INT,
    circuito_id INT,
    posicion_final INT,
    puntos INT,
    FOREIGN KEY (fecha_id) REFERENCES F1_DimFecha(id),
    FOREIGN KEY (piloto_id) REFERENCES F1_DimPiloto(id),
    FOREIGN KEY (equipo_id) REFERENCES F1_DimEquipo(id),
    FOREIGN KEY (circuito_id) REFERENCES F1_DimCircuito(id)
);

CREATE TABLE F1_DimFecha (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    temporada INT
);

CREATE TABLE F1_DimPiloto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    nacionalidad VARCHAR,
    equipo_id INT,
    FOREIGN KEY (equipo_id) REFERENCES F1_DimEquipo(id)
);

CREATE TABLE F1_DimEquipo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    motor VARCHAR,
    pais VARCHAR
);

CREATE TABLE F1_DimCircuito (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    pais VARCHAR,
    longitud FLOAT
);
