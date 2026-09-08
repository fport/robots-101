# MuJoCo'yu anlamak

MuJoCo, eklemli cisimlerin hareketini ve birbirleriyle temasını hesaplayan fizik motorudur. Adı *Multi-Joint dynamics with Contact* ifadesinden gelir. Bu rehberde CPU fizik motorunu kullanıyoruz; görüntü üretimi ayrıca OpenGL bağlamına ihtiyaç duyar. [MuJoCo genel bakış](https://mujoco.readthedocs.io/en/stable/overview.html)

## Bir simülasyonun dört parçası

**Model:** robotun geometri, eklem (joint), kütle (mass), limit ve aktüatör (actuator) tanımı. **Durum (state):** o andaki konum/hız (velocity) değerleri. **Kontrol:** aktüatöre verilen hedefler. **Adımlama:** fizik motorunun zamanı ilerletmesi.

Python API'sinde bunları şu isimlerle görürsün:

```python
model = mujoco.MjModel.from_xml_string(xml)
data = mujoco.MjData(model)
data.ctrl[0] = 0.7
mujoco.mj_step(model, data)
```

`model` ve `data` farklı şeylerdir. `data.ctrl` alanına yazdığın sayının anlamını XML'deki aktüatör belirler: position aktüatöründe hedef açı olabilir, motor aktüatöründe torkla ilişkili kontrol olabilir. İkisine aynı sayıyı vererek aynı hareketi bekleyemezsin.

## MJCF'yi oku

`examples/01_mujoco_basics.py` içinde küçük bir XML model var. Tek bir döner eklem seçildiği için görebildiğin sonucun hangi nedenden kaynaklandığı nettir.

| XML bölümü | Deneydeki anlamı |
|---|---|
| `compiler angle="radian"` | Modelde yazılan eklem açıları radyan |
| `option timestep="0.002"` | Her fizik adımı iki milisaniye |
| `body` | Birlikte hareket eden gövde |
| `joint type="hinge" axis="0 0 1"` | Z etrafında dönen eklem |
| `geom type="capsule"` | Bağlantının görünümü ve çarpışma (collision) şekli |
| `site name="tip"` | Uç nokta için işaret |
| `position ... kp="25"` | Eklem hedefi takip eden aktüatör |

`geom` çarpışma/geometriyi, `joint` hareket serbestliğini tanımlar. Bir mesh'in güzel görünmesi onun kütlesinin, sürtünmesinin ve temas (contact) davranışının gerçekçi ayarlandığı anlamına gelmez. [MuJoCo modelleme kılavuzu](https://mujoco.readthedocs.io/en/stable/modeling.html)

## Çalıştır ve tek değişkeni değiştir

```bash
.venv/bin/python examples/01_mujoco_basics.py --target 0.7
.venv/bin/python examples/01_mujoco_basics.py --target -0.4
```

Her koşu aynı CSV dosyasını yeniler; karşılaştırmak istiyorsan ilkini farklı isimle sakla. İlk sütun sim zamanı, ikinci ölçülen açı, üçüncü hedeftir. Başlangıçtan hedefe geçişi tablo programında çizgi grafiği olarak çiz.

**Deney A:** hedefin işaretini değiştir. Son ölçüm de aynı yönde mi değişiyor? **Deney B:** XML'deki `kp` değerini 25'ten 10'a indir. Hedefe yaklaşma hızı nasıl değişiyor? **Deney C:** `damping` değerini değiştir. Salınım/takip hatasını yalnız son kareye bakarak mı, tüm eğriyi izleyerek mi anlıyorsun?

Her seferinde yalnız bir parametreyi değiştir ve orijinal dosyaya dönmek için değişikliğini not et. Bu deneyde eksen dikey olduğu için yerçekimi (gravity) bu eksen çevresindeki hareketi doğrudan aynı şekilde etkilemez; omuz kaldırma gibi bir deney için eksen/geometri değişikliği gerekir.

## `mj_step`, `mj_forward` ve çizim

`mj_step` zamanı ilerletir. `mj_forward` mevcut durumdan türetilen kinematik/dinamik hesapları günceller; tek başına bir zaman adımı değildir. Görüntü görüntü üretimi (render) etmek de eğitim (training) veya fiziksel kontrol değildir.

Runtime `qpos` vektörünün boyutunu motor sayısına eşitleme: serbest bir küpün pozisyon/quaternion bileşenleri de model durumunda bulunabilir. SO-101 state okurken robotun eklemlerini isimle seçmek, bütün `data.qpos` dizisini “altı robot eklemi” sanmaktan daha güvenilirdir.

## Görüntü penceresi ve headless çalışma

macOS'ta pasif viewer için `mjpython` kullan. Linux'ta masaüstü OpenGL/GLFW veya uygun sunucuda EGL yolu kullanılabilir. `MUJOCO_GL=egl` bir NVIDIA sürücüsü kurmaz ve macOS için genel çözüm değildir. Rendering hatasında önce fiziksiz değil, **görüntüsüz fizik** testinin çalışıp çalışmadığını sınayarak problemi ayır. [Python viewer ve rendering API](https://mujoco.readthedocs.io/en/stable/python.html)

Sonraki bölümde XML'yi elle yazmak yerine Strands'in SO-101 model yüklemesini kullanacaksın.
