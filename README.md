# 🚕 NYC Taxi – Exploratory Data Analysis (EDA)

## 📌 Amaç

Bu çalışmada 6.9 GB büyüklüğündeki NYC Taxi veri seti incelenmiştir.
Amaç:

* Veri setinin genel yapısını anlamak
* Eksik veri ve aykırı değerleri tespit etmek
* Zaman serisi (time series) modellemesi için uygun bir iş senaryosu belirlemek

---

## 📂 Veri Kaynağı

* NYC Taxi Dataset (Kaggle)
* İçerik:

  * Yolculuk zamanları
  * Mesafe ve süre
  * Ücret bilgileri
  * Yolcu sayısı
  * Lokasyon bilgileri

---

## 🧱 Veri Keşfi (DuckDB)

Veri seti RAM’e tamamen alınmadan DuckDB ile incelenmiştir.

### Temel bilgiler:

* Toplam satır sayısı: **83,691** *(%5 sample üzerinden analiz yapılmıştır)*
* Toplam sütun sayısı: **20**

### Sütunlar:

* VendorID
* lpep_pickup_datetime
* lpep_dropoff_datetime
* store_and_fwd_flag
* RatecodeID
* PULocationID
* DOLocationID
* passenger_count
* trip_distance
* fare_amount
* extra
* mta_tax
* tip_amount
* tolls_amount
* ehail_fee
* improvement_surcharge
* total_amount
* payment_type
* trip_type
* congestion_surcharge

---

## 📊 Temel İstatistikler (%5 Örneklem)

Pandas kullanılarak örneklem üzerinden temel istatistikler hesaplanmıştır:

* Sayısal kolonlar için min / max / median değerler incelenmiştir
* Veri dağılımı ve uç değerler gözlemlenmiştir

---

## 🔍 Eksik Veri Analizi

Eksik veri oranları incelenmiştir.

### Bulgular:

* `ehail_fee` kolonu tamamen boştur (%100 missing)
* Aşağıdaki kolonlarda yaklaşık %40 eksik veri bulunmaktadır:

  * VendorID
  * store_and_fwd_flag
  * RatecodeID
  * passenger_count
  * payment_type
  * trip_type
  * congestion_surcharge

👉 Bu durumun veri üretim sürecinden kaynaklanan yapısal bir eksiklik olduğu değerlendirilmiştir.

---

## ⚠️ Aykırı Değer Analizi

Veri setinde aşağıdaki anomali durumları tespit edilmiştir:

* Negatif değerler (özellikle ücret ve mesafe alanlarında)
* `trip_distance <= 0` olan kayıtlar
* `total_amount <= 5` olan kayıtlar
* Olağan dışı yüksek mesafe değerleri
* Negatif veya hatalı süre hesapları

👉 Bu değerler veri kalitesini bozabilecek açık aykırılıklar olarak değerlendirilmiştir.

2015 yılından sonra başlayan 0.3 değerindeki 'improvement_surcharge' için yıl ödeme filtresi yapıldı

- Yolculuk süresi,
- Ortalama hız;
Değerleri hesaplanıp yeni feature olarak eklendi.


---

## 🎯 Senaryo Seçimi

### Ana Senaryo: **Order Count**

* Hedef kolon: `lpep_pickup_datetime`
* Metrik: Günlük yolculuk sayısı (count)
* Paydaş: Operasyon

**İş Sorusu:**
Yarın kaç sürücüye ihtiyaç olacak?

### Alternatif Senaryo: **Average Fare**

* Hedef kolon: `total_amount`
* Metrik: Ortalama ücret (mean)
* Paydaş: Strateji

**İş Sorusu:**
Yolculuk başına ortalama ücret trendi nasıl değişiyor?

---

## 🧠 Senaryo Seçim Gerekçesi

Veri seti zaman damgası (timestamp) içeren zengin bir yapıya sahiptir ve bu nedenle zaman serisi analizine uygundur.
Ana senaryo olarak **Order Count** seçilmiştir çünkü operasyonel planlama açısından doğrudan aksiyona dönüştürülebilir bir çıktıdır (sürücü sayısı planlama).

Alternatif olarak **Average Fare** senaryosu değerlendirilmiştir. Bu senaryo fiyat trendlerini anlamak ve stratejik karar destek sağlamak için uygundur.

Karbon emilimi ile ilgili bir analiz de eklenecektir.
*km ~= 181 gram karbondioksit*

## Medallion mimarisi üzerine
Bu mimaride ETL süreçleri dikkate alınmıştır.

Bronze, Silver ve gold katmanları ile süreç düzenlenmiştir.

### Bronze
Ham verinin yüklenmesi ve kaydedilme sürecini fonksiyonel olarak tutar

### Silver 
Ham verinin orijinal halini bozmadan okur temizler ve özellik mühendisliği ile yeni featurelar oluşturup ayrı bir parquet dosyasında kaydeder.

### Gold
Aldığı silver veriyi kullanıcı için anlamlı istatistiksel bilgi ve grafiklere dönüştürür.

## Load süreci
Postgresql kullanılmış olup süreçlerde oluşturulan bilgiler table olarak kayddilmiştir. buradaki amaç bir süreçte sorun çıktığında baştan başlamamayı sağlamaktır.



