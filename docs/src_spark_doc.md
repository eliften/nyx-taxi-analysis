# NYC Taxi Data Pipeline: Medallion Architecture & Spark Performance Optimization

Bu proje, Kaggle NYC Taxi veri setini kullanarak uçtan uca bir veri işleme boru hattı (ETL) inşa etmektedir. Pipeline, veri kalitesini ve işleme hızını optimize etmek amacıyla Medallion mimarisi ve Spark Adaptive Query Execution (AQE) tekniklerini kullanır.

Dosya geçişlerini sadece isim olarak değil, işlev olarak da tanımlamak raporun ağırlığını artırır.

**Bronze Layer**: Ham verinin (CSV) değişmez (immutable) şekilde Delta formatında saklanması.

**Silver Layer**: Veri tiplerinin düzeltilmesi, null/negatif değer temizliği ve şema doğrulaması.

**Gold Layer**: İş birimleri için hazır, agrege edilmiş yüksek kaliteli veri tabloları.

Veri yükleme adımında AQE kullanılarak %59.02'lik iyileştirme elde edilmiştir.


### Teknik Özet

### Parametre          Baseline (AQE off)         Tuned(AQE on)                 Değişim
Süre                         15.12                    6.33                      %59.02
Shuffle                      Standart                 Broadcast Join            Network I/O Azaltıldı
Partition                    Statik                   Dynamic coalescing        Küçük Dosya Sorunu Çözüldü