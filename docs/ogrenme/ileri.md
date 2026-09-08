# İleri çalışmalar ve RL

İlk uçtan uca görevi ölçtükten sonra hangi darboğazı çözmek istediğine göre ilerle. Her yeni yöntem bir önceki temel sözleşmeleri devralır: kamera, eylem (action), zaman ve başarı ölçütü.

## Asenkron inference ve RTC

Model yeni eylem dizisini hesap ederken robot önceki diziyi yürütürse gecikmenin bir kısmı örtülebilir. Ancak yeni dizi eski gözleme dayanabilir; kuyruktaki eylemlerin ne kadarı yürütüldü, hangileri yenilenecek, iki dizinin geçişi nasıl olacak soruları doğar.

RTC bu geçiş/zamanlama sorununu ele alan mekanizmalar içerir. Yalnız `async=true` benzeri rastgele bayrak eklemek yeterli değildir; sürümün desteklediği çıkarım (inference) yapılandırmasını izle. Önce p50/p95 gecikme (latency) ve kuyruk boşalmasını ölç. [LeRobot async inference](https://huggingface.co/docs/lerobot/en/async), [RTC](https://huggingface.co/docs/lerobot/en/rtc)

## LoRA / PEFT

Tam model veya belirli katmanları eğitmek yerine adaptör parametreleri öğrenilebilir. Bunun belleği ve güncellenen parametre sayısını azaltma potansiyeli vardır; yöntem/politika (policy) desteği, hedef modüller ve kontrol noktası (checkpoint) export davranışı önemlidir.

Bu rehberin SmolVLA komutu action expert ince ayar (fine-tuning) kullanır. Bunu LoRA diye etiketleme. LoRA deneyinde karşılaştırma modeli (baseline)'a göre hangi parametrelerin güncellendiğini, eğitim (training) belleğini ve görev başarısını raporla. [LeRobot PEFT rehberi](https://huggingface.co/docs/lerobot/en/peft_training)

## İnsan müdahaleli veri

Bir model küçük hata yaptığında operatör devralıp doğru davranışı gösterebilir. Böylece politika kendi ziyaret ettiği zor durumlarda nasıl toparlanacağını öğrenir. Müdahale anı, hangi action'ın insana hangisinin modele ait olduğu ve bölüm (episode) etiketi kayıt altına alınmalıdır.

DAgger fikri bu veri dağılımı sorunuyla ilişkilidir. “Başarısız her politika yürütümü (rollout)'u başarılı veri kümesi (dataset)'e ekle” yaklaşımı değildir; hedef eylemi yine doğru bir öğretmen sağlamalıdır. [LeRobot HIL veri toplama](https://huggingface.co/docs/lerobot/en/hil_data_collection)

## Reinforcement learning

RL'de uzman action etiketleri yerine/yanında ödül üzerinden davranış öğrenilir. Bir ortam `observation`, `action`, `reward`, `terminated`, `truncated` sözleşmesi sağlar. MuJoCo fizik motorudur; tek başına iyi tanımlı bir RL görevi veya reward fonksiyonu değildir.

İlk RL projesi kavrama yerine hedefe erişme olabilir. Gözlem (observation) joint durum (state) + hedef, eylem sınırlı motor hedef farkı, ödül uç-hedef mesafesi ve başarı olayı olarak tasarlanabilir. Ancak sadece mesafeyi azaltma ödülüyle masa/engel ihlallerini görmezden gelebilirsin; başarı ve kısıtları ölç.

Reward shaping, termination ve reset kuralları politikayı doğrudan etkiler. Başlangıç noktaları testle aynı olursa başarı genelleme göstermeyebilir. Binlerce sim adımı maliyetsiz değildir; paralel ortam, rastgelelik tohumu (seed) ve sürüm yönetimi gerekir. [LeRobot simülasyonda RL](https://huggingface.co/docs/lerobot/en/hilserl_sim)

## Seçeceğin ileri deney

| Sorun | Deney |
|---|---|
| Model gözlem değişince şaşırıyor | Kontrollü ışık/arka plan varyasyonu, ayrı test |
| Küçük hatadan dönemiyor | Etiketli recovery demonstrasyonları |
| Inference kontrolü yetiştirmiyor | Gecikme ölçümü, daha kısa/yönetilen action horizon, RTC |
| Veri yükleme GPU'yu bekletiyor | Decoder/worker/prefetch profili |
| Kamera örtülüyor | İkinci görüş ve veriyle yeniden eğitim |
| RL görevi istenmeyen kısa yol buluyor | Reward/başarı/reset sözleşmesini yeniden inceleme |

## ROS 2 ve başka simülatörler

ROS 2 mevcut robotik düğümlere/sensörlere entegrasyonda yararlı olabilir. Isaac/diğer GPU sim ortamları büyük ölçekli rendering veya paralel eğitim senaryolarında araştırılabilir. Bunlar ilk SO-101 eğitim döngüsünün zorunlu parçaları değildir; somut ihtiyaç çıktığında ayrı ortamda dene.

Sadece simde başarı hedefliyorsan bile kullanılan environment, embodiment, kamera ve action alanını yaz. Başka bir robotun benchmark checkpoint'ini SO-101'e indirip eylem boyutunu kesmek bir transfer yöntemi değildir.
