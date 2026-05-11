import logging
import pandas as pd
from pipeline.bronze import pipe
from pipeline import silver
from pipeline.gold import create_gold_daily_trips  # Gold modülünü eklediğini varsayıyoruz
from utils.load import DatabaseLoader

# Loglama ayarı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TaxiETL:
    def __init__(self, project_id="anandaramg/taxi-trip-data-nyc"):
        self.project_id = project_id
        self.df_silver = None
        self.df_gold = None

    def run(self):
        logging.info(f"--- Medallion Pipeline Başladı: {self.project_id} ---")

        # Data precessing
        self.df_bronze = pipe(self.project_id)
        self.df_silver = silver.process_silver()
        self.df_gold = create_gold_daily_trips()

        # Load to database
        db_loader = DatabaseLoader()
        db_loader.load_to_sql(self.df_silver, "silver_taxi_trips", if_exists="replace")
        db_loader.load_to_sql(self.df_gold, "gold_daily_trips", if_exists="replace")
        logging.info(f"--- Medallion Pipeline Tamamlandı: {self.project_id} ---")
       

if __name__ == "__main__":
    TaxiETL().run()