# Bu rehberin doğrulama durumu

Kontrol tarihi **8 Eylül 2026**, makine **macOS 26.3.1 / Apple Silicon arm64**, Python **3.12.12**. “Çalıştı” bilgisi aşağıdaki kapsamla sınırlıdır; donanım veya GPU sonucu uydurulmadı.

## Çalıştırılan deneyler

| Deney | Sonuç | Ne kanıtlar? |
|---|---|---|
| MuJoCo tek eklem (joint) | 3 sim saniyesi; 0.7 rad hedef, yaklaşık 2.22e−16 rad son hata | Bu basit modelde fizik ve hedef takibi |
| Strands SO-101 | 30 kontrol adımı, 0 eylem hatası (action error), önce/sonra PNG | Model, arayüz, fizik ve görüntü üretimi (render) hattı |
| Canlı SO-101 viewer | `mjpython --viewer --steps 30` açıldı/çalıştı/kapandı | macOS'ta yerel MuJoCo penceresi |
| LeRobot sim kaydı | 3 bölüm (episode) × 30 kare (frame) = 90 örnek | Görüntülü veri kümesi (dataset) yazımı ve episode sınırları |
| Parquet denetimi | 3 episode, 90 frame, `errors: []` | Şema, frame ve timestamp kontrolleri |
| LeRobot/PyAV okuma | Frame okundu; görüntü tensörü `[3,256,256]`, PNG üretildi | Gerçek video decode ve frame erişimi |
| SO-101 hedef takibi | 3/3 hedef, 121 kontrol adımı, 2.42 sim saniyesi | Ölçülen altı eklem hatasına bağlı aşama geçişi |
| Hedef takibi zaman aşımı (timeout) | 0.1 s sonunda başarısız JSON/CSV, exit 1 | Başarısız deney de raporlanıyor |
| eylem dizisi (Action chunk) deneyi | `[90,50,6]`, %69 doldurma (padding) | Episode sınırını aşmayan etiket penceresi |
| LeRobot chunk karşılaştırması | 6/6 ilk/son episode örneği action/maskesi eşleşti | Öğretim penceresi gerçek okuyucuyla uyuşuyor |
| Flow matching hesabı | MSE 0.025; ideal Euler dönüşü; masked loss 7.5 | Öğrenme hesabının işaret ve maske aritmetiği |
| Düzlemsel iki dallı IK | FK dönüşü ve sayısal Jacobian doğrulandı | Öğretim modelinin matematik tutarlılığı |
| Küçük NumPy BC | 1500 eğitim (training) / 300 test; ortalama uç hata ≈ 0.346 cm | İki eklemli kinematik alıştırmada öğrenme |
| Sabit poz karşılaştırma modeli (baseline) | Ortalama uç hata ≈ 12.05 cm | Küçük BC deneyi için karşılaştırma |
| Eğitim komutu üretimi | Gerçek üstveri (metadata)'dan SmolVLA komutu üretildi | Kamera feature hazırlığı ve parametre üretimi |
| MuJoCo yerçekimi deneyi | Küp z≈0.02497 m; yerçekimi sıfırken 0.60 m | Bu sahnede serbest cisim ve temas |
| MuJoCo sürtünme deneyi | μ=0.1 için 0.3256 m, μ=1 için 0.02976 m yatay hareket | Tek değişkenle sürtünme karşılaştırması |
| MuJoCo servo/itme/reset | 0.7 rad hedef takibi; dış kuvvetle hareket; reset zamanı/hatası 0 | Komut, kuvvet ve başlangıca dönme |
| RGB ve derinlik | 640×480 PNG ve metre cinsinden derinlik dizisi | Grafik yolu; sürücü sınırı aşağıda |
| Hub veri indirme | 470.117 MB; sabit sürüm; 50 episode / 19.631 frame | Tam veri kümesi ve metadata indirildi |
| Hub video okuma | Top/wrist kameraları `[3,480,640]` | PyAV ile gerçek AV1 video çözme (decoding) |
| İlk fizik öğrenmesi | 40 episode / 4000 satır; 28 eğitim, 6 doğrulama, 6 test | Öğretmen → eğitim → ayrı fizikte deneme |
| Öğrenilmiş tek eklem / sabit başlangıç | 6/6 ve 0/6; ortalama hata 0.01848 / 0.61127 rad | Küçük öğretim dağılımında karşılaştırma |
| Sayısal LeRobot dönüştürme | 40 episode / 4000 satır; denetim hatasız | CSV → gerçek yerel LeRobot biçimi |
| Araç testleri | ML ortamında 12/12 geçti; sim ortamında 9 geçti, 3 ML testi atlandı | Şema, tek değerli depolama, komutlar, raporlar, episode sınırı ve IK |
| MkDocs strict build | 43 Türkçe + 43 İngilizce içerik; 49 menü çevirisi | Çeviri kapsamı ve örnek komut bayrakları da denetlendi |
| Chrome kontrolü | 87 HTML bağlantı/anchor kontrolü; 86 mobil içerik sayfası | İki dilde arama, hesaplayıcılar, tema, çözümler ve ortak ilerleme geçti; JavaScript çalışma zamanı hatası yok |
| Mermaid akış şemaları (flowcharts) | 6 konuda, iki dilde toplam 12 şema | Dış internet istekleri engelliyken çizim; açık/koyu tema ve mobil klavye ile kaydırma |

Tarayıcı raporundaki `known_resource_warnings`, temanın mevcut bir dil entegrasyonu sorununu ayrıca gösterir: Material 9.7.7, static-i18n 1.3.1'in verdiği çeviri sayfası adreslerinin altında `sitemap.xml` arar ve 404 alır. Birleşik site haritası (sitemap) kök dizindedir. Bu istekler şema çizimini etkilemez; aynı makalede dil değiştirme ayrıca sınanır. Diğer kaynak yükleme veya JavaScript hataları kontrolü başarısız yapar.

Toy BC deneyinin `%100 < 2 cm` sonucu yalnız aynı örnekleme sınırları içindeki 300 kinematik test noktası içindir. Fizik, görüntü, kavrama veya SO-101 performansı değildir. Yeni SO-101 hedef takibi yalnız eklem uzayındaki görevdir; flow matching örneği de model eğitimi içermez.

Yerel çıktı örnekleri `outputs/`, doğrulanan sim verisi `data/sim-smoke-verified/` altında. Bu klasörler yeniden üretilebilir büyük/yerel çıktılar olduğu için sürüm kontrolü dışında tutulur. Site içinde SO-101 örnek PNG'si ayrıca bulunur.

Yeni tek eklem öğrenmesindeki 6/6 sonucu yalnız altı küçük öğretim denemesidir; SO-101 kavrama veya VLA başarısı değildir. `data/teaching-hinge-verified` kamera içermez. Tek eylem alanı bu LeRobot sürümünde tek değerli tensör olarak okunur.

Hub verisi **SO-100** verisidir; sürüm kimliği `728583b5eaf9e739a7f119e2def466fa1d552402`. Doğrulanan yerel kopya `data/hub-so100-verified`, küçük eğitim sonuçları `outputs/first-learning-verified`, site raporu `outputs/site-check/report.json` altında. İndirmek, her gösterimin görev kalitesini elle incelemek anlamına gelmez.

## Bilinen ortam ayrıntıları

MuJoCo derinlik çıktısında Mac sürücüsü `ARB_clip_control` desteği olmadığını bildirdi; bu derinlik hassasiyetini sınırlayabilir. Kaydedilen dizi bir öğretim çıktısıdır, kalibre edilmiş fiziksel derinlik sensörü ölçümü değildir.

Sandbox içindeki ilk çalıştırmada grafik bağlamı açılamadı; grafik erişimi olan çalıştırmada render ve kayıt tamamlandı. Bu yüzden kayıt scripti artık dataset oluşturmadan önce kamerayı render ederek sınar.

Sistem FFmpeg shared library bulunmadığı için TorchCodec yüklenemedi. LeRobot'un PyAV yolu kullanıldı ve okuma tamamlandı. Bu ortamda TorchCodec başarılı diye işaretlenmez. İki ortamın tam sürümleri `constraints-docs-sim-macos.txt` ve `constraints-ml-macos.txt` dosyalarında saklanır.

30 Hz kontrol ve 0.002 s fizik adımıyla 30 adımda raporlanan sim zamanı yaklaşık 1.02 s idi. Veri/gerçek zaman eşlemesinde bu alt adım yuvarlamasını ayrıca değerlendirmek gerekir.

## Donanım/GPU gerektiği için yapılmayanlar

- Fiziksel SO-101 bağlantısı, kalibrasyonu veya teleoperasyonu.
- Gerçek kamera/leader ile gösterim (demonstration) toplama.
- SmolVLA ağırlıklarını indirerek forward/backward veya tam GPU ince ayar (fine-tuning).
- SmolVLA'nın simde/gerçekte görev başarısını ölçen politika yürütümü (rollout).
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
