# Kaliteli veri toplama

İlk veri setinin görevi dar olsun: **“Pick up the red cube and place it in the tray.”** Aynı görev metnini kayıt ve değerlendirmede kullan. İngilizce başlangıç metni burada açık model ekosistemiyle basit bir başlangıç tercihidir; Türkçe komut başarısı ayrıca deneyle ölçülmelidir.

## Önce beş pilot episode

```bash
source .venv-ml/bin/activate
export DATASET_ID='local/so101-pick-v1'
export TASK='Pick up the red cube and place it in the tray.'

lerobot-record \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id="$FOLLOWER_ID" \
  --robot.use_degrees=false \
  --robot.max_relative_target=2 \
  --robot.cameras="$CAMERAS" \
  --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" \
  --teleop.id="$LEADER_ID" \
  --teleop.use_degrees=false \
  --dataset.repo_id="$DATASET_ID" \
  --dataset.root=data/so101-pick-v1 \
  --dataset.single_task="$TASK" \
  --dataset.fps=30 \
  --dataset.num_episodes=5 \
  --dataset.episode_time_s=25 \
  --dataset.reset_time_s=20 \
  --dataset.push_to_hub=false
```

`FOLLOWER_*`, `LEADER_*` ve `CAMERAS` [önceki sayfalardan](teleop.md) gelir. `local/...` burada yerel repo kimliğidir; `push_to_hub=false` olduğu için kullanıcı hesabı açmaz. Hub'a yüklemek istediğinde gerçek namespace, erişim ve veri görünürlüğünü ayrıca seçersin.

Kayıt sırasında terminaldeki kontrol kısayollarını izle. Güncel kılavuz episode'u erken bitirme, yeniden çekme ve oturumu sonlandırma akışlarını açıklar. `Ctrl+C` veya kayıt sonlandırma komutu donanımdaki fiziksel güç kesme mekanizmasının yerine geçmez. [LeRobot gösterim kaydı](https://huggingface.co/docs/lerobot/en/il_robots#record-a-dataset)

## Her pilotu izle

1. Nesne, tutucu ve kap kritik anlarda görünüyor mu?
2. İlk saniyeler anlamsız bekleme mi, görevin gerçek başlangıcı mı?
3. Action ve state arasındaki fark hareket boyunca makul mü?
4. Aynı görev metniyle farklı, çelişkili hedefler gösteriyor musun?
5. Tutucu nesneyi gerçekten kaldırıyor ve bırakıyor mu?
6. Son kare başarı mı, yalnız tutucunun kabın üstünde olması mı?

Pilot başarısızsa bunu eğitim süresini artırarak telafi etmeye çalışma. Kamera yerleşimi, görev tanımı veya teleop davranışını düzelt, sonra yeni pilot çek.

## Eğitim setine büyüt

Bir atölye başlangıç planı: beş başlangıç bölgesinde yaklaşık onar başarılı gösterim, toplam 50 episode. Bu **başarı garantisi veya minimum matematiksel veri gereksinimi değildir**. Görevin zorluğu, veri çeşitliliği ve pretrained model uyumu belirleyicidir.

Nesnenin başlangıç konumunu küçük aralıkta değiştir; her şeyi aynı anda değiştirme. Kamera pozlarını toplama sırasında sabit tut. Bir sonraki veri sürümünde farklı ışığı ayrı bir değişken olarak ekleyebilirsin. Başarısız denemeleri saklayacaksan etiketle; ilk başarılı-demonstrasyon BC setine sessizce katma.

## Resume ve veri sürümü

Aynı şema/kalibrasyon/kamera düzeniyle kayıt eklemek için önce yardım çıktısında `--resume` davranışını kontrol et. LeRobot'ta ek episode sayısı ile toplam hedef sayısı aynı şey değildir. Kamera, birim veya görev değiştiyse yeni dataset sürümü oluştur: `so101-pick-v2`.

Ham veriyi tek kopya tutma. Yedekleme, dosya manifesti ve deney notlarını beraber sakla. Veri setini Hub'a taşımak bir seçenek; eğitim için zorunlu değil. Özellikle kameranın insanları/özel ortamı gösterdiği kayıtların görünürlüğünü yükleme sırasında bilinçli seç.

## Veri miktarını hesapla

`episode × süre × FPS` zaman adımı sayısıdır. 50 × 20 × 30 = 30.000 örnek. İki kamerada 60.000 görüntü vardır, yine 30.000 action satırı olur. [İnteraktif hesaplayıcı](../temel/laboratuvar.md) ham RGB hacmini gösterir; MP4 boyutunu sıkıştırma belirler.

## Test verisini ayır

Ardışık kareleri rastgele train/test ayırma: aynı hareketin hemen yanındaki kareler iki tarafa düşebilir. Validation'ı episode bazında ayır. Son test içinse kayıt günü/başlangıç bölgesi gibi daha güçlü bir ayrım tasarla ve test koşullarını model seçimi sırasında sürekli kullanma.

Sonraki adım [dataset denetimi](../ogrenme/dataset.md), sonra [SmolVLA eğitimi](../ogrenme/smolvla.md).
