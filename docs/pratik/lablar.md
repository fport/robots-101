# 12 uygulamalı laboratuvar

Her deneyde tek soru sor, çıktıyı sakla ve bir cümlelik sonuç yaz. Buradaki “geçti” koşulları atölye ilerlemesi içindir; endüstriyel robot sertifikasyonu değildir.

## Lab 01 · Ortamını tanı

**Amaç:** dokümantasyon/sim ve ML ortamlarını ayırt etmek.

```bash
.venv/bin/python examples/00_doctor.py
.venv-ml/bin/python examples/00_doctor.py
```

**Beklenen:** farklı executable yolları; ML ortamında LeRobot ve torch. **Değiştir:** aynı komutu sistem `python3` ile çalıştır ve neden paket bulamayabileceğini açıkla. **Geçiş:** kullandığın Python ve paket sürümlerini deney notuna yazdın.

## Lab 02 · Kinematik sezgi

[Tarayıcı laboratuvarını](../temel/laboratuvar.md) aç. q1=0, q2=0 için uç konumunu formülden hesapla, ekrandaki değerle karşılaştır. q2'yi değiştirerek dirseğin göreli açı olduğunu gör.

**Geçiş:** derece/radyan dönüşümünü yapabiliyor ve bu iki eklemli çizimin neden SO-101 modeli olmadığını açıklayabiliyorsun.

## Lab 03 · Hedef takibi

```bash
.venv/bin/python examples/01_mujoco_basics.py --target 0.7
```

**Çıktı:** `outputs/joint_tracking.csv`. **Deney:** hedefi −0.4 yap; son hatanın küçük kaldığını gör. **Geçiş:** sim zamanı, kontrol hedefi ve ölçülen açı arasında ayrım yapıyorsun.

## Lab 04 · SO-101'i yükle

```bash
.venv/bin/python examples/02_strands_so101.py --render
```

**Çıktı:** başlangıç/son PNG ve altı eklem state'i. **Deney:** küp rengini değiştir, kamera konumunu değiştir; hangi değişikliğin sadece gözlemi etkilediğini incele. **Geçiş:** görüntüyü kendin ürettin ve mock'un görev uzmanı olmadığını açıklayabiliyorsun.

## Lab 05 · Dataset oluştur

```bash
.venv-ml/bin/python examples/03_record_sim.py --root data/lab05 --episodes 3 --steps 30
.venv-ml/bin/python examples/04_inspect_dataset.py data/lab05 --expected-episodes 3
```

**Çıktı:** 3 episode, 90 örnek, kamera videosu. **Deney:** `--expected-episodes 4` ile denetimin neden hata verdiğini gör; veri değişmez. **Geçiş:** dosya sayısı yerine gerçek episode metadata'sını denetliyorsun.

## Lab 06 · Veriyi geri oku

```bash
.venv-ml/bin/python examples/08_read_dataset.py --root data/lab05 --repo-id local/sim-smoke --index 15
```

**Çıktı:** `outputs/dataset_frame_15_front.png`, `3×256×256` tensör şekli. **Deney:** ilk ve son frame'i ayrı oku. **Geçiş:** videonun decode edildiğini, şemanın varlığından ayrı doğruladın.

## Lab 07 · Küçük modeli eğit

```bash
.venv/bin/python examples/07_toy_behavior_cloning.py --output outputs/lab07
```

**Çıktı:** loss, ağırlıklar ve ayrı testte uç hatası. **Deney:** yeni çıktı klasöründe `--steps 100` ile kısa eğitim yap ve 2000 adımla karşılaştır. **Geçiş:** held-out hata, sabit baseline ve training loss'un farklı ölçüler olduğunu açıklayabiliyorsun. Bu model VLA değildir.

## Lab 08 · Donanım ve teleop

Robot geldikten sonra [ilk açılış](../donanim/ilk-acilis.md) ve [teleop](../donanim/teleop.md) adımlarını uygula.

**Çıktı:** cihaz kartı, kalibrasyon kaydı, kamera eşlemesi. **Geçiş:** küçük hareketlerde beklenen eklem/yön, tutucu açılışı ve durdurma yolu doğrulandı. Donanım gelmeden bu lab tamamlanmış sayılmaz.

## Lab 09 · Beş pilot gösterim

[Gerçek veri toplama](../donanim/veri.md) komutunu beş episode için çalıştır. Her videoyu izle. En az bir kalite problemini bulabilirsen eğitimden önce düzelt.

**Geçiş:** görev başlangıcı/sonu, kamera görünürlüğü ve action birimi kayıtlı. Beş pilot model başarısı için yeterlilik iddiası değildir.

## Lab 10 · Eğitim komutunu hazırla

```bash
.venv-ml/bin/python examples/05_prepare_training.py \
  --root data/lab05 --repo-id local/sim-smoke \
  --output-dir outputs/train/lab10 --steps 20 \
  --batch-size 1 --device cpu --eval-split 0
```

**Çıktı:** çalıştırılmamış SmolVLA komutu. **Deney:** üretilen `policy.input_features` alanını dataset metadata'sıyla karşılaştır. **Geçiş:** olmayan kamera girişi yok. Mock veriyle kısa eğitim ancak hat üzerinden geçiş deneyidir; gerçek göreve dair sonuç çıkarma.

## Lab 11 · GPU'da smoke + fine-tuning

Gerçek kaliteli veriyle [SmolVLA eğitim](../ogrenme/smolvla.md) tarifindeki 100 adımlık koşuyu bitir; checkpoint dosyalarını doğrula. Sonra ayrı output ile uzun koşu başlat. GPU yoksa önce bu makineyi/oturumu hazırlaman gerekir.

**Geçiş:** loss sonlu, veri okunuyor, checkpoint kaydediliyor, deney sürümleniyor. Uzun eğitimin bitmesi görev testini tamamlamaz.

## Lab 12 · Değerlendir ve iyileştir

20 önceden belirlenmiş denemeyi kaydet. Başarı ve hata etiketlerini CSV'ye yaz, `06_evaluate_results.py` ile raporla. En büyük hata grubuna yönelik yeni veri/ayar deneyi tasarla.

**Geçiş:** bütün denemeler kayıtlı, checkpoint kimliği sabit, test eğitimde kullanılmadı. İki sürüm arasında aynı koşullarda karşılaştırma yapabiliyorsun.
