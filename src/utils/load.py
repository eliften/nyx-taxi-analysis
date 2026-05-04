from sqlalchemy import create_engine
import pandas as pd
import os

class DatabaseLoader:
    def __init__(self):
        # Bilgileri .env dosyasından alıyoruz
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "112233")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "postgres")
        
        self.engine = self._create_engine()

    def _create_engine(self):
        url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        return create_engine(url)

    def load_to_sql(self, df, table_name, if_exists="append"):
        """Veriyi veritabanına yükler."""
        try:
            df.to_sql(
                table_name,
                self.engine,
                index=False,
                if_exists=if_exists,
                chunksize=10000
            )
            print(f"Başarıyla {table_name} tablosuna yüklendi.")
        except Exception as e:
            print(f"Veritabanına yükleme sırasında hata oluştu: {e}")