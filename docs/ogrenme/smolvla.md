# SmolVLA eğitimi

Bu bölümün hedefi `lerobot/smolvla_base` başlangıç modelini kendi SO-101 gösterimlerine uyarlamak. Robotu henüz bekliyorsan sim smoke verisiyle komut üretimini, hazır kaliteli bir dataset ile eğitim hazırlığını öğrenebilirsin. Gerçek görev başarısı için gösterim kalitesi ve değerlendirme gerekir.

!!! info "Bu bilgisayarda doğrulanan sınır"
    Ortam kurulumu, LeRobot veri kaydı/okuma, şema dönüşümü ve eğitim komutu hazırlığı doğrulandı. SmolVLA ağırlıkları indirilerek tam fine-tuning çalıştırılmadı; GPU eğitimi veya fiziksel görev başarısı tamamlandı diye sunulmuyor. [Tam doğrulama kaydı](../basla/dogrulama.md).

## 1. Ön koşullar

Veri setinin metadata/parquet denetimi geçmeli; videolar açılmalı. En az bir gerçek kamera ve altı boyutlu SO-101 state/action şeması beklenir. Gerçek veri ile sim verisinin eylem birimleri farklıysa önce ortak temsil/eşleme tasarlanır.

Normal eğitim hedefi Linux + NVIDIA CUDA; Mac/MPS ve CPU küçük uyumluluk denemeleri için ayrıca ele alınır. Model/bağımlılık indirmesi internet, eğitim ise yeterli bellek ve disk ister. Bu sayfadaki komutlar otomatik ücretli bulut işi veya Hub yüklemesi başlatmaz.

```bash
source .venv-ml/bin/activate
python examples/00_doctor.py
python examples/04_inspect_dataset.py data/so101-pick-v1
```

## 2. Kamera isimleri tuzağı

Base modelin yayımlanan config'inde `observation.images.camera1`, `camera2`, `camera3` girişleri bulunur; senin verin `front` ve `wrist` olabilir. Aynı çözünürlükte olmaları isim uyuşmazlığını çözmez. [SmolVLA base config](https://huggingface.co/lerobot/smolvla_base/blob/main/config.json)

İki yaklaşım vardır. `rename_map` ile mevcut anahtarları checkpoint'in beklediği anahtarlara eşleyebilirsin. Ya da bu görev için giriş feature'larını gerçekten kaydettiğin kamera adlarıyla açık tanımlarsın. Bu atölyenin **komut üreticisi ikinci yolu** kullanır: metadata'dan `policy.input_features` üretir, olmayan üçüncü kamerayı varmış gibi bırakmaz.

Örnek çıktı:

```json
{
  "observation.state": {"type": "STATE", "shape": [6]},
  "observation.images.front": {"type": "VISUAL", "shape": [3, 480, 640]},
  "observation.images.wrist": {"type": "VISUAL", "shape": [3, 480, 640]}
}
```

Bu şema eğitim ve runtime için sözleşme olur. Fotoğrafın çözünürlüğü ile model içindeki resize/padding boyutu aynı şey değildir. `empty_cameras` her yanlış isimli kamera girdisini sihirli biçimde onarmaz; bu tarifte gerçek girişler açıkça belirlendiği için `0` seçilir. [Rename map ve empty camera açıklaması](https://huggingface.co/docs/lerobot/en/rename_map)

## 3. Önce kısa eğitim komutu üret

```bash
python examples/05_prepare_training.py \
  --root data/so101-pick-v1 \
  --repo-id local/so101-pick-v1 \
  --output-dir outputs/train/smolvla-smoke \
  --steps 100 \
  --batch-size 1 \
  --device cuda \
  --eval-split 0 \
  --save-command outputs/commands/smolvla-smoke.sh
```

Bu işlem **komut yazar**, modeli yüklemez veya eğitmez. Dosyayı incele. `lerobot-train` ML ortamının PATH'inde olmalı; sonra:

```bash
bash outputs/commands/smolvla-smoke.sh
```

Bu ikinci komut ilk çalışmada pretrained ağırlıkları/ilgili tokenizer dosyalarını indirir ve eğitimi başlatır. 100 adımın amacı veri loader, GPU, loss ve checkpoint yazımının çalıştığını görmektir; modelin görevi öğrenmesi beklenen sonuç değildir. CPU kullanacaksan `--device cpu`, Apple Silicon denemesinde `--device mps` ile komutu yeniden üret; desteklenmeyen işlem/bellek hatasını küçük koşuda yakala.

## 4. Gerçek fine-tuning komutu

Kaliteli veri ve çalışan smoke koşusundan sonra:

```bash
python examples/05_prepare_training.py \
  --root data/so101-pick-v1 \
  --repo-id local/so101-pick-v1 \
  --output-dir outputs/train/smolvla-pick-v1 \
  --steps 20000 \
  --batch-size 8 \
  --device cuda \
  --eval-split 0.2 \
  --save-command outputs/commands/smolvla-pick-v1.sh

bash outputs/commands/smolvla-pick-v1.sh
```

20.000 adım ve batch 8 burada başlangıç deneyidir; önerilen son optimum veya her GPU'da bellek garantisi değildir. `num_workers=0` ilk denemede hata görünürlüğünü artırır; veri yükleme darboğazı ölçülürse Linux'ta kademeli artır. `dataset.video_backend=pyav` seçimi bu atölyenin doğruladığı okuma yoludur.

Üretici yerel dataset ve çıktı yollarını mutlak yazar. Komutu Mac'ten Linux'a kopyalarsan yollar yanlış olabilir; hedef makinede aynı script ile yeniden üret.

## Parametreler ne yapıyor?

| Parametre | Etki |
|---|---|
| `policy.path=lerobot/smolvla_base` | Hazır SmolVLA checkpoint'inden başlatır |
| `train_expert_only=true` | Action expert odaklı fine-tuning seçimi |
| `freeze_vision_encoder=true` | Görsel encoder güncellemelerini dondurma seçimi |
| `train_state_proj=true` | State projeksiyonunun eğitimini açar |
| `steps` | Optimizer güncelleme sayısı; episode sayısı değildir |
| `batch_size` | Güncellemedeki örnek sayısı; bellek/zamanı etkiler |
| `dataset.eval_split` | Episode bazlı validation payı |
| `eval_steps` | Validation loss hesap sıklığı |
| `save_freq` | Checkpoint kayıt sıklığı |
| `policy.push_to_hub=false` | Eğitim sonunda otomatik Hub yüklemesini kapatır |
| `wandb.enable=false` | Bu örnekte dış deney izleyicisi kullanmaz |

“Expert” burada modelin eylem üreten bölümüdür; kayıt operatörüyle karıştırma. Bu seçim **LoRA değildir**. LoRA düşük rank adaptörler ekleyen ayrı bir eğitim yöntemidir; desteklenen hedef modülleri ve export/merge akışını doğrulamadan parametre sayısını azaltacağı varsayımıyla ekleme. [LeRobot SmolVLA](https://huggingface.co/docs/lerobot/en/smolvla)

## 5. Eğitim loglarını oku

Önce loss'un sonlu olduğunu, batch'in doğru kameraları içerdiğini ve adımların ilerlediğini gör. Eğitim kaybı düşerken validation yükseliyorsa aşırı uyum veya veri ayrımı etkisi olabilir. İkisi de kötü ise yanlış şema, görev karışıklığı, action birimi ve veri kalitesini kontrol et.

Adım süresinin büyük kısmı veri yüklemeyse GPU'yu büyütmek tek başına çözüm olmayabilir. GPU utilization, bellek ve veri okuma süresini birlikte izle. İlk sıcak başlangıç ve model indirmesini kararlı adım süresine karıştırma.

## 6. Checkpoint nerede?

LeRobot eğitim çıktısında `checkpoints/` altında adım klasörleri ve son checkpoint bağlantısı bulunur. Politika klasörü genellikle:

```text
outputs/train/smolvla-pick-v1/checkpoints/last/pretrained_model/
```

`config.json`, ağırlıklar, ön/son işlemci tanımları ve normalizasyon bilgilerini birlikte sakla. Tek `model.safetensors` dosyasını alıp bütün rollout bağlamı taşınmış gibi düşünme. **Tam resume** için optimizer/scheduler/RNG durumunu içeren eğitim checkpoint'i de gerekir.

```bash
lerobot-train \
  --config_path=outputs/train/smolvla-pick-v1/checkpoints/last/pretrained_model/train_config.json \
  --resume=true
```

Resume eski eğitime devam eder. Aynı ağırlıklardan yeni veri/ayarlarla fine-tuning başlatmak ayrı deneydir. [LeRobot eğitim/resume](https://huggingface.co/docs/lerobot/en/il_robots#train-a-policy)

## 7. Aynı veriyle ACT karşılaştırması

```bash
python examples/05_prepare_training.py \
  --policy act \
  --root data/so101-pick-v1 \
  --repo-id local/so101-pick-v1 \
  --output-dir outputs/train/act-pick-v1 \
  --device cuda \
  --steps 20000 \
  --batch-size 8 \
  --save-command outputs/commands/act-pick-v1.sh
```

Aynı veri/split ile kıyas başlar; eşit adım sayısı eşit hesaplama bütçesi anlamına gelmez. Model seçimini son training loss'a göre değil, [ayrılmış görev değerlendirmesine](degerlendirme.md) göre yap.
