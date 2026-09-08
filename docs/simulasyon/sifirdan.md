# Sıfırdan bir simülasyon kur

Ön koşul: [robotikle ilk tanışma](../basla/sifirdan.md). Bu sayfanın sonunda yalnız bir pencere açmış olmayacaksın; simülasyonun (simulation) hangi parçalardan oluştuğunu, hangi soruları sınayabileceğini ve sonraki deneyini nasıl tasarlayacağını bileceksin.

## Önce ne kurduğunu anla

Bir sahne (scene), zemin, nesneler, ışık, kamera ve gerekirse robot içerir. Model (model), bunların şekil, kütle (mass), eklem (joint) ve temas (contact) özelliklerini tanımlar. Durum (state), şu andaki konum ve hızları tutar. Fizik adımı (physics step), zamanı küçük bir miktar ilerletir. Görselleştirme (rendering), o durumun bir kameradan nasıl göründüğünü hesaplar.

Bu beş şeyi ayrı düşün: **sahneyi tanımla → başlangıcı seç → kuvvet/komut uygula → zamanı ilerlet → ölç**. Öğrenme modeli bu döngüye daha sonra karar verici olarak eklenir. MuJoCo kurulunca robot otomatik görev öğrenmez.

## 1. Çalışma klasörünü aç

Bu bilgisayarda proje `/Users/furkanportakal/www/robots`. Yeni terminalde:

```bash
cd /Users/furkanportakal/www/robots
pwd
```

Başka bilgisayarda kendi proje yolunu kullan. `models/`, `examples/` ve `requirements-sim.txt` aynı kökün altında olmalı. Mevcut `.venv` hazırsa üçüncü adıma geç; sırf yeniden denemek için ortamı silme.

## 2. Python ve MuJoCo ortamı

`uv --version` çalışmıyorsa önce [uv resmî kurulumunu](https://docs.astral.sh/uv/getting-started/installation/) tamamla. Ardından:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-docs.txt -r requirements-sim.txt
.venv/bin/python examples/00_doctor.py
```

Sanal ortam (virtual environment), bağımlılıkları (dependencies) bu projeye ayırır. Simülasyon için bu aşamada Hugging Face hesabı veya ücretli GPU gerekmez. İlk paket indirmesi internet ister. Komutlar macOS/Linux içindir; Windows/WSL ve fiziksel USB erişimi burada doğrulanmış değildir.

## 3. Pencere açmadan ilk fizik

```bash
.venv/bin/python examples/13_mujoco_playground.py \
  --scene drop --output outputs/my-first-drop
```

Küpün merkezi 0.60 m yükseklikten başlar; zemine düşünce yaklaşık 0.025 m'de durur. Küp 5 cm kenarlı olduğu için merkezinin z=0 olması beklenmez. Terminalde `metrics.json` özeti görünür; dosyalar belirttiğin klasöre yazılır.

`trajectory.csv` her fizik adımında zamanı, küp konumunu, eklem açısını ve temas sayısını tutar. `contacts` temas sayısıdır; “nesne başarıyla kavrandı” etiketi değildir. Çıktı klasörü zaten varsa yeni bir isim kullan; deneylerini üzerine yazarak kaybetme.

## 4. Sahne dosyasını oku

`models/playground.xml` içindeki yapı:

```xml
<mujoco>
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <worldbody>
    <!-- zemin, kamera, serbest küp ve tek eklemli öğretim kolu -->
  </worldbody>
  <actuator>
    <!-- eklemin hedef açısını takip eden aktüatör -->
  </actuator>
</mujoco>
```

Bu kısa blok yapıyı açıklar; çalıştırılabilir tam model dosyası projede bulunur. MuJoCo'nun yerel XML model biçimine (native XML model format) MJCF denir. `body` gövdeyi, `geom` görünür/çarpışan geometriyi, `joint` hareket serbestliğini tanımlar. Küpteki `freejoint`, nesnenin uzayda hareket etmesini sağlar; yoksa küp üst gövdesine sabitlenir. [MuJoCo modelleme](https://mujoco.readthedocs.io/en/stable/modeling.html)

`size="0.025 0.025 0.025"` kutunun yarı boyutlarıdır; toplam kenar 0.05 m olur. `mass="0.05"` 50 gramdır. Sayıları değiştirirken hangi birimde olduklarını yaz.

## 5. Python döngüsünü anla

```python
model = mujoco.MjModel.from_xml_path("models/playground.xml")
data = mujoco.MjData(model)
for _ in range(1500):
    mujoco.mj_step(model, data)
print(data.time)
```

0.002 saniyelik 1500 adım, 3 simülasyon saniyesi eder. İşlemin bilgisayarında 3 gerçek saniye sürmesi şart değildir. `model` dünya tanımı, `data` değişen durumdur. `mj_forward`, değiştirilmiş durumdan türeyen hesapları günceller; tek başına zamanı ilerletmez. [Python API](https://mujoco.readthedocs.io/en/stable/python.html)

Bu sahnede `nq=8`, `nv=7`, `nu=1`: serbest küpün konumu/quaternion'ı ve hızları da durum vektörüne dahildir. Sekiz konum değeri, sekiz motor demek değildir. İsimle `model.joint("pan")` seçmemizin nedeni hangi eklemi okuduğumuzu açık tutmaktır.

## 6. Görüntüyü aç

macOS masaüstünde:

```bash
.venv/bin/mjpython examples/13_mujoco_playground.py \
  --scene drop --viewer --output outputs/drop-window
```

Linux masaüstünde `.venv/bin/python` ile aynı seçenekleri kullanabilirsin. `--viewer` etkileşimli görüntüleyiciyi (viewer) açar ve adımları duvar saatiyle yavaşlatır. PNG ve derinlik (depth) dosyası için:

```bash
.venv/bin/python examples/13_mujoco_playground.py \
  --scene servo --render --output outputs/servo-camera
```

Bu, `rgb.png` ve metre cinsinden `depth_m.npy` üretir. Grafik bağlamı (graphics context) açılamazsa önce penceresiz deneyi doğrula. Mac'te sandbox grafik erişimini engelleyebilir. `MUJOCO_GL=egl` macOS için genel bir çözüm değildir. Derinlikte arka plan/uzak kesme düzlemi de değer üretebilir; dizinin bütün değerlerini nesne mesafesi olarak yorumlama.

## 7. Tek değişiklikle neden-sonuç gör

```bash
.venv/bin/python examples/13_mujoco_playground.py \
  --scene drop --gravity 0 --output outputs/drop-no-gravity
```

Başlangıç hızı sıfırsa küp 0.60 m'de kalır. Önce sonucu tahmin et, sonra çalıştır. “Yerçekimi (gravity) kapandı, hiçbir nesne hiçbir koşulda hareket edemez” sonucunu çıkarma; başlangıç hızı veya dış kuvvet varsa hareket edebilir.

## Bu ortamla neler yapabilirsin?

| İhtiyaç | Kuracağın deney | Ölçüm |
|---|---|---|
| Fiziği anlamak | Düşme, kayma, itme | Konum, hız (velocity), temas |
| Motor kontrolünü anlamak | Hedef açı ve sönüm (damping) değişimi | Takip hatası, salınım |
| Kamerayı yerleştirmek | Farklı bakış ve çözünürlük | Nesne görünürlüğü, RGB/derinlik |
| Tekrar üretmek | Başlangıcı sıfırla (reset), aynı rastgelelik tohumu (seed)'i kullan | Başlangıç durumu, sonuç farkı |
| Veri üretmek | Uzman kuralı yürüt ve gözlem (observation)/eylem (action) kaydet | Eşzamanlı örnekler, bölüm (episode) sınırları |
| Öğrenmeyi denemek | Küçük politika (policy) eğit ve tekrar simde çalıştır | Ayrı başlangıçlarda görev başarısı |
| SO-101'e ilerlemek | Strands ile gerçek model varlığını yükle | Altı eylem anahtarı, kamera, hedef takibi |

MuJoCo tek başına nesne tanıyıcı, görev planlayıcı, gösterim (demonstration) uzmanı veya model eğiticisi değildir. Bunları sahnenin etrafına sen veya kullandığın kütüphane ekler. Simülasyonun gerçeğe ne kadar benzediği de kullandığın modele bağlıdır.

## Kendi simülasyonunu tasarlama defteri

Koddan önce altı satır yaz: **görev**, **başlangıç dağılımı**, **gözlem**, **eylem**, **başarı ölçütü**, **zaman aşımı (timeout)**. Örnek: “Küpü it; başlangıç x=0.12 m; x konumunu gözle; ilk 0.2 s kuvvet uygula; en az 4 cm ilerlesin; toplam 3 s.” Böylece güzel görüntü ile tamamlanan görevi ayırırsın.

Sonraki sayfa [on MuJoCo deneyi](deneyler.md). Robot varlığına geçmek için [Strands ile SO-101](strands.md); öğrenmeye geçmek için [ilk küçük eğitim](../ogrenme/ilk-ogrenme.md).
