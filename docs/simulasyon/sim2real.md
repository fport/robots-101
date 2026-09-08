# Simülasyondan gerçeğe

Simülasyon (simulation) gerçek robota hazırlanmanın güçlü bir yoludur; modelin dış görünüşünün benzemesi tek başına politika (policy) transferini çözmez. Transferi dört sözleşme üzerinden denetle: **girdi, eylem (action), zaman ve fizik**.

## 1. Girdi sözleşmesi

Kamera isimleri, görüş açıları, çözünürlük, renk sırası ve ön işleme tutarlı mı? Eğitimde üstten bütün masayı gören bir kamera, gerçek kurulumda yandan tutucuyla kapanan bir görüntüye dönüşürse model farklı dağılım görür. Kameranın adını eşlemek yalnız yazılımsal anahtar uyuşmazlığını çözer.

Propriosepsiyon da girdidir: durum (state) vektöründeki her elemanın adı/sırası/birimi aynı olmalı. Simülasyondaki radyan ile kalibre donanımın normalize eklem (joint) değeri sayısal olarak farklıdır. Aynı vektör boyutu uyumluluk kanıtı değildir.

## 2. Eylem sözleşmesi

Şu kartı doldurmadan sim action'ını donanıma uygulama:

```text
action_order: [eklem adları sırasıyla]
arm_units: radians / degrees / normalized
gripper_units: ayrı açıklama
command_semantics: absolute position / delta position / velocity / torque
normalization: kullanılan dataset stats ve ters dönüşüm
control_hz: ...
joint_limits_and_step_limits: ...
```

Strands'in embodiment/processor katmanı bazı eşlemeler sağlar; seçtiğin robot/model için gerçekten hangi eşlemeyi kullandığını state ve action örnekleriyle kontrol et. Bir anahtarı yeniden adlandırmak radyanı dereceye dönüştürmez. [Strands LeRobot local policy](https://github.com/strands-labs/robots/blob/main/docs/policies/lerobot-local.md)

## 3. Zaman sözleşmesi

Eğitimde 30 Hz kaydedilen davranışı 10 Hz'de aynı sayıda adım yürüterek aynı hareket süresini elde edemezsin. Kamera gecikmesi, USB okumaları, çıkarım (inference) ve eylem dizisi (action chunk) uzunluğu toplam davranışı değiştirir. Her kontrol döngüsünde hedeflenen ve gerçekleşen süreyi ölç.

İlk transfer değerlendirmesini kısa süre ve sınırlı görev alanında yap. Daha uzun politika yürütümü (rollout)'a geçmeden önce eylem aralıklarını ve gecikmeyi gözlemle. “Simde 100/100 yaptı” gerçek motor kalibrasyonunu doğrulamaz.

## 4. Fizik sözleşmesi

Gerçek kolun boşlukları, kablo etkisi, sürtünmesi, motor hızı ve baskı esnemesi ideal modelden ayrılır. Nesnenin ağırlığı, tutucu (gripper) yüzeyi ve temas (contact) noktaları kavramayı değiştirir. Dinamik parametreleri ölçmeden aşırı geniş randomization yapmak da anlamlı gerçekçilik sağlamaz.

**Domain randomization** eğitim (training) sahnesindeki özellikleri kontrollü aralıklarda değiştirerek modelin tek görüntüye bağımlılığını azaltmayı amaçlar. Aralıkları gerçek masanda gözleyebileceğin değişimlerle ilişkilendir. Görsel değişkenleri ve fizik değişkenlerini ayrı deneylerde aç; hangi değişikliğin fayda sağladığını ölç.

## Bu atölye için uygulanabilir geçiş

1. Simde arayüz ve kayıt hattını çalıştır.
2. Robot geldiğinde kinematik yönleri ve kamera sözleşmesini kontrol et.
3. Gerçek masadan beş pilot gösterim (demonstration) kaydet; bütün hattı kısa eğitimle sınayıp geri dön.
4. Göreve uygun gerçek gösterim sayısını ve çeşitliliğini artır.
5. Sim ön eğitimi kullanıyorsan gerçek veriyle ince ayar (fine-tuning) sonucunu yalnız gerçek veri karşılaştırma modeli (baseline)'ı ile karşılaştır.

Sim verisi + gerçek veri birleşiminin mutlaka daha iyi olacağını varsayma. Aynı test koşullarında üç koşu karşılaştırabilirsin: yalnız gerçek veri, sim → gerçek fine-tuning, karışık veri. Toplam eğitim bütçesi ve veri miktarı farklıysa bunu sonuç tablosunda belirt.

## Başarısızlık incelemesi

| Gözlem (observation) | Önce bakılacak konu |
|---|---|
| Kol ters yöne gidiyor | İsim/sıra, birim, işaret, kalibrasyon (calibration) |
| Doğru yöne gidiyor ama hedefin yanından geçiyor | Kamera pozu, taban çerçevesi, gecikme (latency) |
| Nesneye geliyor, tutamıyor | Tutucu yönü, genişlik, yüzey ve temas |
| Kaldırırken düşürüyor | Kavrama geometrisi, hız (velocity), kütle (mass), tutucu sınırı |
| Başlangıçta iyi, sonra dağılıyor | Açık döngü ufku, eğitim dışı durumlar, toparlama verisi |

Hata nedenini bilmiyorsan ilk müdahale “eğitimi iki kat uzatmak” olmasın. Bir kamerayı yanlış eşlediğin için oluşan problemi daha fazla eniyileyici (optimizer) adımı çözmez.
