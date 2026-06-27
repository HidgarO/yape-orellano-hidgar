"""
P4 - Docker Desktop: MongoDB local en contenedor
Estudiante: Hidgar Orellano Huerta
Codigo: 2221892872

"""

from pymongo import MongoClient


def conectar_mongo_docker():
    client_docker = MongoClient(
        "mongodb://admin:yape2026@localhost:27017/",
        authSource="admin",
    )

    db_local = client_docker["yape_local"]
    col_local = db_local["comerciantes_test"]

    col_local.delete_many({"nombre_comercio": "Bodega Test Docker"})
    col_local.insert_one({
        "nombre_comercio": "Bodega Test Docker",
        "tipo": "bodega",
        "distrito": "Lima",
        "monto_mensual_soles": 1500.00,
        "yape_activo": True,
        "entorno": "docker_local",
    })

    doc = col_local.find_one({"nombre_comercio": "Bodega Test Docker"})
    print("Documento guardado en MongoDB Docker:")
    print(f"   Nombre:   {doc['nombre_comercio']}")
    print(f"   Entorno:  {doc['entorno']}")
    print(f"   ID:       {doc['_id']}")
    print(f"\nTotal documentos en Docker: {col_local.count_documents({})}")

    client_docker.close()


RESPUESTAS_4_3 = """
4.3 Diferencia entre Docker y Atlas

a) Usaria MongoDB en Docker cuando el equipo de Yape necesita un entorno local de desarrollo o pruebas rapido, aislado y reproducible. Sirve para validar codigo sin tocar datos reales ni depender de internet. Tambien permite levantar y eliminar ambientes temporales durante desarrollo.

b) Atlas M0 tiene ventaja en el contexto universitario porque no requiere administrar el servidor MongoDB, funciona en la nube y permite mostrar la base desde una interfaz web. Tambien facilita evidenciar documentos en Browse Collections y compartir una conexion remota controlada.

c) Si ejecuto docker stop mongodb-yape y luego docker rm mongodb-yape, el contenedor se elimina. Como el comando del examen no define un volumen persistente, los datos del contenedor se pierden al removerlo. En Atlas, los datos permanecen en la nube aunque cierre mi computadora o termine la sesion local.
"""


if __name__ == "__main__":
    conectar_mongo_docker()
    print(RESPUESTAS_4_3)

