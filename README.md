# Evaluacion Parcial Big Data - Yape

| Campo | Detalle |
|---|---|
| Estudiante | Hidgar Orellano Huerta |
| Codigo | 2221892872 |
| Curso | Big Data |
| Docente | Mg. Ruben Quispe Llacctarimay |
| Repositorio | https://github.com/HidgarO/yape-orellano-hidgar |
| Video | https://youtu.be/EnequVsewIc |

## Descripcion

Este repositorio contiene la solucion del parcial de Big Data aplicado a un caso tipo Yape. La implementacion incluye:

- Parte A: arquitectura Big Data, CAP y NewSQL.
- Parte B: pipeline analitico en Databricks con capas Bronze, Silver y Gold.
- Parte C: almacenamiento documental en MongoDB Atlas.
- Parte D: validacion local de MongoDB usando Docker Desktop.

## Archivos incluidos

```text
P1_arquitectura.md       # Arquitectura Big Data, CAP y NewSQL
P2_databricks_yape.py    # Notebook/script Databricks con Bronze, Silver, Gold y dashboard
P3_mongodb_atlas.py      # Script MongoDB Atlas: insercion, consultas y aggregation pipeline
P4_docker.py             # Script MongoDB Docker local + respuestas 4.3
screenshots/             # Evidencias de ejecucion
```

## Parte A - Arquitectura

El archivo `P1_arquitectura.md` contiene la arquitectura propuesta para una billetera digital tipo Yape. Se separan las tecnologias segun el tipo de carga: pagos transaccionales, sesiones temporales, perfiles flexibles de comercios, analitica historica, fraude por grafos y dashboard ejecutivo.

## Parte B - Databricks

Archivo: `P2_databricks_yape.py`

En Databricks se implemento un pipeline con arquitectura Medallion:

- Bronze: generacion y carga de 2000 transacciones sinteticas.
- Silver: limpieza de transacciones completadas, clasificacion de montos, hora pico y calculo de comisiones.
- Gold: agregaciones por distrito y por hora.
- Dashboard: visualizacion con Matplotlib a partir de las tablas Gold.

Evidencias:

```text
screenshots/databricks_celda1.png
screenshots/databricks_celda2.png
screenshots/databricks_celda3.png
screenshots/databricks_dashboard.png
```

## Parte C - MongoDB Atlas

Archivo: `P3_mongodb_atlas.py`

Se creo un cluster en MongoDB Atlas llamado `Yape-BigData`. Dentro del cluster se uso la base `yape_db` y la coleccion `comerciantes`.

El script realiza:

- Conexion a MongoDB Atlas con `pymongo`.
- Insercion de 5 documentos de comercios.
- Consulta de comercios activos con alta calificacion.
- Consulta de comercios con delivery y facturacion mensual relevante.
- Consulta por tipos de comercio.
- Aggregation pipeline agrupado por tipo de comercio.

Evidencia:

```text
screenshots/mongodb_atlas_collection.png
```

## Parte D - Docker Desktop

Archivo: `P4_docker.py`

Se valido MongoDB local usando Docker Desktop. El contenedor usado fue `mongodb-yape`, basado en la imagen `mongo:7`, exponiendo el puerto `27017`.

Comandos usados para la validacion local:

```bash
docker --version
docker ps
docker run -d --name mongodb-yape -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=yape2026 mongo:7
docker ps
py P4_docker.py
```

Evidencia:

```text
screenshots/docker_mongodb_output.png
```

## Video de sustentacion

El video de sustentacion se encuentra en:

https://youtu.be/EnequVsewIc
