# Eğitim verisini nasıl üretirim?

Eğitim verisi (training data), “bir sürü video” demek değildir. Hangi gözlemde (observation) hangi eylemin (action) doğru olduğunu gösteren, zamanı ve görevi tanımlı kayıttır. İlk iş model seçmek değil; öğretmenin ne yaptığını ve bunun neyi öğreteceğini belirlemektir.

## Üç üretim yolu

| Yol | Öğretmen (expert) | Ne üretir? | İlk kullanım |
|---|---|---|---|
| Matematiksel örnek | Bilinen kinematik denklemi | Konum/açı çiftleri | Öğrenme hesabını anlamak |
| Simülasyon (simulation) gösterimi | Kural, kontrolcü veya insan | Durum (state), eylem, gerekirse görüntü | Fizik ve kayıt hattını öğrenmek |
| Gerçek robot gösterimi | İnsan ve leader kol | Kamera, follower durumu, gönderilen eylem | Kendi masandaki görevi öğretmek |

Rastgele politika (mock/random policy), arayüzü denemeye yarar. Küpü kavramayı başarmayan rastgele hareketleri kaydedince bunlar kavrama uzmanı olmaz. Verinin kaynağını her dosya kartında açık yaz.

## 1. En küçük işe yarar görev

“Robot her şeyi yapsın” yerine “tek eklem (joint) verilen hedef açıya ulaşsın” seç. Gözlem `[mevcut açı, hedef açı]`; eylem bir sonraki motor hedefi; başarı son hatanın 0.04 rad altında olması. [İlk öğrenme scripti](ilk-ogrenme.md) bunu fizik içinde üretir.

Görsel pick-and-place görevinde gözlem kameraları, eklem durumunu ve görev metnini içerir. Etiket gelecekteki motor hedefleri olabilir. Başarı, nesnenin gerçekten kaldırılıp doğru bölgeye bırakılmasıdır. Görev farklılaştıkça veri sözleşmesi de genişler.

## 2. Bir satırı tasarla

```text
episode=12, frame=40, time=0.80 s
observation.state = ölçülen eklem konumları
observation.images.front = karar anındaki görüntü
task = "Pick up the red cube and place it in the tray"
action = o gözleme göre gerçekten gönderilen hedef
```

Sonraki state'i önceki görüntüye sessizce eşlemek zaman hizalaması (time alignment) hatasıdır. İnsan komutuyla cihaza gönderilen sınırlandırılmış komut farklıysa kayıtta hangisinin tutulduğunu belirt. [Veri mühendisliği](veri-muhendisligi.md) sayısal örnekleri açar.

## 3. Simde sayısal gösterim üret

```bash
.venv-ml/bin/python examples/15_first_learning.py --output outputs/my-first-learning
```

40 bölüm (episode) × 100 frame = 4000 satırlık `demonstrations.csv` oluşur. Kaynak öğretmen, hedefe küçük açı adımlarıyla giden bir kuraldır. Gözlemde hedef de bulunur; aynı konumdan farklı hedeflere gitme isteği böyle ayırt edilir. Script veriyi eğitim/doğrulama/test episode'larına ayırır, küçük modeli eğitir ve simülasyonda yeni politika yürütümleri (rollouts) yapar.

Bu dosyada görüntü yoktur. “CSV oluştu” diye görüntü-dil-eylem modeli (vision-language-action model, VLA) eğitimine hazır sayılmaz. Sayısal kontrol görevini öğrenmek için tam bir küçük örnektir.

## 4. Kendi CSV'ni LeRobot biçimine çevir

```bash
.venv-ml/bin/python examples/16_create_lerobot_dataset.py \
  outputs/my-first-learning/demonstrations.csv --root data/my-teaching-hinge
.venv-ml/bin/python examples/04_inspect_dataset.py data/my-teaching-hinge --expected-episodes 40
```

Dönüştürücü (converter), LeRobot'un gerçek yazıcısını kullanır:

```python
# Akış özeti; tam çalışan örnek examples/16_create_lerobot_dataset.py içinde.
dataset = LeRobotDataset.create(repo_id=repo_id, root=root, fps=50,
                               robot_type="teaching_hinge", features=features)
dataset.add_frame(frame)      # bir karar örneği
dataset.save_episode()       # bir denemenin sınırı
dataset.finalize()           # kalan dosya/metadata yazımını tamamla
```

`features` her alanın türünü, şeklini ve adlarını belirtir. Otomatik timestamp/index alanlarını rastgele doldurmak yerine yazıcının sözleşmesini kullanırız. `finalize` sonlandırması, dosya/üstverinin tamamlanması için önemlidir. [LeRobot kayıt/biçim API'si](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

Çıktı gerçek LeRobot biçimindedir; robot türü `teaching_hinge`, state boyutu 2, action boyutu 1 ve kamera sayısı 0'dır. SO-101 odaklı `05_prepare_training.py` bunu reddeder; doğru davranıştır. Yanlış robotun boyutunu altıya doldurmak uygun SmolVLA verisi üretmez.

Bu sürümde uzunluğu bir olan sayısal özellik (numeric feature) Parquet içinde tek değer (scalar) olarak saklanır. Gerçek LeRobot okuyucusunda da bu eylem sıfır boyutlu tensör olarak geldi; kendi sayısal tüketicin bir elemanlı vektör bekliyorsa açıkça `reshape(1)` uygula. Bu depolama ayrıntısı altı eleman bekleyen bir sözleşmede tek sayıyı geçerli yapmaz. Denetleyici bu iki durumu ayırır.

## 5. Görüntülü SO-101 sim kaydı

```bash
.venv-ml/bin/python examples/03_record_sim.py --root data/my-so101-smoke
.venv-ml/bin/python examples/04_inspect_dataset.py data/my-so101-smoke --expected-episodes 3
.venv-ml/bin/python examples/08_read_dataset.py --root data/my-so101-smoke --repo-id local/sim-smoke
```

Bu yol gerçek SO-101 modelinde kamera ve eylem kaydını sınar. Politikası mock olduğu için kavrama uzmanı değildir. Sonraki geliştirme, [denetleyici tasarımındaki](../simulasyon/denetleyici.md) yaklaş–kapat–kaldır–bırak aşamalarını başarılı gösterimler (demonstrations) üretecek şekilde kurmak veya simülasyonda insan kontrolü eklemektir. Başarıyı nesnenin hareketinden ölçmeden veriyi başarılı diye etiketleme.

## 6. Robot geldiğinde gerçek gösterim

[İlk açılış](../donanim/ilk-acilis.md) ve [teleoperasyonu](../donanim/teleop.md) tamamla. Ardından [beş pilot episode](../donanim/veri.md) topla. Her videoyu izle. Gösterimi büyütmeden önce nesnenin görünürlüğü, kamera sabitliği, eylem birimi, başarının bitişi ve tutucunun davranışı doğru olmalı.

Örnek çeşitlendirme planı: aynı nesneyi beş başlangıç bölgesinden al. Önce konumu değiştir; sonra başka deney sürümünde ışık veya nesne yönünü değiştir. Daha çok frame ile daha çok farklı durum aynı şey değildir.

## 7. Saklama ve sürüm kartı

Ham kayıt (raw data), temizlenmiş veri (curated data) ve eğitim için ayrılan episode listelerini ayır. Ham kaydı tek kopya üzerinde budama. `ATOLYE_CARD.json` benzeri kartta birimleri, kaynak scripti, episode bölmelerini ve başarı tanımını sakla.

Kamera eklersen veya eylem birimini değiştirirsen yeni veri sürümü oluştur. Eski ve yeni eylemleri tek tabloya fark ettirmeden birleştirmek modelin çelişkili bir ölçek öğrenmesine yol açabilir. Hugging Face'e hazır paket `meta`, `data` ve varsa `videos` ilişkisini korumalıdır; [indirme/paylaşma bölümüne](huggingface.md) bak.

**Bitirme ölçütü:** bir örneğin hangi anda, hangi öğretmenden geldiğini açıklayabiliyor; episode sınırını koruyor; videoyu ve sayısal veriyi ayrı kontrol edebiliyorsun.
