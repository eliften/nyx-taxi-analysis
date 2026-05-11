import kagglehub
import pandas as pd
import os
import logging
import numpy as np

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

    expected_columns = ['VendorID', 'lpep_pickup_datetime', 'trip_distance', 'fare_amount']
    for col in expected_columns:
        assert col in df.columns, f"HATA: {col} sütunu ham veride bulunamadı!"
    
    logging.info("Schema doğrulaması başarılı.")

    return df

def remove_high_missing_columns(df, threshold=0.5):
    return df.loc[:, df.isnull().mean() < threshold]

def eliminate_negatives(data: pd.DataFrame):
    data=data.drop('ehail_fee', axis=1)
    numeric_cols = data.select_dtypes(include=[np.number]).columns

    data = data[(data[numeric_cols] >= 0).all(axis=1)]
    return data

def fix_types(data: pd.DataFrame):
    data["lpep_pickup_datetime"] = pd.to_datetime(
        data["lpep_pickup_datetime"],
        errors="coerce"
    )

    data["lpep_dropoff_datetime"] = pd.to_datetime(
        data["lpep_dropoff_datetime"],
        errors="coerce"
    )
    return data

def pipe(project="anandaramg/taxi-trip-data-nyc"):
    df = get_data_from_kaggle(project)
    df = df.pipe(eliminate_negatives).pipe(fix_types)

    output_path = "data/bronze/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    file_full_path = os.path.join(output_path, "taxi_raw.parquet")
    df.to_parquet(file_full_path, index=False)
    
    logging.info(f"Bronze veri kaydedildi: {file_full_path}")

