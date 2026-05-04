import kagglehub
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO)

def get_data_from_kaggle(project="anandaramg/taxi-trip-data-nyc"):
    logging.info("Kaggle'dan veri indiriliyor...")
    path = kagglehub.dataset_download(project)

    csv_path = None
    for dirname, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".csv"):
                csv_path = os.path.join(dirname, filename)
                break
    
    if not csv_path:
        raise FileNotFoundError("CSV dosyası bulunamadı!")

    df = pd.read_csv(csv_path, low_memory=False)

    # 2. Schema Assert (Şema Doğrulama)
    # Kritik sütunların varlığını kontrol et (Sessiz hataları önlemek için)
    expected_columns = ['VendorID', 'lpep_pickup_datetime', 'trip_distance', 'fare_amount']
    for col in expected_columns:
        assert col in df.columns, f"HATA: {col} sütunu ham veride bulunamadı!"
    
    logging.info("Schema doğrulaması başarılı.")

    # 3. Bronze Katmanına Yaz
    output_path = "data/bronze/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    file_full_path = os.path.join(output_path, "taxi_raw.parquet") # Parquet daha hızlıdır
    df.to_parquet(file_full_path, index=False)
    
    logging.info(f"Bronze veri kaydedildi: {file_full_path}")
    return df
