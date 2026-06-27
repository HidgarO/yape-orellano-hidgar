# ============================================================
# P2 - Pipeline de Transacciones Yape en Databricks
# Estudiante: Hidgar Orellano Huerta
# Codigo: 2221892872
# ============================================================

# COMMAND ----------

# ============================================================
# CELDA 1: Dataset sintetico - 2,000 transacciones Yape
# ============================================================
import numpy as np
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import *

np.random.seed(42)

n = 2000
distritos = ["Miraflores", "San Isidro", "SJL", "Comas", "Villa El Salvador",
             "Los Olivos", "Surco", "Ate", "Callao", "Independencia"]
tipos     = ["persona_a_persona", "persona_a_comercio", "retiro_bcp", "recarga"]
estados   = ["completada", "completada", "completada", "rechazada", "pendiente"]

data = {
    "id_transaccion": [f"YP{i:07d}" for i in range(1, n+1)],
    "fecha":          pd.date_range("2025-01-01", periods=n, freq="1h").strftime("%Y-%m-%d").tolist(),
    "hora":           [f"{h:02d}:{m:02d}" for h, m in zip(np.random.randint(0,24,n), np.random.randint(0,60,n))],
    "monto_soles":    np.round(np.random.exponential(45, n), 2).tolist(),
    "tipo":           np.random.choice(tipos, n).tolist(),
    "distrito_origen":np.random.choice(distritos, n).tolist(),
    "estado":         np.random.choice(estados, n, p=[0.75, 0.1, 0.05, 0.07, 0.03]).tolist(),
    "id_usuario":     [f"USR{np.random.randint(1000,9999)}" for _ in range(n)],
    "es_comercio":    np.random.choice([True, False], n, p=[0.4, 0.6]).tolist()
}

df_pandas = pd.DataFrame(data)
df_bronze = spark.createDataFrame(df_pandas)
spark.sql("CREATE DATABASE IF NOT EXISTS yape_db")
df_bronze.write.mode("overwrite").saveAsTable("yape_db.bronze_transacciones")

print(f"Bronze layer: {df_bronze.count()} transacciones guardadas")
df_bronze.show(5)

# COMMAND ----------

# ============================================================
# CELDA 2: Silver - limpiar y transformar
# ============================================================
df_bronze = spark.table("yape_db.bronze_transacciones")

df_silver = df_bronze \
    .filter(df_bronze.estado == "completada") \
    .filter(df_bronze.monto_soles > 0) \
    .withColumn("categoria_monto",
        F.when(F.col("monto_soles") < 20, "micro")
         .when(F.col("monto_soles") < 100, "medio")
         .otherwise("alto")) \
    .withColumn("es_hora_pico",
        F.when(F.col("hora").between("12:00", "14:00"), True)
         .when(F.col("hora").between("18:00", "22:00"), True)
         .otherwise(False)) \
    .withColumn("comision_yape",
        F.when(F.col("tipo") == "persona_a_comercio",
               F.round(F.col("monto_soles") * 0.015, 2))
         .otherwise(0.0))

df_silver.write.mode("overwrite").saveAsTable("yape_db.silver_transacciones_limpias")

print(f"Silver layer: {df_silver.count()} transacciones validas")
print(f"Eliminadas: {df_bronze.count() - df_silver.count()} (rechazadas/pendientes/monto cero)")
df_silver.groupBy("categoria_monto").count().show()
df_silver.select("id_transaccion", "estado", "monto_soles", "categoria_monto", "es_hora_pico", "comision_yape").show(10)

# COMMAND ----------

# ============================================================
# CELDA 3: Gold - agregaciones para dashboard ejecutivo
# ============================================================
df_silver = spark.table("yape_db.silver_transacciones_limpias")
df_silver.createOrReplaceTempView("transacciones")

# Gold 1: Top 5 distritos por volumen de transacciones
gold_distritos = spark.sql("""
    SELECT 
        distrito_origen,
        COUNT(*)                          AS total_transacciones,
        ROUND(SUM(monto_soles), 2)        AS volumen_total_soles,
        ROUND(AVG(monto_soles), 2)        AS ticket_promedio,
        SUM(CASE WHEN es_comercio THEN 1 ELSE 0 END) AS transacciones_comercio
    FROM transacciones
    GROUP BY distrito_origen
    ORDER BY total_transacciones DESC
    LIMIT 5
""")

# Gold 2: Ingresos Yape por hora del dia (comisiones de comercios)
gold_comisiones = spark.sql("""
    SELECT
        SUBSTRING(hora, 1, 2)             AS hora_dia,
        COUNT(*)                          AS num_transacciones,
        ROUND(SUM(comision_yape), 2)      AS ingresos_yape_soles
    FROM transacciones
    WHERE comision_yape > 0
    GROUP BY SUBSTRING(hora, 1, 2)
    ORDER BY ingresos_yape_soles DESC
""")

spark.sql("DROP TABLE IF EXISTS yape_db.gold_top_distritos")
spark.sql("DROP TABLE IF EXISTS yape_db.gold_ingresos_por_hora")

gold_distritos.write.mode("overwrite").saveAsTable("yape_db.gold_top_distritos")
gold_comisiones.write.mode("overwrite").saveAsTable("yape_db.gold_ingresos_por_hora")


print("TOP 5 DISTRITOS POR VOLUMEN YAPE:")
gold_distritos.show()

print("INGRESOS YAPE POR HORA (comision comercios):")
gold_comisiones.show(5)

# COMMAND ----------

# ============================================================
# CELDA 4: Visualizacion - grafico de barras con matplotlib
# ============================================================
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

df_gold_distritos = spark.table("yape_db.gold_top_distritos").toPandas()
df_gold_comisiones = spark.table("yape_db.gold_ingresos_por_hora").toPandas()

df_gold_comisiones = df_gold_comisiones.sort_values("hora_dia")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Dashboard Ejecutivo YAPE - Analisis de Transacciones", fontsize=14, fontweight="bold")

# Grafico 1: Top 5 distritos
axes[0].barh(
    df_gold_distritos["distrito_origen"].astype(str),
    df_gold_distritos["volumen_total_soles"].astype(float),
    color=["#c41230","#e63950","#f47a8a","#f9b4bc","#fde8ea"]
)
axes[0].set_xlabel("Volumen total (S/)")
axes[0].set_title("Top 5 Distritos - Volumen de Pagos")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"S/{x:,.0f}"))

# Grafico 2: Ingresos Yape por hora
axes[1].plot(
    df_gold_comisiones["hora_dia"].astype(str),
    df_gold_comisiones["ingresos_yape_soles"].astype(float),
    marker="o",
    color="#c41230",
    linewidth=2
)
axes[1].fill_between(df_gold_comisiones["hora_dia"], df_gold_comisiones["ingresos_yape_soles"],
                     alpha=0.15, color='#c41230')
axes[1].set_xlabel("Hora del dia")
axes[1].set_ylabel("Comision recaudada (S/)")
axes[1].set_title("Ingresos Yape por Hora")
axes[1].tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.show()

print("Dashboard generado correctamente usando tablas Gold de yape_db.")

# COMMAND ----------

