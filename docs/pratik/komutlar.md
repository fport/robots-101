# Komut defteri

Komutlar proje kökünde çalışır. İlk kurulum [kurulum sayfasında](../basla/kurulum.md), gerçek motor komutları [donanım bölümünde](../donanim/ilk-acilis.md) açıklanmıştır.

## Site

```bash
make serve
make build
```

İlk komut http://127.0.0.1:8000 adresinde okuma sunucusu açar. İkincisi `site/` üretir. GitHub Pages gibi statik barındırma servisine bu çıktı dağıtılabilir; bu projede dış site yayını yapılmadı.

## Robot olmadan

```bash
make doctor
make physics
make sim
```

`make sim` ilk model indirmesinde internet ve PNG için grafik bağlamı ister. Sadece fizik kontrolü için `make physics` daha küçük deneydir.

## Veri hattı

```bash
.venv-ml/bin/python examples/03_record_sim.py --root data/new-smoke
.venv-ml/bin/python examples/04_inspect_dataset.py data/new-smoke --expected-episodes 3
.venv-ml/bin/python examples/08_read_dataset.py --root data/new-smoke --repo-id local/sim-smoke
```

Mevcut root'a yeniden yazılmaz. Yeni denemede başka klasör seç.

## Küçük öğrenme deneyi

```bash
.venv/bin/python examples/07_toy_behavior_cloning.py --output outputs/toy-run-02
```

Bu gerçek bir küçük eğitim (training) deneyidir, SO-101/VLA modeli değildir.

## SmolVLA komutu üret

```bash
.venv-ml/bin/python examples/05_prepare_training.py \
  --root data/so101-pick-v1 \
  --repo-id local/so101-pick-v1 \
  --output-dir outputs/train/smolvla-v1 \
  --save-command outputs/commands/train-v1.sh
```

Bu satır eğitim başlatmaz. Hazır veri ve uygun cihazla oluşturulan dosyayı çalıştırmak için ML ortamını etkinleştirip `bash outputs/commands/train-v1.sh` kullan. Parametrelerin anlamı [SmolVLA bölümünde](../ogrenme/smolvla.md).

## Test sonucu raporla

```bash
.venv/bin/python examples/06_evaluate_results.py outputs/evaluation.csv
```

CSV'yi `templates/evaluation.csv` başlığına göre gerçek denemelerinle doldur.

## Yardım ve sürüm

```bash
.venv-ml/bin/lerobot-train --help
.venv-ml/bin/lerobot-record --help
.venv-ml/bin/lerobot-rollout --help
uv pip freeze --python .venv-ml/bin/python
```

Github `main` örneğindeki bir bayrak kurulmuş pakette yoksa önce sürüm farkını araştır. Bütün ortamı gelişigüzel güncellemek yerine bir sonraki deneme için ayrı ortam ve yeni sürüm dökümü kullan.
