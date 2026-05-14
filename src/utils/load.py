from sqlalchemy import create_engine
import os
import dotenv

dotenv.load_dotenv() 

class DatabaseLoader:
    def __init__(self):
        # Bilgileri .env dosyasından alıyoruz
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_NAME")
        print(f"DB_USER: {self.user}, DB_PASSWORD: {self.password}, DB_HOST: {self.host}, DB_NAME: {self.db_name}")
        
        self.engine = self._create_engine()

    def _create_engine(self):
        url = f"postgresql://{self.user}:{self.password}@{self.host}/{self.db_name}"
        print(url)
        return create_engine(url)

    def load_to_sql(self, df, table_name, if_exists="append"):
        try:
            df.to_sql(
                table_name,
                self.engine,
                index=True,
                if_exists=if_exists,
                chunksize=10000
            )
            print(f"Başarıyla {table_name} tablosuna yüklendi.")
        except Exception as e:
            print(f"Veritabanına yükleme sırasında hata oluştu: {e}")