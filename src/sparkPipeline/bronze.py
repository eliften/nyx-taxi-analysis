import pyspark, logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import kagglehub, os

logging.basicConfig(level=logging.INFO)

def spark_session():
    spark = SparkSession.builder.appName("NYC Taxi Data Pipeline").getOrCreate()
    return spark

def read_data(project="anandaramg/taxi-trip-data-nyc"):
    path = kagglehub.dataset_download(project)
    csv_path = None

    for dirname, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".csv"):
                csv_path = os.path.join(dirname, filename)
                break
    
    if not csv_path:
        raise FileNotFoundError("CSV dosyası bulunamadı!")
    
    expected_columns = ['VendorID', 'lpep_pickup_datetime', 'trip_distance', 'fare_amount']
    for col in expected_columns:
        assert col in df.columns, f"HATA: {col} sütunu ham veride bulunamadı!"
    
    logging.info("Schema doğrulaması başarılı.")

    df = spark.read.csv(csv_path, header=True, inferSchema=True)
    return df


if __name__ == "__main__":
    spark = spark_session()
    df = read_data()
