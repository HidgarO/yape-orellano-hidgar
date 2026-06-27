# P1 - Arquitectura Big Data para Yape

| Campo | Detalle |
|---|---|
| Estudiante | Hidgar Orellano Huerta |
| Codigo | 2221892872 |
| Curso | Big Data |
| Evaluacion | Parcial - Semana 04 |

## Uso de IA

Para esta seccion use ChatGPT como apoyo para organizar alternativas de arquitectura y comparar tecnologias. Las justificaciones fueron adaptadas al caso Yape, considerando pagos digitales, historial transaccional, analitica y deteccion de fraude.

---

## 1.1 Tabla de arquitectura Big Data de Yape

| Componente del sistema | Tecnologia elegida | Tipo BD/Herramienta | Por que esta tecnologia para Yape |
|---|---|---|---|
| Core de pagos (3.2M transacciones/dia, no puede perder dinero) | CockroachDB | NewSQL distribuida, ACID | El core de pagos necesita transacciones ACID, consistencia fuerte y tolerancia a fallos porque un debito/credito incorrecto afecta dinero real. CockroachDB permite escalar horizontalmente sin perder propiedades transaccionales, a diferencia de una base NoSQL orientada a documentos. |
| Sesiones de login activo (15M usuarios, expira en 30 min) | Redis Cluster | Key-value en memoria | Las sesiones son datos temporales con TTL, lectura muy rapida y expiracion automatica. Redis encaja porque puede manejar millones de claves activas con baja latencia y no requiere consultas complejas. |
| Perfil del comerciante (bodega, restaurante, taxi - atributos distintos) | MongoDB Atlas | Base documental NoSQL | Los comercios tienen esquemas distintos: un taxi tiene vehiculo, una bodega categorias y un restaurante carta. MongoDB permite documentos flexibles sin crear muchas columnas nulas como ocurriria en SQL. |
| Historial de transacciones para analisis (18 TB/anio) | Delta Lake en Databricks sobre almacenamiento cloud | Data Lakehouse / Spark | El historial masivo no debe consultarse como sistema transaccional, sino procesarse por lotes y analitica distribuida. Delta Lake permite arquitectura Medallion, archivos Parquet, control de versiones y procesamiento con Spark. |
| Red de deteccion de fraude (ciclo A->B->C->A en < 5 min) | Neo4j o TigerGraph | Base de datos de grafos | El fraude puede aparecer como relaciones circulares entre cuentas, comercios y dispositivos. Una base de grafos permite buscar caminos, ciclos y patrones de relacion mucho mas rapido que multiples joins en SQL. |
| Dashboard ejecutivo (top 10 distritos, actualizacion diaria) | Power BI conectado a Gold tables de Databricks | BI + tablas analiticas | Los ejecutivos necesitan indicadores agregados, no transacciones crudas. Las tablas Gold preparadas en Databricks reducen costo y tiempo de consulta para dashboards diarios por distrito, tipo de comercio o volumen. |

---

## 1.2 Teorema CAP

| Componente | Combinacion CAP | Propiedad sacrificada | Por que ese sacrificio es correcto o incorrecto para este caso |
|---|---|---|---|
| Core de pagos (debito/credito de saldos) | CP | Disponibilidad durante particiones de red | Es correcto sacrificar disponibilidad temporal si hay una particion, porque es preferible rechazar o pausar una operacion antes que confirmar saldos inconsistentes. En pagos, la consistencia es obligatoria: no se puede duplicar dinero ni descontar dos veces. |
| Historial "mis ultimas 50 transacciones" | AP | Consistencia fuerte inmediata | Es aceptable que el historial tenga consistencia eventual por algunos segundos, porque no modifica dinero sino que muestra informacion de consulta. El usuario puede ver la transaccion con pequeno retraso, pero el servicio debe seguir disponible y responder rapido. |

---

## 1.3 NewSQL

**a) Que limitacion de Oracle resuelve CockroachDB al escalar de 15M a 50M usuarios?**

CockroachDB resuelve la limitacion de escalamiento horizontal del core transaccional. En una arquitectura Oracle tradicional, escalar escrituras distribuidas puede depender de hardware vertical, replicas complejas o particionamiento dificil. CockroachDB distribuye datos y transacciones entre nodos, permitiendo crecer agregando servidores sin abandonar SQL ni ACID.

**b) Por que MongoDB NO puede reemplazar a Oracle para el procesamiento de pagos aunque tambien escala horizontalmente?**

MongoDB es muy adecuado para documentos flexibles, perfiles y catalogos, pero el core de pagos exige transacciones financieras con consistencia fuerte, restricciones, aislamiento y control estricto de debitos y creditos. Aunque MongoDB soporta transacciones, su modelo principal no esta optimizado para ser el libro mayor financiero central donde cada operacion monetaria debe ser ACID y auditable al maximo nivel.

**c) Que mecanismo tecnico usa CockroachDB para mantener ACID en multiples nodos distribuidos?**

CockroachDB usa consenso distribuido basado en **Raft**.

