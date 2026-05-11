from pyspark.sql.functions import col
from pyspark.sql import functions as F
from pyspark.sql.types import NumericType
import kagglehub, os, logging
from src.utils.spark_manager import SparkManager

spark = SparkManager().get_session()

logging.basicConfig(level=logging.INFO)

def get_data_from_kaggle(project="anandaramg/taxi-trip-data-nyc"):
    path = kagglehub.dataset_download(project)
    csv_path = None

    for dirname, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".csv"):
                csv_path = os.path.join(dirname, filename)
                break
    
    if not csv_path:
        raise FileNotFoundError("CSV dosyası bulunamadı!")
    df = spark.read.csv(csv_path, header=True, inferSchema=True)

    expected_columns = ['VendorID', 'lpep_pickup_datetime', 'trip_distance', 'fare_amount']
    for col in expected_columns:
        assert col in df.columns, f"HATA: {col} sütunu ham veride bulunamadı!"
    
    logging.info("Schema doğrulaması başarılı.")

    return df

def fix_types(df):
    df = (df.withColumn("trip_distance", col("trip_distance").cast("float"))
        .withColumn("fare_amount", col("fare_amount").cast("float"))
        .withColumn("extra", col("extra").cast("float"))
        .withColumn("mta_tax", col("mta_tax").cast("float"))
        .withColumn("tip_amount", col("tip_amount").cast("float"))
        .withColumn("tolls_amount", col("tolls_amount").cast("float"))
        .withColumn("total_amount", col("total_amount").cast("float"))
        .withColumn("congestion_surcharge", col("congestion_surcharge").cast("float"))
        )
    return df

def missing_report_pyspark(df):
    null_counts = df.select([
        F.mean(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(c)
        for c in df.columns
    ]).collect()[0].asDict()
    
    report_df = spark.createDataFrame(
    [(k, v) for k, v in null_counts.items()], 
            ["column_name", "missing_ratio"]
        )
    report_df = report_df.withColumn("missing_ratio", col("missing_ratio").cast("float"))
    
    return report_df.withColumn("missing_ratio", F.round("missing_ratio", 4)).orderBy(F.desc("missing_ratio"))

def remove_high_missing_columns(df, threshold=0.5):
    missing_report = missing_report_pyspark(df)
    columns_to_drop = missing_report.filter(col("missing_ratio") > threshold).select("column_name").rdd.flatMap(lambda x: x).collect()
    return df.drop(*columns_to_drop)

def eliminate_negatives(df):
    numeric_cols = [f.name for f in df.schema.fields if isinstance(f.dataType, NumericType)]

    for column in numeric_cols:
        df = df.filter(F.col(column) >= 0)

    return df

def pipe(project="anandaramg/taxi-trip-data-nyc"):
    df = get_data_from_kaggle(project)

    df_cleaned = (df
        .transform(eliminate_negatives)
        .transform(fix_types)
        .transform(remove_high_missing_columns, threshold=0.5)
    )

    output_path = "dataSpark/bronze/taxi_raw"

    (df_cleaned.write
        .format("delta")
        .mode("overwrite")
        .save(output_path))
    
    logging.info(f"Bronze veri Delta formatında kaydedildi: {output_path}")


if __name__ == "__main__":
    pipe()