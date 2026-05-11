from pyspark.sql.functions import col
from pyspark.sql import functions as F
import logging
from utils.spark_manager import SparkManager

spark = SparkManager.get_session()
logging.basicConfig(level=logging.INFO)

def calc_trip_time(df):
    df = df.withColumn("trip_duration", (F.unix_timestamp("lpep_dropoff_datetime") - F.unix_timestamp("lpep_pickup_datetime")) / 60)

    df.select("lpep_pickup_datetime", "lpep_dropoff_datetime", "trip_duration").show(5)

    df = df.withColumn("hour", F.hour("lpep_pickup_datetime"))
    df = df.withColumn("day_of_week", F.date_format("lpep_pickup_datetime", "E"))
    df = df.withColumn("weekend", F.when(F.dayofweek("lpep_pickup_datetime").isin(1, 7), 1).otherwise(0))
    return df

def avg_speed(df):
    df = df.withColumn("avg_speed_kmh", F.when(col("trip_duration") > 0, col("trip_distance") / (col("trip_duration") / 60)).otherwise(0))
    return df

def clip_outliers(df, column, q=0.05):
    lower_q = q
    upper_q = 1 - q
    quantiles = df.approxQuantile(column, [lower_q, upper_q], 0.01)

    lower_val = quantiles[0]
    upper_val = quantiles[1]

    return df.withColumn(column, 
            F.when(F.col(column) < lower_val, lower_val)
            .when(F.col(column) > upper_val, upper_val)
            .otherwise(F.col(column))
    )

def filter_business_rules(df):
    return df.filter((col("total_amount") > 5) &
                     (col("trip_distance") > 0) &
                     (col("passenger_count") > 0) &
                     (~col("RatecodeID").isin(3,4)) &
                     (~col("payment_type").isin(4,5)))

def calc_co2_emissions(df):
    df = df.withColumn("co2_emissions_kg", col("trip_distance") * 170)
    return df

def pipe(project="anandaramg/taxi-trip-data-nyc"):
    spark = SparkManager.get_session()

    path = "dataSpark/bronze/taxi_raw"
    df = spark.read.format("delta").load(path)
    df_cleaned = (df
        .transform(calc_trip_time)
        .transform(avg_speed)
        .transform(filter_business_rules)
        .transform(calc_co2_emissions)
        .transform(lambda d: clip_outliers(d, column="trip_duration"))
        .transform(lambda d: clip_outliers(d, column="fare_amount"))
    )

    output_path = "dataSpark/silver/taxi_raw"

    (df_cleaned.write
        .format("delta")
        .mode("overwrite")
        .save(output_path))
    
    logging.info(f"Silver veri Delta formatında kaydedildi: {output_path}")

    return df_cleaned