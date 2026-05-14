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
Postgresql kullanılmış olup süreçlerde oluşturulan bilgiler table olarak kaydedilmiştir. Buradaki amaç bir süreçte sorun çıktığında baştan başlamamayı sağlamaktır.

