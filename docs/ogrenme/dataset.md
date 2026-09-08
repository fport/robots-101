# LeRobot veri setini okumak

Robot verisi sadece video değildir. Eğitim (training) için görüntülerin, eklem (joint) durum (state)'inin, gönderilen eylem (action)'ın, görev metninin ve zaman indekslerinin birbiriyle ilişkisi gerekir.

## V3 biçimi

LeRobot v3, tablo verilerini parquet, videoları MP4 parçaları ve genel bilgileri üstveri (metadata) olarak saklar. Bir bölüm (episode) her zaman ayrı bir video dosyası demek değildir; paylaşılan dosyada zaman/indeks aralığıyla temsil edilebilir. Dosya adını tahmin etmek yerine metadata'yı kullan. [LeRobotDataset v3](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

```text
dataset-root/
  meta/
    info.json
    stats.json
    episodes/...
    tasks...
  data/
    chunk-.../file-....parquet
  videos/
    observation.images.front/...
    observation.images.wrist/...
```

Bu ağaç kavramsaldır; tam bölümleme/yolları mevcut `info.json` ve episode metadata'sından oku. Eski v2.1 dosya düzenini v3 veri setine elle uygulama.

## Bir örnekte ne görürsün?

| Alan | Anlam |
|---|---|
| `episode_index` | Hangi bağımsız gösterim (demonstration) |
| `frame_index` | Episode içindeki sıra |
| `timestamp` | O episode içindeki örnek zamanı |
| `observation.state` | O an ölçülen robot durumu |
| `action` | O gözlemden sonra gönderilen hedef |
| `observation.images.front` | Kamera görüntüsü veya ilgili video referansı |
| Görev indeksi / metni | Yapılmak istenen iş |

Metadata'daki görüntü şekli HWC olabilir; model tensörü BCHW bekleyebilir. `05_prepare_training.py` görüntü shape'ini kanal-ilk politika (policy) tanımına çevirir. Bu dönüştürme, RGB/BGR sırasını değiştirmekle aynı işlem değildir.

## Sayısal denetim

```bash
.venv-ml/bin/python examples/04_inspect_dataset.py data/sim-smoke-verified --expected-episodes 3
```

Script gerçek parquet satırlarında episode sınırlarını, kare (frame) sırasını, FPS/timestamp ilişkisini, NaN/Inf ve feature boyutlarını kontrol eder. Başarısızlıkta sıfırdan farklı çıkış kodu verir. Test edilen örnekte sonuç `3 episode`, `90 frame`, `errors: []` oldu.

Bu araç küçük/orta atölye verisini belleğe alır; büyük veri için bölüm bölüm veya streaming denetim tasarlamalısın. Hata olmaması görüntülerin anlamlı, görevin başarılı ya da eylem birimlerinin doğru olduğunu göstermez.

## LeRobot ile bir frame oku

`examples/08_read_dataset.py` yerel kökten okur ve ilk görüntüyü PNG olarak çıkarır:

```bash
.venv-ml/bin/python examples/08_read_dataset.py \
  --root data/sim-smoke-verified --repo-id local/sim-smoke
```

Bu atölyede Mac'te FFmpeg shared library bulunmadığında çalışan yol olarak **PyAV decoder** açıkça seçilir. `torchcodec` kurulmuş olsa bile runtime kütüphanesinin yüklenebildiği ayrıca test edilmelidir. Bir encoder'ın MP4 yazabilmesi bütün decoder'ların çalıştığını kanıtlamaz.

## Normalize etmek

State ve action'ın değişken aralıklarını model için uygun ölçeğe taşımak gerekir. Ortalama/standart sapma kullanılan bir örnekte:

```text
normalized = (raw - mean) / std
raw        = normalized * std + mean
```

Politika son işlemesinin ters dönüşümü doğru dataset stats ile yapması gerekir. Başka veri setinin (dataset) stats dosyasını kopyalamak boyutları eşleşse de hatalı hedefler üretir. Çok küçük standart sapma, sabit kanal ve clipping davranışını da kullanılan processor belirler; bunları elle keyfî yamalama.

## Eğitim/validation/test

Eğitim ağırlıkları günceller. doğrulama (Validation) kontrol noktası (checkpoint)/hiperparametre seçmeye yardımcı olur. Son test daha önce karar vermek için kullanılmamış koşullarda rapor üretir. Episode bazlı validation, ardışık frame sızıntısını azaltır; farklı gün/kamera/nesneye genellemeyi tek başına ölçmez.

Bu rehberin komut üreticisi normal eğitim için `dataset.eval_split=0.2` ve periyodik eval loss kullanır. Üç episode'luk smoke veri bu oranla en az bir validation episode sağlamadığı için `--eval-split 0` ile yalnız boru hattı denemesi yapılır. Son testin yerine geçmez.

## Dataset sözleşmesi defteri

Her sürümde kamera adları/pozları, robot ID/kalibrasyonu, action sırası ve birimi, kayıt FPS, görev metni, başarı etiketi, gösterim kaynağı ve split politikasını kaydet. Modelin giriş şeması bu defterle örtüşmüyorsa eğitim başlatmadan önce düzelt.
