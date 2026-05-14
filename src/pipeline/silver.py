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

def clip_outliers(df, col, upper_q=0.95):
    lower = df[col].quantile(1-upper_q)
    upper = df[col].quantile(upper_q)
    df[col] = df[col].clip(upper=upper, lower=lower)
    return df

def filter_business_rules(data):
    data = data[
        (data["trip_distance"] > 0) & 
        (data["total_amount"] > 5) &
        (data["passenger_count"] > 0) &
        ~data["RatecodeID"].isin([3, 4]) &
        ~data["payment_type"].isin([4, 5])
    ]
    
    mask = (
        ((data["lpep_pickup_datetime"].dt.year >= 2015) & (data["improvement_surcharge"] == 0.3)) |
        ((data["lpep_pickup_datetime"].dt.year < 2015) & (data["improvement_surcharge"] == 0.0))
    )
    data = data[mask]
    return data


def pipe():
    input_path = "data/bronze/taxi_raw.parquet"
    if not os.path.exists(input_path):
        raise FileNotFoundError("Bronze veri bulunamadı! Önce bronze.py çalıştırılmalı.")
    
    df = pd.read_parquet(input_path)
    logging.info(f"Bronze veri okundu: {len(df)} satır.")


    df['trip_duration_min'] = calc_trip_time(df['lpep_pickup_datetime'], df['lpep_dropoff_datetime'])

    df['avg_speed_kmh'] = np.where(df['trip_duration_min'] > 0, 
                                   df['trip_distance'] / (df['trip_duration_min'] / 60), 0)
    
    df = clip_outliers(df, 'fare_amount')
    df = clip_outliers(df, 'trip_duration_min')

    df = filter_business_rules(df)
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


