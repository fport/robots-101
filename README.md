# SO-101 Atölyesi

Türkçe, uygulamalı SO-101 rehberi: MuJoCo, Strands Robots, donanım/teleop, LeRobot veri toplama, ACT, SmolVLA fine-tuning ve değerlendirme. MkDocs Material sitesi ve çalıştırılabilir Python alıştırmaları.

## Oku

Hazır ortamda:

```bash
make serve
```

**http://127.0.0.1:8000** adresini aç. Temiz kurulum:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-docs.txt -r requirements-sim.txt
make serve
```

## Dene

```bash
make doctor
make physics
make sim
.venv/bin/python examples/07_toy_behavior_cloning.py
```

SO-101 varlıkları ilk kullanımda indirilir. Scriptler proje altındaki `.cache/` dizinini kullanır. Sim PNG üretimi OpenGL erişimi ister; macOS pasif viewer için `mjpython` kullanılır.

## Veri ve eğitim ortamı

```bash
uv venv --python 3.12 .venv-ml
uv pip install --python .venv-ml/bin/python -r requirements-ml.txt
.venv-ml/bin/python examples/03_record_sim.py --root data/first-smoke
.venv-ml/bin/python examples/04_inspect_dataset.py data/first-smoke --expected-episodes 3
.venv-ml/bin/python examples/08_read_dataset.py --root data/first-smoke --repo-id local/sim-smoke
```

SmolVLA eğitim komutu `05_prepare_training.py` ile dataset metadata'sından üretilir. Ayrıntılar [eğitim sayfasında](docs/ogrenme/smolvla.md).

## Kontroller

```bash
make check
.venv-ml/bin/python -m unittest discover -s tests -v
```

Gerçek SO-101 render, 3 episode/90 frame LeRobot kaydı ve veri okuma yerelde sınandı. NumPy ile küçük BC modeli eğitildi. Tam SmolVLA GPU eğitimi ve fiziksel kol denemeleri yapılmadı. [Doğrulama kaydı](docs/basla/dogrulama.md).

Mock sim verisi yalnız arayüz/kayıt deneyi içindir; başarılı kavrama gösterimi değildir. Tarayıcıdaki iki eklemli mini laboratuvar SO-101 fizik simülasyonu değildir.

Ana kaynaklar: [Strands Robots](https://github.com/strands-labs/robots), [LeRobot](https://huggingface.co/docs/lerobot), [Hashtag Robotics](https://labs.hashtagrobotics.tr/so-101-robot-kol). Rehber satıcının resmî dokümanı değildir.
