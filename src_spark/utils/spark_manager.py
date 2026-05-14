from pyspark.sql import SparkSession

class SparkManager:
    _spark = None

    @staticmethod
    def get_session():
        if SparkManager._spark is None:
            SparkManager._spark = (SparkSession.builder 
                .appName("NYC Taxi Pipeline")
                .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.0,org.postgresql:postgresql:42.7.2")
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                .config("spark.sql.execution.arrow.pyspark.enabled", "true")
                .getOrCreate())
        return SparkManager._spark