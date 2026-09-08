# Bitirme projesi: küpten kaba

Bu projenin çıktısı bir başarılı video ve açıklanabilir bir deney raporudur. Eğitim, veri ve değerlendirme dosyaları birbirine bağlanır; başka gün aynı denemeyi tekrar kurabilirsin.

## Proje tanımı

**Görev:** tek kırmızı küpü çalışma alanından al, belirli kaba bırak. **Ortam:** sabit masa ve kamera düzeni. **Başlangıç varyasyonu:** beş küçük bölge. **Başarı:** küp kap içinde kalır, tutucu geri çekilir ve süre sınırı aşılmaz. **Başarısızlık etiketleri:** `approach_miss`, `grasp_miss`, `drop`, `place_miss`, `timeout`, `system_error`.

Bu etiketler örnek taksonomidir. Senin görevinde “sistem hatası” ile “politika yanlış davranışı”nı ayrı raporlamak yararlıdır. Bir USB kopmasını gizleyerek değerlendirme sayısından silme; protokolünü baştan tanımla.

## Aşama A · Robot gelmeden

Kurulumu tamamla, MuJoCo hedef takip deneyini ve SO-101 görüntüsünü üret. Üç sim episode kaydet, parquet denetimini ve video okumayı çalıştır. Tarayıcıdaki veri planlayıcıyla pilot/ana veri süresini hesapla.

**Teslim:** `doctor` çıktısı, iki sim PNG, dataset denetim raporu, bir decode edilmiş frame. Bu aşamanın sonucu çalışan altyapıdır; kavrama politikası değildir.

## Aşama B · Gerçek pilot

Cihaz kartı ve kalibrasyonu tamamla. Kameralardan bakarak beş pilot gösterim yap. Görüntü, reset, görev metni ve birim sorunlarını düzelt.

**Teslim:** beş okunabilir episode, kamera yerleşim fotoğrafı/notu, kayıt komutu ve kalibrasyon ID'leri.

## Aşama C · Dataset v1

Başlangıç bölgelerinden dengeli gösterimler topla. Başarısız denemeleri etiketle/ayır. Episode bazlı validation ayır; son test için kullanılacak koşulları ayrı not et. Aynı hareketin karelerini rastgele iki tarafa dağıtma.

**Teslim:** veri kökü/revision, kalite raporu, split açıklaması ve görev sözleşmesi.

## Aşama D · İki öğrenme deneyi

Aynı veri üzerinde ACT baseline ve SmolVLA fine-tuning hazırla. İkisinde de önce smoke koşusu yap. Hyperparametre, toplam süre, tepe bellek ve checkpoint adımlarını kaydet.

**Teslim:** loss kayıtları, processor'larıyla birlikte checkpoint ve eğitim komutları. Aynı adım sayısının farklı modeller için farklı hesaplama harcaması olduğunu raporda belirt.

## Aşama E · Test

Beş bölgeden dörder tekrar önerilen 20 denemeyi oluşturur. Model sırasının avantaj yaratmaması için koşulları dengeli sırala. Her denemeyi aynı reset/protokolle başlat. Bütün videolar ve hata etiketleri saklansın.

```text
Model           Başarı    Sık hata          p95 inference   Koşul
ACT-v1          ölç       ölç               ölç             aynı test
SmolVLA-v1      ölç       ölç               ölç             aynı test
SmolVLA-v2      ölç       ölç               ölç             aynı test
```

Bu tablo sonuç şablonudur; sayılar deneyden sonra doldurulur. Son test setine tekrar tekrar göre ayar yaparsan artık model seçme setine dönüşür; yeni final test planla.

## Aşama F · Bir iyileştirme

En sık hata `grasp_miss` ise yalnız buna odaklan: kamera görünürlüğü mü, başlangıç kapsamı mı, yaklaşım gösterimi mi? Hipotezini yaz, tek değişkeni değiştir, dataset/checkpoint v2 oluştur ve aynı validation protokolünde karşılaştır.

## Teslim klasörü

```text
outputs/project-report/
  experiment.md
  environment.txt
  data-contract.json
  training-command.sh
  evaluation.csv
  metrics.json
  videos/
```

`templates/experiment.md` ve `templates/evaluation.csv` başlangıç sağlar. README'ye çalıştırma sırasını yaz. “Bu koşullarda çalışıyor, şu koşullar henüz ölçülmedi” ifadesi raporun pratik değerini artırır.
