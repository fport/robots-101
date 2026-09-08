# Sorun giderme

Önce en küçük başarısız işlemi bul. Aynı anda kamera, CUDA, model ve robot bağlantısını değiştirmek sorunun kaynağını karıştırır. Hata kaydında ilk anlamlı hata satırını ve kullanılan komutu sakla.

## Hızlı tablo

| Belirti | Muhtemel katman | İlk kontrol |
|---|---|---|
| `ModuleNotFoundError` | Python ortamı | `00_doctor.py`, executable yolu |
| Paket çözümlenemiyor | Sürüm / Python / platform | Python 3.12, yayımlanmış sürüm, doğru requirements |
| `World already exists` | Strands başlangıcı | `Robot(...)` sonrasında tekrar `create_world()` çağrısını kaldır |
| SO-101 model bulunamıyor | Asset indirmesi | İlk GitHub/ağ hatası ve `.cache` izinleri |
| PNG yok, fizik çalışıyor | OpenGL/rendering | Ekran oturumu, uygun GL backend, sandbox izinleri |
| macOS viewer başlamıyor | Ana thread | `mjpython ... --viewer` |
| `Missing features: observation.images.front` | Kayıt kamerası | Kayıttan önce aynı kamerayı görüntü üretimi (render) et |
| veri kümesi (Dataset) tek uzun bölüm (episode) | Episode sınırı | `save_episode`, gerçek parquet sayısı |
| `libtorchcodec` / `libavutil` | Video runtime | Torch/codec/FFmpeg uyumu; PyAV deneyi |
| `CUDA out of memory` | Eğitim (training) belleği | örnek grubu (Batch) küçült, gerçek kamera sayısı, eğitilen katmanlar |
| `cuda.is_available() == False` | GPU sürücüsü/wheel | `nvidia-smi`, doğru torch paketi |
| Kamera anahtarı bulunamadı | Model/veri şeması | `input_features`, üstveri (metadata), rename map |
| Eğitim iyi, kol hareketi anlamsız | eylem (Action) sözleşmesi | Birim, sıra, stats, gripper yönü |
| Training loss düşük, görev kötü | Veri/genelleme | Ayrılmış test, coverage, politika yürütümü (rollout) hataları |
| Port meşgul / sync read | Haberleşme | Diğer süreç, güç, kablo, baudrate |
| MkDocs port dolu | Yerel sunucu | 8001 portunu kullan veya eski sunucuyu durdur |

## Bu makinede görülen örnekler

**Python 3.14 sistemde vardı; çalışma ortamı 3.12 kuruldu.** Sistem Python'unu değiştirmek gerekmedi. `.venv` ve `.venv-ml` ayrı olduğu için sim ile ML'nin NumPy/codec bağımlılıkları birbirini bozmadı.

**SO-101 modelinin ilk indirmesi ağ kısıtına takıldı.** Sonradan model indirildi ve görüntü üretildi. Böyle bir hata motor/kinematik problemi değildir; aynı komutu ağ erişimi olan normal terminalde çalıştır.

**Korumalı çalıştırmada OpenGL kamera üretimi başarısızdı.** Kamera gözlemi eksik kaldığı için kayıt da hata verdi. Script'e kayıt öncesi render kontrolü eklendi. Grafik erişimi olan çalıştırmada 3 episode/90 kare (frame) kaydı tamamlandı. Eksik kamerayı sıfır görüntüyle doldurarak hatayı gizleme.

**TorchCodec sistem FFmpeg kütüphanelerini bulamadı.** PyAV fallback ile kayıt ve okuma çalıştı. `dataset.video_backend=pyav` seçimi örneklerde açık verilir. İleride TorchCodec kullanırsan bağımlılığı ayrıca düzelt; burada çalışmış gibi varsayılmıyor.

## Log nasıl tutulur?

```bash
.venv/bin/python examples/00_doctor.py > outputs/environment.json
```

Uzun bir eğitimde stdout/stderr'i dosyaya yönlendirebilirsin; token/credential içermediğinden emin ol. Tam trace'i sakla ama ilk hata öncesi son komutu da yaz. GPU out-of-memory sonrası aynı notebook'ta hâlâ bellekte model kalmış olabilir; yeni process ile küçük koşu, ortam sorununu ayırmada yararlıdır.

## Rapor şablonu

```text
Ne yapmak istedim:
Tam komut:
Beklenen çıktı:
İlk hata:
Python / paket sürümleri:
İşletim sistemi / GPU:
Robot portu ve calibration ID (donanım varsa):
Dataset şema özeti:
En küçük tekrar üretim:
```

Veri sorunu raporlarken kimlik bilgilerini değil, kamera/durum (state)/action anahtarlarını paylaş. Büyük veri setinin tamamını göndermeden önce tek episode veya metadata ile yeniden üretilebilen bir örnek bul.
