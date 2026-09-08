# Değerlendirme ve çalıştırma

Modelin dosyaya kaydedilmesi öğrenilmiş görevin çalıştığını kanıtlamaz. Önce giriş/çıkış sözleşmesini, sonra inference gecikmesini ve en son görev başarısını sınarsın.

## Başarı tanımını önce yaz

Bu atölye için örnek görev tanımı: “Nesne başlangıç bölgesinden kaldırılacak, kaba bırakılacak, tutucu geri çekildikten sonra kapta iki saniye kalacak ve bütün işlem 25 saniye içinde bitecek.” Bunlar önerilen deney sınırlarıdır; görevüne göre değiştir ve test başlamadan sabitle.

Başarıyı şu işaretlerle karıştırma: motor hareket etti, script hata vermedi, inference 30 kere çağrıldı, kol kabın üstüne geldi. Her biri ayrı sistem ölçütüdür.

## Önce inference sözleşmesi

Checkpoint'in `config.json` dosyasındaki kamera adlarını ve state/action boyutlarını oku. Kalibrasyon ID'si, `use_degrees`, görüntü yerleşimi ve kontrol FPS eğitimdeki sözleşmeyle eşleşsin. Ön/son işlemci dosyalarını checkpoint'le birlikte kullan; normalize ağ çıktısını doğrudan motor hedefine verme.

Bir policy simde radyan eylemle eğitildiyse gerçek follower'ın normalize komut aralığına kendiliğinden uyduğunu varsayma. [Sim2real sözleşme kontrolü](../simulasyon/sim2real.md) tamamlanmadan gerçek transfer sonuçları yorumlanamaz.

## Gerçek kol için kısa rollout tarifi

**Bu komut fiziksel kolu hareket ettirir.** Kendi gerçek veri setinle eğitilmiş checkpoint, doğru kalibrasyon, doğrulanmış kameralar ve boş/kontrollü çalışma alanı gerekir. Aşağıdaki ilk 5 saniye görev başarısı testi değil, kontrollü hareket/girdi doğrulamasıdır.

```bash
source .venv-ml/bin/activate
export POLICY_PATH='outputs/train/smolvla-pick-v1/checkpoints/last/pretrained_model'

lerobot-rollout \
  --strategy.type=base \
  --policy.path="$POLICY_PATH" \
  --device=mps \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id="$FOLLOWER_ID" \
  --robot.use_degrees=false \
  --robot.max_relative_target=2 \
  --robot.cameras="$CAMERAS" \
  --task='Pick up the red cube and place it in the tray.' \
  --fps=30 \
  --duration=5
```

Mac örneğinde `device=mps` seçildi; uygun olmayan makinede `cpu` veya NVIDIA makinede `cuda` kullan. Bu cihazlarda gerçek zamanlı inference ölçülmedi. Modelin tek ileri geçişi hedef kontrol aralığından uzunsa senkron rollout yavaşlayabilir. Görsel/durum sözleşmesini doğruladıktan sonra gerçek süreyi ölç ve ilgili inference stratejisini seç. [LeRobot politika çalıştırma](https://huggingface.co/docs/lerobot/en/inference)

## Simde SmolVLA çalıştırma

Strands tarafında `sim.run_policy(..., policy_provider="lerobot_local", policy_config={...})` ile yerel checkpoint çağrılabilir. **Aşağıdaki parça entegrasyon şablonudur; mevcut robot/asset/action birimi için doğrulanmış VLA rollout değildir.**

```python
# Var olan, kameraları ve action sözleşmesi checkpoint ile eşleşen sim üzerinde:
result = sim.run_policy(
    robot_name="so101",
    policy_provider="lerobot_local",
    policy_config={
        "pretrained_name_or_path": "/ABSOLUTE/PATH/TO/pretrained_model",
        "device": "cpu",
        "strict_keys": True,
    },
    instruction="Pick up the red cube and place it in the tray.",
    control_frequency=30,
    n_steps=30,
)
```

Strands'in bu sağlayıcısı model yükleme güven kapısını isteyebilir; kullandığın paket dokümanında `STRANDS_TRUST_REMOTE_CODE` koşulunu oku ve yalnız kaynağını inceleyip güvendiğin checkpoint için etkinleştir. Bu bayrak kamera/birim hatalarını onarmaz. `strict_keys` hata üretirse rastgele kapatıp fallback'e güvenmek yerine eşlemeyi düzelt. [Strands LeRobot sağlayıcısı](https://github.com/strands-labs/robots/blob/main/docs/policies/lerobot-local.md)

## Ölçüm tablosu

`templates/evaluation.csv` dosyasını kopyala. Her denemeyi, başarısız olanları da, aynı tabloya yaz:

```csv
episode_id,condition,success,failure_reason,checkpoint,notes
1,A1,1,,step-10000,nesne kapta kaldı
2,A2,0,grasp_miss,step-10000,çene nesnenin yanına kapandı
3,A3,0,drop,step-10000,kaldırırken düştü
```

Bu satırlar **örnek veri**, gerçek robot sonucu değildir.

```bash
.venv/bin/python examples/06_evaluate_results.py outputs/evaluation.csv
```

Araç başarı oranını, başarısızlık dağılımını ve Wilson %95 aralığını hesaplar. Küçük deneme sayısında belirsizlik büyüktür. Farklı koşulları tek sayıya toplamak sorunu gizleyebilir; kamera/başlangıç bölgesi için ayrı CSV raporları da üret.

## İlk sonuç iyi değilse

**Hareket anlamsız:** action birimi/sırası ve stats. **Nesneyi ıskalıyor:** görüş, kalibrasyon, veri kapsamı. **Bırakmayı öğrenmiyor:** episode sonları/başarı gösterimi. **Birkaç adım sonra dağılıyor:** training dışı state, eylem ufku, toparlama eksikliği.

İkinci deneyde tek şeyi değiştir. Yeni veriyi eski veriyle karıştırmadan önce sürümle. Checkpoint seçmek için kullanılan validation ile son rapor testini birbirinden ayır.
