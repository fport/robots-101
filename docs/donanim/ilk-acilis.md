# İlk açılış ve kalibrasyon

Bu sayfa **donanım geldiğinde** uygulanır. Komutlar gerçek motor veri yolu ile haberleşir. Önce kolu sabitle, kablo hareket paylarını kontrol et ve fiziksel güç kesmeye eriş. İlk hareket sırasında çalışma alanı boş olmalı.

## Hazır kit ile sıfırdan montajı ayır

Verdiğin ürün sayfası kurulu/test edilmiş set tarif ediyor. Bu nedenle “kutuyu aç → bütün motor ID'lerini yeniden yaz” akışı uygun bir varsayım değil. Teslimatta motor ID'leri, baudrate, başlangıç pozu ve kalibrasyonun durumunu satıcı talimatından öğren. [Hashtag Robotics](https://labs.hashtagrobotics.tr/so-101-robot-kol)

`lerobot-setup-motors` yeni/yeniden yapılandırılan motorların ID ve haberleşmesini ayarlar; kalibrasyon komutuyla aynı değildir. Resmî kurulum sıfır motorlar için motorları tek tek bağlama adımı içerir. Hazır zincirde bu işlemi gerekçesiz tekrarlama. [Resmî SO-101 kurulumu](https://huggingface.co/docs/lerobot/en/so101)

## 1. ML ortamını aç

```bash
source .venv-ml/bin/activate
python examples/00_doctor.py
lerobot-find-port
```

Port bulucu, kablo çıkarıp takmanı isteyerek aygıtı ayırt edebilir. Follower ve leader'ı ayrı belirle. macOS'ta `/dev/tty.usbmodem...` veya ilgili seri aygıt, Linux'ta `/dev/ttyACM...`/`/dev/ttyUSB...` görebilirsin. Sondaki numarayı ezberleme; cihazları yeniden takınca değişebilir.

```bash
export FOLLOWER_PORT='/dev/tty.usbmodem_FOLLOWER_PORTUNU_YAZ'
export LEADER_PORT='/dev/tty.usbmodem_LEADER_PORTUNU_YAZ'
export FOLLOWER_ID='atolye_follower'
export LEADER_ID='atolye_leader'
```

Buradaki portlar örnektir; keşfettiğin gerçek değerlerle değiştir. Bu değişkenler yalnız açık terminal oturumunda kalır. Yeni terminalde yeniden tanımla.

## 2. Birim kararını sabitle

Bu rehber gerçek veri örneklerinde **`use_degrees=false`** seçer: kol eklemleri LeRobot'un kalibrasyona bağlı normalize aralığında, tutucu ayrı 0–100 ölçeğinde temsil edilir. Leader ve follower'da aynı seçim yapılır. Denenen LeRobot 0.6.1'de `use_degrees` varsayılanı `true` olduğu için parametreyi açıkça veriyoruz.

Bu seçim “normalize olan her şey fiziksel olarak aynı” anlamına gelmez. Kalibrasyon ve action sırası hâlâ gereklidir. Önceden derece ile toplanmış dataset/checkpoint kullanacaksan onun sözleşmesine uy; aynı veri setinde birimleri sessizce değiştirme. [LeRobot follower kaynak kodu](https://github.com/huggingface/lerobot/blob/v0.6.1/src/lerobot/robots/so_follower/so_follower.py)

## 3. Kalibrasyon

Satıcının verdiği geçerli kalibrasyon dosyası/ID eşlemesi varsa onu koru. Kalibrasyon gerekiyorsa:

```bash
lerobot-calibrate \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id="$FOLLOWER_ID" \
  --robot.use_degrees=false

lerobot-calibrate \
  --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" \
  --teleop.id="$LEADER_ID" \
  --teleop.use_degrees=false
```

Terminalin gösterdiği poz/hareket aralığı adımlarını izle. Motoru mekanik sınırın ötesine zorlamak bir kalibrasyon yöntemi değildir. Kalibrasyon sonuç dosyası ve ID eşleşmesini yedekle; teleop, kayıt ve rollout boyunca aynı ID'leri kullan.

## 4. Kayıt öncesi kabul deneyi

Önce küçük hareketlerle taban, omuz, dirsek, bilek ve tutucu yönlerini kontrol et. Leader hareket ettiğinde beklenen follower eklemi aynı anlamda hareket ediyor mu? Tutucu açılma yönü doğru mu? Eklem limitine yaklaşmadan geri dönebiliyor musun?

Portu iki ayrı süreç açmasın: bir yanda LeRobot teleop, diğer yanda Strands hardware bağlantısı aynı motor bus'ına sahip olmaya çalışmamalı. Tek süreç kontrolüyle başla.

## Bir sorun olduğunda

| Belirti | Kontrol |
|---|---|
| USB aygıtı görünmüyor | Veri taşıyan USB kablosu, adaptör, besleme ve aygıt listesi |
| Port var, motorlar cevap vermiyor | Güç, bus kablosu, kart kanalı, ID/baudrate |
| Yanlış eklem hareketi | Motor ID / isim / sıralama |
| Açı yönü beklenmiyor | Kalibrasyon ve birim seçimi |
| Seri port meşgul | Diğer teleop/record/Strands süreçleri |

Hata mesajıyla birlikte cihaz kartını ve sürümleri kaydet. Başlangıçta paketleri rastgele güncellemek hangi değişikliğin sonucu etkilediğini belirsizleştirir.
