# Teleoperasyon ve kameralar

Teleoperasyon (teleoperation), insanın kontrol ettiği lider hareketin follower hedeflerine dönüşmesidir. Henüz eğitim (training) yoktur. Bu aşamada insanın görevi kameradan bakarak tekrarlanabilir biçimde yapabilmesi önemlidir.

## İlk teleop

[Önceki sayfadaki](ilk-acilis.md) port ve ID değişkenleri aynı terminalde tanımlı olmalı.

```bash
source .venv-ml/bin/activate
lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id="$FOLLOWER_ID" \
  --robot.use_degrees=false \
  --robot.max_relative_target=2 \
  --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" \
  --teleop.id="$LEADER_ID" \
  --teleop.use_degrees=false \
  --fps=30
```

`max_relative_target=2`, bu normalize gösterimde tek güncellemenin hedef farkını sınırlar. **Bu iki derece, evrensel güvenli hız (velocity) veya fiziksel acil durdurma değildir.** Başlangıç için kısıtlı bir komut farkı örneğidir; kontrol Hz, motor kalibrasyonu ve yükle birlikte davranışı değerlendirilir. Leader'ı hızlı hareket ettirirsen follower geride kalabilir.

## Kameraları keşfet

```bash
lerobot-find-cameras opencv
```

Her kameranın görüntüsünü ayrı doğrula. `0` her bilgisayarda masa kamerası demek değildir; Mac'in dahili kamerası olabilir. `front` geniş görev alanını, `wrist` tutucu (gripper)/nesne ilişkisini görsün. Görüntüde nesne veya kap sürekli kapanıyorsa yerleşimi veri toplamadan önce düzelt. [LeRobot kamera kılavuzu](https://huggingface.co/docs/lerobot/en/cameras)

```bash
export CAMERAS='{front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, wrist: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30}}'
```

`0` ve `1` yerine bulduğun indeks/yolları yaz. Tek kameran varsa yalnız gerçekten var olan `front` girdisini bırak. Kamerasız VLA görsel veri alıştırmasına geçme.

Teleop komutuna `--robot.cameras="$CAMERAS"` ekleyerek kameraları birlikte açabilirsin. Görüntü görselleştirme için `--display_data=true` kullanımı Rerun/ilgili görselleştirme bağımlılığını isteyebilir; `lerobot[viz]==0.6.1` extra'sını ve sürümünü kurulumuyla birlikte kontrol et. Temel hareket ve kayıt için bu ekran zorunlu değildir.

## İyi kamera yerleşimi için küçük deney

Kamera önizlemesine bakarak nesneyi beş farklı başlangıç bölgesinden kaba taşı. Kendi gözünle masaya bakmadan yaklaşma yüksekliğini ve çene açıklığını tahmin edebiliyor musun? Edemiyorsan modelden de aynı tek görüntüyle mucize bekleme.

Pozlama/odak sürekli değişiyorsa veri dağılımı da oynar. Destekleyen kamerada ayarları sabitle veya en azından değişimi kontrol altında tut. Bilek kablosunun tutucuya dolanmadığını ve USB bant genişliğinin iki akışı kaldırdığını sınamak için önce kısa kayıt yap.

## Strands ile aynı işlemin yeri

Strands hardware nesnesi `attach_teleop(...)` ve `teleoperate(...)` yüzeyi sunar. İlk kalibrasyon (calibration) ve kayıt tarifinde LeRobot CLI kullanıyoruz; daha sonra [ajan entegrasyonu](../ogrenme/ajan.md) ile bu işlemleri üst düzey orkestrasyona bağlayabilirsin. Ajan kullanmak kalibrasyon ihtiyacını ortadan kaldırmaz. [Strands teleoperation](https://github.com/strands-labs/robots/blob/main/docs/hardware/teleoperation.md)

## Yalnız follower varsa

Şimdilik sim laboratuvarlarını, hazır veriyi okumayı ve eğitim hazırlığını tamamla. Gerçek gösterim (demonstration) için keyboard/gamepad kullanımında hedefin eklem (joint) mi yoksa uç nokta mı olduğunu seçmen gerekir. Uç nokta kontrolünde IK ve limit mantığı vardır. Bir klavye teleoperatörünü SO-101'e bağlamak bütün bu eşlemelerin hazır olduğu anlamına gelmez.
