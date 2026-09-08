# Bu rehberin doğrulama durumu

Kontrol tarihi **8 Eylül 2026**, makine **macOS 26.3.1 / Apple Silicon arm64**, Python **3.12.12**. “Çalıştı” bilgisi aşağıdaki kapsamla sınırlıdır; donanım veya GPU sonucu uydurulmadı.

## Çalıştırılan deneyler

| Deney | Sonuç | Ne kanıtlar? |
|---|---|---|
| MuJoCo tek eklem | 3 sim saniyesi; 0.7 rad hedef, yaklaşık 2.22e−16 rad son hata | Bu basit modelde fizik ve hedef takibi |
| Strands SO-101 | 30 kontrol adımı, 0 action error, önce/sonra PNG | Model, arayüz, fizik ve render hattı |
| Canlı SO-101 viewer | `mjpython --viewer --steps 30` açıldı/çalıştı/kapandı | macOS'ta yerel MuJoCo penceresi |
| LeRobot sim kaydı | 3 episode × 30 frame = 90 örnek | Görüntülü dataset yazımı ve episode sınırları |
| Parquet denetimi | 3 episode, 90 frame, `errors: []` | Şema, frame ve timestamp kontrolleri |
| LeRobot/PyAV okuma | Frame okundu; görüntü tensörü `[3,256,256]`, PNG üretildi | Gerçek video decode ve frame erişimi |
| SO-101 hedef takibi | 3/3 hedef, 121 kontrol adımı, 2.42 sim saniyesi | Ölçülen altı eklem hatasına bağlı aşama geçişi |
| Hedef takibi zaman aşımı | 0.1 s sonunda başarısız JSON/CSV, exit 1 | Başarısız deney de raporlanıyor |
| Action chunk deneyi | `[90,50,6]`, %69 padding | Episode sınırını aşmayan etiket penceresi |
| LeRobot chunk karşılaştırması | 6/6 ilk/son episode örneği action/maskesi eşleşti | Öğretim penceresi gerçek okuyucuyla uyuşuyor |
| Flow matching hesabı | MSE 0.025; ideal Euler dönüşü; masked loss 7.5 | Öğrenme hesabının işaret ve maske aritmetiği |
| Düzlemsel iki dallı IK | FK dönüşü ve sayısal Jacobian doğrulandı | Öğretim modelinin matematik tutarlılığı |
| Küçük NumPy BC | 1500 eğitim / 300 test; ortalama uç hata ≈ 0.346 cm | İki eklemli kinematik alıştırmada öğrenme |
| Sabit poz baseline | Ortalama uç hata ≈ 12.05 cm | Küçük BC deneyi için karşılaştırma |
| Eğitim komutu üretimi | Gerçek metadata'dan SmolVLA komutu üretildi | Kamera feature hazırlığı ve parametre üretimi |
| Araç testleri | ML ortamında 11/11 geçti | Geçersiz veri/komut/rapor, episode sızıntısı ve IK sınırları |
| MkDocs strict build | 37 içerik sayfası | Site yapısı ve Markdown bağlantıları; güncel tarayıcı raporu `outputs/site-check/report.json` |
| Chrome kontrolü | 38 HTML sayfasında yerel bağlantı/anchor; arama, tema, 16 çözüm kutusu, ilerleme ve mobil görünüm geçti | Tarayıcı etkileşimi; JS exception yok |

Toy BC deneyinin `%100 < 2 cm` sonucu yalnız aynı örnekleme sınırları içindeki 300 kinematik test noktası içindir. Fizik, görüntü, kavrama veya SO-101 performansı değildir. Yeni SO-101 hedef takibi yalnız eklem uzayındaki görevdir; flow matching örneği de model eğitimi içermez.

Yerel çıktı örnekleri `outputs/`, doğrulanan sim verisi `data/sim-smoke-verified/` altında. Bu klasörler yeniden üretilebilir büyük/yerel çıktılar olduğu için sürüm kontrolü dışında tutulur. Site içinde SO-101 örnek PNG'si ayrıca bulunur.

## Bilinen ortam ayrıntıları

Sandbox içindeki ilk çalıştırmada grafik bağlamı açılamadı; grafik erişimi olan çalıştırmada render ve kayıt tamamlandı. Bu yüzden kayıt scripti artık dataset oluşturmadan önce kamerayı render ederek sınar.

Sistem FFmpeg shared library bulunmadığı için TorchCodec yüklenemedi. LeRobot'un PyAV yolu kullanıldı ve okuma tamamlandı. Bu ortamda TorchCodec başarılı diye işaretlenmez. İki ortamın tam sürümleri `constraints-docs-sim-macos.txt` ve `constraints-ml-macos.txt` dosyalarında saklanır.

30 Hz kontrol ve 0.002 s fizik adımıyla 30 adımda raporlanan sim zamanı yaklaşık 1.02 s idi. Veri/gerçek zaman eşlemesinde bu alt adım yuvarlamasını ayrıca değerlendirmek gerekir.

## Donanım/GPU gerektiği için yapılmayanlar

- Fiziksel SO-101 bağlantısı, kalibrasyonu veya teleoperasyonu.
- Gerçek kamera/leader ile gösterim toplama.
- SmolVLA ağırlıklarını indirerek forward/backward veya tam GPU fine-tuning.
- SmolVLA'nın simde/gerçekte görev başarısını ölçen rollout.
- Ücretli GPU işi açma, dış servise dataset/model yükleme, kamuya site yayını.

Bu adımlar için ayrıntılı tarifler verildi. Bunların denenmiş yerel örneklerle aynı doğrulama durumunda olmadığını korumak, sorun çıktığında doğru beklentiyle ilerlemeyi sağlar.

## Kontrolleri tekrar çalıştır

```bash
make check
.venv-ml/bin/python -m unittest discover -s tests -v
```

İlk ortamda LeRobot/Parquet'e özel testler atlanır; ikinci ortam bunları da çalıştırır. Testler yanlış robot boyutu, eksik kamera, yetersiz split, bozuk timestamp/action ve geçersiz değerlendirme kayıtlarını sınar. `make build` MkDocs'u strict modda derler.

Tarayıcı kontrolünü yeniden çalıştırmak için yerel Chrome, `requirements-test.txt` bağımlılığı ve açık `make serve` gerekir. Ardından `.venv/bin/python scripts/check_site.py` çalıştır; rapor ve ekran görüntüleri `outputs/site-check/` içine yazılır. Bunlar Chrome'un izole test profilinde yapılır, kişisel tarayıcı geçmişini kullanmaz.

Yeni ortam/cihazla çalıştırdığında bu sayfaya yeni bir satır ekle; eski makinenin sonucunu yeni GPU veya kit için doğrulanmış sayma.
