# Taklit öğrenme, ACT ve VLA

Bir robot davranışını üç farklı yolla üretebilirsin: el yazımı kontrol kuralları, başarılı gösterimlerden taklit öğrenme (imitation learning) veya ödülle etkileşimden pekiştirmeli öğrenme (reinforcement learning). Bu atölyenin ilk öğrenme yolu **taklit öğrenme**.

## Behavior cloning

Gösterimdeki gözleme karşılık uzman eylemini tahmin etmeyi öğrenirsin:

```text
gözlem = kamera görüntüleri + eklem durumu + görev
hedef  = uzmanın gönderdiği action veya gelecek action dizisi
model  = gözlemden hedefe eşleme
```

Basit bir örnekte kayıp (loss), tahmin ile hedef arasındaki ortalama karesel fark olabilir. VLA'nın gerçek kayıp/mimari ayrıntıları modele göre değişir. Bütün modeller “tek kareden altı açıyı MSE ile tahmin eder” biçiminde çalışmaz.

## Önce gerçekten küçük bir modeli eğit

```bash
.venv/bin/python examples/07_toy_behavior_cloning.py
```

Bu alıştırma NumPy ile küçük bir sinir ağı eğitir. İki eklemli düzlemsel kolun bilinen FK denklemlerinden hedef konumu/eklem (joint) çifti üretir. Model hedef `(x,y)` koordinatından iki eklem açısını öğrenir. Eğitim (training) için 1500, aynı sınırlar içinde ayrı test için 300 örnek kullanılır.

`outputs/toy-bc/loss.csv`, `metrics.json` ve `policy.npz` oluşur. Sabit ortalama poz karşılaştırma modeli (baseline)'ı ile modelin uç nokta hatasını karşılaştır. Burada kamera, dil, gerçek motor ve MuJoCo dinamiği yoktur. Bu bir **öğrenme döngüsü alıştırmasıdır**, SO-101 politikası veya VLA eğitimi değildir.

Kod tek bir dirsek çözümü dalından örnek toplar. Aynı hedef için iki farklı geçerli eklem çözümünü tek çıktılı basit regresyona karıştırırsan model ikisinin ortalamasını üretebilir; ortalama her zaman geçerli çözüm değildir. Robot gösterimlerindeki çok modlu davranış sorununu bu küçük örnekle düşün.

## ACT neden başlangıç karşılaştırması?

ACT, eylemleri dizi hâlinde tahmin etmeye odaklanan bir taklit öğrenme yaklaşımıdır. Tek veya sınırlı görevde kamera/durumdan hareket öğrenme baseline'ı olarak kullanılabilir. “Dil komutlarını genel olarak anlayan VLA” ile aynı iddiayı taşımaz. [LeRobot ACT](https://huggingface.co/docs/lerobot/en/act)

Aynı kaliteli veri üzerinde ACT'nin çalışması, kamera/veri/kontrol hattına dair faydalı bir referans sağlar. Sonra SmolVLA'nın pretrained görsel/dil temsilinden ne kadar yararlandığını kıyaslayabilirsin. Görev başarısını yalnız model boyutuyla açıklama.

## Vision–Language–Action

**Vision:** görüntüler. **Language:** görev metni. **Action:** robot kontrol çıktısı. Robot durumu da koşullandırmaya katılabilir. Model, görsel/dil girdisini bir eylem (action) tahmin mekanizmasına bağlar. Bir sohbet cevabı üretmesi veya ekrandaki her nesneyi isimlendirmesi asıl çıktısı değildir.

SmolVLA'nın yayımlanan çalışması yaklaşık 450M parametreli kompakt bir VLA ve asenkron çalıştırma yaklaşımı anlatır. Bu boyut, kendi başına bütün görevleri çözme veya her bilgisayarda gerçek zamanlı çalışma garantisi değildir. [SmolVLA makalesi](https://arxiv.org/abs/2506.01844)

## Pretraining, fine-tuning ve inference

| İşlem | Ne değişir? | Bu projede |
|---|---|---|
| ön eğitim (Pretraining) | Genel başlangıç ağırlıkları geniş veriyle öğrenilir | Sıfırdan yapmıyoruz |
| ince ayar (Fine-tuning) | Hazır model kendi gösterimlerine uyarlanır | SmolVLA ana yolu |
| çıkarım (Inference) | Ağırlıklar (weights) sabitken yeni gözlemden eylem hesaplanır | Sim/gerçek politika yürütümü (rollout) |
| Evaluation | Başarı ve hata dağılımı ölçülür | Ayrı test denemeleri |

`lerobot/smolvla_base` başlangıç kontrol noktası (checkpoint)'i olması, senin kolunun kalibrasyonunu ve masanın düzenini bildiği anlamına gelmez. Göreve uygun veriyle uyarlama ve sözleşme kontrolü gerekir.

## Dağılım kayması ve toparlama

Taklit modeli eğitimde uzmanın gördüğü durumlarda iyi olabilir. Küçük bir hata nesneyi kaydırınca eğitimde görmediği bir durum (state) oluşur; sonraki hatalar birikir. Bu nedenle düşük training loss ile yüksek fiziksel başarı aynı şey değildir.

İlk sette temiz başarılı gösterimler (demonstrations) topla. Sonraki iterasyonda sık karşılaşılan küçük sapmalardan doğru toparlamayı göster. Kararsız/çelişkili hareketleri çoğaltmak ile bilinçli recovery demonstrasyonu farklıdır. [İleri çalışmalar](ileri.md) insan müdahaleli öğrenme ve RL ayrımını açar.
