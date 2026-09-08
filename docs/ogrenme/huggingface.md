# Hugging Face: bul, indir, oku ve kullan

Veri seti (dataset), modelin öğreneceği örneklerdir. Model deposu (model repository), öğrenilmiş ağırlık ve yapılandırma dosyalarını barındırır. Hugging Face Hub ikisini de barındırır; adresleri ve indirme türleri farklıdır. `lerobot/smolvla_base` bir model, `lerobot/svla_so100_pickplace` bir veri setidir.

## 1. Her video robot eğitim verisi değil

Bir robotun videosu, motorlara hangi komutların gönderildiğini otomatik vermez. Taklit öğrenme (imitation learning) için görüntü, ölçülen durum (state), eylem (action), zaman ve görev arasındaki ilişki gerekir. Hub'da `Robotics` etiketi görmek bile senin koluna uygun eylem sözleşmesini kanıtlamaz.

Veri kartında (dataset card) robot türünü, görevi, kameraları, lisansı ve toplama yöntemini oku. Sonra `meta/info.json` üzerinden biçim sürümü, FPS ve özellik (feature) şekillerine bak. Veri kartında yazılmayan birimi yalnız sayılara bakarak kesinleştirme.

## 2. İndirmeden önce boyuta bak

ML ortamı [kurulumda](../basla/kurulum.md) hazırlanır. Bu araç varsayılan olarak yalnız depo listesini ve küçük `meta/info.json` dosyasını çeker:

```bash
.venv-ml/bin/python examples/14_hub_dataset.py lerobot/svla_so100_pickplace
```

8 Eylül 2026'da incelenen sabit sürüm (revision): `728583b5eaf9e739a7f119e2def466fa1d552402`. Yaklaşık 470.12 MB, 50 bölüm (episode), 19.631 kare (frame), 30 FPS ve `top`/`wrist` kameraları içeriyordu. Şema SO-100 olarak tanımlı; bunu SO-101 verisi diye yeniden adlandırmıyoruz. [Kaynak veri seti](https://huggingface.co/datasets/lerobot/svla_so100_pickplace)

`inspect` sırasında küçük üstveri (metadata) önbelleğe alınabilir; “hiç ağ/veri kullanmaz” anlamına gelmez. Büyük video dosyaları bu modda indirilmez.

## 3. Yalnız metadata ön izlemesi

```bash
.venv-ml/bin/python examples/14_hub_dataset.py lerobot/svla_so100_pickplace \
  --mode metadata --root data/hub-preview --max-mb 5
```

Bu klasör şemayı incelemek içindir; videoları ve bütün örnekleri içeren hazır eğitim (training) seti değildir. Ardından tam indirme yapmak için farklı bir kök seç. Araç mevcut kökün üzerine yazmaz.

## 4. Sabit sürümü indir

```bash
.venv-ml/bin/python examples/14_hub_dataset.py lerobot/svla_so100_pickplace \
  --revision 728583b5eaf9e739a7f119e2def466fa1d552402 \
  --mode download --root data/hub-so100 --max-mb 500
```

Script seçilen dosyaların boyutunu indirmeden kontrol eder. Varsayılan 250 MB sınırına bu örnek sığmaz; burada 500 MB açık seçildi. `main` zamanla değişebilir; script isteği commit kimliğine çözüp o sürümü indirir ve `ATOLYE_DOWNLOAD.json` dosyasına yazar. Hub indirme API'sinde `repo_type="dataset"`, `revision` ve dosya filtreleri bu ayrımı sağlar. [Hub indirme kılavuzu](https://huggingface.co/docs/huggingface_hub/en/guides/download)

Bu çalışma alanında tam indirme **`data/hub-so100-verified/`** içine yapıldı. O kopyayı hemen inceleyebilirsin; yeniden indirmek zorunda değilsin. Başka bilgisayarda bu klasörün hazır olduğunu varsayma.

## 5. Dosyayı aç, sonra görüntüyü aç

```bash
.venv-ml/bin/python examples/04_inspect_dataset.py data/hub-so100-verified --expected-episodes 50
.venv-ml/bin/python examples/08_read_dataset.py \
  --root data/hub-so100-verified --repo-id lerobot/svla_so100_pickplace --index 20
```

Yerel denetimde 50 episode/19.631 frame geçti. İki kamera da gerçek video çözücüsü (video decoder) üzerinden `[3,480,640]` tensör (tensor) olarak okundu; PNG'ler `outputs/` altında. Bu, bütün gösterimlerin görev başarısını tek tek incelediğimiz anlamına gelmez.

LeRobot'un okuyucusu (dataset reader), episode ve video parçalarının ilişkisini metadata'dan çözer. Genel `datasets.load_dataset()` ile tabloyu açabilmek, robotun eşzamanlı video pencerelerinin de doğru okunduğunu kanıtlamaz. [LeRobotDataset biçimi ve okuma](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

## 6. Bir episode seçmek her zaman küçük indirme demek mi?

LeRobot okuyucusunda `episodes=[0]` gibi seçimler vardır. Ancak v3'te birçok episode aynı Parquet/MP4 parçasında (shard) olabilir. Tek episode'un verisini açmak için paylaşılan büyük dosyayı indirmek gerekebilir. Dosya sayısını veya seçili episode sayısını doğrudan ağ boyutu sanma.

Akış halinde okuma (streaming), büyük veriyi tümüyle yerel diske almadan kullanma seçeneğidir; ağ, decoder ve rastgele erişim davranışı farklılaşır. İlk deneyde küçük ve sabit bir yerel kopyayla çalışmak hatayı bulmayı kolaylaştırır. Daha sonra [resmî streaming tarifini](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3#stream-datasets) kurulu sürümünle karşılaştır.

## 7. Bunu eğitimde nasıl kullanırım?

Önce eylem boyutu, sırası, birimi, kamera adları ve görevi yaz. İndirilen örnekte altı eylem bileşeni bulunması bizim kolumuzdaki altı sayıyla aynı fiziksel anlamı taşıdığını kanıtlamaz. Özellikle `top` ve `wrist` adlarını keyfî biçimde `front` ve `camera1` diye değiştirme; veri ve politika (policy) yapılandırması birlikte eşlenmelidir.

Eğitim komutunu hazırlamak için:

```bash
.venv-ml/bin/python examples/05_prepare_training.py \
  --root data/hub-so100-verified --repo-id lerobot/svla_so100_pickplace \
  --output-dir outputs/train/hub-so100-practice \
  --device cpu --steps 20 --batch-size 1
```

Bu komut yalnız sonraki eğitim komutunu **üretir**. Çalıştırırsan model ağırlıkları indirilebilir ve CPU çok yavaş olabilir; tam ince ayar (fine-tuning) için [hesaplama ortamına](hesaplama.md) geç. Buradaki veri üzerinde eğitim yapmak, ortaya çıkan modeli gerçek SO-101'ine doğrudan güvenle gönderebileceğini göstermez.

## 8. Kendi verini Hub'a hazırlamak

Önce yerelde üret, kapat/finalize et, şemayı ve videoları doğrula. Veri kartına robot türü, görev, eylem birimi/sırası, kamera düzeni, FPS, gösterim (demonstration) kaynağı, başarının nasıl ölçüldüğü ve lisans seçimini ekle. [Veri üretimi sayfası](veri-uretimi.md) üç yolu gösterir.

Hub'a yüklemek (upload/push) eğitim için zorunlu değildir. Paylaşmak istediğinde gerçek kullanıcı/kurum namespace'i ve görünürlük seçilir; `local/...` çevrimdışı alıştırma kimliğidir. Hesap erişimi ve özel/açık depo seçimini hazırladıktan sonra resmî `LeRobotDataset.push_to_hub` akışını kullanabilirsin. Bu atölyedeki scriptler veri yüklemez veya yeni hesap açmaz. [Kayıt ve Hub akışı](https://huggingface.co/docs/lerobot/en/il_robots)

**Bölüm çıktısı:** sürümü kaydedilmiş yerel veri, temiz sayısal denetim, açılmış kamera örnekleri ve eğitimden önce doldurulmuş eylem/kamera sözleşmesi.
