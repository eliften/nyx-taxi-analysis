import logging
import time
import shutil
import os
import dotenv
from spark_pipeline import bronze, silver, gold
from pyspark.sql.functions import broadcast
from utils.spark_manager import SparkManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
dotenv.load_dotenv()

class TaxiETL:
    def __init__(self, project_id="anandaramg/taxi-trip-data-nyc"):
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.driver = os.getenv("DRIVER")
        self.project_id = project_id
        self.data_path = "dataSpark"
        self.spark = SparkManager.get_session()

    def clear_data_folders(self):
        if os.path.exists(self.data_path):
            logging.info(f"Temizlik yapılıyor: {self.data_path} siliniyor...")
            shutil.rmtree(self.data_path)

    def load_to_postgresql(self, df, table_name, mode="overwrite"):
        jdbc_url = "jdbc:postgresql://localhost:5432/postgres"
        properties = {
            "user": self.user,
            "password": self.password,
            "driver": self.driver
        }
        df.write.jdbc(url=jdbc_url, table=table_name, mode=mode, properties=properties)

    def prepare_vendor_lookup(self):
        lookup_data = [(1, "Uber"), (2, "Yellow Taxi")]
        lookup_df = self.spark.createDataFrame(lookup_data, ["VendorID", "VendorName"])
        lookup_df.write.format("delta").mode("overwrite").save("dataSpark/lookup/vendor_lookup")
        return lookup_df

    def execute_pipeline(self, scenario_name):
        start_time = time.time()
        logging.info(f">>> {scenario_name} Başlatıldı...")

        df_bronze = bronze.pipe(self.project_id)
        df_silver = silver.pipe()
        df_gold_r, df_gold_t = gold.pipe()

        lookup = self.prepare_vendor_lookup()
        df_final_with_lookup = df_bronze.join(broadcast(lookup), "VendorID", "left")

        logging.info(f"{scenario_name} için DB yazma işlemi başlıyor...")
        self.load_to_postgresql(df_bronze, f"bronze_{scenario_name}")
        self.load_to_postgresql(df_silver, f"silver_{scenario_name}")
        self.load_to_postgresql(df_gold_r, f"gold_rev_{scenario_name}")
        self.load_to_postgresql(df_final_with_lookup, f"bronze_rev_lookup_{scenario_name}")

        end_time = time.time()
        return end_time - start_time

    def run_benchmarks(self):
        results = {}

        # 1. BASELINE: AQE Kapalı, Broadcast Kapalı
        self.clear_data_folders()
        self.spark.conf.set("spark.sql.adaptive.enabled", "false")
        self.spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
        results['Baseline'] = self.execute_pipeline("Baseline_AQE_Off")

        # 2. TUNED: AQE Açık, Broadcast Otomatik (10MB)
        self.clear_data_folders() 
        self.spark.conf.set("spark.sql.adaptive.enabled", "true")
        self.spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true") 
        self.spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760") # 10MB
        results['Tuned'] = self.execute_pipeline("Tuned_AQE_On")

        logging.info("="*40)
        for key, value in results.items():
            logging.info(f"{key} SÜRE: {value:.2f} saniye")
        
        improvement = ((results['Baseline'] - results['Tuned']) / results['Baseline']) * 100
        logging.info(f"TOPLAM İYİLEŞME: %{improvement:.2f}")
        logging.info("="*40)

if __name__ == "__main__":
    etl = TaxiETL()
    etl.run_benchmarks()