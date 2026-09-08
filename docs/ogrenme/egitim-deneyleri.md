# Eğitimi deney olarak yürütmek

Başlangıç modelini seçip `steps=20000` yazmak deney tasarımı değildir. İyi bir eğitim koşusunda hangi varsayımı sınadığın, neyi sabit tuttuğun, neye göre checkpoint seçeceğin ve sonucu nasıl tekrar üreteceğin açık olmalıdır.

Bu bölümdeki sayılar çalışma örnekleridir. Donanımında ölçülmüş eğitim süresi/VRAM veya garanti edilen SmolVLA başarısı olarak verilmez. Çalıştırılacak komutlar [eğitim tarifinde](smolvla.md); burada ayarların anlamını ve teşhis sırasını ele alıyoruz.

## 1. Step, batch ve epoch hesabı

Datasetinde eğitim için 24.000 karar frame'i, batch büyüklüğü 8 ve 20.000 optimizer güncellemesi olduğunu varsay. Tek GPU, bir batch başına bir güncelleme için toplam örnek kullanımı `8×20.000=160.000`; kaba epoch eşdeğeri `160.000/24.000≈6.67` olur.

Bu, her frame'in tam 6.67 kez kullanıldığı anlamına gelmez. Sampler, drop-last, episode filtreleri ve örnekleme biçimi dağılımı etkiler. Action chunk'ların örtüşmesi nedeniyle toplam etiket yuvası sayısı da bağımsız gösterim sayısı değildir.

Genel effective batch hesabı `B_device × GPU_sayısı × accumulation_adımı`. Bu bir kavram formülüdür; kurulu CLI'nın desteklemediği bir accumulation bayrağını uydurarak ekleme. Mevcut komut üreticisi bu atölyede tek cihaz ve doğrudan batch seçimiyle kullanılıyor.

**Alıştırma:** batch'i 8'den 4'e düşürüp aynı step sayısını korursan optimizer güncellemesi aynı, kullanılan örnek sayısı yarıya iner. “Yalnız bellek değişti, deney eşit kaldı” diyemezsin.

## 2. Öğrenme oranı ve warmup

Öğrenme oranı, optimizer'ın gradyan bilgisini ağırlık güncellemesine hangi ölçekte çevirdiğini etkiler. Çok büyük seçmek kararsızlık; çok küçük seçmek sınırlı bütçede yavaş uyum gösterebilir. AdamW ayrıca hareketli moment tahminleri ve ayrık weight decay kullanır. [PyTorch AdamW](https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html)

Warmup, koşunun başında öğrenme oranını artıran bölüm; decay sonraki değişim planıdır. Kurulu SmolVLA config'inde varsayılan warmup 1000, decay 30.000 adımdır. Kendi checkpoint config'i ve eğitim logundaki gerçek LR esas alınır. [SmolVLA eğitim ayarları](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/policies/smolvla/configuration_smolvla.py)

100 adımlık smoke denemesi bu varsayılanla warmup'ın içinde kalır. Dosya okuma, forward/backward ve checkpoint hattını sınamak için faydalıdır; uzun vadeli model kalitesini o loss eğiminden ilan etme. Öğrenme oranını değiştirirken kullanılan schedule ve toplam adımı da kaydet.

## 3. VRAM hesabını parçalara ayır

Bellek yalnız model ağırlığı değildir. Ağırlıklar, eğitilen parametrelerin gradyanları, optimizer durumu, aktivasyonlar, giriş görüntüleri ve geçici çalışma alanları birlikte yer kaplar.

Tamamen örnek bir modelde 100 milyon eğitilen FP32 parametre olsun: ağırlık yaklaşık 400 MB, gradyan yaklaşık 400 MB, Adam'ın iki FP32 momenti yaklaşık 800 MB. Bunlar tek başına yaklaşık **1.6 GB ondalık** eder; aktivasyonlar ve diğer bileşenler eklenmemiştir. Bu sayı SmolVLA'nın ölçülmüş gereksinimi değildir. BF16/mixed precision düzeni ve optimizer uygulaması depolama hesabını değiştirir.

İki 512×512 RGB kamera, B=8, float32 için ham görüntü batch'i `8×2×3×512×512×4 = 50,331,648 byte`, yani 48 MiB. Model içindeki aktivasyonların toplamı bundan çok daha büyük olabilir. “Görüntüler sadece 48 MiB, neden OOM oldu?” sorusunun cevabı kalan bileşenlerdir.

OOM'da önce batch'i küçült; sonra desteklenen precision ve activation checkpointing seçeneklerini sürümünden doğrula. Kamera kaldırmak veya çözünürlüğü değiştirmek giriş bilgisini de değiştirir; yalnız altyapı ayarı gibi değerlendirme. Hata preprocessing/ilk model yüklemesinde mi, ilk backward'da mı geliyor diye aşamayı kaydet.

## 4. Minimum deney kartı

`templates/experiment.md` genel şablonunu şu alanlarla doldur:

| Alan | Örnek |
|---|---|
| Hipotez | Wrist kamera kapanış anındaki hataları azaltır |
| Veri sürümü | `pick-v2`, episode listeleri ve birimler kayıtlı |
| Sabitler | Başlangıç checkpoint'i, görev, train/test grupları, seed, eğitim bütçesi |
| Değişken | Front'a ek wrist görüntüsü |
| Ana ölçüt | Önceden tanımlı pick-and-place görev başarısı |
| Tanı ölçütleri | Kaçırma, düşürme, yanlış bölge, gecikme, training/validation loss |
| Sonuç | Sayım, belirsizlik, başarısız video yolları |

Tek değişken kuralı ilk karşılaştırmaları yorumlamayı kolaylaştırır. Daha ileri deneylerde etkileşimleri birlikte inceleyebilirsin; başlangıçta beş ayarı aynı anda değiştirip iyileşmenin nedenini tahmin etmeye çalışma.

## 5. Dört koşuluk ilk deney dizisi

| Koşu | Amaç | Ne tamamlanınca ilerle? |
|---|---|---|
| A: Veri okuma | Şema, video, birim, maskeler | İncelenen batch doğru |
| B: Kısa eğitim | Forward/backward/checkpoint hattı | Sonlu loss ve yüklenebilir çıktı |
| C: Referans eğitim | İlk görev baseline'ı | Sabit test protokolüyle rollout |
| D: Hedefli değişiklik | En büyük hata grubunu azaltmak | C ile aynı koşullarda karşılaştırma |

B koşusunda aynı birkaç örneğe aşırı uyum denemesi de eğitim sinyalinin akıp akmadığını anlamaya yardım edebilir. Bu özellikle veri/etiket hatasını aramak içindir; ezberlenen küçük grubun başarısını genelleme sonucu diye sunma. Base checkpoint'e göre daha iyi olup olmadığını ayrıca ölç.

## 6. Loss düşüyor ama robot kötü: inceleme sırası

**Önce sözleşme.** Checkpoint doğru mu, kamera isimleri doğru mu, RGB/BGR doğru mu, action sırası ve birim aynı mı, normalizasyon geri çevriliyor mu? Bunlardan biri bozuksa yeni 20.000 adımlık eğitim yanlış sorunu çözer.

**Sonra zaman.** Görüntü yaşı, çıkarım süresi, kontrol hızı ve yürütülen chunk uzunluğunu ölç. Robot nesne yerindeyken doğru yaklaşabiliyor, nesne hareket edince yetişemiyorsa gecikme hipotezi anlamlıdır; bunu sabit/dinamik nesne karşılaştırmasıyla sına.

**Sonra dağılım.** Eğitim başlangıçlarıyla rollout başlangıçlarını karşılaştır. Küp hep merkezde öğretildiyse masa köşesindeki başarısızlık daha çok training step gerektiğini tek başına göstermez. O bölgede kaliteli gösterim bulunup bulunmadığına bak.

**Sonra öğrenme.** Train loss düşerken validation kötüleşiyorsa aşırı uyum hipotezi kur. İkisi de kötü kalıyorsa hedef/normalizasyon, öğrenme oranı, eğitilebilir parametreler ve veri çeşitliliğini incele. Hiçbir loss eğrisi tek başına bu nedenleri kesin ayırmaz; kontrollü deneye ihtiyaç var.

## 7. Gözlenen belirti → sınanabilir deney

| Belirti | İlk hipotez | Ayırıcı deney |
|---|---|---|
| Kol ilk komutta yanlış yönde | Joint sırası/işaret/birim | Küçük tek eklem komutunu state ile eşle |
| Nesneye geliyor, erken kapatıyor | Görüş veya zamanlama | Kapanış çevresinde kamera/action zamanlarını incele |
| Tüm başlangıçlarda aynı yere uzanıyor | Konum çeşitliliği yetersiz | Eğitim konumlarını haritala; yeni bölge testi yap |
| Başarılı kavrıyor, taşırken düşürüyor | Taşıma gösterimi/temas/komut değişimi | Kaldırma ve taşıma aşamalarını ayrı puanla |
| Simde iyi, gerçek kolda kötü | Birim, dinamik veya görüntü farkı | Önce state/action sözleşmesi, sonra görsel/dinamik farkları ayrı dene |
| Validation çok iyi, yeni günde kötü | Veri sızıntısı veya gün değişimi | Gün bazlı bağımsız test oluştur |
| Loss birden NaN | Veri/ölçek/nümerik sorun | İlk bozuk batch'i sakla; finite ve aralık kontrolü yap |

Bu tablo olası nedenleri sıralar; otomatik teşhis değildir. Her satırda hipotezi destekleyen veya çürüten bir ölçüm üretmen gerekir.

## 8. Checkpoint seçimi ve son test

Son checkpoint her zaman en iyi checkpoint değildir. Önceden belirlediğin validation yöntemiyle seçim yap; fiziksel denemeler pahalıysa az sayıda aday seçip karşılaştırma protokolünü sabitle. Son test koşullarını seçim sırasında tekrar tekrar kullanırsan test bilgisini ayarlara taşımış olursun.

Örneğin A 20 denemede 14, B 20 denemede 16 başarı sağlasın. Yalnız `%70 → %80` yazmak küçük örnek belirsizliğini saklar. [Değerlendirme aracı](degerlendirme.md) sayımları ve Wilson aralığını verir. Aynı başlangıç koşulları ve birden fazla tekrar güçlü karşılaştırmaya yardım eder; yalnız güven aralıklarının örtüşmesine bakmak da tek başına formal karşılaştırma testi değildir.

Başarısız denemeyi “robotu yanlış koydum” diyerek sonradan çıkarmak yerine dışlama koşulunu baştan yaz. Başlangıç geçersizse bunu ayrı kaydet, kaç denemenin dışlandığını göster. Görev başarısı insanın videoyu seçmesine bağlı olmamalı.

## 9. Tekrarlanabilirliğin pratik sınırı

Seed kaydı faydalıdır; GPU çekirdekleri, kütüphane sürümleri, kamera zamanlaması ve fiziksel temas nedeniyle bütün koşullar bit düzeyinde aynı olmayabilir. Hedef, aynı sonucu makul sınırlar içinde yeniden üreten bir çalışma düzenidir.

Veri episode listesi, base model revision'ı, tam komut, paket sürümleri, eğitim logu, preprocessing dosyaları, checkpoint ve test CSV'si aynı deney kimliğine bağlanmalı. Model klasöründeki yalnız ağırlık dosyasını kopyalamak bütün runtime sözleşmesini taşımayabilir.

**Bitirme koşulu:** başka biri deney kartından hangi modeli hangi veriye hangi ayarla eğittiğini ve hangi testte ne bulduğunu anlayabiliyor. Sonraki koşunun neden yapıldığını bir cümleyle açıklayabiliyorsun.
