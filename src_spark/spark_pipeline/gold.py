from pyspark.sql import functions as F
from pyspark.sql.functions import col
import logging
from src_spark.utils.spark_manager import SparkManager

def create_hourly_traffic_stats(df):
    """Saatlik bazda trafik yoğunluğu ve ortalama hız analizi."""
    return df.groupBy("hour", "day_of_week", "weekend").agg(
        F.avg("avg_speed_kmh").alias("avg_speed_kmh"),
        F.avg("trip_duration").alias("avg_duration_min"),
        F.count("lpep_pickup_datetime").alias("total_trips")
    )

def create_revenue_metrics(df):
    """Ödeme türü ve gün bazında gelir analizi."""
    return df.groupBy("day_of_week", "payment_type").agg(
        F.sum("total_amount").alias("total_revenue"),
        F.avg("fare_amount").alias("avg_fare"),
        F.sum("co2_emissions_kg").alias("total_co2_kg")
    )

def pipe():
    spark = SparkManager.get_session()
    logging.basicConfig(level=logging.INFO)

    silver_path = "dataSpark/silver/taxi_raw"
    df_silver = spark.read.format("delta").load(silver_path)

    df_traffic = create_hourly_traffic_stats(df_silver)
    traffic_output = "dataSpark/gold/hourly_traffic_stats"
    df_traffic.write.format("delta").mode("overwrite").save(traffic_output)

    df_revenue = create_revenue_metrics(df_silver)
    revenue_output = "dataSpark/gold/revenue_metrics"
    df_revenue.write.format("delta").mode("overwrite").save(revenue_output)

    logging.info("Gold tabloları başarıyla oluşturuldu.")
    return df_revenue, df_traffic

