import pandas as pd, numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO)


def calc_trip_time(pickup: np.array, dropoff: np.array) -> np.array:
    trip_duration = (dropoff - pickup).dt.total_seconds() / 60

    return trip_duration

def avg_speed(distance, duration):
    avg_speed = distance / duration
    return avg_speed

def process_silver():
    input_path = "data/bronze/taxi_raw.parquet"
    if not os.path.exists(input_path):
        raise FileNotFoundError("Bronze veri bulunamadı! Önce bronze.py çalıştırılmalı.")
    
    df = pd.read_parquet(input_path)
    logging.info(f"Bronze veri okundu: {len(df)} satır.")


    df['trip_duration_min'] = calc_trip_time(df['lpep_pickup_datetime'], df['lpep_dropoff_datetime'])

    df['avg_speed_kmh'] = np.where(df['trip_duration_min'] > 0, 
                                   df['trip_distance'] / (df['trip_duration_min'] / 60), 0)
    
    assert (df['fare_amount'] >= 0).all(), "HATA: Silver veride hala negatif ücret var!"
    assert (df['trip_distance'] > 0).all(), "HATA: Mesafe 0 veya negatif olamaz!"
    assert not df['lpep_pickup_datetime'].isna().any(), "HATA: Tarih sütununda boş değerler var!"
    
    logging.info(f"Silver temizliği tamamlandı: {len(df)} satır kaldı.")

    output_path = "data/silver/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    file_full_path = os.path.join(output_path, "taxi_cleaned.parquet")
    df.to_parquet(file_full_path, index=False)
    
    logging.info(f"Silver veri kaydedildi: {file_full_path}")
    return df


