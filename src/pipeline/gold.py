import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_gold_daily_trips():
    input_path = "data/silver/taxi_cleaned.parquet"
    if not os.path.exists(input_path):
        raise FileNotFoundError("Silver veri bulunamadı! Önce silver.py çalıştırılmalı.")
    
    df = pd.read_parquet(input_path)
    logging.info(f"Silver veri okundu. Satır sayısı: {len(df)}")

    df['pickup_date'] = df['lpep_pickup_datetime'].dt.date

    gold_df = df.groupby('pickup_date').agg(
        total_trips=('VendorID', 'count'),
        avg_fare=('fare_amount', 'mean'),
        total_distance=('trip_distance', 'sum')
    ).reset_index()

    assert not gold_df.empty, "HATA: Gold tablosu boş oluştu!"
    assert (gold_df['avg_fare'] > 0).all(), "HATA: Ortalama ücretlerde tutarsızlık var!"
    
    logging.info(f"Gold özeti oluşturuldu. Gün sayısı: {len(gold_df)}")

    output_path = "data/gold/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    file_full_path = os.path.join(output_path, "daily_trips.parquet")
    gold_df.to_parquet(file_full_path, index=False)
    
    logging.info(f"Gold veri başarıyla kaydedildi: {file_full_path}")
    return gold_df