# SmolVLA içeride nasıl öğreniyor?

Komutu [SmolVLA eğitim sayfasından](smolvla.md) üretebilirsin. Burada o komutun kurduğu problemi açıyoruz: görüntü, metin ve robot durumundan gelecekteki eylem dizisi üretmek. Açıklama, kurulu **LeRobot 0.6.1** kodu ve ayrıca incelenen kaynak sürümü üzerinden hazırlanmıştır. Checkpoint config'i bazı varsayılanları değiştirebilir; kendi kaydedilmiş config'in çalışma için esas kaynaktır.

## 1. Üç girdi, bir eylem dizisi

```text
front/wrist görüntüleri ── görüntü özellikleri ─┐
görev metni ────────────── dil tokenları ───────┤
ölçülen eklem durumu ───── state projection ───┤
                                             ↓
                                   koşullandırılmış temsil
                                             ↓
gürültülü eylem dizisi + akış zamanı ── action expert
                                             ↓
                                    eylem düzeltme alanı
                                             ↓
                                  gelecekteki eklem hedefleri
```

SmolVLA, görsel-dil temsilini eylem üreten bir uzmanla birleştirir; flow matching ve eylem dizileri kullanır. Bu tasarımda dil, görevi koşullandırır. Modelin eylem çıktısı bir sohbet yanıtı olarak yazılmış Python kodu değildir. [SmolVLA makalesi](https://arxiv.org/abs/2506.01844)

“Kırmızı küpü al” metni tek başına küp koordinatı sağlamaz; görüntü, durum ve eğitimdeki örnek ilişkiler gerekir. Her episode'a aynı metni yazdıysan farklı nesne seçme talimatlarını öğrendiğini yalnız bu veriyle göstermiş olmazsın.

## 2. Tensörleri sayılarla okuyalım

Örnek ayar: batch `B=8`, iki kamera, kayıt çözünürlüğü 480×640, SO-101 action boyutu `D=6`, ufuk `H=50`.

| Aşama | Şekil örneği | Açıklama |
|---|---|---|
| Bir kamera, disk metadata | `[480,640,3]` | Yükseklik, genişlik, renk |
| Bir kamera, batch | `[8,3,480,640]` | Batch, kanal, yükseklik, genişlik |
| State | `[8,6]` | Karar anındaki eklem/tutucu durumu |
| Action hedefi | `[8,50,6]` | 50 gelecekteki altı boyutlu komut |
| Zaman padding maskesi | `[8,50]` | Episode dışına taşan etiketler |
| Dil tokenları | `[8,L]` | Metin token uzunluğu; action ufku değil |
| İç action/state boyutu | Son eksen 32'ye tamamlanır | Farklı robot boyutları için iç şekil |

İki kamera genellikle iki adlandırılmış feature olarak hazırlanır; veri okuyucusunun otomatik `[B,2,3,H,W]` verdiğini varsayma. Görüntü resize/padding'i içeride ayrıca yapılır. Kurulu config'de kare hedef 512×512, `max_state_dim=max_action_dim=32`, `chunk_size=n_action_steps=50`, `num_steps=10` değerleri bulunur. [SmolVLA config kaynağı](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/policies/smolvla/configuration_smolvla.py)

32'ye padding, robotun 32 motoru olduğu anlamına gelmez. Gerçek altı action boyutu runtime'da korunur. Ayrıca shape'in doğru olması joint sırası ve birimin doğru olduğunu kanıtlamaz.

## 3. Normalizasyon nerede duruyor?

State/action değerleri eğitim istatistikleriyle ölçeklenir. Örneğin iki eklemin standart sapması çok farklıysa ham kare hata büyük sayılı boyuta fazla ağırlık verebilir. Ortalama/std ile ölçekleme bunu değiştirir. Çalıştırmada aynı preprocessing ve ters action dönüşümü checkpoint'le birlikte kullanılmalıdır.

Görüntüler okuyucudan tipik olarak `[0,1]` float aralığında gelir; SmolVLA görüntü hazırlığı resize/padding sonrası bunları encoder için `[-1,1]` aralığına taşır. Dışarıda bir daha aynı dönüşümü uygulamak aralığı bozar. [Kurulu uygulamayla karşılaştırılan model kaynağı](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/policies/smolvla/modeling_smolvla.py)

Pratik kontrol: bir batch'in adlarını, şekillerini, min/max ve sonluluk durumunu yazdır. Kamera kanalını RGB yerine BGR bırakmak shape kontrolünden geçer; renkli bir test nesnesinin görüntüsünü de izle.

## 4. Neden doğrudan tek MSE eylemi değil?

Bir nesnenin etrafından sağdan veya soldan dolaşan iki geçerli davranış düşün. Bu iki yolun nokta nokta ortalaması nesnenin içinden geçebilir. Koşullu bir üretici model bir eylem dağılımını temsil etmeye çalışır. Bu bir tasarım motivasyonudur; kullanılan veri ve model her çoklu davranışı kusursuz çözer anlamına gelmez.

Flow matching'de eğitim örneğinin eylem dizisi ile rastgele gürültü arasında ara örnekler kurulur. Model, koşullara bakarak bu uzaydaki yön/hız alanını öğrenir. Bu sayfadaki `t`, 30 Hz robot zamanı veya episode frame indeksi değildir; **veri ile gürültü arasındaki akış parametresidir**.

## 5. İşaretleri karıştırmadan flow matching

Bu uygulamanın yön sözleşmesi:

```text
A = normalleştirilmiş gerçek action chunk
ε = aynı şekilde standart normal gürültü
t = akış parametresi

x_t = (1 - t) A + t ε
u_t = ε - A
```

`t=0` veri, `t=1` gürültüdür. Model `vθ(x_t,t,koşullar)` üretir; hedef alan `u_t` ile kare hata üzerinden eğitilir. Bu formüller için bazı başka anlatımlarda ters zaman yönü kullanılır; başka bir kaynaktaki işareti buraya tek başına taşıma. [SmolVLA forward hesabı](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/policies/smolvla/modeling_smolvla.py)

Özgün iki boyutlu hesap örneğimiz:

```text
A = [0.2, -0.4]
ε = [1.0,  0.6]
t = 0.75

x_t = [0.8, 0.35]
u_t = [0.8, 1.0]

Model tahmini v = [0.7, 1.2] ise:
MSE = ((0.7-0.8)² + (1.2-1.0)²) / 2 = 0.025
```

Bu sayılar normalize eylem uzayında seçilmiş öğretim değerleridir; fiziksel kol hedefi olarak gönderilmez.

## 6. Çıkarımda gürültüden eyleme

Çıkarım `t=1`'de gürültüyle başlar, `t=0`'a gider. Basit Euler adımı `Δt=-1/N` ve `x ← x + Δt v` şeklindedir. Kurulu ortak integratör bu işaret sözleşmesini kullanır. [LeRobot flow matching integratörü](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/policies/common/flow_matching.py)

Önceki örnekte modelin ideal sabit alanı tam bildiğini varsayalım. Dört adım:

| Akış t | x |
|---|---|
| 1.00 | `[1.00, 0.60]` |
| 0.75 | `[0.80, 0.35]` |
| 0.50 | `[0.60, 0.10]` |
| 0.25 | `[0.40, −0.15]` |
| 0.00 | `[0.20, −0.40]` |

```bash
.venv/bin/python examples/11_flow_matching.py
```

Script MSE'yi, ideal Euler yolunu ve masked loss hesabını doğrular. Model indirmez veya eğitmez. Gerçek öğrenilmiş alan sabit olmak zorunda değildir; tablodaki tam geri dönüş ideal hesap örneğine aittir.

`num_steps=10`, “robot on adım hareket eder” demek değildir; bir action chunk üretirken çözücünün kaç güncelleme yaptığıdır. `chunk_size=50` üretilen robot komutu sayısını belirler. Bu iki sayıyı karıştırma.

## 7. Bir eğitim güncellemesi

Bir batch seçilir; görüntüler/durum/metin hazırlanır ve gelecekteki action etiketleri toplanır. Gürültü ve akış zamanı örneklenir. Ağ tahmin üretir. Geçersiz episode adımları loss'tan maskelenir. Backward ile eğitilebilir parametrelerin gradyanları hesaplanır; optimizer ağırlıkları değiştirir; scheduler öğrenme oranını günceller. Kurulu eğitici gradyan kırpma da uygular. [LeRobot eğitim döngüsü](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/scripts/lerobot_train.py)

`loss.backward()` robota komut göndermez. `optimizer.step()` de fizik adımı değildir. Eğitimdeki 20.000 step ile simülasyondaki 20.000 `mj_step` farklı işlemlerdir.

Aynı dataset örneğine farklı gürültü/t verilince training loss değişebilir. Bir batch'in loss'unu başka batch ile doğrudan görev başarısı gibi yorumlama. Normalizasyon ve padding kapsamı değişirse loss ölçeği de değişebilir.

## 8. Hangi ağırlıklar değişiyor?

Bu atölyenin tarifinde `train_expert_only=true`, `freeze_vision_encoder=true`, `train_state_proj=true` açık seçilir. VLM tarafı dondurulurken eylem uzmanı ve ilgili öğrenilebilir projeksiyonlar görev verisine uyarlanır. Bu, bütün modelin sıfırdan eğitimi veya otomatik LoRA kurulumu değildir. [Expert dondurma uygulaması](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/policies/smolvla/smolvlm_with_expert.py)

Modeli gerçekten yüklediğin ortamda şu küçük inceleme anlamlıdır:

```python
# policy: yüklenmiş model nesnen; bu parça tek başına model indirmez.
total = sum(p.numel() for p in policy.parameters())
trainable = sum(p.numel() for p in policy.parameters() if p.requires_grad)
print({"total": total, "trainable": trainable})
for name, parameter in policy.named_parameters():
    if parameter.requires_grad:
        print(name, tuple(parameter.shape))
```

“Yalnız expert” adıyla yetinme; çıktıyı deney notuna kaydet. Checkpoint/uygulama sürümündeki değişiklik eğitim kapsamını etkileyebilir.

## 9. Action queue ve yeni gözlem

50 komut ürettiğinde hepsini 30 Hz'de çalıştırmak yaklaşık 1.67 s sürer. Bu süre boyunca yeni politika çıkarımı yapmayan bir uygulama, komutları eski gözleme göre yürütür. Daha kısa yürütme ufku sık yeniden planlamaya izin verebilir; fakat model gecikmesi yüksekse kuyruk boşalabilir.

Örneğin çıkarım 180 ms ve kontrol 30 Hz olsun. Sadece bir komut 33 ms'yi kapsar, 10 komut yaklaşık 333 ms'yi kapsar. Bu aritmetik akış kapasitesini anlamaya yardım eder; kuyruk mimarisi, kamera gecikmesi ve jitter ayrıca ölçülür. Asenkron/RTC seçeneğini açmak yeni chunk ile eski chunk'ın sınırını otomatik olarak her görevde doğru yapmaz. [Mevcut gecikme laboratuvarı](../temel/laboratuvar.md) ile sayıları değiştir.

## 10. Bölümü bitirme sınaması

Şu üç cümleyi kendi örneğinle açıklayabilmelisin: “`t` robot zamanı değil”; “32 iç boyut, 32 motor değil”; “düşük flow loss, nesne bırakma başarısı değil.” Sonra [eğitim deneylerine](egitim-deneyleri.md) geç: bu iç hesapları bilmenin amacı logları okuyup doğru deney seçmek.
