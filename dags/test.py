from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# 1. Tanımlama: Bu iş akışının kimliği ve ayarları
with DAG(
    dag_id='ilk_denemem_airflow',      # Arayüzde göreceğin isim
    start_date=datetime(2024, 5, 1),   # Ne zamandan itibaren çalışabilir?
    catchup=False                      # Geçmişe dönük eksik günleri çalıştırma
) as dag:

    # 2. Görevler (Tasks): Yapılacak işler
    ilk_is = BashOperator(
        task_id='merhaba_de',
        bash_command='echo "test test!"'
    )

    ikinci_is = BashOperator(
        task_id='vakit_tamam',
        bash_command='date'
    )

    # 3. Akış (Pipeline): İşlerin sırası
    ilk_is >> ikinci_is