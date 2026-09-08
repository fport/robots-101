# Kurulum ve ilk 30 dakika

Komutlar bu projenin kök klasöründe çalıştırılır. Mevcut çalışma alanı `/Users/furkanportakal/www/robots`. Komut bloklarındaki `$` terminal istemi değildir; değişkenlere ait olduğu yerlerde olduğu gibi bırak.

## 1. Önce okumayı aç

Projede `.venv` hazırsa:

```bash
cd /Users/furkanportakal/www/robots
make serve
```

Tarayıcıda **http://127.0.0.1:8000** aç. Sunucuyu durdurmak için terminalde `Ctrl+C`. Port doluysa `.venv/bin/mkdocs serve --dev-addr 127.0.0.1:8001` kullan. Başka bilgisayardan erişmek için ağ paylaşımını ayrıca yapılandırman gerekir; varsayılan yalnız bu bilgisayarda dinler.

## 2. Temiz bilgisayara kurulum

`uv` bir Python ortam/paket aracıdır. Kurulu olup olmadığını `uv --version` ile kontrol et; yoksa [resmî kurulum sayfasını](https://docs.astral.sh/uv/getting-started/installation/) kullan. Sistemin Python'unu değiştirmene gerek yok.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-docs.txt -r requirements-sim.txt
.venv/bin/python examples/00_doctor.py
.venv/bin/mkdocs serve --dev-addr 127.0.0.1:8000
```

`uv` Python 3.12 bulamazsa bu sürümü indirmeyi önerebilir. Bu rehberin denenen tabanı Python **3.12**'dir; bilgisayarındaki 3.14'ü kullanarak aynı sonucu varsayma. macOS/Linux komutları verilmiştir. Windows için sim/eğitim tarafında Linux ortamı ayrı değerlendirilir; USB donanımını WSL'ye aktarmak ek kurulum gerektirir ve burada sınanmadı.

## 3. Gerçek fizik motorunu çalıştır

Yeni terminal aç; site sunucusu önceki terminalde açık kalabilir:

```bash
.venv/bin/python examples/01_mujoco_basics.py
```

`simulation_seconds` yaklaşık `3.0`, `target_rad` `0.7`, `error_rad` ise `0.02`'den küçük olmalı. `outputs/joint_tracking.csv` zaman, ölçülen açı ve hedef sütunlarını içerir. Bu deney kol modeli indirmez ve görüntü penceresi gerektirmez.

Pencereli deney:

=== "macOS"

    ```bash
    .venv/bin/mjpython examples/01_mujoco_basics.py --viewer
    ```

=== "Linux masaüstü"

    ```bash
    .venv/bin/python examples/01_mujoco_basics.py --viewer
    ```

MuJoCo'nun macOS pasif görüntüleyicisi ana iş parçacığı için `mjpython` ister. PNG üretimi ile bu etkileşimli pencere aynı çalışma yolu değildir. [MuJoCo Python açıklaması](https://mujoco.readthedocs.io/en/stable/python.html#passive-viewer)

## 4. SO-101'i sahneye getir

```bash
.venv/bin/python examples/02_strands_so101.py --render
```

macOS'ta canlı kol penceresi: `.venv/bin/mjpython examples/02_strands_so101.py --viewer --steps 900`.

İlk kullanımda SO-101 model dosyaları internetten indirilir. Sonraki kullanım yerel önbellekten yararlanır. Beklenen çıktılar: robot eklem durumu, rollout sonucu ve `outputs/so101_before.png`, `outputs/so101_after.png`. Bunları yan yana aç. Robot hareket etmiş olabilir; küpü kavraması beklenmez, çünkü politika `mock`.

İndirme başarısızsa “model yok” hatasını bir kinematik hatası sanma; önce ilk GitHub/ağ hatasını oku. Script model yüklenemediğinde başka robotu sessizce onun yerine koymaz.

## 5. Veri ve eğitim için ayrı ortam

Bu adım daha büyük bağımlılıklar indirir. Sadece okumak ve ilk sim deneylerini yapmak için gerekli değildir.

```bash
uv venv --python 3.12 .venv-ml
uv pip install --python .venv-ml/bin/python -r requirements-ml.txt
.venv-ml/bin/python examples/00_doctor.py
```

CUDA makinesinde önce [GPU kurulum notlarını](../ogrenme/hesaplama.md) oku. PyTorch, torchvision, torchcodec ve FFmpeg'in birbirine uyumu önemlidir. `requirements-ml.txt` NVIDIA sürücüsünü kurmaz.

## Çalışma klasörleri

| Yol | İçerik |
|---|---|
| `docs/` | Okuduğun MkDocs Markdown sayfaları |
| `examples/` | Çalıştırılabilir Python alıştırmaları |
| `requirements-*.txt` | Doğrulanan ana bağımlılık sürümleri |
| `constraints-*.txt` | Bu makinedeki tam paket dökümü; platforma özel referans |
| `data/` | Yerel episode verileri; sürüm kontrolüne girmez |
| `outputs/` | PNG, CSV, eğitim komutu, rapor ve checkpoint çıktıları |
| `.cache/` | Scriptlerin model/varlık önbellekleri |
| `site/` | `make build` ile üretilen statik site |

Siteyi yeniden üretmek için `make build`; yerel HTTP ile statik çıktıyı okumak için `.venv/bin/python -m http.server 8000 --directory site --bind 127.0.0.1`. Dosyayı `file://` ile açmak arama ve dizin bağlantılarını bozabilir.
